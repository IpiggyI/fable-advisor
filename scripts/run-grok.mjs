#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createHash, randomBytes, randomUUID } from "node:crypto";
import { mkdir, readFile, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { createInterface } from "node:readline";

const DEFAULT_TIMEOUT_SEC = 600;
const PREPARATION_TIMEOUT_MS = 30_000;
const OUTPUT_TAIL_LENGTH = 2_000;
const MAX_TIMER_DELAY_MS = 2_147_483_647;
const SPEC_KEYS = new Set([
  "objective",
  "files",
  "interfaces",
  "constraints",
  "verification",
  "model",
  "timeout_sec",
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
  if (
    value.timeout_sec !== undefined
    && (typeof value.timeout_sec !== "number"
      || !Number.isFinite(value.timeout_sec)
      || value.timeout_sec <= 0)
  ) {
    throw new Error("timeout_sec must be a positive number");
  }

  return {
    objective: value.objective,
    files: value.files,
    interfaces: value.interfaces,
    constraints: value.constraints,
    verification: value.verification,
    model: value.model ?? null,
    timeout_sec: value.timeout_sec ?? DEFAULT_TIMEOUT_SEC,
  };
}

function renderPrompt(spec) {
  const files = spec.files.map((file) => `- ${file}`).join("\n");
  const verification = spec.verification.join("\n");

  return [
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
    [...stdout.matchAll(/^\s*\*\s+(\S+)/gm)].map((match) => match[1]),
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

    if (!state.eventObserved) {
      state.eventObserved = true;
      onEvent();
    }
    if (event === null || typeof event !== "object" || Array.isArray(event)) {
      return;
    }
    if (event.type === "text" && typeof event.data === "string") {
      state.grokFinalMessage += event.data;
    }
    if (event.type === "end") {
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
        state.grokSessionId = event.sessionId;
      }
    }
  });
}

async function executeGrok(spec, cwd, promptPath) {
  const sessionId = randomUUID();
  const state = {
    grokSessionId: sessionId,
    stopReason: null,
    usage: null,
    totalCostUsd: null,
    grokFinalMessage: "",
    eventObserved: false,
  };
  const args = [
    "--prompt-file", promptPath,
    "-m", spec.model,
    "--permission-mode", "acceptEdits",
    "--cwd", cwd,
    "--output-format", "streaming-json",
    "--session-id", sessionId,
  ];
  const child = spawn("grok", args, {
    detached: process.platform !== "win32",
    stdio: ["ignore", "pipe", "pipe"],
  });

  let failure = null;
  let exited = false;
  let clearPreparationTimer = () => {};
  const failAndKill = (errorClass) => {
    if (failure !== null || exited) return;
    failure = errorClass;
    void killProcessTree(child);
  };
  const clearWallTimer = createDeadlineTimer(
    spec.timeout_sec * 1_000,
    () => failAndKill("timeout"),
  );
  clearPreparationTimer = createDeadlineTimer(
    PREPARATION_TIMEOUT_MS,
    () => {
      if (!state.eventObserved) failAndKill("preparation_stalled");
    },
  );

  observeGrokEvents(child, state, () => clearPreparationTimer());
  child.stderr.pipe(process.stderr);

  const result = await new Promise((resolve) => {
    let spawnError = null;
    child.once("error", (error) => { spawnError = error; });
    child.once("close", (code, signal) => resolve({ code, signal, spawnError }));
  });
  exited = true;
  clearWallTimer();
  clearPreparationTimer();

  if (failure === null && (result.spawnError || result.code !== 0)) {
    failure = "grok_failed";
  } else if (failure === null && !state.eventObserved) {
    failure = "preparation_stalled";
  }

  return { ...state, childExitCode: result.code, errorClass: failure };
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
    return [];
  }
  return parseChangedFiles(result.stdout);
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
    grokSessionId: null,
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
    grok_session_id: state.grokSessionId,
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
  } catch (error) {
    diagnostic(`invalid spec: ${errorMessage(error)}`);
    state.errorClass = "spec_invalid";
    return emitReceipt(state);
  }

  const catalogResult = await captureProcess("grok", ["models"]);
  if (catalogResult.error || catalogResult.code !== 0) {
    const detail = catalogResult.error
      ? errorMessage(catalogResult.error)
      : catalogResult.stderr.trim() || `exit status ${catalogResult.code}`;
    diagnostic(`grok models failed: ${detail}`);
    state.errorClass = "grok_unavailable";
    return emitReceipt(state);
  }

  const { availableModels, defaultModel } = parseModelCatalog(catalogResult.stdout);
  if (availableModels.size === 0) {
    diagnostic("grok model catalog was unparseable");
    state.errorClass = "grok_unavailable";
    return emitReceipt(state);
  }
  if (spec.model !== null && !availableModels.has(spec.model)) {
    diagnostic(`invalid spec: model must be one of: ${[...availableModels].join(", ")}`);
    state.errorClass = "spec_invalid";
    return emitReceipt(state);
  }
  spec.model = spec.model ?? defaultModel;
  state.model = spec.model;

  let promptPath;
  try {
    const prompt = renderPrompt(spec);
    promptPath = await writePromptFile(prompt);
    const grokResult = await executeGrok(spec, state.cwd, promptPath);
    state.grokSessionId = grokResult.grokSessionId;
    state.stopReason = grokResult.stopReason;
    state.usage = grokResult.usage;
    state.totalCostUsd = grokResult.totalCostUsd;
    state.grokFinalMessage = grokResult.grokFinalMessage;
    state.childExitCode = grokResult.childExitCode;
    state.errorClass = grokResult.errorClass;
  } catch (error) {
    diagnostic(`grok execution failed: ${errorMessage(error)}`);
    state.errorClass = "grok_failed";
  } finally {
    if (promptPath !== undefined) {
      await removePromptFile(promptPath);
    }
  }

  state.changedFiles = await collectChangedFiles(state.cwd);
  if (state.errorClass !== "preparation_stalled" && state.errorClass !== "timeout") {
    state.verification = await runVerification(spec.verification, state.cwd);
    if (state.errorClass === null) {
      state.errorClass = state.verification.every((result) => result.exit_code === 0)
        ? "complete"
        : "verification_failed";
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

const exitCode = await main();
process.exitCode = exitCode;
