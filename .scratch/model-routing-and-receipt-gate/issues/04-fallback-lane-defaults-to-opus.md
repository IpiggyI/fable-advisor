# 04 — 兜底 lane 默认改 Opus

**What to build:** 两条 CLI lane 都不可用时，兜底 lane 跑 Opus 而不是 Sonnet。这不是锦上添花：本机 grok CLI 未认证，实际只有 codex 一条 CLI lane，codex 一挂就直接掉到兜底——它不是上游设想的「罕走兜底」，而是**第二顺位**。

改完后兜底 lane 与架构师同模型同单价，所以它的存在理由必须一并重写：省的不再是 token 单价，而是**架构师上下文的永久增长**——派出去的实现细节不进架构师上下文、不被每轮重读。这条论证不写进文档，orchestration 现有的成本纪律就会与默认值自相矛盾。

不提供 `model="sonnet"` 降级出口：兜底 lane 本就罕走，多一个没人会用却要每次判断的决策点没有价值。

驱动 grok CLI 的那个壳**不改**——它只做转发、取证和写报告，真正的 diff 审判在架构师手里，且该 lane 当前未认证闲置，为它付 Opus 单价没有收益。顾问 agent 也不改。

**Blocked by:** 01, 03 — 与 03 共用同几份文档，且本票的新论证要引用 03 定下的「架构师」称谓；并行会互相踩。

**Status:** ready-for-agent

**Spec:** `.scratch/model-routing-and-receipt-gate/spec.md`

- [x] 兜底 lane 的 agent frontmatter 默认模型为 `opus` 别名（跟随最新 Opus，非具体版本 pin）
- [x] agent 描述与正文中删除「Sonnet by default」及「高风险时用 `model="opus"`」整套叙述
- [x] agent 正文的存在理由改写为上下文隔离论证，明确它与架构师同族、无跨厂评审这一既有权衡保持不变
- [x] 文档明确不提供 sonnet 降级出口
- [x] orchestration 的成本纪律不再写「spend Sonnet on volume」之类与默认值矛盾的表述
- [x] orchestration 的 lanes 表中 Fallback 行的 producer 与路由说明同步更新
- [x] README 中兜底 lane 的模型叙事三处同步更新
- [x] 驱动 grok CLI 的壳与顾问 agent 的 model 字段**均未改动**
- [x] plugin 版本升至 3.3.0（默认模型是行为变更，不打 patch），description 中 in-house lane 的措辞同步
- [x] README 的版本升级说明补 v3.3 一句
- [x] 一致性检查：无残留的 "Sonnet by default"、"spend Sonnet on volume"、"model tiers shift down one"

## Comments

2026-07-25 — 已实现并通过双轴评审；验收清单逐项核对通过（回归证据见 tests/test_receipt_gate.py 7/7，决策记录见 docs/adr/0005）。
