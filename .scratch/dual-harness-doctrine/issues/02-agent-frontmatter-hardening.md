# 02 — agents 文件双 harness 加固与别名解析实测

**What to build:** `fable-advisor` 在 Cursor 侧获得真实生效的只读约束（`readonly: true`），两个 agent 的 Claude 模型别名（`fable`、`opus`）在 Cursor 的解析行为有实测结论并记录在案，Claude Code 侧行为不变。

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] `agents/fable-advisor.md` frontmatter 加 `readonly: true`，正文与 `tools:` 行不动
- [ ] 行为验证：Cursor 侧派发 fable-advisor 子代理，确认其无法编辑文件（推迟：子代理类型枚举于会话启动时固定，新 frontmatter 需插件更新后的新会话才被加载；`readonly` 语义有官方文档确认）
- [x] 实测 `model: fable` 与 `model: opus` 在 Cursor 的解析（解析为对应模型 / 回落 inherit），结论写入 ADR 0010（若 01 未完成则暂记本票 Comments，由 01 收编）
- [ ] Claude Code 侧回归：确认未知 frontmatter 字段被忽略、advisor 契约不变（未验证假设：需 Claude Code 会话实测，本会话不可达）

## Comments

2026-08-12 — 主体完成，两项验证留残留。实测结论（已入 ADR 0010 备注）：`model: fable` 在 Cursor 解析成功（子代理自报 "powered by Fable 5"，弱证据）；3.8.0 缓存版 advisor 在 Cursor 侧工具全开（含 Write/StrReplace/Delete/Shell），证实 `tools:` 字段被忽略、加 `readonly: true` 的必要性。`model: opus` 未单独实测，按同机制推定。两项未勾选验证的触发条件：插件更新到 3.9.0 后，各在 Cursor 新会话与 Claude Code 会话派发 advisor 一次即可关闭。
