# 01 — orchestration skill 双 harness 改写 + ADR 0010

**What to build:** Cursor 会话读到的 orchestration skill 直接指导它用 Task 钉模型委派四条车道（Routine → Grok 4.5，Cross-vendor → GPT-5.6 Sol，In-house → Opus，Judgment → fable-advisor），五部 spec 作子代理 prompt、报告带内返回、三层验收照旧；Claude Code 会话读到的 runner/receipt 流程语义零变化。决策与实测证据落成 ADR 0010。

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] `skills/orchestration/SKILL.md` 车道表 Invoke 列按 harness 双写；新增 harness 判别与 Cursor 调用小节；Parallelism 补单消息并行 Task 一句
- [x] Claude Code 节（runner、pending/receipt、receipt gate、dispatch-not-probes、Handoff）经路径限定 diff 审读确认零语义改动
- [x] `docs/adr/0010-dual-harness-single-source.md` 新建：单源双 harness 决策、Cursor 兼容路径加载实测证据、复盘条件
- [x] 活体干跑验证：Cursor 会话 Task 钉 Grok 4.5 与 GPT-5.6 Sol 各完成一个五部 spec 只读任务，报告过 Tier 1 抽查
- [x] `tests/test_receipt_gate.py` 保持绿（未触碰）

## Comments

2026-08-12 — 已实现。干跑证据为同日会话两次实测（Grok 4.5 分析 receipt-gate.py、GPT-5.6 Sol 分析 run-grok.mjs，行号抽查全对）；diff 审读确认 Claude Code 节仅标题加 "(Claude Code)" 标注与表格单元格 harness 前缀，正文零改动；回归 7/7 passed（脚本为自带 runner，`python3 tests/test_receipt_gate.py` 直跑，非 pytest 收集）。准则散文按 stage 1（spec 无法承载的判断）由架构师亲写，未委派。
