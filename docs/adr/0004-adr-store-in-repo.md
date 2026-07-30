# 0004 — 决策记录落 `docs/adr/` 并入库

- **Status**: accepted
- **Date**: 2026-07-25
- **Supersedes**: [ADR 0003](./0003-codex-lane-param-policy.md) 选项表中的「决策落点」一行

## 背景

2026-07-15 定过一次决策落点：决策写 `.memory/decisions/`，**不**引入 `docs/adr/`，理由是避免双份真相源（原记录见 ADR 0003 的选项表与 `.memory/tasks/2026-07/07-15-codex-lane-parametrization/prd.md`）。当时 `.memory/` 是仓库唯一的决策存储，那个理由成立。

2026-07-25 配置工程 skill 套件（`to-spec` / `triage` / `wayfinder` / `domain-modeling`）时发现一条当初没有权重的事实：**`.memory/` 在 `.gitignore` 里，`git ls-files .memory` 计数为 0——完全未跟踪**。于是决策历史只存在于单台机器上：新克隆拿不到，另一台机器拿不到，上游 PR 里也看不到。而 `domain.md` 要求所有 skill 在探索前必读 ADR 目录——指向一个未跟踪目录等于对新环境失效。

## 选项对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| 沿用 `.memory/decisions/` | 尊重既有决策，零迁移成本 | 决策不跟仓走；skill 在新环境读到空目录 |
| **改用 `docs/adr/` 入库（选定）** | 决策跟仓走、跨机器可见、可进 PR；与入库的 `.scratch/` tracker 方向一致 | 推翻一条已记录决策；需迁移 3 条现有决策并修交叉引用 |
| `.memory/` 整体入库 | 决策与任务档案一并跟仓 | `journal`/`recall`/`tasks` 也一并入库（大量个人工作记录与探针输出），与 `mem` skill 的本地惯例相背 |

## 决策

`docs/adr/` 是**唯一**决策存储，跟仓入库。`.memory/decisions/` 的 3 条决策已迁入并删除原目录：

| 原文件 | 新位置 |
|---|---|
| `upstream-sync-fork.md` | [ADR 0001](./0001-upstream-sync-fork.md) |
| `codex-lane-dewrapper-receipt-gate.md` | [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md) |
| `codex-lane-param-policy.md` | [ADR 0003](./0003-codex-lane-param-policy.md) |

`.memory/tasks/`、`.memory/journal/`、`.memory/recall/` 不受影响，仍是未跟踪的本地任务档案。

**核心理由**：原决策的前提（"`.memory/decisions/` 是仓库的决策存储"）在"存储须对新克隆可见"这个新要求下不再成立。双份真相源的顾虑通过**迁移并删除原目录**消除——不是并存，是搬家。

## 实施代价

- 3 条决策迁入 `docs/adr/0001-0003`，删除 `.memory/decisions/`。
- 修 `.memory/tasks/**` 与 `.memory/recall/*.jsonl` 中指向 `.memory/decisions/` 的链接与 `resources` 数组。
- `docs/*.txt`（历史会话转储）中的引用**不改**——那是过去会话的逐字记录，改它等于伪造历史。
- ADR 0003 选项表中的「决策落点」一行加删除线并注明被本 ADR 取代，正文其余保持原样。

## 复盘条件

- 若日后决定把 `.memory/` 整体入库，本 ADR 与 `docs/adr/` 的关系需重新评估（可能出现真正的双份真相源）。
- 若上游 `DannyMac180/fable-advisor` 引入自己的 `docs/adr/`，同步时须处理编号冲突。
