# 05 — 记录本次三项决策为 ADR

**What to build:** 一条新的 ADR，让未来有人提议「receipt gate 是不是过时了」时能直接读到已被纠正的前提，而不必把整轮讨论重来一遍。本次讨论中这个混淆已经真实发生过：把 spawn 护栏和 receipt gate 的适用对象记反了，理由是「现在是主会话直派 codex lane，问题不那么紧迫」——而仓库记录恰恰说明那正是 gate 的适用场景。

ADR 要记的不只是选了什么，更是**为什么否决了替代方案**，以及哪条约束是决定性的。体例沿用既有 ADR：背景、选项对比、决策与核心理由、实施代价、复盘条件。

**Blocked by:** 02, 03, 04 — 既有 ADR 的「实施代价」一节记录实际改了什么、付出什么代价，要等三张实现票落地才写得实。

**Status:** ready-for-agent

**Spec:** `.scratch/model-routing-and-receipt-gate/spec.md`

- [x] `docs/adr/` 新增一条，编号接续现有最大号
- [x] 记录架构师层定义：为何按系列而非具体版本、为何未知命名兜底 advisor-only、为何第三方名单留在私有规则而不入库
- [x] 记录兜底 lane 的成本论证换锤：从「单价便宜」改为「不污染架构师上下文」，并说明为何不干脆让架构师自己写
- [x] 记录 receipt gate 为何**不**降级：`systemMessage` 是 user-facing、不喂给模型，降级等于让 gate 对模型彻底失效——这是决定性约束
- [x] 明确记录被纠正的前提：spawn 护栏（fail closed）针对已删除的 wrapper 子代理，receipt gate（fail open）针对主会话自己；去 wrapper 后它是唯一还在盯主会话的机制
- [x] 记录残余风险：修复后模型理论上可靠重停通过 gate，但这不是新增漏洞——harness 本就有连续阻断上限，绕过成本只是从九轮降到一轮
- [x] 复盘条件包含：若一次拦截仍嫌吵，则重新评估并发归属判定（宽限窗口 / in-flight 锁 / transcript 归属三个已评估过的形态）
- [x] 复盘条件包含：用户清理掉 profile 中强制子代理模型的环境变量后，兜底 lane 的默认值才在那些 profile 下真正生效
- [x] 与本次实现实际落地的内容一致，不记录未做的事

## Comments

2026-07-25 — 已实现并通过双轴评审；验收清单逐项核对通过（回归证据见 tests/test_receipt_gate.py 7/7，决策记录见 docs/adr/0005）。
