# Claude Code 中的 CLI lane —— runner，而非 agent

在 Claude Code 中派发 lane 之前阅读本文。两条 CLI lane 都没有 wrapper agent：架构师通过确定性 runner 直接驱动两个生产者——没有 subagent 启动成本，也没有可能悄悄自行实现的 wrapper。Routine lane 需要 [Grok CLI](https://x.ai/cli)；Cross-vendor lane 需要 codex CLI 与 Node。In-house lane 是 `implementer` agent——一次普通的 subagent 派发，无 runner——从而在两条 CLI 都缺失时保持插件自包含。

两条 CLI lane 流程相同；以 codex 演练为典范，grok 的差异紧随其后。

## 0. 前言到达每一条 lane

两条 runner 都读取 `<plugin-root>/skills/orchestration/lane-preamble.md`（相对它们自己的目录 `<plugin-root>/scripts/` 解析），并将其原文前置到 lane 提示，排在五个部分之前。前言缺失会使 runner 在拉起任何东西之前以非零退出——执行侧契约从不被静默丢掉。不要把前言粘进 spec；spec 只携带契约。

## 1. 撰写 spec

从干净的工作树开始——`git status --porcelain` 为空。runner 用 `git status` 检测 lane 的变更，因此预先存在的脏状态会让空跑看起来像做了工作（见下文 `no_diff`）。

把五部 spec 写成 JSON，写入目标仓库的 `.fable-advisor/pending/<slug>.json`：

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-6-astra", "effort": "medium", "service_tier": "fast", "timeout_sec": 600
}
```

调谐字段可选，且失败即响——越界值或未知顶层键会被拒绝为 `spec_invalid`，从不被静默强制转换。receipt 记录实际使用的值。

- `model` — `gpt-6-astra`（默认）或 `gpt-5.6-luna`；codex 目录是静态白名单，因此已退役的名字是 `spec_invalid`。
- `effort` — `model_reasoning_effort`：`low | medium | high | xhigh | max`。默认随模型：astra → `medium`，luna → `max`。建议用法（准则，不强制）：astra 用 `medium` 或 `high`；luna 只用 `max`。
- `service_tier` — 省略则用 Codex 自己的默认；仅在以质量换速度时用 `"fast"`。
- `timeout_sec` — 用于杀掉卡住进程的墙钟；不是等待策略。
- `resume_session_id` — 先前的 codex session id；见下文「返工票」。

把 codex lane 按质量优先来调：选*哪一条* lane 是成本优先（grok 是默认，且 lane 级比较按默认拨盘给 codex 计价，即 astra 配 `medium`），但一旦任务值得走 codex lane，在其内部做一次质量上调是负担得起的。对异常困难的任务升到 `high`。Luna 不是进入 codex lane 的更便宜路径：仅在用户声明时请求它，或当任务简单且本来就要 GPT 家族时。

**回退。** 若 astra 在会话建立之前失败（`preparation_stalled`，或尚无 session id 的 `codex_failed`），runner 按 luna 的默认 effort 在 luna 上重试一次；receipt 显示 `model_requested: gpt-6-astra`、`model_used: gpt-5.6-luna`，以及非空的 `fallback_reason`。一旦会话已存在则不回退——半成品运行不会在另一模型上重做。直接请求 luna 从不回退。验收一次发生过回退的运行时，用你自己的话复述降级；receipt 负责披露，你负责承认。

## 2. 运行 runner

本 skill 的基目录是 `<plugin-root>/skills/orchestration`，因此 runner 在上两级：

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. 等待 runner

lane 完成于 **runner 进程退出** —— 不是事件流出现 `end` 事件时，也不是一次 sleep 到期时。等待方式只有两种，没有第三种：

- 在前台运行 runner，让 Bash 在退出时返回。
- 若已后台化，对该 Bash 任务调用 `TaskOutput(task_id, block=true)`。

完成证据是 pending 文件消失，或 receipt 出现在 `.fable-advisor/receipts/` 下。绝不要用 `sleep N` 再 `ls .fable-advisor/pending/` 充当等待——固定睡眠会在 runner 已经退出之后继续烧完整段间隔。`timeout_sec` 只杀掉卡住的进程；Bash 的 `timeout` 只封顶一次前台阻塞。对于并行 lane，逐条 block 每个后台任务，或在同一条消息里前台运行各 runner。

## 4. 裁决 receipt

runner 把 receipt 打印到 stdout，并写入 `.fable-advisor/receipts/<spec_hash>.json`：

- `error_class` — `complete | spec_invalid | codex_unavailable | preparation_stalled | timeout | codex_failed | verification_failed | no_diff | git_status_failed`。
- `codex_session_id` — 绑定到所拉起进程的事件流，不受并发会话串扰；在恢复运行上它等于被恢复的 id。
- `model_requested`、`model_used`、`fallback_reason`（无回退时为 null）、`resumed_from`（无恢复时为 null）、`end_to_close_ms`（终止事件到进程 close；未见终止事件时为 null——这是诊断，不是门禁）。
- `changed_files`，外加核验命令的实际退出码与输出尾部。

`no_diff` 意味着 `files` 非空且没有任何变更；pending 文件保留。在普通 spec 上这是一次静默空跑——去查。在返工票上，当 lane 发现缺陷无法复现时，这是预期答案：读报告、删除 pending 文件，并说明。`git_status_failed` 意味着 runner 无法判定改了什么；它不是 `complete`。

CLI lane 验收 = `error_class: complete`、非空 session id、可对照工作树抽查的核验输出，**并且** diff 通过 [SKILL.md](SKILL.md) 中的分层验收。缺失或非 complete 的 receipt 即未完成。

对于第 3 层评审，OpenAI Codex 插件的 `/codex:adversarial-review`（有 schema 支撑的裁决，只读沙箱）是现成的上下文干净 reviewer。

receipt 由机械强制执行：插件 Stop hook（**receipt gate**）在 `.fable-advisor/pending/` 下任何 spec 缺少 `complete` receipt 时阻止结束。一旦 `complete`，runner 自行删除 pending spec。若你放弃或改道一项 pending 任务，删除其 pending 文件并显式说明——绝不让 gate 成为唯一知情者。gate 强制的是 receipt 的存在；其内容仍由你裁决。

把 `.fable-advisor/` 加入目标仓库的 `.gitignore`——receipt 内嵌命令输出。receipt 按 spec 哈希键控，因此带不同 spec 文件的并行 runner 调用不会碰撞；「挑选更强 diff」的竞速是两个 runner 作为后台 Bash，对同一 spec 内容使用两个不同的 pending 文件。

## 返工票

返工票是一份新的五部 pending 文件，携带 `resume_session_id` —— 被返工那次运行的 `codex_session_id`（或 `grok_session_id`）。runner 调用 `codex exec resume <id>`（grok：`--resume <id>`），因此 lane 保留它已经付过的上下文；receipt 记录 `resumed_from`，其 session id 等于被恢复的那个。Objective = 缺陷，Files = 原范围，Verification = 失败的那条检查——里面不写修复方案（形态见 [SKILL.md](SKILL.md)）。两轮失败之后，任务在新会话中重走阶段 1：省略 `resume_session_id`。

## Grok 差异

`scripts/run-grok.mjs` —— 同一 CLI 契约（`--spec`、`--cwd`），同一前言，同一 pending/receipt 流程，同一 receipt gate，同一等待协议。

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec 键：五个部分加上可选的 `model`、`timeout_sec` 和 `resume_session_id` 而已——没有 `effort`/`service_tier`（grok CLI 没有这些旋钮）。
- `model` —— 默认省略：未设置则不发送 `-m` 标志，因此 CLI 跑自己的默认并跟踪实时目录（当前为 grok-4.6，2026-09），世代更换时 spec 零改动。仅在有意挑选 `grok models` 列出的非默认目录条目时才设置。当目录可读时，`model` 对照每一个列出的条目校验——不在目录中的模型是 `spec_invalid`。目录不可读不是 `grok_unavailable`：runner 记录一条诊断、跳过校验，由真正的运行决定可用性。
- 错误类镜像 codex lane（`grok_unavailable | grok_failed | …`，外加 `no_diff` 与 `git_status_failed`）。receipt 携带同样的 `model_requested` / `model_used` / `fallback_reason` / `resumed_from` / `end_to_close_ms` 字段（`fallback_reason` 保持 null——grok lane 没有定义模型回退），并额外记录 grok 结束事件中的 `usage` 与 `total_cost_usd`。`grok_session_id` 由 runner 注入（`--session-id`），而非从流中嗅探。

## 派发，而非探测

切勿预先探测 CLI 的认证状态（例如 `grok models` 登录快照之类）：grok CLI 只在真正运行时刷新登录，且用户侧的提供商配置可以完全绕过认证，因此登出快照不是该 lane 宕机的证据。预检最多可检查安装（`which grok`）。把 spec 路由出去，让 runner 的 receipt 决定——`*_unavailable` 触发 [SKILL.md](SKILL.md) 中的改道规则。
