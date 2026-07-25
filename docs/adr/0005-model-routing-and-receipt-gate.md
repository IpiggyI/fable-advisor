# 0005 — 模型路由校准 + receipt gate 修复

- **Status**: accepted
- **Date**: 2026-07-25
- **影响范围**: `hooks/receipt-gate.py`、`tests/test_receipt_gate.py`、`agents/implementer.md`、`skills/orchestration/SKILL.md`、`README.md`、`.claude-plugin/plugin.json`、根目录 `CONTEXT.md`；判定式在用户私有规则（仓外）
- **关联**: [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（receipt gate 选型与"后续澄清"）；spec 归档 `.scratch/model-routing-and-receipt-gate/spec.md`

## 背景

本批次收敛三项彼此纠缠的决策：架构师层如何判定会话模型身份、Fallback lane 默认模型如何论证、receipt gate 在发现重复拦截 bug 后修到何种程度。议题提出时有一条已被仓库记录否定的前提——以为"主会话直派 codex 之后 receipt gate 不紧迫"。本 ADR 把三项决策与被否决的替代方案一并钉死，避免同一轮讨论重来。

## 选项对比

### 决策一：架构师层判定粒度

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 写死具体型号（如"session model is Fable"） | 匹配精确、无歧义 | 每出新旗舰型号就要改规则；Opus 5 / Opus 4.8 能力足以当架构师却被判进 advisor-only | 忘改则静默降级——本应派活的会话默默自己写 |
| **按系列判定（选定）** | 下一代发布自动适用；Fable 系列 / Opus 系列 → 架构师层，Sonnet / Haiku 系列 → advisor-only | 系列边界需维护一份短名单 | 系列命名漂移时需复盘边界（可预期、可审） |
| 未知命名默认架构师层 | 新模型不被挡在门外 | 能力未知却自动获得"写 spec 派活"权限 | 弱模型冒充架构师、派活质量失控 |
| 第三方名单入库 | 公开可见、随 fork 传播 | 授权应显式、可审、可撤；公开 fork 不应承载他人私有授权 | 他人 fork 继承不相关的第三方型号绑定 |

### 决策二：Fallback lane 默认模型

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| 默认 sonnet（原状） | 单价便宜 | 本机 grok CLI 长期未认证时只有 codex 一条 CLI lane，codex 一挂直接掉兜底——兜底不是"罕走"而是第二顺位；便宜论证与真实使用频率错位 | 高频走兜底却用弱槽位，质量与架构师层不对齐 |
| **默认 opus 别名槽位（选定）** | 与架构师同层同单价；论证改为上下文隔离——实现细节、试错、命令输出不进架构师上下文、不被每轮以架构师单价重读 | 兜底单价上升 | 无；别名槽位跟随最新 Opus |
| 架构师自己写、不要 Fallback | 省掉一次 spawn | 所有实现细节永久驻留架构师上下文、每轮重读——省的不是单价而是上下文的永久增长 | 长会话上下文膨胀，架构师判断质量下降 |
| 提供 `model="sonnet"` 降级出口 | 保留便宜选项 | 没人会用，却每次派工多一个决策点 | 决策税；出口形同虚设 |
| grok 驱动壳也升 opus | 与 Fallback 对齐 | 驱动壳只做转发取证，未认证时闲置 | 为空闲壳付 Opus 单价 |
| 顾问 agent 也改 | 统一 frontmatter | 顾问职责是跨模型意见，应留在 `model: fable` | 失去跨系列第二意见 |

### 决策三：receipt gate 修复范围

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| **只修 `stop_hook_active`（选定）** | 同一会话收尾从拦到 harness 连续阻断上限（9 次）降到拦 1 次；最小改动 | 不处理并发归属等推测痛点 | 见残余风险 |
| 降级为不阻断的警告（exit 0 + systemMessage） | 不再吵 | `systemMessage` 是 user-facing only、不喂给模型；gate 对模型彻底失效 | 功能上约等于删掉这个 hook |
| 加豁免开关 | 用户可临时放行 | 模型自己就能 waive，棘轮价值归零 | 形同拆除 |
| 加并发归属判定 | 理论上可消除"别的会话 pending 拦下无关会话" | 痛点未经验证；三种形态（宽限窗口 / in-flight 锁 / transcript 归属）均未实测 | 为推测问题加复杂度 |
| 因"主会话直派 codex"而搁置/删除 | 少维护 | **被纠正的前提**：spawn 护栏盯的是 wrapper 子代理（已随 v3.2 / `b114e78` 删除）；receipt gate 盯的是主会话自己。去 wrapper 后它是唯一还在盯主会话的机制——"直派 codex"恰恰是适用场景 | 拆除唯一主会话棘轮 |

## 决策

**选择**:

1. **架构师层按系列判定**（判定式在用户私有规则，不入库）：Fable 系列 / Opus 系列 → 架构师层；Sonnet / Haiku 系列 → advisor-only；未知命名兜底 advisor-only。第三方架构师名单留在私有规则、默认为空。
2. **Fallback lane 默认改 opus 别名槽位**；论证从"单价便宜"换为"上下文隔离"。不提供 sonnet 降级出口；`agents/grok-implementer.md` 与 `agents/fable-advisor.md` 的 model 不变。
3. **receipt gate 只修 `stop_hook_active`**：解析 stdin 后、扫 pending 前，该字段为真即输出 `{}` 退出 0。不降级、不加豁免、不加并发归属。

**核心理由**:

1. **系列优于单名**：单名匹配把同等旗舰能力的 Opus 变体静默判进 advisor-only，且每代发布都要改规则。系列判定让下一代自动适用；未知命名不得自动获得派活权——能力未知不应被授予"写 spec 派活"。第三方名单不入库：授权显式、可审、可撤；公开 fork 对他人保持普适。匹配语义（剥 `<gateway>/` 前缀与 `[1m]` 后缀比对裸模型名）依据一手探针：第三方模型在会话环境块中以裸模型 ID 出现（形如 `<gateway>/<vendor-id>[1m]`），句式与 Anthropic 官方模型不同，故系列判定不会把第三方误判成 Opus。
2. **Fallback 省的是架构师上下文，不是单价**：本机现实里兜底是第二顺位。改 opus 后与架构师同层同单价，价值在于实现细节不进、不被每轮重读。架构师自己写会把全部试错永久钉进上下文。sonnet 降级出口无人用却制造决策点；grok 壳未认证闲置不为它付 Opus；顾问保持 `fable` 以保留跨模型意见。
3. **receipt gate 未过时，只是有 bug**：议题原始判断（"防子代理静默自实现，主会话直派后不紧迫"）已被 [ADR 0002 后续澄清](./0002-codex-lane-dewrapper-receipt-gate.md) 否定。spawn 护栏（PreToolUse，fail closed）针对 wrapper 子代理静默自实现——wrapper 已删；receipt gate（Stop hook，fail open）针对主会话自己——排了 spec 却不跑、或把非-complete receipt 当完成。决定性约束：`systemMessage` 不喂模型 → 降级警告 = 功能删除；豁免开关可被模型自行 waive → 棘轮归零；并发归属属推测痛点 → 先修 bug 观察。

## 实施代价

- `hooks/receipt-gate.py`：解析 stdin 后、扫 pending 前，`stop_hook_active` 为真即输出 `{}` 退出 0（4 行新增）；`hooks/hooks.json` 未动。
- `tests/test_receipt_gate.py` 新建：零依赖回归脚本，七例进程边界用例（TDD 先红后绿入库），一条命令 `python3 tests/test_receipt_gate.py`。
- `agents/implementer.md`：`model: sonnet` → `model: opus`，description 与正文改写为上下文隔离论证；`agents/grok-implementer.md`、`agents/fable-advisor.md` 未动。
- `skills/orchestration/SKILL.md` / `README.md`：去型号化（架构师改旗舰层表述，删 "spend Sonnet on volume"、"model tiers shift down one"）；README 补 v3.3 升级说明。
- `.claude-plugin/plugin.json`：3.2.1 → 3.3.0（默认模型是行为变更，不打 patch）。
- 根目录 `CONTEXT.md` 新建（术语表）。
- 用户私有规则 `~/.claude/rules/fable-advisor.md`（仓外）：判定式按系列改写 + 新增默认为空的第三方架构师名单区块。

## 复盘条件

- 若 1 次拦截仍嫌吵（多会话并行、别的会话在飞的 pending spec 拦下无关会话）→ 重新评估并发归属判定，三个已评估过的形态：宽限窗口 / in-flight 锁 / transcript 归属。
- 用户清理掉 profile 中强制子代理模型的环境变量（`CLAUDE_CODE_SUBAGENT_MODEL`，存在于若干本机 settings profile）后，Fallback lane 的 `model: opus` 与顾问的 `model: fable` 才在那些 profile 下真正生效——该变量覆盖每次调用的 model 参数与 frontmatter。
- grok CLI 认证恢复后，Routine lane 回归默认路由。

## 备注

- **残余风险**（receipt gate）：修复后模型理论上可靠"再停一次"通过 gate，但不是新增漏洞——harness 本就有连续阻断上限，绕过成本只是从九轮降到一轮；棘轮的实际强度"至少把信息说出来一次"不变。
- 关联：[ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（receipt gate 选型与"后续澄清"）；spec 归档 `.scratch/model-routing-and-receipt-gate/spec.md`。
