# 08: ADR 0014 + `AGENTS.md` 边界句随姿态 + 仓外用户规则文本

**What to build:** 未来读者能在 `docs/adr/0014-*.md` 里看到本次决策链（Q1–Q22）、被否决方案与复盘条件；`AGENTS.md` 的委派边界句带上"编排姿态下"限定并把 `implementer` 改为 `worker`；两份仓外用户规则（`~/.claude/rules/fable-advisor.md`、`.cursor/rules/fable-advisor.mdc`）的替换文本准备好放在 `.scratch/role-pool-posture/user-rules/` 下，含姿态默认与声明词、填充表（用户五行映射到角色 × 档位，逐行日期戳与失效条件）、决策类型门清单；第三方架构师名单区块退役。

**Blocked by:** None（可从 spec 直接写；实现阶段发现的事实作追记）

**Status:** ready-for-agent

产物类别：协调件，架构师亲写。

- [x] `docs/adr/0014-role-pool-posture.md`：Status / Date / 影响范围 / 关联；背景；选项对比（至少覆盖：门的三种拆法、边界三选、五分类 vs 三角色×三档位、审查员独立 vs 并入 advisor、advisor 工具三选、前言三选、runner 报告模式 vs 只用内建、家族门三选、`--no-subagents`）；决策；核心理由；实施代价；复盘条件；备注（grok build 两条未知、Cursor Stop hook 假设、与上游方向相反按 ADR 0001 记分叉）
- [x] `AGENTS.md`："the architect never edits deliverables, whatever the size" 改为编排姿态限定；产物类别映射不变；`implementer` 若出现改 `worker`
- [x] `.scratch/role-pool-posture/user-rules/claude-fable-advisor.md` 与 `cursor-fable-advisor.mdc`：两模式文字删除；姿态默认规则与声明词；填充表；决策类型门；日期戳 2026-09-11
- [x] 上述三处术语与 `CONTEXT.md` 一致

## Comments

2026-09-11 — 已写：`docs/adr/0014-role-pool-posture.md`、`AGENTS.md` 边界句、`.scratch/role-pool-posture/user-rules/` 两份替换文本（待用户安装到 `~/.claude/rules/fable-advisor.md` 与 `.cursor/rules/fable-advisor.mdc`）。
