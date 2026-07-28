# 上下文纪律（context discipline）：分层 diff 验收 + 报告预算 + spec 前探针

Status: ready-for-agent

## Problem Statement

对真实会话 3ca1541f（2026-07-28，四票据构建，峰值 265k tokens）的量化归因显示：委派往返仅占上下文增长的 7%（约 16.5k tokens），膨胀主因是架构师自身行为——委派前把 6 个源文件全文读入主上下文（80,798 字符），委派后 16 次 git diff 复核（43,164 字符），同批文件被看两遍约 35k tokens；单份 lane 报告最大 14.5k 字符；另有 35% 是随轮数增长的 thinking 回灌。doctrine 已有 "keep the context lean" 原则，但缺少可执行机制，实践中被无差别的 "read the diff" 验收规则抵消。

## Solution

三处机制化，全部纯文档改动：

1. **分层 diff 验收**取代无差别 "read the diff"：默认层（lane 验证证据 + `git diff --stat`）→ 抽查层（仅对存疑文件做路径限定 diff）→ 全审层（正确性关键任务与 in-house 产出，派 context-clean reviewer 子代理读全量 diff，只带回 verdict + 疑点 hunk；in-house diff 优先用跨厂商 lane 当 reviewer，顺带补回该车道缺失的 cross-vendor review）。全量无限定 diff 不进架构师上下文。handoff 车道验收（亲读 diff）因产出模型族未知且无 receipt，显式豁免、维持原样。
2. **报告预算**写进两个 lane agent 的报告契约：全报告 ≤30 行；VERIFIED 只给命令 + 退出码 + 输出尾部 ≤10 行；CHANGES 每文件一行；禁止贴 diff 全文与完整命令输出（diff 留在工作区，走分层验收取用）。
3. **spec 前探针规则**：为写 spec 而 Read 全文件是一个信号——应派 scout 拿结构图（exports、签名、行号），架构师只亲读要写进 Interfaces/Constraints 的行；lane 的工作流第一步本就会在自己上下文里重读命名文件，架构师的全文读等于同一内容按架构师单价计费两次。

## Implementation Decisions

- `skills/orchestration/SKILL.md`：Verification 节重写为三层协议（保留 "reports are claims"、corrected-spec、idle-subagent 规则；codex 验收句 "and you read the diff" 对齐分层协议；handoff 豁免注明）；"Keep the context lean" 段追加 spec 前探针规则。
- `agents/implementer.md`、`agents/grok-implementer.md`：报告契约加硬预算。
- `docs/adr/0008-context-discipline.md`：新建，中文，沿 ADR 0003 结构，含量化背景、决策、复盘条件。
- `README.md`：验收措辞（约第 61 行）对齐分层协议；Upgrading 段追加 v3.6 一句并链接 ADR 0008。
- `.claude-plugin/plugin.json`：3.5.0 → 3.6.0（验收语义变更，沿 minor 先例）。
- 用户侧配套（不在本仓库）：检索纪律与视觉验收纪律两条已写入 `~/.claude/rules/fable-advisor.md` 的 Architect mode 节，2026-07-29。
- 经由 codex 车道实施（dogfood）：spec 见 `.fable-advisor/pending/context-discipline.json`。
