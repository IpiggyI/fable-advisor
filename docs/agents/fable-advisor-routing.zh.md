# Fable Advisor 路由配置

本用户路由配置声明于 2026-09-11。它锚定 Grok 4.6、GPT-6 Astra、GPT-5.6 Luna、Opus 5 和 Fable 5.1。任一模型换代时，重估涉及该模型的条目。

下表给出用户指定的候选顺序和推理强度。格子内显式取值优先；格子未指定时，`worker` 使用 `medium`，`explorer` 使用 `medium`，`advisor` 使用 `high`。`fable-advisor:orchestration` 使用本配置并负责全部编排行为。

## Claude Code 候选

| 格子 | 候选，优者在前 |
|---|---|
| `explorer @ light` | grok-4.6[medium] › gpt-5.6-luna[high] › 宿主内建 Explore |
| `explorer @ standard / senior` | 使用同档位的 `worker` 候选 |
| `worker @ light` | grok-4.6[medium] › gpt-5.6-luna[high]。仅在我声明时，或任务简单且需要 GPT 家族时，才用 Luna 作为 `worker` |
| `worker @ standard` | grok-4.6[xhigh] › claude-opus-5[high] |
| `worker @ senior` | gpt-6-astra[medium]；特别难的任务使用 gpt-6-astra[high] |
| `advisor`（默认 `senior`） | gpt-6-astra[high] › claude-fable-5-1[high] |

## Cursor 候选

Cursor 的模型家族取值来自当前可用名单，不持久化可能过期的型号标识。格子未指定推理强度时，使用上面的角色默认值。

| 格子 | 候选，优者在前 |
|---|---|
| `explorer @ light` | grok-4.6[medium] › gpt-5.6-luna[high] › 宿主内建 `explore` |
| `explorer @ standard / senior` | 使用同档位的 `worker` 候选 |
| `worker @ light` | 当前可用的 Grok 家族型号标识 › gpt-5.6-luna[high]。仅在我声明时，或任务简单且需要 GPT 家族时，才用 Luna 作为 `worker` |
| `worker @ standard` | 当前可用的 Grok 家族型号标识 › 当前可用的 Opus 家族型号标识 |
| `worker @ senior` | gpt-6-astra[medium]；特别难的任务使用 gpt-6-astra[high] |
| `advisor`（默认 `senior`） | 当前可用的 Fable 家族型号标识 › gpt-6-astra[high] |

## 资源偏好

声明于 2026-09-06：

- 速度，从快到慢：grok-4.6 > fable5.1 ≈ astra ≈ opus5 > Luna-max。
- 价格，从便宜到贵：Luna-max < grok-4.6 << opus5 ≤ astra ≤ fable5.1。
- 能力：Luna-max < grok-4.6 ≤ opus5 < astra ≈ fable5.1。
- 专长：前端偏 `claude` 车道，后端偏 `codex` 车道。反例积累后重估。
- 额度余量和工期仅在开工时由我口头声明，只在当次会话有效，绝不持久化。没有声明时，使用列表中最便宜且胜任的候选及所列推理强度。
- `handoff` 车道只有我按任务或按会话声明后才进入候选集。
