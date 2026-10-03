# Fable Advisor 路由档案（中文译本，不随插件发布）

本用户路由档案于 2026-10-03 声明。锚定 `grok-4.7`、`gpt-6-luna`、`gpt-6.1-sol`、`gpt-6-astra`、`haiku-4-5`、`sonnet-5-5`、`opus-5-5`、`fable-5-1` 与 Cursor 的 `composer-2.5-fast`。任一相关模型换代时重估对应条目。`fable-advisor:orchestration` 读取本档案并拥有编排行为，包括档位准入与升级梯。运行中的会话重启之前仍用旧档案。

## 档位与格内选择

- 三列：`mainstay`（主力）承担大多数日常工作，`crux`（攻坚）处理难点，`rescue`（后援）只在 `crux` 失败后或凭我的声明进入。一个档位是每个角色的一组拨盘；同一型号可以按不同强度落在不同档位。
- `›` 分隔候选。
- 候选顺序是我的偏好，不是能力或价格排名。不同模型家族各有擅长点，因此按需选择候选。一处顺序是有意的：explorer `rescue` 把 `opus-5-5` 放在更便宜的 `gpt-6.1-sol` 前面，因为在 Claude Code 里 explorer 优先用 Claude 家族。
- 任务落在某个后面候选的擅长点上时选它。擅长点是多样的；以下是示例，不是完整清单：型号排名表里各家族的擅长点；在列出 `gpt-6-luna` 的格里，相对简单但量大的任务优先它；价格低本身就是擅长点；想听不同厂商的意见时优先跨厂商的候选。
- 车道默认顺序是 grok 车道 › codex 车道 › claude 车道。它只在几个候选同样合适时，以及需要替换候选时起作用——整条车道不可用、单个候选不可用、codex runner 对某个型号启动失败，都按这个顺序换，不按书写顺序。
- 例外，只在 Claude Code：explorer 在平手和替换时按 claude 车道 › grok 车道 › codex 车道，格内也把 Claude 候选写在最前。Claude Code 自带的 explorer 不能指定模型；本插件补上这一块。
- 升档示例路径（worker）：`grok-4.7[high]` → `gpt-6.1-sol[xhigh]` → `opus-5-5[xhigh]` → 我。

## 型号排名

- 能力按定位排名，从低到高依次是 `starter`（入门）、`midrange`（中端）、`premium`（高端）、`flagship`（旗舰）。每个家族只给自己的型号定位。一个型号的定位更低，才算低于另一个型号；同一定位里不同家族的型号不分高下，在它们之间换模型不算降级。破折号表示该家族在这个定位没有型号。

| 家族 | `starter` | `midrange` | `premium` | `flagship` | 擅长 |
|---|---|---|---|---|---|
| Claude | haiku-4-5 | sonnet-5-5 | opus-5-5 | fable-5-1 | 前端 |
| GPT | gpt-6-luna | — | gpt-6.1-sol | gpt-6-astra | 后端、复杂任务 |
| Grok | composer-2.5-fast | grok-4.7 | — | — | 价智比高 |

- 价格：`gpt-6-luna` << `grok-4.7` < `gpt-6.1-sol` < `sonnet-5-5` < `opus-5-5` < `gpt-6-astra` < `fable-5-1`。
- 各型号速度无明显差异。

## 已声明假设

- 换模型带来的提升大于提高强度。
- `xhigh` 有明显跃升。

两条都在下一次模型换代时失效；届时重估本表。

## advisor 映射

- 验收形状：`mainstay` 的默认，`gpt-6.1-sol[medium]`。
- 决策形状：`mainstay` 默认之后的那一档强度，`gpt-6.1-sol[high]`。
- verdict 自报低置信度：`crux`。
- `rescue`：只凭我的声明。

## 会话续用窗口

- claude 车道在 Claude Code（向子代理发 `SendMessage`）：1 小时。
- codex 车道：30 分钟。
- grok 车道：1 小时。
- Cursor 的 `Task` `resume`：1 小时。

每个窗口从该车道的上次活动起算。这些窗口是我的续用政策，不是实测的缓存寿命。

## Claude Code 候选

到达方式：Grok 经 grok runner，`model` 和 `effort` 两者都设；runner 拒绝省略其中任一项的 spec；GPT 经 codex runner（spec `model`、`effort`）；Claude 经本插件的 agent 文件加按次 `model`（派发不带 `name`）。按次 `model` 只接受别名 `haiku`、`sonnet`、`opus`、`fable`；别名是指针，实际运行的型号以子代理记录中的 `message.model` 为准。每个 Claude 拨盘对应的 agent 文件：

- explorer：`haiku-4-5` → `explorer-h` 配 `haiku`（没有强度维度，文件的强度无效果）；`sonnet-5-5[high]` → `explorer-h` 配 `sonnet`；`opus-5-5[high]` → `explorer-h`，`opus-5-5[xhigh]` → `explorer-xh`，都配 `opus`。没有 explorer 文件携带 `medium`，所以 `sonnet-5-5[medium]` 同样经 `explorer-h` 派发，以 `high` 运行。
- worker：`sonnet-5-5[high]` → `worker-h`，`sonnet-5-5[xhigh]` → `worker-xh`，都配 `sonnet`；`opus-5-5[medium]` → `worker-md`，`[high]` → `worker-h`，`[xhigh]` → `worker-xh`，都配 `opus`。
- advisor：`[low]` → `advisor-l`，`[medium]` → `advisor-md`，`[high]` → `advisor-h`，`[xhigh]` → `advisor-xh`，配 `opus` 或 `fable`。

| 角色 | `mainstay` | `crux` | `rescue` |
|---|---|---|---|
| explorer | haiku-4-5 › gpt-6-luna[high*, xhigh] › grok-4.7[medium*, high] | sonnet-5-5[medium*, high] › gpt-6-luna[max] › grok-4.7[xhigh] | opus-5-5[high*, xhigh] › gpt-6.1-sol[high*, xhigh] |
| worker | grok-4.7[high*, xhigh] › sonnet-5-5[high*, xhigh] › gpt-6.1-sol[medium*, high] | opus-5-5[medium*, high] › gpt-6-astra[low*, medium] › gpt-6.1-sol[xhigh*, max] | opus-5-5[xhigh] › gpt-6-astra[high*, xhigh] |
| advisor | gpt-6.1-sol[medium*, high] › opus-5-5[medium*, high] › gpt-6-astra[low*, medium] › fable-5-1[low*, medium] | gpt-6.1-sol[xhigh] › opus-5-5[xhigh] › gpt-6-astra[high] › fable-5-1[high] | gpt-6-astra[xhigh] › fable-5-1[xhigh] |

## Cursor 候选

worker 与 advisor 行同 Claude Code。explorer 行按车道默认顺序排，`composer-2.5-fast` 在 `mainstay` 首位。

可用性按每个候选的实际调用入口判断：GPT 候选经 Shell 走 codex runner（explorer 与 advisor 用报告模式）；`grok-4.7`、Claude 候选与 `composer-2.5-fast` 经钉型号的 `Task`（advisor 用 `advisor-*` agent，其余用 `explore` 或 `generalPurpose`）。当回合的 allowlist 只约束钉型号的 `Task` 派发。其中缺少所需变体的候选跳过，并在披露里说明。每个 `Task` 的 slug 都取自当回合的 allowlist。

| 角色 | `mainstay` | `crux` | `rescue` |
|---|---|---|---|
| explorer | composer-2.5-fast › grok-4.7[medium*, high] › gpt-6-luna[high*, xhigh] › haiku-4-5 | grok-4.7[xhigh] › gpt-6-luna[max] › sonnet-5-5[medium*, high] | gpt-6.1-sol[high*, xhigh] › opus-5-5[high*, xhigh] |
| worker | grok-4.7[high*, xhigh] › sonnet-5-5[high*, xhigh] › gpt-6.1-sol[medium*, high] | opus-5-5[medium*, high] › gpt-6-astra[low*, medium] › gpt-6.1-sol[xhigh*, max] | opus-5-5[xhigh] › gpt-6-astra[high*, xhigh] |
| advisor | gpt-6.1-sol[medium*, high] › opus-5-5[medium*, high] › gpt-6-astra[low*, medium] › fable-5-1[low*, medium] | gpt-6.1-sol[xhigh] › opus-5-5[xhigh] › gpt-6-astra[high] › fable-5-1[high] | gpt-6-astra[xhigh] › fable-5-1[xhigh] |
