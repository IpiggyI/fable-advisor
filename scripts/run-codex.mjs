#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createHash, randomBytes } from "node:crypto";
import { mkdir, readFile, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { createInterface } from "node:readline";

const DEFAULT_MODEL = "gpt-5.6-sol";
const DEFAULT_EFFORT = "high";
const DEFAULT_TIMEOUT_SEC = 600;
const SESSION_TIMEOUT_MS = 30_000;
const OUTPUT_TAIL_LENGTH = 2_000;
const MAX_TIMER_DELAY_MS = 2_147_483_647;
const SPEC_KEYS = new Set([
  "objective",
  "files",
  "interfaces",
  "constraints",
  "verification",
  "model",
  "effort",
  "timeout_sec",
]);

function diagnostic(message) {
  process.stderr.write(`[run-codex] ${message}\n`);
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
  if (value.effort !== undefined && typeof value.effort !== "string") {
    throw new Error("effort must be a string");
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
    model: value.model ?? DEFAULT_MODEL,
    effort: value.effort === "xhigh" ? "xhigh" : DEFAULT_EFFORT,
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

function isSessionId(value) {
  return typeof value === "string" && value.trim() !== "";
}

const SESSION_EXTRACTORS = [
  (event) => event.thread_id,
  (event) => event.session_id,
  (event) => event.rollout_id,
  (event) => event.session?.session_id,
  (event) => event.session?.thread_id,
  (event) => event.msg?.session_id,
  (event) => event.msg?.thread_id,
  (event) => event.msg?.session?.session_id,
  (event) => event.msg?.session?.thread_id,
  (event) => event.msg?.payload?.session_id,
  (event) => event.msg?.payload?.thread_id,
  (event) => event.payload?.session_id,
  (event) => event.payload?.thread_id,
  (event) => event.payload?.session?.session_id,
  (event) => event.payload?.session?.thread_id,
];

function extractSessionId(event) {
  for (const extract of SESSION_EXTRACTORS) {
    const candidate = extract(event);
    if (isSessionId(candidate)) {
      return candidate;
    }
  }
  return null;
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

async function codexIsAvailable() {
  const result = await captureProcess("codex", ["--version"]);
  return result.error === null;
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

function observeCodexEvents(child, state, onSession) {
  const lines = createInterface({ input: child.stdout, crlfDelay: Infinity });
  lines.on("line", (line) => {
    let event;
    try {
      event = JSON.parse(line);
    } catch {
      return;
    }

    if (state.codexSessionId === null) {
      const sessionId = extractSessionId(event);
      if (sessionId !== null) {
        state.codexSessionId = sessionId;
        onSession();
      }
    }
    if (event.type === "item.completed" && event.item?.type === "agent_message") {
      if (typeof event.item.text === "string") {
        state.codexFinalMessage = event.item.text;
      }
    }
  });
}

async function executeCodex(spec, cwd, promptContents) {
  const state = { codexSessionId: null, codexFinalMessage: null };
  const args = [
    "exec",
    "--json",
    "--model", spec.model,
    "-c", `model_reasoning_effort=${spec.effort}`,
    "--sandbox", "workspace-write",
    "--skip-git-repo-check",
    "--cd", cwd,
  ];
  const child = spawn("codex", args, {
    detached: process.platform !== "win32",
    stdio: ["pipe", "pipe", "pipe"],
  });

  let failure = null;
  let exited = false;
  let clearSessionTimer = () => {};
  const failAndKill = (errorClass) => {
    if (failure !== null || exited) return;
    failure = errorClass;
    void killProcessTree(child);
  };
  const clearWallTimer = createDeadlineTimer(
    spec.timeout_sec * 1_000,
    () => failAndKill("timeout"),
  );
  clearSessionTimer = createDeadlineTimer(
    SESSION_TIMEOUT_MS,
    () => {
      if (state.codexSessionId === null) failAndKill("preparation_stalled");
    },
  );

  observeCodexEvents(child, state, () => clearSessionTimer());
  child.stderr.pipe(process.stderr);
  child.stdin.on("error", (error) => diagnostic(`codex stdin failed: ${errorMessage(error)}`));
  child.stdin.end(promptContents);

  const result = await new Promise((resolve) => {
    let spawnError = null;
    child.once("error", (error) => { spawnError = error; });
    child.once("close", (code, signal) => resolve({ code, signal, spawnError }));
  });
  exited = true;
  clearWallTimer();
  clearSessionTimer();

  if (failure === null && (result.spawnError || result.code !== 0)) {
    failure = "codex_failed";
  } else if (failure === null && state.codexSessionId === null) {
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
    model: DEFAULT_MODEL,
    effort: DEFAULT_EFFORT,
    codexSessionId: null,
    childExitCode: null,
    startedAt,
    errorClass: null,
    changedFiles: [],
    verification: [],
    codexFinalMessage: null,
  };
}

function buildReceipt(state) {
  const exitStatus = state.childExitCode ?? null;
  return {
    receipt_version: 1,
    spec_hash: state.specHash,
    cwd: state.cwd,
    producer: "codex",
    model: state.model,
    effort: state.effort,
    codex_session_id: state.codexSessionId,
    started_at: state.startedAt,
    finished_at: new Date().toISOString(),
    exit_status: exitStatus,
    error_class: state.errorClass,
    changed_files: state.changedFiles,
    verification: state.verification,
    codex_final_message: state.codexFinalMessage,
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
  const promptPath = path.join(tmpdir(), `codex-prompt-${process.pid}-${suffix}.md`);
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
    state.effort = spec.effort;
  } catch (error) {
    diagnostic(`invalid spec: ${errorMessage(error)}`);
    state.errorClass = "spec_invalid";
    return emitReceipt(state);
  }

  if (!(await codexIsAvailable())) {
    diagnostic("codex is not available on PATH");
    state.errorClass = "codex_unavailable";
    return emitReceipt(state);
  }

  let promptPath;
  try {
    const prompt = renderPrompt(spec);
    promptPath = await writePromptFile(prompt);
    const promptContents = await readFile(promptPath);
    const codexResult = await executeCodex(spec, state.cwd, promptContents);
    state.codexSessionId = codexResult.codexSessionId;
    state.codexFinalMessage = codexResult.codexFinalMessage;
    state.childExitCode = codexResult.childExitCode;
    state.errorClass = codexResult.errorClass;
  } catch (error) {
    diagnostic(`codex execution failed: ${errorMessage(error)}`);
    state.errorClass = "codex_failed";
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
