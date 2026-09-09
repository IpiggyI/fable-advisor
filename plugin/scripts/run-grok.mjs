#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createHash, randomBytes, randomUUID } from "node:crypto";
import { mkdir, readFile, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { performance } from "node:perf_hooks";
import path from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

const DEFAULT_IDLE_TIMEOUT_SEC = 600;
const interruption = new AbortController();
const PREPARATION_TIMEOUT_MS = 30_000;
const OUTPUT_TAIL_LENGTH = 2_000;
const MAX_TIMER_DELAY_MS = 2_147_483_647;
const PREAMBLE_PATH = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "skills",
  "orchestration",
  "lane-preamble.md",
);
const SPEC_KEYS = new Set([
  "objective",
  "files",
  "interfaces",
  "constraints",
  "verification",
  "model",
  "timeout_sec",
  "idle_timeout_sec",
  "resume_session_id",
]);

function diagnostic(message) {
  process.stderr.write(`[run-grok] ${message}\n`);
}

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}

function parseArguments(argv) {
  let specPath;
  let cwd;

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument !== "--spec" && argument !== "--cwd") {
      return { specPath, cwd, error: `unknown argument: ${argument}` };
    }

    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      return { specPath, cwd, error: `missing value for ${argument}` };
    }
    if (argument === "--spec") {
      if (specPath !== undefined) {
        return { specPath, cwd, error: "--spec may only be provided once" };
      }
      specPath = value;
    } else {
      if (cwd !== undefined) {
        return { specPath, cwd, error: "--cwd may only be provided once" };
      }
      cwd = value;
    }
    index += 1;
  }

  if (specPath === undefined) {
    return { specPath, cwd, error: "--spec is required" };
  }
  return { specPath, cwd, error: null };
}

function requireString(value, name, { nonEmpty = false } = {}) {
  if (typeof value !== "string" || (nonEmpty && value.trim() === "")) {
    throw new Error(`${name} must be ${nonEmpty ? "a non-empty string" : "a string"}`);
  }
}

function requireStringArray(value, name, { nonEmptyItems = false, minLength = 0 } = {}) {
  if (!Array.isArray(value) || value.length < minLength) {
    throw new Error(`${name} must be an array with at least ${minLength} item(s)`);
  }
  for (const item of value) {
    requireString(item, `${name} item`, { nonEmpty: nonEmptyItems });
  }
}

function requirePositiveNumber(value, name) {
  if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) {
    throw new Error(`${name} must be a positive number`);
  }
}

function normalizeSpec(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("spec must be a JSON object");
  }

  const unknownKeys = Object.keys(value).filter((key) => !SPEC_KEYS.has(key));
  if (unknownKeys.length > 0) {
    throw new Error(`unknown top-level key(s): ${unknownKeys.join(", ")}`);
  }

  requireString(value.objective, "objective", { nonEmpty: true });
  requireStringArray(value.files, "files");
  requireString(value.interfaces, "interfaces");
  requireString(value.constraints, "constraints");
  requireStringArray(value.verification, "verification", {
    nonEmptyItems: true,
    minLength: 1,
  });

  if (value.model !== undefined) {
    requireString(value.model, "model");
  }
  if (value.timeout_sec !== undefined) {
    requirePositiveNumber(value.timeout_sec, "timeout_sec");
  }
  if (value.idle_timeout_sec !== undefined) {
    requirePositiveNumber(value.idle_timeout_sec, "idle_timeout_sec");
  }
  if (value.resume_session_id !== undefined) {
    requireString(value.resume_session_id, "resume_session_id", { nonEmpty: true });
  }

  return {
    objective: value.objective,
    files: value.files,
    interfaces: value.interfaces,
    constraints: value.constraints,
    verification: value.verification,
    model: value.model ?? null,
    timeout_sec: value.timeout_sec ?? null,
    idle_timeout_sec: value.idle_timeout_sec ?? DEFAULT_IDLE_TIMEOUT_SEC,
    resume_session_id: value.resume_session_id ?? null,
  };
}

function renderPrompt(spec, slug) {
  const files = spec.files.map((file) => `- ${file}`).join("\n");
  const verification = spec.verification.join("\n");

  return [
    `[fable-advisor] ${slug}`,
    "# Objective",
    spec.objective,
    "# Files",
    files,
    "# Interfaces",
    spec.interfaces,
    "# Constraints",
    spec.constraints,
    "# Verification",
    `\`\`\`bash\n${verification}\n\`\`\``,
    "Run the verification command and include its actual output in your final message.",
  ].join("\n\n");
}

function parseModelCatalog(stdout) {
  const availableModels = new Set(
    [...stdout.matchAll(/^\s*[-*]\s+(\S+)/gm)].map((match) => match[1]),
  );
  const defaultMatch = /^Default model:\s+(\S+)/m.exec(stdout);
  const defaultModel = defaultMatch?.[1] ?? availableModels.values().next().value;
  return { availableModels, defaultModel };
}

function createDeadlineTimer(delayMs, callback) {
  const deadline = Date.now() + delayMs;
  let handle;

  const schedule = () => {
    const remaining = deadline - Date.now();
    if (remaining <= 0) {
      callback();
      return;
    }
    handle = setTimeout(schedule, Math.min(remaining, MAX_TIMER_DELAY_MS));
  };

  schedule();
  return () => clearTimeout(handle);
}

function captureProcess(command, args, options = {}) {
  return new Promise((resolve) => {
    let child;
    try {
      child = spawn(command, args, { ...options, stdio: ["ignore", "pipe", "pipe"] });
    } catch (error) {
      resolve({ code: null, stdout: "", stderr: "", error });
      return;
    }

    let stdout = "";
    let stderr = "";
    let spawnError = null;
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.once("error", (error) => { spawnError = error; });
    child.once("close", (code) => resolve({ code, stdout, stderr, error: spawnError }));
  });
}

async function killProcessTree(child) {
  if (!child.pid) {
    return;
  }

  if (process.platform === "win32") {
    const result = await captureProcess("taskkill", ["/pid", String(child.pid), "/T", "/F"]);
    if (result.error || result.code !== 0) {
      diagnostic(`taskkill failed: ${errorMessage(result.error ?? result.stderr.trim())}`);
    }
    return;
  }

  try {
    process.kill(-child.pid, "SIGKILL");
  } catch (error) {
    if (error?.code !== "ESRCH") {
      diagnostic(`process-group kill failed: ${errorMessage(error)}`);
      try {
        child.kill("SIGKILL");
      } catch (fallbackError) {
        diagnostic(`child kill failed: ${errorMessage(fallbackError)}`);
      }
    }
  }
}

function observeGrokEvents(child, state, onEvent) {
  const lines = createInterface({ input: child.stdout, crlfDelay: Infinity });
  lines.on("line", (line) => {
    let event;
    try {
      event = JSON.parse(line);
    } catch {
      return;
    }

    const observedAt = performance.now();
    state.maxIdleMs = Math.max(
      state.maxIdleMs ?? 0,
      Math.floor(observedAt - state.lastEventAt),
    );
    state.lastEventAt = observedAt;

    state.eventObserved = true;
    onEvent();
    if (event === null || typeof event !== "object" || Array.isArray(event)) {
      return;
    }
    if (event.type === "text" && typeof event.data === "string") {
      state.grokFinalMessage += event.data;
    }
    if (event.type === "end") {
      state.terminalEventAt = Date.now();
      state.stopReason = typeof event.stopReason === "string" ? event.stopReason : null;
      state.usage = event.usage !== null
        && typeof event.usage === "object"
        && !Array.isArray(event.usage)
        ? event.usage
        : null;
      state.totalCostUsd = typeof event.total_cost_usd === "number"
        ? event.total_cost_usd
        : null;
      if (typeof event.sessionId === "string" && event.sessionId.trim() !== "") {
        if (event.sessionId !== state.grokSessionId) {
          diagnostic(
            `session id mismatch: injected ${state.grokSessionId}, event reported ${event.sessionId}`,
          );
        }
        if (!state.resumed) {
          state.grokSessionId = event.sessionId;
        }
      }
    }
  });
}

async function executeGrok(spec, cwd, promptPath) {
  const sessionId = spec.resume_session_id ?? randomUUID();
  const state = {
    grokSessionId: sessionId,
    stopReason: null,
    usage: null,
    totalCostUsd: null,
    grokFinalMessage: "",
    eventObserved: false,
    terminalEventAt: null,
    maxIdleMs: null,
    lastEventAt: null,
    resumed: spec.resume_session_id !== null,
  };
  const args = [
    "--prompt-file", promptPath,
    ...(spec.model !== null ? ["-m", spec.model] : []),
    "--permission-mode", "bypassPermissions",
    "--cwd", cwd,
    "--output-format", "streaming-json",
    ...(spec.resume_session_id === null
      ? ["--session-id", sessionId]
      : ["--resume", sessionId]),
  ];
  if (interruption.signal.aborted) {
    return { ...state, childExitCode: null, errorClass: "interrupted", endToCloseMs: null };
  }
  state.lastEventAt = performance.now();
  const child = spawn("grok", args, {
    detached: process.platform !== "win32",
    stdio: ["ignore", "pipe", "pipe"],
  });

  let failure = null;
  let exited = false;
  let termination = Promise.resolve();
  let clearIdleTimer = () => {};
  let clearPreparationTimer = () => {};
  const failAndKill = (errorClass) => {
    if (failure !== null || exited) return;
    failure = errorClass;
    termination = killProcessTree(child);
  };
  const armIdleTimer = () => {
    if (failure !== null || exited) return;
    clearIdleTimer();
    clearIdleTimer = createDeadlineTimer(
      spec.idle_timeout_sec * 1_000,
      () => failAndKill("idle_timeout"),
    );
  };
  const onInterrupt = () => failAndKill("interrupted");
  interruption.signal.addEventListener("abort", onInterrupt, { once: true });
  const clearWallTimer = spec.timeout_sec === null
    ? () => {}
    : createDeadlineTimer(
      spec.timeout_sec * 1_000,
      () => failAndKill("timeout"),
    );
  if (state.resumed) {
    armIdleTimer();
  } else {
    clearPreparationTimer = createDeadlineTimer(
      PREPARATION_TIMEOUT_MS,
      () => {
        if (!state.eventObserved) failAndKill("preparation_stalled");
      },
    );
  }

  observeGrokEvents(child, state, () => {
    clearPreparationTimer();
    armIdleTimer();
  });
  child.stderr.pipe(process.stderr);

  const result = await new Promise((resolve) => {
    let spawnError = null;
    child.once("error", (error) => { spawnError = error; });
    child.once("close", (code, signal) => resolve({ code, signal, spawnError }));
  });
  exited = true;
  interruption.signal.removeEventListener("abort", onInterrupt);
  clearWallTimer();
  clearIdleTimer();
  clearPreparationTimer();
  const endToCloseMs = state.terminalEventAt === null
    ? null
    : Math.max(0, Date.now() - state.terminalEventAt);
  await termination;

  if (failure === null && result.spawnError?.code === "ENOENT") {
    failure = "grok_unavailable";
  } else if (failure === null && (result.spawnError || result.code !== 0)) {
    failure = "grok_failed";
  } else if (failure === null && !state.eventObserved) {
    failure = "preparation_stalled";
  }

  return {
    ...state,
    childExitCode: result.code,
    errorClass: failure,
    endToCloseMs,
  };
}

function parseChangedFiles(output) {
  return output.split(/\r?\n/u).flatMap((line) => {
    if (line.length < 4) return [];
    const status = line.slice(0, 2);
    let file = line.slice(3);
    if (status.includes("R") || status.includes("C")) {
      const renameSeparator = file.lastIndexOf(" -> ");
      if (renameSeparator !== -1) {
        file = file.slice(renameSeparator + 4);
      }
    }
    return file === "" ? [] : [file];
  });
}

async function collectChangedFiles(cwd) {
  const result = await captureProcess("git", ["-C", cwd, "status", "--porcelain"]);
  if (result.error || result.code !== 0) {
    diagnostic(`git status unavailable: ${errorMessage(result.error ?? result.stderr.trim())}`);
    return { files: [], failed: true };
  }
  return { files: parseChangedFiles(result.stdout), failed: false };
}

function appendTail(current, chunk) {
  const combined = current + chunk;
  return combined.length <= OUTPUT_TAIL_LENGTH
    ? combined
    : combined.slice(-OUTPUT_TAIL_LENGTH);
}

function runVerificationCommand(command, cwd) {
  return new Promise((resolve) => {
    let child;
    try {
      child = spawn(command, { cwd, shell: true, stdio: ["ignore", "pipe", "pipe"] });
    } catch (error) {
      resolve({ command, exit_code: 1, output_tail: errorMessage(error) });
      return;
    }

    let outputTail = "";
    let spawnError = null;
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => { outputTail = appendTail(outputTail, chunk); });
    child.stderr.on("data", (chunk) => { outputTail = appendTail(outputTail, chunk); });
    child.once("error", (error) => { spawnError = error; });
    child.once("close", (code) => {
      if (spawnError) outputTail = appendTail(outputTail, errorMessage(spawnError));
      resolve({ command, exit_code: code ?? 1, output_tail: outputTail });
    });
  });
}

async function runVerification(commands, cwd) {
  const results = [];
  for (const command of commands) {
    results.push(await runVerificationCommand(command, cwd));
  }
  return results;
}

function initialState(startedAt) {
  return {
    specHash: null,
    cwd: process.cwd(),
    model: null,
    modelRequested: null,
    modelUsed: null,
    fallbackReason: null,
    grokSessionId: null,
    resumedFrom: null,
    endToCloseMs: null,
    maxIdleMs: null,
    idleTimeoutSec: null,
    timeoutSec: null,
    stopReason: null,
    usage: null,
    totalCostUsd: null,
    childExitCode: null,
    startedAt,
    errorClass: null,
    changedFiles: [],
    verification: [],
    grokFinalMessage: null,
  };
}

function buildReceipt(state) {
  const exitStatus = state.childExitCode ?? null;
  return {
    receipt_version: 1,
    spec_hash: state.specHash,
    cwd: state.cwd,
    producer: "grok",
    model: state.model,
    model_requested: state.modelRequested,
    model_used: state.modelUsed,
    fallback_reason: state.fallbackReason,
    grok_session_id: state.grokSessionId,
    resumed_from: state.resumedFrom,
    end_to_close_ms: state.endToCloseMs,
    max_idle_ms: state.maxIdleMs,
    idle_timeout_sec: state.idleTimeoutSec,
    timeout_sec: state.timeoutSec,
    stop_reason: state.stopReason,
    usage: state.usage,
    total_cost_usd: state.totalCostUsd,
    started_at: state.startedAt,
    finished_at: new Date().toISOString(),
    exit_status: exitStatus,
    error_class: state.errorClass,
    changed_files: state.changedFiles,
    verification: state.verification,
    grok_final_message: state.grokFinalMessage,
  };
}

async function emitReceipt(state) {
  const receipt = buildReceipt(state);
  const json = `${JSON.stringify(receipt, null, 2)}\n`;

  if (state.specHash !== null) {
    const receiptDirectory = path.join(state.cwd, ".fable-advisor", "receipts");
    const receiptPath = path.join(receiptDirectory, `${state.specHash}.json`);
    try {
      await mkdir(receiptDirectory, { recursive: true });
      await writeFile(receiptPath, json, "utf8");
    } catch (error) {
      diagnostic(`could not write receipt ${receiptPath}: ${errorMessage(error)}`);
    }
  }

  process.stdout.write(json);
  return receipt.error_class === "complete" ? 0 : 1;
}

async function loadSpec(specPath, state) {
  const raw = await readFile(specPath);
  state.specHash = createHash("sha256").update(raw).digest("hex");
  return normalizeSpec(JSON.parse(raw.toString("utf8")));
}

async function writePromptFile(contents) {
  const suffix = randomBytes(16).toString("hex");
  const promptPath = path.join(tmpdir(), `grok-prompt-${process.pid}-${suffix}.md`);
  await writeFile(promptPath, contents, { encoding: "utf8", mode: 0o600, flag: "wx" });
  return promptPath;
}

async function removePromptFile(promptPath) {
  try {
    await unlink(promptPath);
  } catch (error) {
    diagnostic(`could not remove prompt file ${promptPath}: ${errorMessage(error)}`);
  }
}

async function main() {
  const state = initialState(new Date().toISOString());
  const parsedArguments = parseArguments(process.argv.slice(2));
  if (parsedArguments.cwd !== undefined) {
    state.cwd = path.resolve(parsedArguments.cwd);
  }
  if (parsedArguments.error) {
    diagnostic(parsedArguments.error);
    state.errorClass = "spec_invalid";
    return emitReceipt(state);
  }

  let spec;
  try {
    spec = await loadSpec(parsedArguments.specPath, state);
    state.model = spec.model;
    state.modelRequested = spec.model;
    state.modelUsed = spec.model;
    state.grokSessionId = spec.resume_session_id;
    state.resumedFrom = spec.resume_session_id;
    state.idleTimeoutSec = spec.idle_timeout_sec;
    state.timeoutSec = spec.timeout_sec;
  } catch (error) {
    diagnostic(`invalid spec: ${errorMessage(error)}`);
    state.errorClass = "spec_invalid";
    return emitReceipt(state);
  }

  let preamble;
  try {
    preamble = await readFile(PREAMBLE_PATH, "utf8");
  } catch (error) {
    diagnostic(`could not read lane preamble ${PREAMBLE_PATH}: ${errorMessage(error)}`);
    return 1;
  }

  const catalogResult = await captureProcess("grok", ["models"]);
  const catalogReadable = !catalogResult.error
    && catalogResult.code === 0;
  const { availableModels } = catalogReadable
    ? parseModelCatalog(catalogResult.stdout)
    : { availableModels: new Set() };

  if (!catalogReadable || availableModels.size === 0) {
    const detail = catalogResult.error
      ? errorMessage(catalogResult.error)
      : catalogResult.code !== 0
        ? (catalogResult.stderr.trim() || `exit status ${catalogResult.code}`)
        : "empty or unparseable output";
    diagnostic(
      `grok model catalog unavailable (${detail}) — skipping model validation; availability is decided by the real run`,
    );
    state.model = spec.model;
  } else {
    if (spec.model !== null && !availableModels.has(spec.model)) {
      diagnostic(`invalid spec: model must be one of: ${[...availableModels].join(", ")}`);
      state.errorClass = "spec_invalid";
      return emitReceipt(state);
    }
    state.model = spec.model;
  }

  const slug = path.basename(parsedArguments.specPath, ".json");
  let promptPath;
  try {
    const prompt = `${preamble}\n\n${renderPrompt(spec, slug)}`;
    promptPath = await writePromptFile(prompt);
    const grokResult = await executeGrok(spec, state.cwd, promptPath);
    state.grokSessionId = grokResult.grokSessionId;
    state.stopReason = grokResult.stopReason;
    state.usage = grokResult.usage;
    state.totalCostUsd = grokResult.totalCostUsd;
    state.grokFinalMessage = grokResult.grokFinalMessage;
    state.childExitCode = grokResult.childExitCode;
    state.errorClass = grokResult.errorClass;
    state.endToCloseMs = grokResult.endToCloseMs;
    state.maxIdleMs = grokResult.maxIdleMs;
  } catch (error) {
    diagnostic(`grok execution failed: ${errorMessage(error)}`);
    state.errorClass = "grok_failed";
  } finally {
    if (promptPath !== undefined) {
      await removePromptFile(promptPath);
    }
  }

  const changedFilesResult = await collectChangedFiles(state.cwd);
  state.changedFiles = changedFilesResult.files;
  if (interruption.signal.aborted) state.errorClass = "interrupted";
  if (state.errorClass !== "preparation_stalled"
    && state.errorClass !== "timeout"
    && state.errorClass !== "idle_timeout"
    && state.errorClass !== "interrupted") {
    state.verification = await runVerification(spec.verification, state.cwd);
    if (state.errorClass === null) {
      if (!state.verification.every((result) => result.exit_code === 0)) {
        state.errorClass = "verification_failed";
      } else if (changedFilesResult.failed) {
        state.errorClass = "git_status_failed";
      } else if (spec.files.length > 0 && state.changedFiles.length === 0) {
        state.errorClass = "no_diff";
      } else {
        state.errorClass = "complete";
      }
    }
  }

  const exitCode = await emitReceipt(state);
  if (state.errorClass === "complete") {
    const resolvedSpecPath = path.resolve(parsedArguments.specPath);
    const pendingDirectory = path.resolve(state.cwd, ".fable-advisor", "pending");
    const relativeSpecPath = path.relative(pendingDirectory, resolvedSpecPath);
    const isPendingSpec = relativeSpecPath !== ""
      && relativeSpecPath !== ".."
      && !relativeSpecPath.startsWith(`..${path.sep}`)
      && !path.isAbsolute(relativeSpecPath);
    if (isPendingSpec) {
      try {
        await unlink(resolvedSpecPath);
        diagnostic(`cleared pending spec ${resolvedSpecPath}`);
      } catch (error) {
        diagnostic(`could not clear pending spec ${resolvedSpecPath}: ${errorMessage(error)}`);
      }
    }
  }
  return exitCode;
}

const onInterrupt = () => interruption.abort();
process.on("SIGTERM", onInterrupt);
process.on("SIGINT", onInterrupt);
try {
  process.exitCode = await main();
} finally {
  process.removeListener("SIGTERM", onInterrupt);
  process.removeListener("SIGINT", onInterrupt);
}
