> 中文对照版，不参与部署，以英文版为准。权威版本：plugin/skills/orchestration/lanes-cursor.md

# Cursor 中的各 lane —— 钉死的 subagent，无 runner（The lanes in Cursor — pinned subagents, no runners）

在 Cursor 中派发 lane 之前阅读本文。Cursor 通过其 Claude 插件兼容路径加载本 skill，并原生暴露每条 lane 的模型：一次 subagent 派发钉死自己的模型。[lanes-claude-code.md](lanes-claude-code.md) 中的 runner 装置是 Claude Code 的机制——完全跳过：无 pending 文件、无 receipt、无 receipt gate。

- **调用。** 把同一份五部 spec 原文作为 subagent 的提示写出，并在每次派发上显式钉死该 lane 的模型：Routine lane 用 Grok 4.6，Cross-vendor lane 用 GPT-5.6 Sol，In-house lane（仓内车道）用 Opus 钉死，派发 `fable-advisor` 做判断时用 Fable 钉死（例如 `claude-fable-5-thinking-high`）。Agent 的 frontmatter `model:` 对 Cursor 中插件加载的 agent 不生效——一次未钉死的具名 agent 派发会静默继承会话模型，因此从非旗舰会话发出的未钉死派发会悄悄降级该 lane（已于 2026-08-12 核验）。
- **验收。** 报告作为派发结果在带内返回，失败或不可用的派发也在带内大声失败。验收完全按 [SKILL.md](SKILL.md) 中的核验层运行——它们从来就是真正的裁决者；receipt gate 只曾管辖带外 CLI 运行，而 Cursor 没有那种运行。
- **改道。** 因用户套餐上模型不可用而失败的派发，改道到另一条 Cross-vendor lane，并显式披露——与 CLI lane 同一规则。此处「派发而非探测」规则没有对象：没有会被诱去探测的 CLI 认证状态。
- **effort 钉死在 slug 上。** 临时模型钉死携带固定的 effort 档——codex lane 的 `effort` 旋钮在裸派发上不存在。方括号参数（`gpt-5.6-sol[effort=high]`）仅在自定义 agent 定义文件中可用；仅当任务真正需要升高 effort 时才有意添加一份定义文件，而非默认。
- **竞速。** 「挑选更强 diff」的竞速是同一条消息中的两次钉死派发——无需保持不同的 pending 文件。
- **经济不变。** 各厂模型在 Cursor 中占用各自的额度池，因此各 lane 之间的价格梯度——以及整套成本纪律——按原文适用。

## Subagent 生命周期（Subagent lifecycle）

带 `name`（「teammate」）拉起的 subagent 在完成后仍会保留，以便再次发消息——每一批你未清理的具名批次都会作为后台工作徘徊，直到会话退出。两条规则：

- 串行批次（同一文件、严格顺序）从后台化得不到任何好处：用 `run_in_background: false` 运行，并当场消费报告。
- 当一批确实在后台运行时，一旦其工作已核验且没有后续角色，就停止其 teammate。不要让已核验的 lane 闲置到会话结束。
