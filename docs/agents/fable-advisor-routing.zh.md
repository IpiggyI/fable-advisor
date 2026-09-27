# Fable Advisor 路由档案（中文备份，不是活体，不安装）

本用户路由档案于 2026-09-26 声明，取代 2026-09-16 的版本。锚定 `grok-4.7`、`gpt-6-luna`、`gpt-6-sol`、`gpt-6-astra`、`haiku-4-5`、`sonnet-5`、`opus-5-5`、`fable-5-1` 与 Cursor 的 `composer-2.5-fast`。任一相关模型换代时重估对应条目。`fable-advisor:orchestration` 读取本档案并拥有编排行为，包括档位准入与升级梯；本文件承载用户的取值，以及这些取值所依赖的格内选择规则。

## 档位与格内选择

- 三列：`mainstay`（主力）承担大多数日常工作，`crux`（攻坚）处理难点，`rescue`（后援）只在 `crux` 失败后或凭我的声明进入。档位按型号划分，强度只做档内细分。
- 拨盘记法：`model[a*, b, c]` 列出该型号在该格可选的强度；`*` 是默认，没有 `*` 的格以第一个列出的强度为默认。没有强度维度的型号裸写。`›` 分隔候选。
- 格内第一个候选是默认。没有声明、也没有合适的擅长点时，取格内第一个候选的 `*` 拨盘。
- 候选顺序是我的偏好，不是能力或价格排名。不同模型家族各有擅长点，按需选择取代"越往后越依赖判断"。三处顺序是有意的：
  - explorer `rescue` 把 `opus-5-5` 放在较弱的 `gpt-6-sol` 前面，因为在 Claude Code 里 explorer 优先用 Claude 家族；
  - worker `mainstay` 把 `grok-4.7` 放在更便宜的 `gpt-6-luna` 前面，因为 `grok-4.7` 的价智比更高；
  - advisor `mainstay` 把 `gpt-6-astra` 放在更便宜的 `opus-5-5` 前面，因为我希望听到不同厂商的意见。
- 任务落在某个后面候选的擅长点上时选它。擅长点是多样的；以下是示例，不是完整清单：相对简单但量大的任务优先 `gpt-6-luna`；价格低本身就是擅长点；前端偏 claude 车道；后端和复杂任务偏 codex 车道；想听不同厂商的意见时优先跨厂商的候选。
- 车道默认顺序是 grok 车道 › codex 车道 › claude 车道。它只在几个候选同样合适时，以及需要替换候选时起作用——整条车道不可用、单个候选不可用、codex runner 对某个型号启动失败，都按这个顺序换，不按书写顺序。
- 例外，只在 Claude Code：explorer 在平手和替换时按 claude 车道 › grok 车道 › codex 车道，格内也把 Claude 候选写在最前。Claude Code 本身有 explorer，但不能指定模型；本插件补上这一块。这个理由在 Cursor 不成立。
- 升档示例路径（worker）：`grok-4.7[high]` → `gpt-6-sol[xhigh]` → `opus-5-5[xhigh]` → 我。

## 型号排名

- 能力：`gpt-6-luna` ≈ `sonnet-5` < `grok-4.7` ≤ `gpt-6-sol` < `opus-5-5` ≈ `gpt-6-astra` ≈ `fable-5-1`。≈ 按同级读，≤ 保留方向：`gpt-6-sol` 与 `grok-4.7` 接近，但不低于它。同级型号之间跨厂商换模型不算降级。
- 价格：`gpt-6-luna` << `grok-4.7` < `gpt-6-sol` < `opus-5-5` < `gpt-6-astra` < `fable-5-1`；`sonnet-5` 价格接近 `opus-5-5`。`grok-4.7` 与 `gpt-6-sol` 能力接近，更便宜。
- `haiku-4-5`（只在 explorer 中作为最基础的调查员）与 `composer-2.5-fast` 不排级。从它们升档，按同样的按需规则在 `crux` 格里选。
- 速度不列：各型号没有明显差异。
- `sonnet-5` 是即将推出的 `sonnet-5-5` 的占位，所以现在的表看着有些奇怪。`sonnet-5-5` 发布，或 `sonnet` 别名改指其他型号时重估。

## 已声明假设

- 换模型带来的提升大于提高强度。
- `xhigh` 有明显跃升。

两条都在下一次模型换代时失效；届时重估本表。

## advisor 映射

- 验收形状：`mainstay` 的默认，`gpt-6-astra[low]`。
- 决策形状：`mainstay` 的 `medium` 强度。
- verdict 自报低置信度：`crux`。
- `rescue`：只凭我的声明。

## Claude Code 候选

到达方式：Grok 经 grok runner——省略 `model`，跟随 CLI 默认，当前为 `grok-4.7`（2026-09-27 观测），并设 `effort`；GPT 经 codex runner（spec `model`、`effort`）；Claude 经本插件的 agent 文件加按次 `model`（派发不带 `name`）。按次 `model` 只接受别名 `haiku`、`sonnet`、`opus`、`fable`；别名是指针，实际运行的型号以子代理记录中的 `message.model` 为准。每个 Claude 拨盘对应的 agent 文件：

- explorer：`haiku-4-5` → `explorer-h` 配 `haiku`（没有强度维度，文件的强度无效果）；`sonnet-5[high]` → `explorer-h` 配 `sonnet`；`opus-5-5[high]` → `explorer-h`，`opus-5-5[xhigh]` → `explorer-xh`，都配 `opus`。
- worker：`opus-5-5[medium]` → `worker-md`，`[high]` → `worker-h`，`[xhigh]` → `worker-xh`，都配 `opus`。
- advisor：`[medium]` → `advisor-md`，`[high]` → `advisor-h`，`[xhigh]` → `advisor-xh`，配 `opus` 或 `fable`。

| 角色 | `mainstay` | `crux` | `rescue` |
|---|---|---|---|
| explorer | haiku-4-5 › gpt-6-luna[high*, xhigh] › grok-4.7[medium*, high] | sonnet-5[high] › gpt-6-luna[max] › grok-4.7[xhigh] | opus-5-5[high*, xhigh] › gpt-6-sol[high*, xhigh] |
| worker | grok-4.7[high*, xhigh] › gpt-6-luna[xhigh*, max] › gpt-6-sol[high] | gpt-6-sol[xhigh*, max] › opus-5-5[medium*, high] › gpt-6-astra[low*, medium] | opus-5-5[xhigh] › gpt-6-astra[high*, xhigh] |
| advisor | gpt-6-astra[low*, medium] › opus-5-5[medium] › fable-5-1[medium] | opus-5-5[high*, xhigh] › gpt-6-astra[high] › fable-5-1[high] | gpt-6-astra[xhigh] › fable-5-1[xhigh] |

## Cursor 候选

worker 与 advisor 行同 Claude Code。explorer 行按车道默认顺序排，`composer-2.5-fast` 在 `mainstay` 首位。

可用性按每个候选的实际调用入口判断：GPT 候选经 Shell 走 codex runner（explorer 与 advisor 用报告模式）；`grok-4.7` 的 `medium`、`high` 经 Shell 走 grok runner，`xhigh` 经钉型号的 `Task`；Claude 候选与 `composer-2.5-fast` 经钉型号的 `Task`（advisor 用 `advisor-*` agent，其余用 `explore` 或 `generalPurpose`）。当回合的 allowlist 只约束钉型号的 `Task` 派发。其中缺少所需变体的候选跳过，并在披露里说明。slug 不写进本档案。

| 角色 | `mainstay` | `crux` | `rescue` |
|---|---|---|---|
| explorer | composer-2.5-fast › grok-4.7[medium*, high] › gpt-6-luna[high*, xhigh] › haiku-4-5 | grok-4.7[xhigh] › gpt-6-luna[max] › sonnet-5[high] | gpt-6-sol[high*, xhigh] › opus-5-5[high*, xhigh] |
| worker | grok-4.7[high*, xhigh] › gpt-6-luna[xhigh*, max] › gpt-6-sol[high] | gpt-6-sol[xhigh*, max] › opus-5-5[medium*, high] › gpt-6-astra[low*, medium] | opus-5-5[xhigh] › gpt-6-astra[high*, xhigh] |
| advisor | gpt-6-astra[low*, medium] › opus-5-5[medium] › fable-5-1[medium] | opus-5-5[high*, xhigh] › gpt-6-astra[high] › fable-5-1[high] | gpt-6-astra[xhigh] › fable-5-1[xhigh] |

同模派发（编排姿态下的 doctrine 散文）仍是省略 `model` 的 `generalPurpose` 派发，不在本表内。

## 口头声明

- 额度余量与截止压力只经我在开工时的口头声明进入，仅在该会话有效，从不持久化。没有声明时，取格内第一个候选的 `*` 拨盘。
- handoff 车道只在我按任务或按会话声明时进入候选集。

## 调整本档案

1. 在此改格。本文件的英文版是唯一编辑源；本中文文件是翻译，不安装。
2. 从仓库检出运行伴生安装器刷新活体，本机为 `python3 scripts/install-user-level.py --home ~ --home /mnt/c/Users/Shy`；`--check` 只报漂移不写。
3. 别的都不用动：技能在档案变化时重读，改取值不需要改 doctrine 或插件。表变化时更新首段的声明日期。
