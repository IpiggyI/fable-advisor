# 02 — agents 文件双 harness 加固与别名解析实测

**What to build:** `fable-advisor` 在 Cursor 侧获得真实生效的只读约束（`readonly: true`），两个 agent 的 Claude 模型别名（`fable`、`opus`）在 Cursor 的解析行为有实测结论并记录在案，Claude Code 侧行为不变。

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] `agents/fable-advisor.md` frontmatter 加 `readonly: true`，正文与 `tools:` 行不动
- [x] 行为验证：Cursor 侧派发 fable-advisor 子代理，确认其无法编辑文件 → **测试完成，结果为证伪**：`readonly: true` 对插件兼容路径加载的 agent 既未剥离可变工具也未拦截调用（用户第一方实测，2026-08-12，插件 3.9.0）。归档见 ADR 0010 追记；Cursor 侧只读性降级为行为约定
- [x] 实测 `model: fable` 与 `model: opus` 在 Cursor 的解析 → **结论反转**：frontmatter `model:` 对插件兼容路径 agent 不被采纳，裸派发 inherit 父模型；落到 Fable 需 dispatch 级显式钉 `claude-fable-5-thinking-high`（用户第一方实测；早先探针因从 Fable 父会话发出而不可判别，作废）。见 ADR 0010 第二批追记
- [ ] Claude Code 侧回归：确认未知 frontmatter 字段被忽略、advisor 契约不变（未验证假设：需 Claude Code 会话实测，本会话不可达）

## Comments

2026-08-12 — 主体完成，两项验证留残留。实测结论（已入 ADR 0010 备注）：`model: fable` 在 Cursor 解析成功（子代理自报 "powered by Fable 5"，弱证据）；3.8.0 缓存版 advisor 在 Cursor 侧工具全开（含 Write/StrReplace/Delete/Shell），证实 `tools:` 字段被忽略、加 `readonly: true` 的必要性。`model: opus` 未单独实测，按同机制推定。两项未勾选验证的触发条件：插件更新到 3.9.0 后，各在 Cursor 新会话与 Claude Code 会话派发 advisor 一次即可关闭。

2026-08-12（第二次）— Cursor 侧行为验证回报：`readonly: true` 无机制效力（工具清单未剥离、调用未拦截）。加固目标未达成，但 flag 保留（无害，解析行为改善即自动生效）；证伪与降级措辞归档于 ADR 0010 追记，README "mechanically enforced" 措辞已更正。`.cursor/agents/` 原生定义入口未测。剩余残留仅 Claude Code 侧回归一项。

2026-08-12（第三次）— 第二项证伪回报：裸派发 `fable-advisor` inherit 父模型，frontmatter `model:` 不被采纳；SKILL.md Cursor 节改为"每次派发显式钉模型"，README 同步，版本 3.9.1。详见 ADR 0010 第二批追记。
