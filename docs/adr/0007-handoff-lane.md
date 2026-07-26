# 0007 — 新增 Handoff lane（交接车道）：用户中介、opt-in、无机械门禁

- **Status**: accepted
- **Date**: 2026-07-26
- **影响范围**: `skills/orchestration/SKILL.md`、根目录 `CONTEXT.md`、`README.md`、`.claude-plugin/plugin.json`；用户侧 profile 在私有规则 `~/.claude/rules/fable-advisor.md`（仓外）。零代码改动，`hooks/`、`scripts/`、`tests/` 不触碰
- **关联**: [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md)（两段式路由与 profile 分层，本车道是其 stage 2 的条件成员）；[ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（receipt gate 的职责边界）；[ADR 0001](./0001-upstream-sync-fork.md)（分叉纪律）；spec 归档 `.scratch/handoff-lane/spec.md`

## 背景

现有三条实现车道有一条共同的物理前提：**本会话能直接调用执行器**（grok CLI、codex CLI、仓内子代理）。用户手上有另一类资源不满足这个前提——其他 harness（Cursor、OpenCode 等）的固定订阅额度，边际成本≈0，但只能由用户本人在那个窗口里驱动。结果是这份额度对编排系统完全不可见：架构师既不能用它，也不知道什么任务适合用它，用户只能在 doctrine 之外临时手工搬运，搬运回来的成果又缺一套验收规则。

用户愿意充当"人肉执行器"（把 spec 复制到另一个窗口、跑完拿回结果），用往返时延换近零成本与 harness 自由度。缺的不是能力，是 doctrine 里的一条路：车道定义、进入条件、产出物形态、验收标准、未决件的兜底。

## 选项对比

### 决策一：要不要把这条路写进 doctrine

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 不加车道，继续临时手工搬运 | 规则不膨胀 | 无 spec 契约、无验收规则；每次都重新发明 | 手工搬运的产出按"看着像对的"接收，绕过验证纪律 |
| **加为第四条车道（选定）** | 订阅额度进入路由函数；产出物与验收有统一契约 | 车道数 +1，判定面变宽 | 架构师误把它当常规车道自动路由（由 opt-in 边界封堵） |
| 只写一段"用户可自行外包"的提示 | 最轻 | 提示不是契约：既不定义产出物，也不定义验收 | 与不加车道等价，只是多一段散文 |

### 决策二：进入条件——自动路由还是用户声明

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 架构师可自动路由（按成本最优） | 额度利用率最高 | 车道的执行器是用户本人，架构师无法保证其在场 | 任务被派到无人执行的车道 = 静默搁浅，比慢更糟 |
| **opt-in：仅用户显式声明后进入候选集（选定）** | 与车道的物理依赖一致；架构师仍可在甜点区建议 | 用户不声明时这条路等于不存在 | 用户忘记声明导致额度闲置（代价可接受，且可由建议提醒） |
| 架构师可建议并默认执行（否决制） | 少一次交互 | 把"未反对"当成在场承诺 | 与自动路由同一失败模式，只是慢一拍 |

### 决策三：验收要不要机械门禁

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 复用 `pending/` + receipt gate | 与 codex 车道同构、fail closed | handoff 件横跨用户离开会话的时段，gate 会拦住本就不该完成的收尾 | 收尾被长期拦死，用户被迫绕过 gate，连带削弱它对 codex 车道的约束力 |
| 为 handoff 造新的门禁与回执格式 | 仍有机械约束 | 回执要求目标 harness 配合 = 重新引入对特定 harness 的耦合 | 违背这条车道存在的理由（harness 无关） |
| **无门禁：目录在 gate 视野外 + 会话末清点软规则（选定）** | harness 完全无关；gate 语义不被稀释 | 依赖架构师自觉，fail open | 交接件静默积压（由会话末清点兜底，且列入复盘条件） |

## 决策

**选择**:

1. **新增 Handoff lane**：架构师把五部 spec **加操作指南**（建议用什么模型/模式跑）写成 `.fable-advisor/handoff/<slug>.md`，由用户手动带到自选 harness 执行。接收方零上下文、不能回问，因此该文件必须自含。帕累托坐标显式入库：价格≈0（订阅套利）、速度最慢（人肉往返）、能力=用户当场选定、可用性=仅用户在场且已声明。
2. **opt-in 边界**（不变量入库）："The handoff lane never enters stage 2 uninvited — it becomes selectable only after an explicit user declaration; the architect may suggest it for a large, fully-specified, non-urgent task, but a suggestion never routes." 它是 [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md) 两段式里 stage 2 候选集的**条件成员**，两段式判定规则本体不改；逃生门规则零改动——进入靠声明，不靠逃生门。
3. **验收=diff，不要 receipt**：架构师读改动文件、亲自重跑 verification 命令；产出模型族未知，一律按不可信来源对待，回传报告可有可无（报告是复述，diff 是证据）。
4. **handoff 目录在 receipt gate 视野之外**（gate 只读 `.fable-advisor/pending/`，`hooks/receipt-gate.py` 一字不改），以会话末清点软规则兜底，措辞对齐既有 pending 规则并注明 fail open：会话结束前清点 `.fable-advisor/handoff/`，未决项须落地、放弃（删文件并说明）或明确声明留待下次。
5. **甜点区判据**：大颗粒 + spec 完全确定 + 不赶时间 + 用户已声明外部额度充裕；小任务明确不建议——往返开销压倒收益。

**核心理由**:

1. **进入条件必须与车道的物理依赖一致**。这条车道的执行器是用户本人，不是一个进程；架构师无法探测"用户是否在场并愿意跑"，所以只能由声明提供。自动路由在这里的失败模式不是慢，是任务静默搁浅——最坏的一类失败。
2. **建议与路由分离**。架构师对甜点区仍有判断权，把判断表达为建议即可；把建议升格为路由，等于替用户承诺他的时间。
3. **门禁换 harness 无关性是自觉的取舍**。机械门禁需要目标 harness 产出可编程回执，而"任意 harness"正是这条车道的全部价值。放弃门禁不是疏忽，是为保住 harness 无关性付的价——因此必须写明是 fail open，并配一条与 pending 同句式的软规则兜底。
4. **不稀释 receipt gate 的语义**。把横跨会话的 handoff 件塞进 `pending/` 会让 gate 经常性地拦住合理收尾；一个经常需要被绕过的 fail-closed 门禁，会连带失去它在 codex 车道上的约束力。视野边界保持原样，代价局部化。
5. **验收纪律不因车道而降级**。既有规则"报告是主张、diff 才是证据"在这条车道上只是更彻底：连模型族都未知，更没有理由采信报告。

## 实施代价

- `skills/orchestration/SKILL.md`：车道表加 Handoff 行（含帕累托坐标）；stage 2 段落后追加一句条件成员表述（两段式规则本体不动）；"User routing profile" 一节新增 handoff 声明段与 opt-in 不变量句；新增"The handoff lane"一节（产出物、无 receipt 的验收、gate 视野外 + 会话末清点软规则、甜点区）。既有三车道语义、逃生门、Cost discipline 全部不动。
- 根目录 `CONTEXT.md`：**lane** 词条枚举改四条（Routine / Cross-vendor / In-house / Handoff，并注明 Handoff 是条件成员）；新增 **Handoff lane（交接车道）** 词条。
- `README.md`：车道表加 Handoff 行；"Upgrading" 段落只追加 v3.5 条目、历史叙述不改写。`.claude-plugin/plugin.json`：version 3.4.0 → 3.5.0（新增车道属路由语义变更，打 minor，沿用 [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md) 先例）；description 不提 handoff——它是可选的人工车道，不属于开箱即用的卖点。
- 用户私有规则 `~/.claude/rules/fable-advisor.md`（仓外）：Routing profile 区加一条 handoff 声明机制（按任务/会话口头声明；订阅额度状态可作持久判断记录，带日期与失效条件）。
- 零代码：`hooks/`、`scripts/`、`tests/` 不触碰，`hooks/receipt-gate.py` 一字不改。
- 无可执行校验器（纯散文变更）；以一次性结构化 grep 检查验收，不新建常驻测试装置。

## 复盘条件

- `.fable-advisor/handoff/` 积压频繁（会话末清点常发现多条未决，或出现被遗忘的交接件）→ 软规则不足以兜底，重估是否需要机械提醒或更强的清点约束。
- 某 harness 提供可编程回执（CLI 或可被本会话读取的结构化产物）→ "无门禁"的前提落地，重估门禁取舍：该 harness 可升级为一条可直接调用的车道，或为 handoff 补一层可选回执。
- 架构师建议 handoff 的命中率异常（几乎不建议 = 甜点区判据过窄；建议后频繁被否 = 过宽）→ 重新界定甜点区。
- 用户的外部订阅失效或额度耗尽 → 该车道的价格优势前提消失，用户规则中的相应持久记录按其失效条件下线。

## 备注

- 决策链：上游 v4.0.0 审计后关于"第四条路"的讨论；使用边界（用户声明制）由用户拍板，架构师补"可建议不可自动路由"与验收/兜底规则。
- 本车道与 [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md) 的两段式框架完全兼容：stage 1 的胜任筛选照旧，handoff 只是 stage 2 候选集的条件成员，声明不得推翻胜任判定。
- 本次相对上游 [`DannyMac180/fable-advisor`](https://github.com/DannyMac180/fable-advisor) 再添一处有意分叉（第四条车道），按 [ADR 0001](./0001-upstream-sync-fork.md) 的纪律记录在案，同步上游时按"本地硬化提交"处理。
