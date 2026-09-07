# Handoff — fable-advisor codex lane 在 Windows 上不可用

生成时间：2026-08-09
工作区：`D:\Development\Local\harness`（harness 配置管理工作区，非应用代码库，无 build/lint/test）

## 一句话状态

Windows 下 fable-advisor 的 codex lane 恒定失败（`error_class: codex_unavailable`），根因已确认为 `run-codex.mjs` 的 spawn 未带 shell；**插件缓存副本已热修并端到端验证通过**；正式修复待由用户在插件开发仓库 `IpiggyI/fable-advisor` 落地并发版。

## 根因（已实测确认，非推断）

`scripts/run-codex.mjs` 两处 `spawn("codex", ...)` 未带 `shell`。Windows 上没有 `codex.exe`，PATH（`D:\Environment\nodejs\node_global`）里只有 npm shim。node v22.17.1 实测：

| 调用方式 | 结果 |
|---|---|
| `spawn("codex", ["--version"])` | `ENOENT` |
| `spawn("codex.cmd", ["--version"])` | `EINVAL`（Node 20.12+ 因 CVE-2024-27980 禁止无 shell 直接 spawn `.cmd`） |
| `spawn("codex", ["--version"], {shell:true})` | ✅ `codex-cli 0.146.0` |

`codexIsAvailable()` 拿到 ENOENT 即短路，codex 进程从未被启动。

补充结论：

- **不是回归**。缓存里 3.5.0 / 3.6.0 / 3.7.0 三份 `run-codex.mjs` 的 spawn 写法完全一致，Windows 上从未通过过。与历史文档 `docs/codex-implementer错误调用问题排查.txt` 记录的是两件不同的事。
- **grok lane 不受影响**：`grok` 是原生 `C:\Users\Shy\.grok\bin\grok.exe`，`spawn("grok",["--version"])` 实测正常。所以现象是"只有 Codex 挂"。
- 3.6.0 → 3.7.0 之间 `run-codex.mjs` 的唯一改动是 `--sandbox workspace-write` → `danger-full-access`（与本问题无关，但值得留意）。

## 已落的热修（仅缓存副本）

文件：`C:\Users\Shy\.claude\plugins\cache\fable-advisor\fable-advisor\3.7.0\scripts\run-codex.mjs`

1. 常量区新增 `const IS_WINDOWS = process.platform === "win32";`
2. `codexIsAvailable()` 之前新增 helper（含两行英文注释，匹配该文件既有的英文风格）：
   ```js
   function quoteForShell(argument) {
     return /[\s"^&|<>()%!]/u.test(argument) ? `"${argument.replace(/"/gu, '""')}"` : argument;
   }
   ```
3. `codexIsAvailable()`：`captureProcess("codex", ["--version"], { shell: IS_WINDOWS })`
4. `executeCodex()`：`spawn("codex", IS_WINDOWS ? args.map(quoteForShell) : args, { ..., shell: IS_WINDOWS, ... })`

未改动：`killProcessTree`（win32 分支的 `taskkill /T /F` 正好收掉 cmd.exe 整棵树）、`detached`、`run-grok.mjs`。

**为什么必须自己加引号**：`shell:true` 在 Windows 上把 args 原样拼接后交给 `cmd.exe`，不做任何转义。已实测 `--cd "D:\Program Files\my repo"` 经 shell 路径后子进程收到的 argv 与非 shell 路径逐字节相同。

## 验证证据

临时目录 `%TEMP%\fa-probe` 实跑 trivial spec（`gpt-5.6-terra` / effort `low` / 目标是创建 `hello.txt`），receipt 关键字段：

```json
"codex_session_id": "019fe6de-313c-7c62-8a93-80a04a9c0a0a",
"exit_status": 0,
"error_class": "complete",
"verification": [{ "command": "type hello.txt", "exit_code": 0, "output_tail": "ok\n" }]
```

`hello.txt` 确实由 codex 创建、内容为 `ok`。修复前同一调用返回 `codex_unavailable`。探针目录与临时测试脚本均已清理（不必去找）。

两个已排除的干扰项：`changed_files` 为空是因为临时目录不是 git 仓库（runner 已打印 `git status unavailable` 诊断）；codex 自述 `type hello.txt` 在 bash 里 not found，是它自己选了 bash 复述，runner 侧的 verification 走 cmd.exe，退出码 0 才是判据。

## 遗留工作（下一个会话的主线）

用户自述：由本人去插件开发仓库正式修复并发布新版本。若下个会话被要求协助：

1. 源仓库 `IpiggyI/fable-advisor`；本机 marketplace 克隆在 `C:\Users\Shy\.claude\plugins\marketplaces\fable-advisor`，排查时 HEAD 为 `219bbbd`、工作区干净。
2. 把上述热修等价改动落到源仓库的 `scripts/run-codex.mjs`，按仓库既有惯例考虑是否需要 ADR（`docs/adr/` 已有 0001–0009，codex lane 相关的是 0002/0003）与版本号 bump（`.claude-plugin/plugin.json`）。
3. **残留风险**：缓存热修会被下次 `/plugin update` 覆盖，届时 codex lane 静默退回 `codex_unavailable`。发版前若插件更新过，需要重新打补丁。
4. 授权边界：commit / push / 发版属于外部变更，必须在当次请求中显式授权后才执行。

## 关键路径速查

| 用途 | 路径 |
|---|---|
| 生效中的 runner（已热修） | `C:\Users\Shy\.claude\plugins\cache\fable-advisor\fable-advisor\3.7.0\scripts\run-codex.mjs` |
| 源仓库克隆 | `C:\Users\Shy\.claude\plugins\marketplaces\fable-advisor` |
| lane 使用文档 | 插件内 `skills/orchestration/SKILL.md`（codex lane 走查在 "Dialing the codex lane" 一节附近） |
| codex CLI shim | `D:\Environment\nodejs\node_global\codex.cmd`（实体入口 `node_modules\@openai\codex\bin\codex.js`） |

## 用户偏好（本次会话观察到）

- 结论要 action-first，先给路径/命令/改动，再解释；中文技术表述，不要客套。
- 修复前先给出根因与补丁方案，写宿主配置/插件文件属于需要授权的动作，要停下来问（用 `[需确认]` 标记）。
- **本次排查结论不要以"记忆"形式沉淀**，用本类 handoff 文档格式。

## Suggested skills

下个会话按需调用，不要一次全开：

- `sync-upstream` — 如果 `IpiggyI/fable-advisor` 是 fork（仓库内 `docs/adr/0001-upstream-sync-fork.md` 提示如此），正式修复前先同步上游，避免在过期基线上打补丁。
- `code-review` — 补丁落到源仓库后，对 diff 做标准/规格双轴复核；改动虽小但涉及跨平台进程启动与引号转义，值得一次复核。
- `diagnosing-bugs` — 仅当修复后 Windows 上又出现新的 codex lane 失败类别（`preparation_stalled` / `codex_failed` / `timeout`）时使用；当前的 `codex_unavailable` 已定性，无需重跑诊断循环。
- `fable-advisor:orchestration` — 若下个会话要实际驱动 codex/grok lane 派活，读它拿到 spec 五段式、receipt 判读与验收分级规则。
- 不建议用 `mem` / `mem-sync`：用户明确要求本次结论不进记忆库。
