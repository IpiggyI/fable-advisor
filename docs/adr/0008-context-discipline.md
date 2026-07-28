# 0008 — 上下文纪律：分级 diff 验收、报告预算与 spec 准备探针

- **Status**: accepted
- **Date**: 2026-07-29
- **影响范围**: `skills/orchestration/SKILL.md`、`agents/implementer.md`、`agents/grok-implementer.md`、`README.md`、`.claude-plugin/plugin.json`
- **关联决策**: [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（codex receipt 提供 Tier 1 验证证据）、[ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md)（in-house 车道缺少跨厂商复核）、[ADR 0007](./0007-handoff-lane.md)（handoff 验收继续亲自读取 diff）

## 背景

会话 `3ca1541f`（2026-07-28，四 ticket 构建，峰值 265k tokens）的归因显示，主要上下文成本不在委派本身，而在架构师反复摄入原始材料。委派往返约 16.5k tokens，仅占上下文增长的 7%；架构师自己的读取约占 39%：写 spec 前完整读取 6 个文件，共 80,798 chars，委派后又做 16 次 `git diff` 审查，共 43,164 chars，同一批文件因此被看两遍，约 35k tokens。单条最大车道报告达 14.5k chars；另有约 35% 来自随 turn 数增长而放大的 thinking feedback。

现有 doctrine 要求架构师无条件读取完整 diff，也没有限制 implementer 报告大小；同时，写 spec 前的文件准备没有区分“只需地图”和“必须亲读的约束原文”。三处机制叠加后，廉价车道已经读过的内容会再次进入旗舰上下文，并在后续每个 turn 被重复计价。

## 决策

自 v3.6.0 起采用三项机制：

1. **三级 diff 验收**：Tier 1 为所有车道的默认验收，以命令、退出码、输出尾部等验证证据（对 working tree 抽查）加 `git diff --stat` 为依据，完整且未限定范围的 `git diff` 不进入架构师上下文；报告、stat 或验证输出引发具体疑点时进入 Tier 2，只读取可疑文件的 path-scoped diff；正确性关键任务及每个 in-house diff 进入 Tier 3，由 context-clean reviewer subagent 审查完整 diff、返回 verdict 与 flagged hunks，架构师只亲读被标记的 hunks，并保留最终判断与扩大抽查的权力。in-house diff 优先交给跨厂商车道复核。handoff 因生产模型家族未知且没有 receipt，明确豁免分级，仍由架构师亲自读取 diff。
2. **车道报告硬预算**：`implementer` 与 `grok-implementer` 的完整报告控制在约 30 行以内；验证证据只含命令、退出状态和最多最后 10 行输出；每个文件恰好一行变更摘要，不附 diff body 或完整命令输出。只有真实 spec 歧义或未完成项可让 `GAPS` 超出常规长度。
3. **spec 准备探针**：为了写 spec 而完整读取文件视为异味。先让廉价、只读 scout 返回 exports、signatures 与 line numbers 的地图，架构师只亲读将写入 Interfaces/Constraints 的行；接收车道仍以重读指定文件作为第一步，避免同一内容先后按旗舰价和车道价各计一次。

版本随 doctrine 与公开契约变更从 3.5.0 升至 3.6.0。

## 核心理由

1. **成本归因指向读取，而非委派**：委派往返只占增长的 7%，架构师读取约占 39%；优化验收和 spec 准备，比减少车道调用更贴近最大可控项。
2. **证据强度随风险递增**：默认使用 receipt/report 中可抽查的验证证据与 diff stat，不等于放弃审查；具体疑点和高风险工作分别触发 scoped diff 与独立完整审查，让上下文投入与风险匹配。
3. **压缩报告不压缩判据**：命令、退出码和输出尾部足以定位验证是否真实执行；diff 留在 working tree，通过分级验收读取，避免最大 14.5k chars 的报告再次复制代码体。
4. **抑制 turn 放大效应**：越早阻止全文件、全 diff 和完整输出进入旗舰上下文，越少内容参与约 35% 的 thinking feedback 随 turn 数放大。

## 实施代价

- `SKILL.md`：增加 spec 准备探针和三级验收协议；codex acceptance 改为引用分级验收；handoff 明确保留个人 diff 审查。
- 两个 implementer agent：报告生成需执行行数、输出尾部和逐文件摘要预算；遇到真实 spec gap 时仍可完整报告。
- 高风险及 in-house 变更多一次 reviewer 调用；架构师仍需判断 verdict、亲读 flagged hunks，必要时扩大抽查。
- Tier 1 的 `git diff --stat` 信息少于完整 diff，具体异常依靠 Tier 2/3 升级处理。

## 复盘条件

- 若 Tier 1 验收让车道引入的缺陷漏过 → 收紧默认 tier。
- 若报告预算使架构师拿不到形成 verdict 所需的证据 → 放宽输出尾部。
- 若 harness 提供更廉价的 diff-summary 机制 → 重新评估三级划分。
