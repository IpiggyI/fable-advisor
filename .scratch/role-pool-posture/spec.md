# 角色池与姿态：拆掉按模型身份划分的架构师 / 顾问模式

Status: ready-for-agent

关联：讨论记录 `docs/chatgpt_模型编排模式比较_6aa2cfb9.md`；本次 grilling 会话 Q1–Q22；被改写的前提见 [ADR 0005](../../docs/adr/0005-model-routing-and-receipt-gate.md)（架构师层按系列判定）、[ADR 0006](../../docs/adr/0006-pareto-lane-routing-inhouse-promotion.md)（两段式路由、In-house 升格）、[ADR 0013](../../docs/adr/0013-delivery-contract-not-build-instructions.md)（产物类别边界、前言单源）。术语以根目录 `CONTEXT.md` 为准（本次已改写 `角色与档位` / `车道` / `姿态` 三节）。决策记录待落 ADR 0014。

## Problem Statement

插件从 v1 到 v4.2 的组织哲学是"一强带弱"：会话模型身份决定模式——Fable / Opus 系列进架构师层（只写契约、派活、验收，不碰交付物），其余模型进 advisor-only（自己实现，只在承诺边界问顾问）。这套划分有三个已经暴露的问题：

1. **前提没被遵守。** 用户实际最常用的架构师是 Opus 而不是 Fable（单价原因）；"主代理必须是最强模型"这个假设在实践里已经松动。与 GPT 的两轮讨论（`docs/chatgpt_模型编排模式比较_6aa2cfb9.md`）也得出：没有哪一种"谁当主代理"的固定组合天然胜出，任务结构比组织形式更重要。
2. **grok build 的意外观察。** grok build 继承 Claude Code 配置（`grok inspect` 一手证实：读 `~/.claude/CLAUDE.md`、`~/.claude/rules/*.md`、插件与 hooks），本插件在其中直接可用。一个 grok-4.6 主代理在现行规则下本应被判进 advisor-only，却表现得像架构师：主线程推进判断、派子代理调查、派子代理执行、不时问顾问。模式门挡的是模型身份，挡不住能力，也挡不住用户的真实用法。
3. **五个平行分类各自绑死型号。** 用户设想的下一步是"预先划分好多个角色，让主代理自行调用"。但若把 轻量工作 / 常规实现 / 高级实现 / 高级顾问 / 审查员 五类各自钉上型号写进仓库，型号每几个月换代一次，公开 fork 会承载一名用户的排名，与 ADR 0006 "机制入库、判断入用户规则" 的分层冲突。

另有三处与现状脱节的事实（2026-09-11 一手探针）：grok CLI 1.0.25 已有 `--effort {low,medium,high,xhigh}`，但 `lanes-claude-code.md` 仍写 "the grok CLI has no such knobs"，runner 也不传；两条 runner 都假设有 diff（`no_diff` 是错误），所以 explorer / advisor 这类只读角色无法经 runner 到达 grok / GPT 家族；Claude Code 子代理已支持按次 `model` 参数（ADR 0013 复盘条件命中），同模派发在 Claude Code 侧可以落地。

## Solution

**用"角色 × 档位 × 车道 × 姿态"取代"模式 × 车道"。**

- **姿态**取代模式：主代理对交付物只有两种关系——`编排`（不亲手改交付物）与 `实现`（可亲手改）。两者只差这一条规则；派发任一角色在两种姿态下都可用。选择器是用户声明或上层指示，不是模型身份；没人声明时，存在上游任务件（`.scratch/<feature>/issues/`、Trellis task、spec 文件）即 `编排`，否则 `实现`。ADR 0013 的产物类别边界只在 `编排` 姿态下生效。
- **决策类型门**取代身份门：对任何主代理都适用的一张关键点清单（架构 / 数据迁移 / API 形状 / 重构策略；推翻既定方案；改公共接口或跨模块依赖；放宽验收标准；同一问题两次失败；宣告多步交付物完成前）。到这些点位咨询 advisor；没有机械门，不逐 diff 过审。
- **三角色**（契约形状）：`explorer` 只读检索回证据；`worker` 可写实现回 diff 与验证证据；`advisor` 只读判断，两种请求形状（`决策` / `验收`）。**三档位**：`light` / `standard` / `senior`，与角色正交。用户的五分类映射为：轻量工作 = explorer@light + worker@light；常规实现 = worker@standard；高级实现 = worker@senior（接管 = senior worker + 接管契约）；高级顾问与审查员 = advisor（合并）。
- **车道改机制名**：`grok lane` / `codex lane` / `claude lane` / `handoff lane`。车道回答"怎么到达"，角色与档位回答"派什么"。
- **填充表**（角色, 档位）→ 候选车道与拨盘，放用户级规则，逐行带日期戳与失效条件；仓库 doctrine 不含型号排名。
- **runner 补两个入参**：grok 的 `effort`；两条 runner 的 `mode: "report"`（只读、不期待 diff、receipt 记报告正文）。
- **前言瘦身**到三行：姿态行、GAPS 定义行、报告形状行。
- **第一原则改写**为与主代理档位无关的三句：把判断花在它稀缺的地方；把体量隔离在主代理上下文之外；编排姿态下每一处交付物改动都有一个不同于作者的读者。
- **版本 5.0.0**（模式退役、车道改名、runner 契约扩展、前言语义变更、`implementer` agent 移除——破坏性）。

## User Stories

1. 作为用 Opus 当主代理的用户，我想让会话在需要时直接做架构师的事而不被"你不是 Fable"拦住，以便主代理的选择由我决定而不是由型号名决定。
2. 作为用 grok-4.6 当主代理的用户（grok build 或 Cursor），我想让主代理能派 explorer 调查、派 worker 执行、问 advisor 判断，以便廉价主代理也能用整套角色池。
3. 作为主代理，我想从"用户声明 → 上层指示 → 是否存在上游任务件"这个顺序读出自己的姿态，以便不靠"改动够不够小"这种自判来决定能不能碰交付物。
4. 作为处于 `编排` 姿态的主代理，我想继续受产物类别边界约束（交付物一律经 worker 修改），以便"小改动亲手做"的泄漏点不会因为拆了模式门而重新出现。
5. 作为处于 `实现` 姿态的主代理，我想直接改交付物，同时照样能派 explorer 查 bug、派多个 worker 并行、在关键点问 advisor，以便"实现姿态"不被读成"一把梭、不派活"。
6. 作为主代理，我想有一张对任何模型都适用的关键点清单来决定何时问 advisor，以便咨询发生在决定下一小时是否白费的点位上，而不是每次改动都问。
7. 作为主代理，我想在宣告多步交付物完成前把契约、diff 与 receipt 交给 advisor 的 `验收` 形状，以便最后一次判断来自一个没有参与实现的上下文。
8. 作为主代理，我想按"判断力依赖度"先选（角色, 档位），再在该格的填充里按我的 profile 做帕累托选择，以便正确性筛选先于偏好，与 ADR 0006 的两段式一致。
9. 作为主代理，我想在一张返工票失败并归因为能力不足后，把任务升到更高档位的 worker 并附上原契约、前车道报告与 receipt，以便接管不从零开始，也不重复失败的车道。
10. 作为主代理，我想在归因为契约缺口时修正契约并复用原车道会话，以便不把契约问题误当能力问题去升级。
11. 作为用户，我想把"角色 → 型号 + effort"的填充表写在自己的规则文件里并带日期戳，以便换代时只改我的表，仓库 doctrine 保持型号中立。
12. 作为用户，我想在开工时口头声明额度与工期约束，以便它们只影响当次会话的帕累托选择、不落盘、不过期陈旧。
13. 作为 fork 维护者，我想让仓库 doctrine 里的角色与车道定义不含任何型号名，以便他人 fork 不继承我的排名。
14. 作为架构师，我想在 grok spec 里写 `effort`，以便 worker@light 与 worker@standard 在 grok lane 上能用不同的思考档位。
15. 作为架构师，我想在 grok spec 里写了非法 `effort` 时立即得到 `spec_invalid` 而不是一次付费调用后的模糊失败，以便与 codex lane 的 fail-loud 一致。
16. 作为架构师，我想用 `mode: "report"` 派一个 grok 或 GPT 家族的 explorer 去只读检索并拿回报告正文，以便填充表里 explorer@light 的 grok / luna 填充不是空话。
17. 作为架构师，我想用 `mode: "report"` 派 astra 当 advisor，以便 advisor 的填充不限于 Fable 家族。
18. 作为架构师，我想让报告模式下工作树出现改动被记为独立失败类而不是 `complete`，以便只读角色越权时 fail loud。
19. 作为 worker 车道，我想前言只告诉我"你持有本契约 Files 范围内的交付物、机器级'架构师不碰交付物'规则不适用、拆分派发是你的事"和 GAPS / 报告的定义，以便不被当成什么都不懂的人来教。
20. 作为 worker 车道，我想在需要时派自己的子代理把任务拆开并行，以便车道原本的能力不被 `--no-subagents` 砍掉。
21. 作为 advisor，我想保持 Read / Grep / Glob 只读三件套，`验收` 形状靠读 diff 与 receipt 里的真实命令输出，以便不引入写权限、也不重跑已经有一手证据的验证。
22. 作为 Cursor 会话的主代理，我想通过 Shell 跑 codex runner 到达 GPT 家族，以便 Cursor 的 Task 枚举里没有 GPT 时仍有 codex lane。
23. 作为 Cursor 会话的主代理，我想派 `fable-advisor` 时只被要求"显式、非 inherit 的 `model`"而不被要求特定家族，以便填充表决定家族、门只防静默继承。
24. 作为 Cursor 用户，我想 `lanes-cursor.md` 不枚举 allowlist 里有什么型号，以便 allowlist 随时调整时文档不过期。
25. 作为 Claude Code 用户，我想 `worker` agent 以 `opus` 别名为默认、按次 `model` 参数可覆盖，以便同模派发在 Claude Code 侧真正落地而不是"退化为 Opus 并披露"。
26. 作为读 README 的新用户，我想看到插件的定位是"角色池 + 姿态 + 升级 + 独立评审"而不是"旗舰架构师带廉价车道"，以便不被引导去买最贵的模型当主代理。
27. 作为中文读者，我想 `docs/zh/` 下每个运行时 md 的孪生在同一提交里更新，以便 `tests/test_zh_mirror.py` 保持绿且内容不落后。
28. 作为回头想在旧路线上迭代的用户，我想有一条分支保留 4.2.0 时点的完整仓库，以便原路线可以继续研究而不受 5.0.0 影响。

## Implementation Decisions

### 概念层（doctrine）

- **姿态取代模式。** `架构师层` / `advisor-only` 两个概念退役；`架构师` 保留为编排姿态下主代理的职责名；新增 `主代理`。姿态选择器与默认规则如 Solution 所述。姿态是相对派发关系的：被派出的车道对其契约是 `实现` 姿态，它若再派子代理，对子代理就是 `编排`。
- **决策类型门对任何主代理硬性适用**——"硬"指清单对所有档位都生效，不指机械执行；触发点只有清单上的关键点。"宣告完成前"一项改归 advisor 的 `验收` 形状。
- **三角色 × 三档位**按 `CONTEXT.md` 定义。角色是契约形状（输入 / 权限 / 输出），不含型号；档位是能力等级；拨盘（型号 + effort）是档位在某条车道上的实现。advisor 任一档位都可派——它的权威来自读到的代码，doctrine 不用档位否定这一点。
- **车道改机制名**：`grok lane` / `codex lane` / `claude lane` / `handoff lane`。旧名 Routine / Cross-vendor / In-house 在运行时文字与 README 中全部替换；历史 ADR 不追改。`同模派发` 是 claude lane 的一个拨盘，只用于编排姿态下的准则散文类交付物。
- **两段式路由**改为：stage 1 按判断力依赖度定（角色, 档位）；stage 2 在该格的填充里按用户 profile 做帕累托；无声明时退化为该格最便宜的胜任填充、各车道按默认拨盘计价。低置信度逃生门两触发器不变。
- **升级路径**：一张返工票失败 + 归因（能力 vs 契约缺口）。能力不足 → 新会话、更高档位 worker、接管契约（原契约 + 前车道报告 + receipt）；契约缺口 → 修正契约、复用原车道会话。senior 档也允许作为首选入口。取代现行"两次失败 → 新会话重跑 stage 1"。
- **委派深度不限。** 车道可派子代理，runner 不传 `--no-subagents`。复盘条件：出现成本失控或无法归因的失败。
- **第一原则**改为三句（见 Solution），全文去掉"会话模型是最贵的车道"这一前提。
- **advisor 合并审查员。** 一个角色、两种请求形状（`决策` / `验收`）。现行 Tier 3 文字改为"advisor 的 `验收` 形状"；`/codex:adversarial-review` 从 doctrine 里移到填充表可选项。agent 名保留 `fable-advisor`；description 与正文去掉 Fable 系列身份句，保留"上下文干净的第二读者"与 300 词上限。
- **前言三行**：姿态行 / GAPS 行 / 报告形状行。报告头改 `WORKER REPORT`（OBJECTIVE / CHANGES / VERIFIED / GAPS 四字段不变；runner 不解析它，receipt 已含 `changed_files` 与验证输出）。
- **grok build 不转正**：不写 `lanes-grok-build.md`；已知未知（`implementer` 未被其发现、receipt gate hook 在其中是否生效）记入 ADR 备注。

### 插件 agent 定义

- `implementer.md` 退役，改为 `worker.md`：`model: opus`（别名槽位，按次覆盖调档位）、`effort: medium`（角色默认）、`tools` 不限；正文只保留 claude lane 特有的三条披露（同族无跨厂评审、共享 Anthropic 额度、最高单价）与"若跨厂 CLI 车道其实可用则在报告中说明"。
- `fable-advisor.md` 保留文件名与 agent 名：`model: fable`（默认，按次可覆盖）、`effort: high`、`tools: Read, Grep, Glob`、只读；正文写两种请求形状的输入与输出。
- explorer 不建文件：Claude Code 用内建 `Explore`，Cursor 用 `explore`，grok / GPT 家族经 runner 报告模式。Claude Code 文档写明同名用户定义可覆盖 `Explore`，需要时再补。

### runner 契约

- **grok spec 新增 `effort`**：白名单 `{low, medium, high, xhigh}`（grok CLI 1.0.25 实测取值），越界 `spec_invalid`；省略则不传 `--effort`，交 CLI 默认；receipt 记实际使用值。codex 的 `effort` 枚举与按模型默认不变；codex 模型白名单 `{gpt-6-astra, gpt-5.6-luna}` 不变，`gpt-5.6-sol` 不加回。
- **两条 runner 新增 `mode`**：取值 `implement`（默认，现行语义）与 `report`。报告模式下：以只读工具集起 CLI（grok 用 `--tools` / `--disallowed-tools` 限制到只读内建工具；codex 用 `--sandbox read-only`）；`files` 是只读范围，允许为空；`verification` 允许为空；运行结束工作树无改动是正常态（`no_diff` 在该模式下不是错误类）；工作树出现改动记新错误类 `unexpected_diff`，不得 `complete`；receipt 新增 `mode` 与 `report`（CLI 最终消息正文）。五部字段复用，不另起 schema。具体只读工具集的取值由车道以一手探针确定并记入 receipt 契约测试。
- 前言加载、`resume_session_id`、静默截止、receipt gate 语义不变；报告模式的 pending spec 同样受 receipt gate 管辖。
- `lanes-claude-code.md` 更正 "grok has no such knobs"，补 `effort` 与 `mode` 两节。

### Cursor

- `lanes-cursor.md` 改写：Task 钉模型派发仍是 claude / grok 家族的路径；GPT 家族经 Shell 跑 codex runner，pending / receipt 流程照走，**无 receipt gate**（Cursor 是否加载插件 Stop hook 未探明，记为待探针假设）、fail open、主代理亲自判 receipt——与 handoff lane 同一安全等级。不枚举 allowlist 内容；effort 钉在 slug 的说明保留。
- `cursor-hooks/fable-lane-family-gate.py`：只守具名 agent `fable-advisor`；要求 `model` 显式且非 `inherit`；删除家族匹配与 `implementer` 分支。`fable-lane-pin.mdc` 同步改写。

### 文档与版本

- `SKILL.md` 重写受影响章节（第一原则、委派边界改随姿态、车道表、两段式、升级、承诺边界并入决策类型门、验证三层的 Tier 3 措辞），词数不超过 ADR 0012 / 0013 约定的约 1.9k；harness 判别句与两个分支文件指针保留。
- `README.md`：定位语、车道表、"Upgrading" 只追加 v5.0.0 条目、历史叙述不改写。`plugin.json` description 与 version → 5.0.0；`docs/agents/plugin-release.md` 若有版本示例同步。
- `docs/zh/` 镜像：新增 `docs/zh/agents/worker.md`，删除 `docs/zh/agents/implementer.md`，所有改动的运行时 md 的孪生同批更新。
- 仓外（用户安装，架构师起草文本）：`~/.claude/rules/fable-advisor.md` 与 `.cursor/rules/fable-advisor.mdc` 改为姿态默认与声明词、填充表（用户五行映射到角色 × 档位，逐行日期戳与失效条件）、决策类型门清单；第三方架构师名单区块退役。

### 已记录的假设（带失效条件）

- grok CLI `--effort` 取值 `{xhigh, high, medium, low}`（2026-09-11，v1.0.25 实测）；CLI 换版重验。
- Claude Code 子代理支持按次 `model`、frontmatter `effort`（2026-09-11 官方文档）；`effort` 无按次参数，故档位在 claude lane 上只能靠按次 `model` 调。
- Cursor 不加载插件 Stop hook（未探明，按"无 gate"设计）；一旦探明加载，`lanes-cursor.md` 改为"有 gate"。
- grok build 能读到插件 agent 目录但只发现 `fable-advisor`（2026-09-11 `grok inspect`）；`worker.md` 是否被发现待观察。

## Testing Decisions

好的测试只看进程边界上的可观察行为：给 runner 一个 spec 与一组假 CLI，检查 receipt 字段与传给假 CLI 的参数；给 gate 一个 stdin payload，检查允许 / 拒绝；给镜像脚本一棵目录树，检查一一对应。不测 prompt 措辞，不 mock 内部函数。

- **runner 契约**（既有 seam：`tests/test_runner_contract.py`，假 `codex` / `grok` / `git` 二进制经 PATH 注入）：
  - grok `effort` 合法值被以 `--effort <v>` 传给假 grok 并记入 receipt；非法值 → `spec_invalid`、不 spawn；省略 → 不传该 flag。
  - `mode: "report"`：只读工具限制参数出现在假 CLI 收到的 argv 中；假 CLI 不改工作树 → `error_class: complete` 且 receipt 含 `mode: "report"` 与非空 `report`；假 CLI 改了工作树 → `unexpected_diff`；`files` 与 `verification` 为空被接受。
  - `mode: "implement"` 与省略 `mode` 的行为与现行完全一致（回归）。
  - 非法 `mode` → `spec_invalid`。
- **Cursor 家族门**（既有 seam：`tests/test_lane_family_gate.py`，stdin payload → 退出码 / 输出）：`fable-advisor` 无 `model` / `inherit` → 拒绝；任意显式非 inherit 型号（含非 Fable 家族）→ 放行；`generalPurpose` 无论有无 `model` → 放行；原 `implementer` 分支用例删除。
- **zh 镜像**（既有 seam：`tests/test_zh_mirror.py`）：`worker.md` 孪生存在、`implementer.md` 孪生不存在。
- **receipt gate**（既有 seam：`tests/test_receipt_gate.py`）：不改语义，保持绿；可加一例"报告模式 pending 无 complete receipt 仍拦"。
- **准则散文**（无可执行校验器）：结构化 grep 确认退役短语消失（`Routine lane`、`Cross-vendor lane`、`In-house lane`、`architect tier`、`advisor-only`、`IMPLEMENTER REPORT`、`no such knobs`）、新短语出现（`posture`、`explorer` / `worker` / `advisor`、`light` / `standard` / `senior`、`mode: "report"`）；`SKILL.md` 词数 ≤ 约 1.9k；两个行为场景——一张有上游任务件的小票在 `编排` 姿态下派给 grok worker@standard 记往返次数与 GAPS 内容；一次无任务件的 bug 排查在 `实现` 姿态下派 explorer 后由主代理直接修，记 advisor 是否在清单点位被咨询。

## Out of Scope

- grok build 作为正式 harness（独立 lanes 文件、其 hook 与 agent 发现问题的修复）。
- 按（角色, 档位）拆多个 agent 文件；explorer 的独立 agent 文件。
- advisor 获得 Bash 或任何写权限；advisor 自己重跑验证。
- 委派深度、并发、重试、咨询次数的机械限制与成本账本。
- `gpt-5.6-sol` 回到 codex 白名单；codex `effort` 默认值调整。
- Cursor 加载插件 Stop hook 的探针与据此的 gate 设计（先按无 gate 落地，探明后另开票）。
- 决策类型门的机械执行（hook 级强制）。
- 上游同步与 ADR 0001 分叉纪律之外的任何上游吸收。
- 用户级规则文件的安装（架构师只起草文本）。

## Further Notes

- **决策记录**：本 spec 落地前后写 ADR 0014，记录整条决策链（Q1–Q22）与被否决方案：完全拆门 / 门变默认（选决策类型门）；恢复大小例外 / 审查员兜底（选边界随姿态）；五平行分类（选三角色 × 三档位）；独立审查员角色（并入 advisor）；advisor 加 Bash / 走 codex 沙箱（选只读三件套）；前言保留 Gaps 整段 / 删前言（选三行）；runner 不改只用 harness 内建 explorer（选报告模式）；家族门保留家族检查 / 拆门（选只查显式 pin）；`--no-subagents`（选不限深度）。
- **旧路线保留**：分支 `feature/v4-architect-mode` 指向 4.2.0 时点的 `main`（提交 `25ddc8d`），供在原"一强带弱"路线上继续迭代或调研。
- **复盘条件**（写入 ADR 0014）：深度不限导致成本失控或失败无法归因 → 重议一层委派；姿态默认误判（有任务件却该直接改、或反之）累计 ≥3 次 → 重议默认规则或声明词；填充表某格长期只有一个填充 → 该档位是否多余；Cursor 探明加载 Stop hook → 改 `lanes-cursor.md`；任一模型换代 → 用户填充表按失效条件重估。
- 与上游 v5.x（钉死 Fable 5.1 架构师、强制终审）方向相反，按 ADR 0001 纪律记为有意分叉。

## Comments

### 2026-09-12 — 实施记录（工单 01–08 完成，09 至版本号与全测）

- 提交区间 `25ddc8d..HEAD`（`main`）；旧路线分支 `feature/v4-architect-mode` = `25ddc8d`。
- 派发：01 / 02 / 02b codex lane（astra，隔离 worktree，已合入并删除）；03 / 04 同模派发；05 / 06 / 07 grok lane；08 架构师亲写。返工两次：07（历史段落还原）、06（拒绝文案）。
- advisor 验收形状对 runner 合并 diff：ACCEPT；发现契约空白（空报告可 `complete`）→ 02b 新增 `empty_report`。
- 四个测试脚本全绿（15/15、16/16、7/7、8/8）；旧名清扫零命中（README 历史段落除外）。
- `/code-review`（基点 `25ddc8d`）：Standards 轴一条硬违规——运行时 md 与中文孪生未落同一提交（HEAD 配对完整，提交未 push，是否压缩由用户定）；Divergent Change → 后续票 10（报告模式前言分流，`needs-triage`）。Spec 轴：`CONTEXT.md` 残留"承诺边界"、`AGENTS.md` 首句旧定位——已修；`unexpected_diff` 覆盖 `*_failed` 记作已知（见 02 票评论）。
- 范围外披露：06 车道把门脚本与 pin 规则同步到了 WSL / Windows live 路径（为保 ADR 0011 漂移用例绿）；`docs/chatgpt_模型编排模式比较_6aa2cfb9.md` 作为讨论记录随规划提交入库。
- 未做：push、两侧 `claude plugin update`、两个姿态的真实场景（须在更新后的插件上跑）——等用户授权。

