# 04: agent 定义 —— `worker.md` 取代 `implementer.md`，`fable-advisor.md` 改写

**What to build:** Claude Code 会话里可派两个插件 agent：`worker`（claude lane 的可写实现角色：`model: opus` 别名默认、`effort: medium`、工具不限；正文只保留 claude lane 特有的三条披露与"若跨厂 CLI 车道其实可用则在报告中说明"；引用前言而不重述）与 `fable-advisor`（只读判断角色：`model: fable` 默认、`effort: high`、`tools: Read, Grep, Glob`；正文写 `决策` 与 `验收` 两种请求形状的输入与输出，保留"上下文干净的第二读者、权威来自读到的代码"与约 300 词上限，去掉 Fable 系列身份句与"审查员"式措辞）。`implementer` agent 不再存在。

**Blocked by:** 03（前言定稿与词汇）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "插件 agent 定义" 节。范围：`plugin/agents/`（中文孪生归 05 票）。产物类别：准则散文。

- [ ] `plugin/agents/worker.md` 存在，frontmatter `name: worker`、`model: opus`、`effort: medium`，无 `tools` 限制；正文指向 `lane-preamble.md`，只含 claude lane 特有内容
- [ ] `plugin/agents/implementer.md` 删除
- [ ] `plugin/agents/fable-advisor.md` frontmatter 保留 `name: fable-advisor`、`model: fable`、`tools: Read, Grep, Glob`，新增 `effort: high`；description 改为职责句（两种请求形状），不含 Fable 系列身份
- [ ] 两个文件都不出现 `implementer`、`In-house`、`architect tier`、`reviewer`
- [ ] `claude plugin validate plugin/agents`（若本机可用）通过；否则以 frontmatter 可解析（`---` 首行、YAML 合法）为验收
- [ ] 不改动 `docs/zh/**`
