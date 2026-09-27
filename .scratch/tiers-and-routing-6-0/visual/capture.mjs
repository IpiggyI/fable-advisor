// 视觉验收截图：node capture.mjs <html 路径> <输出 png> <宽> <高> [元素 id]
// 经 Chrome DevTools 协议把指定 id 的元素滚到视口顶端后截图；不给 id 时截页首。
// 无头浏览器路径可用环境变量 CHROME 覆盖。
import { spawn } from "node:child_process";
import { writeFile, mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const [file, out, width, height, anchor] = process.argv.slice(2);
if (!file || !out || !width || !height) {
  console.error("usage: node capture.mjs <html> <png> <width> <height> [id]");
  process.exit(2);
}
const chrome = process.env.CHROME
  ?? `${process.env.HOME}/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome`;
const port = 9300 + Math.floor(Math.random() * 500);
const profile = await mkdtemp(path.join(tmpdir(), "capture-"));
const child = spawn(chrome, [
  "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    target = list.find((t) => t.type === "page");
  } catch { /* browser still starting */ }
}
if (!target) { child.kill(); throw new Error("devtools endpoint not reachable"); }

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let seq = 0;
const pending = new Map();
const events = [];
ws.onmessage = (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  else if (msg.method) events.push(msg.method);
};
const send = (method, params = {}) => new Promise((r) => {
  const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params }));
});

try {
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride",
    { width: Number(width), height: Number(height), deviceScaleFactor: 1, mobile: Number(width) < 600 });
  await send("Page.navigate", { url: `file://${path.resolve(file)}` });
  for (let i = 0; i < 50 && !events.includes("Page.loadEventFired"); i++) await sleep(100);
  if (anchor) {
    const r = await send("Runtime.evaluate", {
      expression: `(() => { const e = document.getElementById(${JSON.stringify(anchor)});
        if (!e) return false; e.scrollIntoView({ block: "start", behavior: "instant" }); return true; })()`,
      returnByValue: true,
    });
    if (r.result?.result?.value !== true) throw new Error(`id not found: ${anchor}`);
  }
  await sleep(800);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  await writeFile(out, Buffer.from(shot.result.data, "base64"));
  console.log(`wrote ${out}`);
} finally {
  ws.close();
  child.kill();
}
