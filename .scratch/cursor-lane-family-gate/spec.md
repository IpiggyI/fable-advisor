# Cursor 车道家族门（lane family gate）

Cursor 用户级 `preToolUse` hook：`Task` 派发 `fable-advisor` / `implementer` 时必须钉对家族模型；省略或 `inherit` 必须 deny。`explore` / `generalPurpose` 的 inherit 放行。`resume` 不重查模型。

仓库留档（权威脚本，不随插件分发）在 `cursor-hooks/`，见 [ADR 0011](../../docs/adr/0011-cursor-lane-family-gate-user-level.md)。活体仍在用户目录，不在 `plugin/hooks/`（那边只有 Claude Code 的 receipt-gate）：

- Windows：`C:\Users\Shy\.cursor\hooks\fable-lane-family-gate.py`、`C:\Users\Shy\.cursor\hooks.json`
- WSL：`/home/hyy/.cursor/hooks/`（`hooks.json` 与 Windows 份已分叉）

## Tickets

- [01-unpinned-fable-advisor-not-denied](./issues/01-unpinned-fable-advisor-not-denied.md) — 2026-08-18 Windows + Grok 会话：`fable-advisor` + `inherit` 未拦截
