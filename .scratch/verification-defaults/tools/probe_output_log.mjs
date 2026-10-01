// 探针：从 runner 源码取出 appendTail、monitorProcess、openVerificationLog、runVerificationCommand，
// 配模拟子进程和慢写入端（每块延迟 20 毫秒），检查 output_log 的行为。
// 用法：node probe_output_log.mjs <plugin/scripts/run-grok.mjs 或 run-codex.mjs> <slow-exit | cap>
//   slow-exit：命令输出 1 MiB 后退出，写盘还没跟上。期望日志完整，日志与尾部都含 FINAL-MARKER。
//   cap：命令输出 40 MiB，写盘落后超过 16 MiB。期望 output_log 为 null，诊断打出，
//        不完整的文件被删除，尾部仍含 FINAL-MARKER。
// 下面的常量照抄 runner；runner 改了这些常量或函数名，探针要跟着改。
import * as fs from "node:fs";
import path from "node:path";
import { tmpdir } from "node:os";
import { EventEmitter } from "node:events";
import { PassThrough, Writable } from "node:stream";
import { unlink } from "node:fs/promises";

const [file, scenario] = process.argv.slice(2);
const src = fs.readFileSync(file, "utf8");
const grab = (name) => src.match(new RegExp(`^(?:async )?function ${name}\\b[\\s\\S]*?\\n}\\n`, "m"))[0];
const body = ["appendTail", "monitorProcess", "openVerificationLog", "runVerificationCommand"].map(grab).join("\n");
const consts = "const OUTPUT_TAIL_LENGTH = 2000; const PROCESS_GRACE_MS = 2000; const LOG_QUEUE_LIMIT = 16 * 1024 * 1024; let forcedCleanup = false;";
const diagnostics = [];
let writer, maxQueued = 0, written = [];
const createWriteStream = (p) => {
  fs.writeFileSync(p, "");
  writer = new Writable({ highWaterMark: 16384, write(chunk, enc, cb) { written.push(chunk); setTimeout(cb, 20); } });
  return writer;
};
const total = scenario === "cap" ? 40 * 1024 * 1024 : 1024 * 1024;
const chunk = "x".repeat(scenario === "cap" ? 65536 : 4096);
const spawn = () => {
  const child = new EventEmitter();
  child.pid = 4242; child.unref = () => {}; child.kill = () => {};
  child.stdout = new PassThrough(); child.stderr = new PassThrough();
  child.stdio = [null, child.stdout, child.stderr];
  let ended = 0;
  for (const s of [child.stdout, child.stderr]) s.on("end", () => { if (++ended === 2) setImmediate(() => child.emit("close", 3, null)); });
  setImmediate(async () => {
    for (let sent = 0; sent < total; sent += chunk.length) {
      child.stdout.write(chunk);
      if (writer) maxQueued = Math.max(maxQueued, writer.writableLength);
      if (sent % (chunk.length * 16) === 0) await new Promise((r) => setImmediate(r));
    }
    child.stdout.end("\nFINAL-MARKER\n"); child.stderr.end();
    child.emit("exit", 3, null);
  });
  return child;
};
const run = new Function("spawn", "createWriteStream", "path", "diagnostic", "errorMessage", "unlink",
  `${consts}\n${body}\nreturn runVerificationCommand;`)(spawn, createWriteStream, path,
  (m) => diagnostics.push(m), (e) => (e instanceof Error ? e.message : String(e)), unlink);
const dir = fs.mkdtempSync(path.join(tmpdir(), "p3-"));
const started = Date.now();
const result = await run("fake", dir, "probe.log");
const log = Buffer.concat(written.map((c) => Buffer.from(c))).toString();
console.log(JSON.stringify({
  runner: path.basename(file), scenario, ms: Date.now() - started,
  exit_code: result.exit_code, output_log: result.output_log,
  tail_has_final: result.output_tail.includes("FINAL-MARKER"),
  log_bytes: log.length, log_has_final: log.includes("FINAL-MARKER"),
  max_queued: maxQueued, partial_file_exists: fs.existsSync(path.join(dir, "probe.log")),
  diagnostics,
}));
