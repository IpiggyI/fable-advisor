# Cursor 中的各 lane —— 钉死的 subagent，无 runner

在 Cursor 中派发 lane 之前阅读本文。Cursor 通过其 Claude 插件兼容路径加载本 skill，并原生暴露每条 lane 的模型：一次 subagent 派发钉死自己的模型。[lanes-claude-code.md](lanes-claude-code.md) 中的 runner 装置是 Claude Code 的机制——完全跳过：无 pending 文件、无 receipt、无 receipt gate。

- **调用。** 派发提示以一行开场，把 subagent 指向 `<plugin-root>/skills/orchestration/lane-preamble.md` —— 这里没有东西替你前置它，而执行侧契约必须到达每一条 lane。五部契约原文紧随其后。在每一次厂商 lane 和具名 agent 派发上显式钉死该 lane 的模型（同模派发是下一则中的唯一例外）：Routine lane 用本轮 allowlist 里的 Grok-family slug，Cross-vendor lane 用 GPT-family slug（GPT lane 就是当时存活的 GPT-family slug——allowlist 可能缺少某一世代），In-house lane 用 Opus slug，派发 `fable-advisor` 做判断时用 Fable-family slug。Agent 的 frontmatter `model:` 对 Cursor 中插件加载的 agent 不生效——一次未钉死的具名 agent 派发会静默继承会话模型，因此从非旗舰会话发出的未钉死派发会悄悄降级该 lane。
- **同模派发。** 唯一不携带 `model` 的派发：准则散文的 In-house 拨盘是一次省略 `model` 的 `generalPurpose` 派发——继承会话模型是目的，不是疏漏，且它不是具名 agent 派发，所以上面的降级风险不会出现。在路由披露中写明「inherit」，以免被误当成未钉死的 lane。
- **验收。** 报告作为派发结果在带内返回，失败或不可用的派发也在带内大声失败。验收完全按 [SKILL.md](SKILL.md) 中的核验层运行；receipt gate 管辖带外 CLI 运行，而 Cursor 没有那种运行。
- **返工。** 返工票是一次带先前派发 agent id 的 Task `resume`，把返工契约（缺陷、原范围、失败的检查）作为新提示带上——lane 保留它已经建好的上下文。两轮失败之后，用新派发重跑阶段 1。
- **改道。** 因用户套餐上模型不可用而失败的派发，改道到另一条 Cross-vendor lane，并显式披露——与 CLI lane 同一规则。
- **effort 钉死在 slug 上。** 临时模型钉死携带固定的 effort 档——codex lane 的 `effort` 旋钮在裸派发上不存在。方括号参数（`<slug>[effort=high]`）仅在自定义 agent 定义文件中可用；仅当任务真正需要升高 effort 时才有意添加一份定义文件，而非默认。
- **竞速。** 「挑选更强 diff」的竞速是同一条消息中的两次钉死派发——无需保持不同的 pending 文件。
- **经济不变。** 各厂模型在 Cursor 中占用各自的额度池，因此各 lane 之间的价格梯度——以及整套成本纪律——按原文适用。

## Subagent 生命周期

带 `name`（「teammate」）拉起的 subagent 在完成后仍会保留，以便再次发消息——每一批你未清理的具名批次都会作为后台工作徘徊，直到会话退出。两条规则：

- 串行批次（同一文件、严格顺序）从后台化得不到任何好处：用 `run_in_background: false` 运行，并当场消费报告。
- 当一批确实在后台运行时，仅在验收之后才停止其 teammate——核验通过不是结束，因为返工票会恢复同一 agent。一旦 diff 已验收且预期没有后续，就停止它；不要让已验收的 lane 闲置到会话结束。
