# 0002 — codex 车道去 wrapper 化 + receipt gate 选型

- **Status**: accepted
- **Date**: 2026-07-15
- **影响范围**: `scripts/run-codex.mjs`、`hooks/`、`skills/orchestration/SKILL.md`、`agents/`（codex-implementer 已删）
- **Migrated**: 2026-07-25，从 `.memory/decisions/codex-lane-dewrapper-receipt-gate.md` 迁入（见 [ADR 0004](./0004-adr-store-in-repo.md)）

## 背景

07-08 / 07-12 两次"CLI lane 静默自实现"事故收敛出 final.md 整改路线（P0 hook 收编 → P1 确定性 runner → P1.5 封 wrapper → P2 去 wrapper）。P0/P1 完成后，P1.5 的两条路线（hook-allowlist、MCP 单工具）经实测均可行，需要决定：封 wrapper 还是直接删。receipt 的强制执行点也需在 Stop hook 与显式 command 之间选型。

## 选项对比

| 方案 | 优点 | 缺点 | 风险 |
|------|------|------|------|
| P1.5 MCP 单工具封 wrapper | 能力层封死最彻底（无 Bash） | wrapper 失去自验能力，只剩转发价值；多一层成本仍在 | 等于花钱维护一个已无判断价值的层 |
| P1.5 hook-allowlist 封 wrapper | 保留 wrapper 自验（Read/Grep） | 依赖 hook 输入 `agent_type` 字段的版本稳定性 | harness 更新字段变动则护栏静默退化 |
| **P2 直接去 wrapper（选定）** | 删除重复验证层；runner receipt 已承载执行与证据；每次派工省 ~25k token 的 Sonnet 启动基线 | codex 路径的可发现性依赖 orchestration skill 被加载（agent 列表里不再有 codex 项） | 未加载 doctrine 的会话不知道 codex 车道存在 |

## 决策

**选择**: 直接 P2 去 wrapper（architect → run-codex.mjs → Codex → architect），receipt 绑定 Stop hook（`hooks/receipt-gate.py`），用户明确"暂时不打算改成 MCP"。

**核心理由**:

1. MCP 封死后 wrapper 唯一剩余职责（自验）也消失，逻辑上已等价于去 wrapper——不如直接删，省掉每次派工的 wrapper 启动成本。
2. receipt gate 实测可机制化拦截"声称完成"（Stop hook `exit 2`，含无头模式），补上"主模型根本不路由给 Codex"这第三类威胁。
3. fail 方向分层：spawn 护栏（PreToolUse）fail closed 是主防线；receipt gate fail open 是棘轮——python 缺失时拦所有 Stop 的代价大于收益。

## 实施代价

- 删除 `agents/codex-implementer.md`；SKILL.md/README 全面改写为 runner 叙事；版本 3.2.0（commit `b114e78`）。
- 工作流约定新增：spec 排入 `.fable-advisor/pending/<slug>.json`，runner complete 后自清；放弃任务须手动删 pending 并向用户披露。
- 消费仓库需把 `.fable-advisor/` 加 `.gitignore`（receipt 内嵌命令输出）。

## 复盘条件

- 真实使用中发现"codex 路径不可发现"（doctrine 未加载导致 codex 长期闲置）→ 补显式 command 入口（如 `/codex-task`），claude-004 已论证该形态。
- harness 修复 named-teammate 白名单绕过，或 hook 输入字段变动 → 重新评估防线冗余度。
- grok 车道若也出现顶替事故 → 同法做 run-grok runner（当前 grok 仍是 wrapper agent + 无名 spawn 护栏）。

## 备注

- 依据实测：四项待验证项记录见 [`.memory/tasks/2026-07/07-15-guardrail-mechanization/investigation.md`](../../.memory/tasks/2026-07/07-15-guardrail-mechanization/investigation.md)（Claude Code 2.1.210，环境假设注明在档）。
- 讨论归档：`.agent-discuss/codex-implementer-architecture/final.md`。
- commits: `fb30ac8`（P0+P1）、`b114e78`（P2）。

## 后续澄清（2026-07-25）

receipt gate 与 PreToolUse spawn 护栏针对的是**两类不同威胁**，容易记混：

- **spawn 护栏**（`hooks/block-named-cli-lane.py`，fail closed）针对 07-08 / 07-12 事故里的 **wrapper 子代理静默自实现**。wrapper 已随本 ADR 删除。
- **receipt gate**（`hooks/receipt-gate.py`，fail open）针对**主会话自己**——排了 spec 却不跑、或把非-complete receipt 当完成。去 wrapper 之后它是唯一还在盯主会话的机制。

"现在是主会话直派 Codex lane" 不是 gate 过时的理由，恰恰是它的适用场景。
