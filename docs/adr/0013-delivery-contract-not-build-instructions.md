# 0013 — 交付契约取代施工说明：架构师控制面收缩、委派边界按产物类别、返工票与会话复用

- **Status**: accepted（2026-09-06 用户确认 Q1–Q27 共识）
- **Date**: 2026-09-06
- **影响范围**: `plugin/skills/orchestration/SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md`、新增 `lane-preamble.md`；`plugin/agents/implementer.md`、`plugin/agents/fable-advisor.md`；`plugin/scripts/run-codex.mjs`、`run-grok.mjs`（`resume_session_id`、前言加载；其余 runner 变更见 ADR 0003 / 0009 追记）；`README.md`、`docs/zh/`；根目录 `CONTEXT.md`、`AGENTS.md`；版本 4.0.0；用户私有规则（仓外）
- **关联**: [ADR 0005](./0005-model-routing-and-receipt-gate.md)（架构师层按系列判定）、[ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md)（两段式路由、profile 分层）、[ADR 0008](./0008-context-discipline.md)（三级验收，本次保留并加一条 Tier 2 触发）、[ADR 0012](./0012-orchestration-skill-progressive-disclosure.md)（第 6 条引入的经济豁免，本次撤回）、[ADR 0003](./0003-codex-lane-param-policy.md) 与 [ADR 0009](./0009-grok-lane-dewrapper-runner.md) 的同批追记；讨论记录 `docs/chatgpt_插件架构调整建议.md`

## 背景

插件从 v1 起的组织哲学是「一强带弱」：主会话先把需求、架构、接口、调试假设想清，写成五部 spec，车道只把完整规格变成代码。这套哲学在 `SKILL.md` 里落成几句硬话："Reason once, then hand off"、"hypothesis selection when debugging" 归架构师、"A lane that reports a spec gap gets a corrected spec, not a 'use your judgment'"；在 `implementer.md` 里落成 "The main session does the thinking … You do the typing" 与 "Implement exactly the spec"。

三件事让这套前提松动：

1. 车道模型换代（Grok 4.6 / 4.7、GPT-6 Astra、Opus 5）。用户的判断是三家旗舰能力接近；本 ADR 把它记为**设计假设**而非事实——改造方向不依赖「完全同级」，只依赖「车道已能独立完成契约内的实现」。
2. 经济豁免（ADR 0012 第 6 条，「spec 比 diff 还贵的改动才亲手改」）在实践里被用成「架构师自判小改动就 inline」，改动脱离了委派—执行—评审链，没人评审。什么算小由模型自判，这是泄漏点。
3. 执行侧姿态只到达 in-house lane：两条 runner 的 `renderPrompt` 只原样转发五部（`run-codex.mjs:148`、`run-grok.mjs:123`）；Cursor 侧 frontmatter 被忽略、`implementer` 不在 Task 枚举，没有任何车道读 `implementer.md`。

与 GPT 的两轮讨论（`docs/chatgpt_插件架构调整建议.md`）先扩到「组长 + 任务负责人 + 独立审查员」的全面组队，再被用户收回到：上游已有规划工作流（`.scratch/` issue 与 spec、Trellis task），插件只负责让既定方案落地；硬骨架（强制委派、执行边界、评审闭环）不动，只收缩「老师对实现细节的控制」。本 ADR 记录这条收敛后的路线及其边界。

## 选项对比

### 决策一：架构师的控制面

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 保留「先想清再派」 | 现状稳定、无返工争议 | 替已能独立完成的车道预先决定每个细节，干预的增量价值说不清；旗舰 token 花在实现细节上 | 车道越强，指导越接近反效果 |
| 全面组队：组长 + 任务负责人 + 独立审查员（GPT 第 4 轮） | 角色最清楚 | 与上游规划工作流重叠；需要 attempt_id、状态机、worktree 隔离等一整套工程 | 一次改动跨度过大，无法归因收益 |
| **契约不是教程，硬骨架不动（选定）** | 只改「spec 写什么」和「车道如何读 spec」，机制不动 | 软规下架构师可能漂回老师姿态 | 以复盘条件兜住（见下） |

### 决策二：委派边界

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 经济豁免（现状） | 省一次派发 | 「小」由模型自判；inline 改动无人评审 | 边界可协商即无边界 |
| 完全无例外 | 最硬 | 版本号、ADR、词表也要走车道，往返压倒收益 | 规则被实践绕过 |
| **按产物类别划界 + 同模派发（选定）** | 类别清单无需逐次判断；准则散文的一致性有专门出口 | 类别表要维护 | 类别归属争议时默认按交付物处理 |

### 决策三：spec 形状

| 方案 | 优点 | 缺点 |
|------|------|------|
| **五部不变、改语义（选定）** | 零 runner 变更；授权集合 = Constraints 补集，不必枚举 | 「Files = 授权范围」要靠文字说清 |
| 六部：加 `authority`（delegated / requires_approval） | 授权边界显式可见 | 枚举授权本身就是替车道想实现；车道易把「不在 delegated」读成禁止；碰 fail-loud 键白名单；与上游 v5「六段 spec」（第六段是 model/effort）撞名 |
| Constraints 内固定 "Reserved:" 子标题 | 折中 | 是第一方案的子集 |

### 决策四：对「怎么做」的禁令强度

软规先行（不要求写步骤，允许写），带观察窗与硬化触发；硬禁作为后续方向。用户裁定：先观察。

### 决策五：返工形态

| 方案 | 缺点 |
|------|------|
| 新 spec、新会话 | 车道重建上下文，成本与漂移都高 |
| Cursor 发消息、Claude Code 重跑 | 两套写法 |
| **返工票 + 默认复用会话（选定）** | runner 需加 `resume_session_id` |

### 决策六：执行侧姿态如何到达车道

| 方案 | 缺点 |
|------|------|
| 只靠 `implementer.md` | Cursor 侧与 CLI 侧都读不到 |
| 架构师每张 spec 手写一段 | 每次花旗舰输出 token，且会漂 |
| **`lane-preamble.md` 单源（选定）** | runner 需运行时读文件 |

## 决策

1. **契约不是教程。** 五部 spec 的语义改为：Objective = 结果与验收标准，不写步骤；Files = 授权范围（可触碰的路径或目录，范围内新增文件允许）；Interfaces = 只列共享 / 对外契约，可为 none；Constraints = 保留项（不得改的东西、上游已钉死的选择）；Verification = 验收证据命令，至少一条「目标未达成就会失败」的检查。Constraints 未规定的实现选择默认归车道。「spec 没规定怎么做」不是契约缺口。
2. **区分契约缺口与未规定的实现选择。** 缺口（预期行为不明、要求冲突、须改保留接口、无法判定通过）上报并修正契约；实现选择（内部函数划分、等价数据结构、测试组织、契约内错误处理）车道自决，不上报、不等待。`SKILL.md` 原句「spec gap 只给修正 spec、不许 use your judgment」拆成两句。
3. **调试假设归车道。** 车道自有缺陷由车道调试，架构师只提供可复现失败；仅当缺陷归属不明（跨模块）时架构师定假设——那属于分解。
4. **委派边界按产物类别。** 交付物（随插件发布、被测试、或对外描述行为的产物）一律经车道修改，无论改动大小；协调件（任务件、决策记录、工作流状态文件、发布版本字段）架构师可直接写。ADR 0012 第 6 条的经济豁免撤回。类别口径入 `SKILL.md`（机制），本仓库的路径映射入 `AGENTS.md`。
5. **同模派发。** In-house lane 的一个拨盘：模型钉为会话模型。只用于准则散文类交付物（`plugin/skills/**`、`plugin/agents/**`），理由是与架构师判断的一致性、减少 edit/diff 往返；触发按产物类别，不由模型判「够不够核心」。Cursor 侧 = `generalPurpose` 不带 `model`（inherit）；Claude Code 侧 `implementer` 为 `model: opus`，按次覆盖机制未探明前退化为 Opus in-house 并披露。
6. **评审对象改为契约。** 三级验收保留；新增 Tier 2 触发：验收测试由车道自写时，架构师读该测试文件。返工只引用违反的要求、可复现问题、缺失验证、受影响的保留接口；结构偏好不开返工票。
7. **返工票默认复用会话。** 返工票是一张新的五部 pending 文件（Objective = 缺陷：违反的要求 / 可复现失败 / 期望行为 / 证据；Files = 原范围；Verification = 原本失败的检查），带 `resume_session_id`；两条 runner 以 `codex exec resume <id>` / `grok --resume <id>` 调用，receipt 记 `resumed_from`。Cursor 侧用 Task `resume`；lifecycle 从「验证通过即 stop teammate」改为「验收通过再 stop」。两次失败仍触发重跑 stage 1，届时换新会话。
8. **`lane-preamble.md` 单源。** 新增 `plugin/skills/orchestration/lane-preamble.md`（约 150 词）：角色、授权边界、缺口协议、退出机器级编排默认（目标仓库约定仍遵守）、报告格式与验证要求。runner 运行时读取并前置到 prompt，缺失即 fail-loud；Cursor 侧派发 prompt 首行指向该文件。`implementer.md` 收敛为引用该文件加 in-house 三披露。`fable-advisor.md` 的身份句由「本会话最强模型」改为职责句（上下文干净的第二读者，权威来自读到的代码）。
9. **上游任务件按路径引用。** 上游任务件存在时，spec 引用其路径并只内联验收标准、保留项、验证命令，写明哪些节是约束性的；架构师不重述、不重新规划。措辞 harness 与 tracker 中立。
10. **软规 + 观察口径。** 不要求 spec 写步骤，允许写。观察窗：接下来 10 次派发或到下一个 minor，先到为准。
11. **Luna 与车道级帕累托。** 车道级比较按各车道默认拨盘计价（codex = astra@medium）；拨盘内档位不进车道级比较；Luna-max 只经用户声明或「任务简单且要 GPT 家族」进入。用户 profile 更新为 2026-09-06 的三行排名（Luna-max / grok-4.6 / opus5 / astra / fable5.1），入仓外规则不入本仓。
12. **文字去代际化。** 角色定义文字改「Fable 系列」「codex 车道当前目录」；具体型号只以带日期的「currently …」示例出现；`lanes-cursor.md` 不再写 slug，改写「当轮 allowlist 里的 Fable-/Grok-/GPT-family slug」。机制层（`model: fable` 别名、grok 省略 `-m`、Cursor 门禁字元匹配）已与代际无关，不动。
13. **版本 4.0.0。** 同批 runner 契约含破坏性变更（Sol / Terra 移出白名单，见 ADR 0003 追记）且姿态反转。本 fork 版本线独立，与上游 v4 / v5 无关。
14. **运行时 md 的中文版镜像。** `plugin/**/*.md` 每个文件在 `docs/zh/` 下有同相对路径的中文版（`docs/zh/skills/orchestration/…`、`docs/zh/agents/…`；现有 `docs/zh/orchestration/` 四个文件迁入）。改动运行时 md 的提交必须同批更新中文版，规则写入 `AGENTS.md` 与 `docs/agents/plugin-release.md`；`tests/test_zh_mirror.py` 只校验一一对应存在，不校验内容。中文版 repo-only，不随插件发布。

## 核心理由

1. **角色隔离与成员自主不矛盾。** 角色隔离规定「谁能做什么」，成员自主规定「在自己范围内可以自行决定多少」。本次只调后者，不放松前者。
2. **边界按类别不按大小。** 大小判断留给模型就是把硬规则变成可协商规则；类别表没有判断点。
3. **单源优于每次手写。** 执行侧姿态是确定性内容，放进代码 / 文件比让架构师每张 spec 重写便宜且不漂（用户规则第 5 条：确定性转换归代码）。
4. **复用会话是成本与一致性问题。** 车道的探索上下文是它自己付过的；返工重建一遍等于双计。
5. **自主权只存在于契约没规定的部分。** 上游钉死的接口、算法、惯例仍必须遵循；不能拿「独立判断」推翻方案。

## 实施代价

- 准则散文（同模派发）：`SKILL.md`（L7 / L18 / L20 / L70-76 / L100 重写，词数不超 ADR 0012 的约 1.9k）、`lanes-claude-code.md`（新增 Wait for the runner 节、模型段改 astra / luna、`resume_session_id`）、`lanes-cursor.md`（去 slug、lifecycle、前言指向）、新 `lane-preamble.md`、`implementer.md`（收敛）、`fable-advisor.md`（身份句）。
- runner（codex 车道，正确性关键，Tier 3 评审）：`resume_session_id` 与前言加载归本 ADR；模型白名单 / 默认 / 回退 / receipt 字段归 ADR 0003 追记；`end_to_close_ms`、`no_diff` 归 ADR 0009 追记。验证不耗额度：`node --check`、无效 spec 被拒、PATH 去掉 CLI 触发 `*_unavailable` 并检查 receipt 新字段。
- 文档同步（routine lane，串行在准则散文之后）：`README.md` 标语与 "never type code yourself"；`docs/zh/` 镜像 `plugin/` 下全部运行时 md（含新 `lane-preamble.md` 与两个 agent 文件）；新增 `tests/test_zh_mirror.py`。
- 协调件（架构师）：本 ADR、两条追记、`CONTEXT.md`（已写：架构师层重写、交付契约与产物六条、同模派发）、`AGENTS.md` 产物类别映射、版本两处、`~/.claude/rules/fable-advisor.md`；Cursor 侧用户规则由用户粘贴。
- 无可执行校验器（散文变更）：结构化 grep 检查退役短语（"do the typing"、"Reason once"、"exact paths"、"Implement exactly"）消失、新短语出现；一次行为场景——挑一张真实小票按新契约派给 routine lane，记录往返次数与 `GAPS` 内容。

## 复盘条件

- 车道改动了 Constraints 保留项、或把未规定的实现选择当 GAPS 上报，累计 ≥3 次 → 重开六部 `authority` 方案。
- 观察窗内 ≥3 张 spec 含上游未钉死的步骤清单，或出现一次「车道照架构师给的步骤做了、步骤本身错」导致的返工 → 「怎么做」从软规改硬禁。
- Claude Code 的 Task 支持按次覆盖 model（文档或实测）→ 同模派发在 Claude Code 侧落地，撤销「退化为 Opus」措辞。
- Cursor Task 枚举出现 Astra / Luna → 核对 `lanes-cursor.md` 的家族措辞是否仍足够。
- 任一模型换代 → 用户规则中 2026-09-06 的三行排名按其失效条件重估（ADR 0006 既有条件）。
- `end_to_close_ms` 数据显示 grok / codex 在 `end` 后常态滞留 → 再做 runner 行为修复（本次只加诊断，未证实的原因不修）。
- 同模派发的 edit/diff 往返并未少于跨厂车道 → 撤回该拨盘，准则散文回到常规路由。

## 备注

- 与上游 v5.0.0 方向相反（上游钉死 Fable 5.1 当架构师、强制终审、六段 spec）；按 [ADR 0001](./0001-upstream-sync-fork.md) 纪律记为有意分叉。`docs/upstream-sync/2026-09-05-digest.md` 的两项吸收（空 diff 不得 complete、退出机器级编排默认）随本批落地，后者扩展为 `lane-preamble.md`。
- 决策链见本会话 grilling Q1–Q26；用户在 GPT 讨论中的两条关键裁定：没有「组长自己出的方案」（方案来自上游任务件）；小任务例外破坏角色独立性，不设。
- 术语已入 `CONTEXT.md`：架构师层（重写）、交付契约（spec）、契约缺口、未规定的实现选择、返工票、交付物、协调件、同模派发。
