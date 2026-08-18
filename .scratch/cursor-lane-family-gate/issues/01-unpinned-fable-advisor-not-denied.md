# 01 — 未钉模型的 fable-advisor 未被拦截

**What to build:** `Task` 派发 `subagent_type=fable-advisor` 且未钉 Fable 家族模型（省略 `model`，或 `model=inherit`）时，hook 必须 deny：用户看到拦截文案，agent 收到钉 slug 的指示。先取证现场 stdin，再按证据改接线；不要先改 `decide()` 的家族规则。

**Blocked by:** None

Type: task
Status: ready-for-agent
Date: 2026-08-18
Harness: Cursor Windows（漏拦会话）

完成标准：再派一次不钉模型的 `fable-advisor` 被拦；钉当轮 allowlist 里带 `fable` 的 slug（例如 `claude-fable-5-thinking-xhigh`）放行；`explore` / `generalPurpose` 的 inherit 仍放行；`resume` 仍跳过检查。

## 现场（已核实）

1. 会话 transcript `C:\Users\Shy\.cursor\projects\d-Development-Local-skills\agent-transcripts\ec446abc-0819-4b4c-b596-d2f21ff62c6f\ec446abc-0819-4b4c-b596-d2f21ff62c6f.jsonl` 第 12 行，`tool_use.name=Task`，`input` 键为 `description` / `model` / `prompt` / `subagent_type`：
   - `subagent_type` = `fable-advisor`
   - `model` = `inherit`
   - `model` 键存在（不是省略）
2. 子代理跑完：同目录 `subagents\92c8429d-6a77-4c84-bf4a-a9f4d3c08ddb.jsonl`
3. `C:\Users\Shy\.cursor\hooks.json` 已挂 `preToolUse`，`matcher` 为 `Task`，命令为 `python C:/Users/Shy/.cursor/hooks/fable-lane-family-gate.py`，**无** `failClosed`
4. `fable-lane-family-gate.py` 的 `decide()` 对 `{subagent_type: fable-advisor, model: inherit}` 返回 `deny`（`--self-test` 第 4 条；2026-08-18 本机复跑 `self-test ok 9`）
5. deny 日志路径 `C:\Users\Shy\.cursor\hooks\logs\fable-lane-family-gate.jsonl`：目录存在、文件不存在。脚本只在 `permission=="deny"` 时写日志 → **deny 分支未执行**

WSL 另有 `/home/hyy/.cursor/hooks/` 与另一份 `hooks.json`（与 Windows 份不是同一文件）。本次漏拦发生在 Windows Cursor。未点名不要改 WSL 用户级 `hooks.json`。

## 不是原因（已排除）

- 不是「`inherit` 没写进 deny 条件」。条件已覆盖 omitted / 空串 / `inherit`。
- 不是「拦了但 Cursor 丢弃 deny」。若进了 deny 会有 jsonl 行；没有。
- 不是本仓 `plugin/hooks/receipt-gate.py`（Claude Code Stop / pending receipt）。本次是 Cursor 用户级 `preToolUse`。

## 脚本 fail-open（已本地复现）

`main()` 只把 `payload["tool_input"]` 当 dict。不是 dict 就当成 `{}`，`subagent_type` 读空，**静默 allow、不写日志**。

| stdin 形状 | `decide` 实际看到 | 结果 |
|---|---|---|
| `{tool_name: Task, tool_input: {subagent_type, model: inherit}}` | 完整 tool_input | deny |
| 扁平：`{subagent_type, model, prompt, ...}`（无 `tool_input` 键） | `{}` | allow |
| `{tool_name: Task, toolInput: {...}}` | `{}` | allow |
| `{tool_name: Task, arguments: {...}}` | `{}` | allow |
| `{tool_name: Task, tool_input: "<json string>"}` | `{}` | allow |

另：非 0/2 退出且未设 `failClosed` → Cursor 默认放行。stdin 空、JSON 坏、`python` 起不来，都与「无 deny 日志 + 子代理仍跑」相容。

## 未闭合假设（必须先探针）

按「无 deny 日志」只知道没进 deny。三选一，现场 stdin 才能定：

1. **hook 没跑**：`matcher` `Task` 对不上现场 `tool_name`；或这条 Grok Task 路径不走 `preToolUse`。
2. **hook 跑了，payload 不是 `tool_input` dict**：走上表静默 allow。
3. **`decide` 之前进程 fail-open**：同样无日志。

脚本头注释「Cursor 3.16.17，2026-08-17，preToolUse 看见 omitted model 且认 deny」**不能**当作 2026-08-18 这条 Windows + Grok 调用已进同一管道。那是前一日记录；测试会话还提到 WSL 路径 `/home/hyy/.cursor/hooks/`。

## 实施步骤

### 1. 取证 stdin

改 `main()`：解析前后都把一条 JSONL 追加到 `logs/fable-lane-family-gate.jsonl`（allow 也写）。每条至少含：

- `ts`
- `phase`: `raw` | `parsed` | `decision`
- `hook_event_name`、`tool_name`、payload 顶层键列表
- `tool_input` 的 Python 类型；若是 dict 则键列表 + `subagent_type` + `model`；若是 str 则前 200 字
- `permission`（decision 行）
- `raw_bytes` 或完整 `raw`（取证期可以；修完后可改为只留 parsed 摘要）

完成标准：再派一次 `fable-advisor` + `inherit`（或省略 `model`）后，日志里至少有一行，能读出 `tool_name` 与 `tool_input` 形状。若完全无新行 → 假设 1 或 3，不要再猜形状。

临时把 `matcher` 去掉、或改成同时匹配 `Task|task`，只能作为假设 1 的对照实验，并在本票 Comments 记下哪次有日志。

### 2. 按证据修接线

- 假设 1：让事件真的打到脚本（确认 `preToolUse` 的现场 `tool_name`；必要时加 `subagentStart` **仅作观测**——2026-08-17 记录过 `subagentStart` 的 deny 不拦进程，不能当唯一门）。`failClosed: true` 只在确认命令稳定能跑之后再加。
- 假设 2：归一化输入后再交给现有 `decide()`。至少覆盖：`tool_input` dict、JSON 字符串、`toolInput`、`arguments`、以及 `subagent_type` 在顶层的扁平 payload。顶层 `model` 是**父会话**模型（文档如此），**不要**拿它当子代理钉模型。
- 假设 3：先让 hook 进程在 Cursor hook 环境里对 stdin 回显成功；再考虑 `failClosed` 与 `python`/`py`/`python3` 解析。

不要改 `FAMILY`、不要把 `explore` inherit 改成 deny、不要对 `resume` 再查模型。

### 3. 回归

用脚本自测覆盖现有 9 例，并加上归一化层用例（上表五种 stdin）。再用一次真 Task：

- deny：`fable-advisor` + 省略/`inherit`/`cursor-grok-4.6-xhigh`
- allow：`fable-advisor` + 当轮 allowlist 里含 `fable` 的 slug
- allow：`explore` inherit
- allow：带 `resume` 的续跑

完成标准：deny 路径写出日志且子代理不启动；allow 路径子代理启动。取证期的全量 raw 日志若过大，回归通过后收窄到 deny + 一份 parsed 摘要，并在本票 Comments 记下取证结论（哪条假设、现场 `tool_name`、现场键名）。

## 不要做

- 不要用「父会话已是旗舰所以 inherit 无损」当放行理由。漏拦会话父模型是 Grok 4.6，正是 hook 要防的静默降级。
- 不要先改 `decide()` 里的家族 token 来绕过漏拦。
- 未经用户点名不要改 `/home/hyy/.cursor/hooks.json`。Windows 与 WSL 的用户级 `hooks.json` 已经分叉。

## 证据指针

- hook：`C:\Users\Shy\.cursor\hooks\fable-lane-family-gate.py`
- 配置：`C:\Users\Shy\.cursor\hooks.json`
- 本会话 Task：transcript `ec446abc-0819-4b4c-b596-d2f21ff62c6f.jsonl` 第 12 行
- 子代理产物：同目录 `subagents\92c8429d-6a77-4c84-bf4a-a9f4d3c08ddb.jsonl`
- Cursor hooks 文档：`preToolUse` 输入含 `tool_name` + `tool_input` 对象；顶层 `model` 是父会话模型；`subagentStart` 另有 `subagent_type` / `subagent_model`（2026-08-18 查 [hooks.md](https://cursor.com/docs/hooks.md)）

## Comments

### 2026-08-18 接线结论（WSL 会话落地脚本，Windows 真 Task 仍待验）

Cursor hook 日志（`workspaceId-3eb39591`，2026-08-18T02:16:33Z）已经是现场 stdin：

- 假设 1 否：`python C:/Users/Shy/.cursor/hooks/fable-lane-family-gate.py` 跑了，exit 0，658ms。
- 假设 2 否：INPUT 是 `tool_name=Task` + `tool_input={model: inherit, subagent_type: fable-advisor}`。
- 假设 3 收敛：OUTPUT 是恰好 `{"permission":"allow"}`。同一份 INPUT 用 Windows Python `subprocess` 喂进去是 **deny**；空 stdin 才是 **allow**。`decide()` 没漏 inherit。

同一步 `preToolUse` 并行 3 个 Task hook（项目 `inject-subagent-context`、本门、claude-project 同脚本）。Cursor 的 INPUT 日志是「打算派发的载荷」，不是子进程读到的字节。

顾问 [fable-advisor](05b65163-9a3a-46d8-ab75-4191e9927479) 选 A：Task 匹配的门对空/坏 stdin fail-closed；`stdin.buffer` UTF-8；stdout `ensure_ascii=True`；JSONL 记 `raw_len`。不改 `decide()` / `FAMILY`，不改 WSL `hooks.json`。两份 `.py` 已同步。

空 stdin 的 deny 文案与「未钉模型」分开。若 Windows 上兄弟 hook 抢走 stdin，所有 Task 都会被拦并带 `raw_len=0`——响的失败，用来定案假设 1；下一步才是项目侧 matcher。

自测：`python …/fable-lane-family-gate.py --self-test` → `self-test ok 21`（WSL python3 与 Windows python 各一次）。漏拦 payload 回放现为 deny。

WSL 本会话真 Task（`raw_len` 均 >0，stdin 到了）：

- deny：`fable-advisor` + `inherit`（文案是未钉模型，不是空 stdin）
- deny：`fable-advisor` + `cursor-grok-4.6-xhigh`
- allow：`fable-advisor` + `claude-fable-5-thinking-xhigh`
- allow：`explore` + `inherit`
- allow：带 `resume` 的 `fable-advisor` + `inherit`

待椰椰在 **Windows Cursor / skills 仓** 再派一次不钉模型的 `fable-advisor`：看拦截文案、子代理是否未启动、`C:\Users\Shy\.cursor\hooks\logs\fable-lane-family-gate.jsonl` 新行的 `raw_len` / `reason`。`raw_len=0` 或 `reason=empty_stdin` 就坐实兄弟 hook 抢 stdin；`raw_len>0` 且未钉模型 deny 则本票在 Windows 也收口。

### 2026-08-18 UTF-8 BOM（Windows 钉 fable 仍被拦）

现场（用户报告，第一方 JSONL）：

- 两次 `fable-advisor` + `claude-fable-5-thinking-low` 均 deny，文案是「未收到 Task 参数」。
- `2026-08-18T06:02:08Z` `raw_len=1418` `reason=json_decode` `Unexpected UTF-8 BOM (decode using utf-8-sig)`
- `06:02:24Z` 同错，`raw_len=1055`
- 对照 `03:32Z` 无 BOM 时能解出信封。不是没钉模型，是 BOM 让 fail-close 误报。

脚本改为 `utf-8-sig` 解码；JSON 解析失败与空 stdin 分文案。两份 `.py` 已同步。`decide()` / WSL `hooks.json` 仍未改。

### 2026-08-18 grok `4.6` slug 拆 JSON（文案不再说 BOM）

现场 JSONL：

- `06:20:08Z` / `06:21:02Z`：`raw_len=851`，`Expecting ',' delimiter: line 1 column 186`。钉的是 `cursor-grok-4.6-medium`。
- 同结构 `kimi-k3-max`（`raw_len=837`）能解析并按错家族 deny。
- `06:17:26Z`：长 prompt `raw_len=1450` 同类 delimiter 错。Cursor 日志里的 INPUT 是合法对象；子进程读到的字节不是。签名与 `"cursor-grok-"4.6"-medium"`（`4.6` 变成 JSON 数字）一致。

脚本：解析失败文案改为带 decoder 原文、明确「不是家族校验」；日志加 `error_at`；对这种被拆开的 version slug 做窄修复后再 `decide()`；仍解不开则尽量从原文抽 `subagent_type`/`model`。不改 `FAMILY`，不改 WSL `hooks.json`。长 prompt 若把后续键也吃掉，仍会 fail-close，那是 Cursor 信封问题。

### 2026-08-18 仓库留档

权威脚本入 `cursor-hooks/fable-lane-family-gate.py`（与两侧活体逐字节一致）。不进 `plugin/`，不 bump 版本，不改两侧活体 `hooks.json`。见 [ADR 0011](../../../docs/adr/0011-cursor-lane-family-gate-user-level.md)。
