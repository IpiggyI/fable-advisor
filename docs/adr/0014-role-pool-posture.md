# 0014 — 角色池与姿态取代按模型身份划分的架构师 / 顾问模式

- **Status**: accepted（2026-09-11 用户确认 Q1–Q22 共识并批准工单拆分）
- **Date**: 2026-09-11
- **影响范围**: `plugin/skills/orchestration/`（五个英文 md）、`plugin/agents/`（`implementer.md` → `worker.md`，`fable-advisor.md` 改写）、`plugin/scripts/run-grok.mjs`（`effort`）、两条 runner（`mode: "report"`）、`tests/test_runner_contract.py`、`cursor-hooks/**` 与 `tests/test_lane_family_gate.py`、`README.md`、`docs/zh/**`、根目录 `CONTEXT.md`（已改写）、`AGENTS.md`；版本 5.0.0；用户私有规则（仓外）
- **关联**: [ADR 0005](./0005-model-routing-and-receipt-gate.md)（架构师层按系列判定——本次退役）、[ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md)（两段式路由与 profile 分层——本次保留机制、改索引对象）、[ADR 0011](./0011-cursor-lane-family-gate-user-level.md)（家族门——本次放宽为只查显式 pin）、[ADR 0012](./0012-orchestration-skill-progressive-disclosure.md)（词数预算与分支文件——本次沿用）、[ADR 0013](./0013-delivery-contract-not-build-instructions.md)（产物类别边界与前言单源——本次边界改随姿态、前言瘦身）；讨论记录 `docs/chatgpt_模型编排模式比较_6aa2cfb9.md`；spec 与工单 `.scratch/role-pool-posture/`

## 背景

插件从 v1 到 v4.2 的组织哲学是"一强带弱"：会话模型身份决定模式。Fable / Opus 系列进架构师层（只写契约、派活、验收、不碰交付物），其余进 advisor-only（自己实现、只在承诺边界问顾问）。三件事让这个前提松动：

1. **前提没被遵守。** 用户最常用的架构师是 Opus 而非 Fable（单价原因）；"主代理应是最强模型"在实践里已经不成立。与 GPT 的两轮讨论也得出：没有哪种"谁当主代理"的固定组合天然胜出，任务结构比组织形式更重要；混用的净节省 = 被替代的强模型工作 − 新增的交接、重复读取、验收与返工。
2. **grok build 的意外观察。** `grok inspect`（2026-09-11，v1.0.25）一手证实 grok build 加载 Claude Code 配置（`~/.claude/CLAUDE.md`、`~/.claude/rules/*.md`、插件、hooks），本插件在其中直接可用。一个 grok-4.6 主代理按现行规则应进 advisor-only，却表现得像架构师：主线程推进判断、派子代理调查与执行、不时问顾问——而那个"顾问"也是 grok-4.6（`model: fable` 在那里解析不到），价值来自干净上下文而非更强模型。
3. **五分类各自绑型号。** 用户设想的下一步是预先划分多个角色让主代理自行调用。若把 轻量工作 / 常规实现 / 高级实现 / 高级顾问 / 审查员 五类各钉型号写进仓库，会与 ADR 0006 "机制入库、判断入用户规则" 冲突，且型号几个月换一代。

三处与现状脱节的事实（2026-09-11 一手探针）：grok CLI 1.0.25 已有 `--effort {low,medium,high,xhigh}`，而 `lanes-claude-code.md` 仍写 "no such knobs"、runner 不传；两条 runner 都假设有 diff（`no_diff` 是错误），只读角色无法经 runner 到达 grok / GPT 家族；Claude Code 子代理已支持按次 `model` 参数（ADR 0013 复盘条件命中）。

## 选项对比

### 决策一：模式门拆到什么程度

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 完全拆除：任何主代理拥有全部权限，doctrine 对身份沉默 | 最简 | 失去 ADR 0005 "能力未知者不得自动派活" 的保护 | 弱模型写坏契约、派强车道忠实执行错任务 |
| 门变默认：不禁止，但档位决定起点姿态 | 平滑 | 仍以身份为信号；第三方名单常年为空，别名槽位可重定向，身份是弱信号 | 判定漂移 |
| **门换形态：按决策类型，不按身份（选定）** | 可判定；对任何主代理一致 | 需要维护一张关键点清单 | 清单过宽打断成灾、过窄形同虚设（复盘条件兜住） |

### 决策二：主代理是否碰交付物

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| ADR 0013 边界对所有主代理原样保留 | 泄漏点不复现 | 无任务件的小改动也要写契约派活，"没有架构师概念时强制不让写反而怪" | 规则被实践绕过 |
| 恢复大小例外（撤 ADR 0013 §4） | 顺手 | "什么算小"由模型自判——ADR 0013 已判定为泄漏点 | 边界可协商即无边界 |
| 换不变量："每处交付物改动都过审查员" | 主代理可直接改 | 每次亲手改都付一次审查员，通常比派一次 worker 更贵 | 成本倒挂 |
| **边界随姿态（选定）** | 编排姿态下边界原样；实现姿态下可直接改；选择器锚在可观察事实（上游任务件是否存在） | 多一个概念 | 默认误判（复盘条件兜住） |

### 决策三：角色如何切

| 方案 | 缺点 |
|------|------|
| 五个平行分类（轻量 / 常规 / 高级 / 顾问 / 审查员），各绑型号 | 前三类契约形状完全一样只差拨盘；型号入库 |
| **三角色（explorer / worker / advisor，按权限与输出形状）× 三档位（light / standard / senior）（选定）** | 需要"档位"这个新词 |

### 决策四：审查员是否独立角色

| 方案 | 缺点 |
|------|------|
| 独立 `审查员` 角色 | 与 advisor 用同一批模型、同为只读判断，边界说不清 |
| **并入 advisor，作为 `验收` 请求形状（选定）** | — |

### 决策五：advisor 的工具

| 方案 | 缺点 |
|------|------|
| **只读三件套（Read / Grep / Glob），验收形状读 diff + receipt（选定）** | 不能自己重跑验证——但 receipt 已含真实命令输出 |
| 加 Bash | Bash 可写，"只读"变成靠 prompt |
| 走 codex 只读沙箱（`/codex:adversarial-review`） | 只在 Claude Code 可用；作为填充表可选项保留 |

### 决策六：前言保留多少

| 方案 | 缺点 |
|------|------|
| 保留五段 | 把车道当成什么都不懂的人教；Authority / Gaps 段的观察窗内无误报证据 |
| **三行：姿态 / GAPS / 报告形状（选定）** | — |
| 删掉前言 | 姿态行抵消的是机器级规则泄漏（grok 车道读 `~/.claude/rules`、codex 车道读 `~/.codex/AGENTS.md`），不是能力问题，删不得 |

### 决策七：只读角色如何到达 grok / GPT 家族

| 方案 | 缺点 |
|------|------|
| 不改 runner，explorer 只用 harness 内建、advisor 的 astra 只经 `/codex:adversarial-review` | 填充表里 grok / luna / astra 在 explorer 与 advisor 上都是空话；Cursor 里 runner 是唯一 GPT 通道 |
| **runner 加 `mode: "report"`（选定）** | runner 契约扩展 |

### 决策八：Cursor 家族门

| 方案 | 缺点 |
|------|------|
| 保留家族检查 | advisor 只能是 Fable，与"填充表决定家族"冲突 |
| **只守具名 agent `fable-advisor`、只查显式非 inherit pin（选定）** | `generalPurpose` 派发无标记可区分 worker 与 scout，门无法扩到它 |
| 拆门 | 失去 ADR 0011 防静默继承的保护 |

### 决策九：委派深度

| 方案 | 缺点 |
|------|------|
| 一层：runner 传 `--no-subagents`，车道不派不问 | 砍掉车道原本的能力（一个 grok worker 把任务拆三份并行是合理的）；主会话排查 bug 也要派 explorer |
| **不限（选定）** | 可追踪性与成本靠复盘条件兜 |

## 决策

1. **姿态取代模式。** `架构师层` / `advisor-only` 退役。主代理对交付物只有两种关系：`编排`（不亲手改）与 `实现`（可亲手改）；两者只差这一条规则，派发任一角色在两种姿态下都可用。选择器：用户声明 → 上层指示 → 存在上游任务件即 `编排`、否则 `实现`。姿态相对派发关系：车道对其契约是 `实现`，对自己派出的子代理是 `编排`。ADR 0013 的产物类别边界只在 `编排` 姿态下生效。`架构师` 保留为编排姿态下主代理的职责名。
2. **决策类型门对任何主代理适用。** 清单：架构 / 数据迁移 / API 形状 / 重构策略；推翻既定方案；改公共接口或跨模块依赖；放宽验收标准；同一问题两次失败；宣告多步交付物完成前（→ advisor `验收` 形状）。无机械门，不逐 diff 过审。
3. **三角色 × 三档位。** 角色 = 契约形状（explorer 只读回证据；worker 可写回 diff 与证据；advisor 只读回 verdict，`决策` / `验收` 两种形状）；档位 = light / standard / senior，与角色正交；拨盘 = 车道内型号 + effort。advisor 任一档位可派。
4. **车道改机制名**：grok / codex / claude / handoff lane。旧名 Routine / Cross-vendor / In-house 退役；历史 ADR 不追改。同模派发是 claude lane 的拨盘，只用于编排姿态下的准则散文。
5. **填充表放用户规则**（角色, 档位）→ 候选车道与拨盘，逐行日期戳与失效条件；仓库 doctrine 不含型号排名。两段式改为：stage 1 定（角色, 档位），stage 2 在该格填充内帕累托。
6. **升级路径**：一张返工票失败 + 归因。能力不足 → 新会话、更高档位 worker、接管契约（原契约 + 前车道报告 + receipt）；契约缺口 → 修正契约、复用会话。senior 亦可首选。
7. **第一原则改写**为三句：把判断花在它稀缺的地方；把体量隔离在主代理上下文之外；编排姿态下每一处交付物改动都有一个不同于作者的读者。
8. **advisor 合并审查员**；工具保持只读三件套；Tier 3 改为 advisor 验收形状；agent 名保留 `fable-advisor`。
9. **前言三行**；报告头 `WORKER REPORT`。
10. **agent 文件**：`worker.md`（`model: opus`、`effort: medium`）取代 `implementer.md`；`fable-advisor.md`（`model: fable`、`effort: high`）改写。explorer 借 harness 内建。
11. **runner**：grok spec 加 `effort`（白名单 `{low,medium,high,xhigh}`，fail-loud，省略不传）；两条 runner 加 `mode ∈ {implement, report}`，报告模式只读工具集、`files` / `verification` 可空、无改动 `complete`、有改动 `unexpected_diff`、receipt 记 `mode` 与 `report`；codex 白名单与默认 effort 不变，sol 不加回。
12. **Cursor**：GPT 家族经 Shell 跑 codex runner，无 receipt gate（Cursor 是否加载插件 Stop hook 未探明）、fail open、主代理判 receipt；文档不枚举 allowlist；家族门只守 `fable-advisor` 的显式非 inherit pin。
13. **委派深度不限**；runner 不传 `--no-subagents`。
14. **grok build 不转正。** 不写独立 lanes 文件。
15. **版本 5.0.0**（模式退役、车道改名、`implementer` 移除、runner 契约扩展——破坏性）。旧路线保留在分支 `feature/v4-architect-mode`（`25ddc8d`）。

## 核心理由

1. **身份是弱信号，决策类型是可判定信号。** 门的目的从来是"关键决策不被能力不足者独断"；按决策类型设门直接命中目的，按身份设门只是代理变量。
2. **边界的理由不随主代理档位变化，但适用场景随姿态变化。** ADR 0013 否决大小例外的理由（模型自判即泄漏）仍成立，所以编排姿态下边界原样；无任务件的直接改动本就不在"委派—执行—评审"链上，用可观察事实（任务件存在与否）而非大小来切换。
3. **角色是契约形状，不是能力标签。** 三个契约形状穷尽了权限与输出的组合；能力差异放到档位这条正交轴，型号放到用户表——三层各自独立换代。
4. **advisor 的权威来自读到的代码。** 这句已在 ADR 0013 写入身份句；grok-on-grok 顾问仍有价值是它的直接旁证，因此 doctrine 不用档位否定它。
5. **前言只保留车道无法从代码库推断的事实。** 机器级规则泄漏是事实，契约语义是车道已会的事。
6. **填充表空话是最坏的 doctrine。** 只读 runner 模式是让 explorer / advisor 的 grok / GPT 填充成立的唯一路径。

## 实施代价

见 `.scratch/role-pool-posture/spec.md` 与 `issues/01`–`09`。分派：runner（01、02）走 codex lane（Cursor 下经 Shell 跑 runner，隔离 worktree），advisor 验收形状做 Tier 3；准则散文（03、04）同模派发；Cursor 门（06）、中文镜像（05）、README（07）走 grok lane；ADR / `AGENTS.md` / 用户规则文本（08）与发布（09）架构师亲做。

## 复盘条件

- 深度不限导致成本失控或失败无法归因 → 重议一层委派（runner 传 `--no-subagents`、车道以 `REQUEST` 上报）。
- 姿态默认误判（有任务件却该直接改、或反之）累计 ≥3 次 → 重议默认规则或声明词。
- 决策类型门几乎不触发或频繁打断 → 重界清单。
- 填充表某格长期只有一个填充 → 该档位是否多余。
- Cursor 探明加载插件 Stop hook → `lanes-cursor.md` 改为"有 gate"。
- grok build 发现不到 `worker.md`（如同 4.2.0 下的 `implementer`）→ 查插件 agent 发现规则。
- 任一模型换代 → 用户填充表按失效条件重估。
- advisor 验收形状因不能重跑验证而漏判 ≥2 次 → 重议决策五。

## 备注

- 决策链见本会话 grilling Q1–Q22；用户三条关键裁定：对"主代理是最好的模型"产生动摇、不想被"强 + 弱"一种组合困住；`实现` 姿态不能读成"不派子代理"；allowlist 随时变、不要过度关注。
- 与上游 v5.x（钉死 Fable 5.1 架构师、强制终审、六段 spec）方向相反，按 [ADR 0001](./0001-upstream-sync-fork.md) 纪律记为有意分叉。
- ADR 0003 追记（2026-09-06）把"astra 用 medium / high、luna 只值得 max"这类档位偏好放进 doctrine 文字；本 ADR 决策五把所有拨盘判断收进用户侧填充表，该落点随之作废，`lanes-claude-code.md` 只保留 runner 的机制事实（白名单、按模型默认值）。
- 已记录假设：grok `--effort` 取值（v1.0.25 实测）；Claude Code 子代理 `effort` 仅 frontmatter、`model` 有按次参数（官方文档 2026-09-11）；Cursor 不加载插件 Stop hook（未探明）；grok build 对插件 agent 的发现规则（4.2.0 下只见 `fable-advisor`）。
