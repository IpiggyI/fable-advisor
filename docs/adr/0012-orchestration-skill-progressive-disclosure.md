# 0012 — 编排 skill 分层重构与触发描述重写

- **Status**: accepted
- **Date**: 2026-08-20
- **影响范围**: `plugin/skills/orchestration/`（SKILL.md 重写；新增 `lanes-claude-code.md` / `lanes-cursor.md` / `handoff-lane.md`）、`docs/agents/plugin-release.md`（抽查示例）、版本 3.11.0
- **关联**: [ADR 0010](./0010-dual-harness-single-source.md)（双 harness 单源——本次把 harness 专属机制沉入分支文件，单源不变）

## 背景

SKILL.md 增长到 3878 词（约 8k token），每个架构师会话整篇加载；但其中 CLI runner 机制只有 Claude Code 会话到达，钉模型派发只有 Cursor 会话到达，handoff 机制只在用户声明后到达。按 writing-for-agents 的分支判据（只被部分运行到达的引用材料应下沉到指针之后），这些混在主文里既摊薄注意力也抬高每会话成本。触发描述同时有三个同义分支（delegating / choosing runners / writing a spec 同属派活时刻）和一个缺失分支（「如何验收车道产出」无触发词）。

## 选项对比

| 方案 | 优点 | 缺点 |
|---|---|---|
| **拆分支文件（选定）** | 每会话只加载主文 + 恰一个 harness 文件（≈2.3k 词，降约 40%）；handoff 材料仅声明后加载 | 指针可能被跳读，需靠措辞（「首次派发前必读」）兜住 |
| 就地修剪不拆文件 | 无跳读风险 | 只能降到 ~2.9k 词，harness 无关会话仍为用不到的机制付费 |

## 决策

1. SKILL.md 只保留 harness 无关的准则：成本纪律、车道表与两阶段裁决、User routing profile、五部 spec 契约、验证三层、承诺边界、并行。wc 实测 1896 词（约降 51%）。
2. harness 专属机制沉入同目录分支文件，主文保留 harness 判别句与指针：
   - `lanes-claude-code.md` — runner 流程、spec JSON 与拨盘、receipt 与 receipt gate、grok deltas、dispatch-not-probes、`/codex:adversarial-review`；
   - `lanes-cursor.md` — 钉模型派发、无 receipt、effort 钉在 slug、subagent lifecycle；
   - `handoff-lane.md` — 流程、diff 即验收、gate 视野外与会话末清点、甜点区。
3. 触发描述重写：合并同义派活分支、补 "verifying or accepting lane work" 分支、砍冗长身份句。
4. 语义零变更：车道语义、两阶段规则、re-route 与 dispatch-not-probes、handoff opt-in 不变量、验证协议逐条保留，只挪位置与去重（re-route 与 double-billing 论证各只陈述一次）。
5. 章节名 "User routing profile" 保留——仓外用户规则按名引用它。
6. 同批仓外改动（不入库）：`~/.claude/rules/fable-advisor.md` 收敛为两模式（架构师 = Fable/Opus 系列 + 第三方名单；其余模型一律 advisor-only），架构师触发段改为默认姿态加经济豁免（spec 比 diff 还贵的改动才亲手改）。

## 复盘条件

- 架构师未读 harness 文件就派发（分支文件被跳读）→ 加强指针措辞，或把最关键两句收回主文。
- harness 增删或两侧机制合流 → 重估分支文件的划分。
- 触发抽查失败（派活场景未加载 skill）→ 回填触发词或重写描述分支。
