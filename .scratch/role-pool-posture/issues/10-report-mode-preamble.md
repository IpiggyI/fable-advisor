# 10: 报告模式的执行侧契约 —— 前言按 `mode` 分流

**What to build:** 报告模式（explorer / advisor）下车道读到的执行侧契约不再自相矛盾。现状：runner 在报告模式下仍前置 `lane-preamble.md`（"你持有 Files 范围内的交付物 … 以 `WORKER REPORT` 结尾"），再叠一段 runner 内联的只读 overlay（`run-grok.mjs` / `run-codex.mjs` 的 "Report mode: act as a read-only explorer or advisor…"）。两段对同一车道说了相反的事，且 overlay 文本散落在两条 runner 里，违背 ADR 0013 "执行侧契约单源" 的初衷（code-review Standards 轴 2026-09-12 标记为 Divergent Change）。目标：worker 前言与报告前言各自单源、按 `mode` 选用；Cursor 侧派 explorer / advisor 时也指向报告前言。

**Blocked by:** 09（发布后再动运行时文本，避免与 5.0.0 同批）

**Status:** needs-triage

来源：`/code-review` Standards 轴对 `25ddc8d...HEAD` 的判断项；ADR 0014 决策九、十一。范围：`plugin/skills/orchestration/`（新增报告前言文件或在 `lane-preamble.md` 内分节）、两条 runner 的前言加载、`lanes-claude-code.md` / `lanes-cursor.md` 对应句、`docs/zh/` 孪生、契约测试（前言缺失 fail-loud 用例扩到报告前言）。

- [ ] 报告模式下 runner 不再前置 worker 前言，改前置报告前言（只读、回答 Objective、证据或 verdict 形状），缺失即 fail-loud
- [ ] runner 内联的 report-mode overlay 文本删除，单源回到前言文件
- [ ] `lanes-cursor.md`：explorer / advisor 派发首行指向报告前言
- [ ] 契约测试覆盖：报告模式 prompt 含报告前言且不含 `WORKER REPORT`；implement 模式不变
- [ ] 中文孪生同提交更新；`python3 tests/test_zh_mirror.py`、`python3 tests/test_runner_contract.py` 绿
