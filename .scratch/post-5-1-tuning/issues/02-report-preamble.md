# 02: 报告模式前置只读的报告前言

**What to build:** 报告模式（explorer / advisor）的车道读到的执行侧契约不再自相矛盾：runner 按 `mode` 前置 worker 前言或报告前言，报告前言只读、Files 是读取范围、回答 Objective、以证据或 verdict 形状结尾、不含 `WORKER REPORT`；runner 内联的 report-mode overlay 文本删除；任一前言缺失即 fail-loud。承接 `.scratch/role-pool-posture/issues/10-report-mode-preamble.md` 的全部验收项。

**Blocked by:** 01（同一批 runner 文件与契约测试；prompt 首行已改为标题）

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 3 条；ADR 0013（执行侧契约单源）、ADR 0014 决策 11。范围：两条 runner 的前言加载与 prompt 拼装、报告前言新文件（与 worker 前言同目录）、契约测试、`lanes-claude-code.md` 报告模式段、两份前言的中文孪生。

- [x] 新增报告前言文件：只读、Files 是读取范围不是写权限、回答 Objective、explorer 以证据形状（`file:line`、符号、原文）结尾、advisor 以 verdict 形状结尾、不出现 `WORKER REPORT`
- [x] runner 报告模式前置报告前言、不前置 worker 前言；implement 模式不变
- [x] runner 内联的 "Report mode: act as a read-only explorer or advisor…" 段删除，单源回到前言文件
- [x] 任一模式所需前言缺失 → 退出非零、不 spawn、stderr 指名缺失文件
- [x] 契约测试：报告模式 prompt 含报告前言且不含 `WORKER REPORT`；implement 模式 prompt 含 worker 前言且不变；报告前言缺失用例
- [x] `lanes-claude-code.md` 第 0 节与报告模式段写明按 `mode` 分流；中文孪生同提交；报告前言的中文孪生存在
- [x] `python3 tests/test_runner_contract.py`、`python3 tests/test_zh_mirror.py` 绿
- [x] 原工单 10 的 Status 改为 `wontfix`，末尾注明由本票承接

## Comments

### 2026-09-16 — 实施记录（grok 车道，resume 工单 01 的会话，`cursor-grok-4.6-xhigh`，requested, not confirmed）

- 新增 `lane-preamble-report.md`（Posture / Gaps / Answer 三段）与中文孪生；runner 按 `mode` 选前言路径，缺文件非零退出并点名；`renderPrompt` 删 `# Mode` overlay。
- TDD：15/17 红 → 17/17 绿；`test_zh_mirror` 15/15。
- 验收：架构师复跑 17/17、15/15；读了报告前言全文与 runner diff。工单 10 已由架构师关闭为 `wontfix`。
- 追加修正契约（同会话）：`lanes-claude-code.md` 返工段 "higher-tier worker" 对齐升级梯。
