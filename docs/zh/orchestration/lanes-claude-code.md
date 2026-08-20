> 中文对照版，不参与部署，以英文版为准。权威版本：plugin/skills/orchestration/lanes-claude-code.md

# Claude Code 中的 CLI lane —— runner，而非 agent（The CLI lanes in Claude Code — runners, not agents）

在 Claude Code 中派发 lane 之前阅读本文。两条 CLI lane 都没有 wrapper agent：架构师通过确定性 runner 直接驱动两个生产者——没有 subagent 启动成本，也没有可能悄悄自行实现的 wrapper。Routine lane 需要 [Grok CLI](https://x.ai/cli)；Cross-vendor lane 需要 codex CLI 与 Node。In-house lane（仓内车道）是 `implementer` agent——一次普通的 subagent 派发，无 runner——从而在两条 CLI 都缺失时保持插件自包含。

两条 CLI lane 流程相同；以 codex 演练为典范，grok 的差异紧随其后。

## 1. 撰写 spec（1. Write the spec）

把五部 spec 写成 JSON，写入目标仓库的 `.fable-advisor/pending/<slug>.json`：

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-5.6-sol", "effort": "high", "service_tier": "fast", "timeout_sec": 600
}
```

三个调谐字段可选，且失败即响——越界值或未知顶层键会被拒绝为 `spec_invalid`，从不被静默强制转换。receipt 记录实际使用的值。

- `model` — `gpt-5.6-sol`（默认，≈ 旗舰）、`gpt-5.6-terra`（≈ Sonnet）或 `gpt-5.6-luna`（≈ Haiku）。
- `effort` — `model_reasoning_effort`：`low | medium | high | xhigh | max`，默认 `high`。
- `service_tier` — 省略则用 Codex 自己的默认；仅在以质量换速度时用 `"fast"`。

把 codex lane 按质量优先来调：选*哪一条* lane 仍是成本优先（grok 是默认），但一旦任务值得走 codex lane，在其内部做一次质量上调是负担得起的。默认 `gpt-5.6-sol` 配 `high`；仅对异常困难的任务把 effort 升到 `xhigh`/`max`（二者都会明显拖慢完成）；仅当 codex 家族任务确实简单时才降到 `terra`/`luna` 或更低 effort——这并不取代 grok 作为常规默认。

## 2. 运行 runner（2. Run the runner）

本 skill 的基目录是 `<plugin-root>/skills/orchestration`，因此 runner 在上两级：

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. 裁决 receipt（3. Judge the receipt）

runner 把 receipt 打印到 stdout，并写入 `.fable-advisor/receipts/<spec_hash>.json`：`error_class`（`complete | spec_invalid | codex_unavailable | preparation_stalled | timeout | codex_failed | verification_failed`）、`codex_session_id`（绑定到所拉起进程的事件流——不受并发会话串扰）、`changed_files`，以及核验命令的实际退出码与输出尾部。

CLI lane 验收 = `error_class: complete`、非空 session id、可对照工作树抽查的核验输出，**并且** diff 通过 [SKILL.md](SKILL.md) 中的分层验收。缺失或非 complete 的 receipt 即未完成。

对于第 3 层评审，OpenAI Codex 插件的 `/codex:adversarial-review`（有 schema 支撑的裁决，只读沙箱）是现成的上下文干净 reviewer。

receipt 由机械强制执行：插件 Stop hook（**receipt gate**）在 `.fable-advisor/pending/` 下任何 spec 缺少 `complete` receipt 时阻止结束。一旦 `complete`，runner 自行删除 pending spec。若你放弃或改道一项 pending 任务，删除其 pending 文件并显式说明——绝不让 gate 成为唯一知情者。gate 强制的是 receipt 的存在；其内容仍由你裁决。

把 `.fable-advisor/` 加入目标仓库的 `.gitignore`——receipt 内嵌命令输出。receipt 按 spec 哈希键控，因此带不同 spec 文件的并行 runner 调用不会碰撞；「挑选更强 diff」的竞速是两个 runner 作为后台 Bash，对同一 spec 内容使用两个不同的 pending 文件。

## Grok 差异（Grok deltas）

`scripts/run-grok.mjs` —— 同一 CLI 契约（`--spec`、`--cwd`），同一 pending/receipt 流程，同一 receipt gate。

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec 键：五个部分加上可选的 `model` 与 `timeout_sec` 而已——没有 `effort`/`service_tier`（grok CLI 没有这些旋钮）。
- `model` —— 默认省略：未设置则不发送 `-m` 标志，因此 CLI 跑自己的默认并跟踪实时目录（今日为 grok-4.6），世代更换时 spec 零改动。仅在有意挑选 `grok models` 列出的非默认目录条目时才设置。当目录可读时，`model` 对照每一个列出的条目校验——不在目录中的模型是 `spec_invalid`。目录不可读不是 `grok_unavailable`：runner 记录一条诊断、跳过校验，由真正的运行决定可用性。
- 错误类镜像 codex lane（`grok_unavailable | grok_failed | …`）。receipt 额外记录 grok 结束事件中的 `usage` 与 `total_cost_usd`，且 `grok_session_id` 由 runner 注入（`--session-id`），而非从流中嗅探。

## 派发，而非探测（Dispatch, not probes）

切勿预先探测 CLI 的认证状态（例如 `grok models` 登录快照之类）：grok CLI 只在真正运行时刷新登录，且用户侧的提供商配置可以完全绕过认证，因此登出快照不是该 lane 宕机的证据。预检最多可检查安装（`which grok`）。把 spec 路由出去，让 runner 的 receipt 决定——`*_unavailable` 触发 [SKILL.md](SKILL.md) 中的改道规则。
