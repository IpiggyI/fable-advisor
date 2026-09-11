# 04: agent 定义 —— `worker.md` 取代 `implementer.md`，`fable-advisor.md` 改写

**What to build:** Claude Code 会话里可派两个插件 agent：`worker`（claude lane 的可写实现角色：`model: opus` 别名默认、`effort: medium`、工具不限；正文只保留 claude lane 特有的三条披露与"若跨厂 CLI 车道其实可用则在报告中说明"；引用前言而不重述）与 `fable-advisor`（只读判断角色：`model: fable` 默认、`effort: high`、`tools: Read, Grep, Glob`；正文写 `决策` 与 `验收` 两种请求形状的输入与输出，保留"上下文干净的第二读者、权威来自读到的代码"与约 300 词上限，去掉 Fable 系列身份句与"审查员"式措辞）。`implementer` agent 不再存在。

**Blocked by:** 03（前言定稿与词汇）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "插件 agent 定义" 节。范围：`plugin/agents/`（中文孪生归 05 票）。产物类别：准则散文。

- [x] `plugin/agents/worker.md` 存在，frontmatter `name: worker`、`model: opus`、`effort: medium`，无 `tools` 限制；正文指向 `lane-preamble.md`，只含 claude lane 特有内容
- [x] `plugin/agents/implementer.md` 删除
- [x] `plugin/agents/fable-advisor.md` frontmatter 保留 `name: fable-advisor`、`model: fable`、`tools: Read, Grep, Glob`，新增 `effort: high`；description 改为职责句（两种请求形状），不含 Fable 系列身份
- [x] 两个文件都不出现 `implementer`、`In-house`、`architect tier`、`reviewer`
- [x] `claude plugin validate plugin/agents`（若本机可用）通过；否则以 frontmatter 可解析（`---` 首行、YAML 合法）为验收
- [x] 不改动 `docs/zh/**`

## Comments

2026-09-11 — 已实现（同模派发，inherit）。`worker.md` 29 行、`fable-advisor.md` 35 行；退役词 grep exit 1；`claude plugin validate plugin/agents` 通过；frontmatter 经严格 YAML 解析（车道发现并修掉 description 里裸 `: ` 的历史隐患）。顺带把 02b 的 `empty_report` 补进 `lanes-claude-code.md`（L68 / L94-95 / L111）。zh 镜像测试按预期 6/8（缺 `worker.md` 孪生、多 `implementer.md` 孪生），归 05。架构师通读两文件。
