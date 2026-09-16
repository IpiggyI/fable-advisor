# Fable Advisor 路由档案（中文备份，不是活体，不安装）

本用户路由档案于 2026-09-16 声明，取代 2026-09-11 的版本。锚定 Grok 4.6、GPT-6 Astra、GPT-5.6 Sol、GPT-5.6 Luna、Opus 5、Sonnet 5、Haiku 4.5、Fable 5.1 与 Cursor 的 Composer 2.5。任一相关模型换代时重估对应条目。`fable-advisor:orchestration` 读取本档案并拥有编排行为；本文件只承载用户的取值。

## 首轮池与 senior 门

- `light` 与 `standard` 两列是一个**首轮池**。两档之间按技能的 Stage 1 判断选择，都没有前置条件；首轮派发可以取池内任一拨盘，任务需要时取最贵的那个也可以。没有别的理由时，取最便宜的够用候选，用它的 `*` 拨盘。
- `senior` 列有门：只经技能的升级梯（池内两次能力归因的失败）或我的声明到达。这一列的拨盘刻意换用与池内不同的型号。
- 拨盘记法：`model[a*, b, c]` 列出该型号在该格可选的强度，全部首轮可选，`*` 是默认。没有 effort 维度的型号裸写。
- 格内候选顺序即车道默认顺序：grok lane › codex lane › claude lane。专长只作平手裁决：前端偏 claude lane，后端偏 codex lane。复杂问题偏 codex lane。
- 升级按技能的升级梯 R1–R4。同一型号只提升一次，所以典型路径是 `grok-4.6[medium]` → `grok-4.6[xhigh]` → `gpt-6-astra[medium]`。

## Claude Code 候选

到达方式：Grok 经 grok runner（spec `effort`）；GPT 经 codex runner（spec `model`、`effort`）；Claude 经本插件的 agent 文件加按次 `model`（派发不带 `name`）。每个 effort 对应的 agent 文件：explorer `explorer-h` / `explorer-xh`；worker `worker-md` / `worker-h` / `worker-xh`；advisor `advisor-l` / `advisor-md` / `advisor-h` / `advisor-xh`。Haiku 没有 effort 维度：经 `explorer-h` 派发，effort 声明无效果。

| 角色 | light | standard | senior（有门） |
|---|---|---|---|
| explorer | grok-4.6[medium] › gpt-5.6-luna[high] › haiku-4-5 | grok-4.6[xhigh] › gpt-5.6-luna[max] › sonnet-5[high*, xhigh] | gpt-5.6-sol[high*, xhigh] › opus-5[high*, xhigh] |
| worker | grok-4.6[medium*, high] › gpt-5.6-luna[xhigh] › sonnet-5[high] | grok-4.6[xhigh] › gpt-5.6-sol[high*, xhigh] › gpt-6-astra[low] › opus-5[high*, xhigh] | gpt-6-astra[medium*, high] |
| advisor | gpt-6-astra[low] › fable-5-1[low] | gpt-6-astra[medium] › fable-5-1[medium] | gpt-6-astra[high*, xhigh] › fable-5-1[high*, xhigh] |

advisor 默认格：决策形状用 `standard` 格；验收形状用 `light` 格。advisor 只在 verdict 自报低置信或我声明时到 `senior`。Luna 作 worker：只在我声明、或任务简单且想用 GPT 家族时。

## Cursor 候选

到达方式：GPT 行经 Shell 跑 codex runner（explorer 与 advisor 用报告模式）；Grok 的 `medium` / `high` 经 Shell 跑 grok runner，Grok 的 `xhigh` 用钉了活 Grok slug 的 Task；Claude 行用钉了该家族活 slug 的 Task（advisor 用 `advisor-*` agent，其余用 `explore` 或 `generalPurpose`）；Composer 用钉了其 slug 的 `explore`（cursor lane）。slug 来自本轮 allowlist，不在此持久化：钉住的 slug 的 effort 是它的后缀，所以一格只列 allowlist 里有的变体，变体缺席的候选跳过并在披露里说明。2026-09-16 的 allowlist 有 Grok 4.6 xhigh、Opus 5 high、Fable 5.1 xhigh、Composer 2.5 fast；Sonnet 与 Haiku 没有 slug。

| 角色 | light | standard | senior（有门） |
|---|---|---|---|
| explorer | composer-2.5-fast › grok-4.6[medium] › gpt-5.6-luna[high] | grok-4.6[xhigh] › gpt-5.6-luna[max] | gpt-5.6-sol[high*, xhigh] › opus-5[high] |
| worker | grok-4.6[medium*, high] › gpt-5.6-luna[xhigh] | grok-4.6[xhigh] › gpt-5.6-sol[high*, xhigh] › gpt-6-astra[low] › opus-5[high] | gpt-6-astra[medium*, high] |
| advisor | gpt-6-astra[low] | gpt-6-astra[medium] | gpt-6-astra[high*, xhigh] › fable-5-1[xhigh] |

Fable 只出现在 senior 格，因为 allowlist 只有它的 xhigh 变体；Cursor 里 standard 的 advisor 因此是经 codex runner 的 Astra。同模派发（编排姿态下的 doctrine 散文）仍是省略 `model` 的 `generalPurpose` 派发，不在本表内。

## 资源偏好

2026-09-06 声明：

- 速度，最快在前：grok-4.6 > fable5.1 ≈ astra ≈ opus5 > Luna-max。
- 价格，最便宜在前：Luna-max < grok-4.6 << opus5 ≤ astra ≤ fable5.1。
- 能力：Luna-max < grok-4.6 ≤ opus5 < astra ≈ fable5.1。
- 专长：前端偏 claude lane；后端偏 codex lane。反例累积时重估。
- 额度余量与截止压力只经我在开工时的口头声明进入，仅在该会话有效，从不持久化。没有声明时，用最便宜的够用候选，按它列出的拨盘。
- handoff lane 只在我按任务或按会话声明时进入候选集。

2026-09-16 声明：

- 不同型号之间的能力差距大于同一型号不同 effort 之间的差距。依据，同一测试集：opus-5[high] 73%±2%、opus-5[medium] 69%±1%、sonnet-5[high] 48%±5%、sonnet-5[medium] 40%±3%。这就是为什么一次提升之后要换型号、以及 senior 列直接换型号。

## 调整本档案

1. 在此改格。本文件的英文版是唯一编辑源；本中文文件是翻译，不安装。
2. 从仓库检出运行伴生安装器刷新活体，本机为 `python3 scripts/install-user-level.py --home ~ --home /mnt/c/Users/Shy`；`--check` 只报漂移不写。
3. 别的都不用动：技能在档案变化时重读，改取值不需要改 doctrine 或插件。表变化时更新首段的声明日期。
