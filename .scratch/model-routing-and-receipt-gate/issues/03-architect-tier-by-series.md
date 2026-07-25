# 03 — 架构师层按系列判定 + 仓库去型号化

**What to build:** 跑在 Opus 5 或 Opus 4.8 上的会话被判定为架构师，不再因为判定式写死单个模型名而退回 advisor-only；下一代 Fable/Opus 发布时判定式自动适用，无需再改一次规则。遇到既不属 Fable/Opus 也不属 Sonnet/Haiku 的模型时兜底落 advisor-only——一个能力未知的模型不应被自动授予「写 spec 派活」的权限。

第三方模型（用户在多网关 profile 下会真实跑到的那些）经**用户私有规则里的显式名单**授权，名单默认留空、由用户部署时自填。仓库一个字都不提具体第三方型号，保持对外普适。

**这张票要改仓外文件**：判定式只存在于用户的私有规则文件（`~/.claude/rules/fable-advisor.md`），那是全局配置而非仓库内容。仓库的 orchestration doctrine 通篇没有以模型名做的准入门控，所以仓库侧只是文档一致性工作。

匹配语义已由一手探针确定：会话环境块给的是**裸模型 ID**（形如 `hs/glm-5.2[1m]`），显示名不出现，且第三方模型的句式与 Anthropic 官方模型不同——故按系列判定不会把第三方误判成 Opus。名单比对必须剥掉网关前缀与 `[1m]` 后缀。

**Blocked by:** 01 — 需要术语表定下「架构师层 / advisor-only」与「别名槽位 ≠ 模型身份」的口径。

**Status:** ready-for-agent

**Spec:** `.scratch/model-routing-and-receipt-gate/spec.md`

- [x] 私有规则的判定式按**系列**表述：Fable 系列 / Opus 系列 → 架构师模式；Sonnet / Haiku 系列 → advisor-only
- [x] 规则中写明兜底方向：两边都不匹配的模型落 advisor-only
- [x] 私有规则含一个**默认为空**的第三方架构师名单区块，附填写说明
- [x] 名单区块写明匹配语义：剥掉 `<gateway>/` 前缀与 `[1m]` 后缀后比对裸模型名，不做全等比对
- [x] 规则仍要求「读环境块的模型身份，不要猜」
- [x] 仓库文档不再以 Fable 5 具名架构师，改为旗舰层表述；Fable 可作为举例保留
- [x] 「没有 Fable 权限」的兜底段照实重写：此时 session 与 advisor 都只能用 Opus，顾问只剩上下文隔离价值
- [x] 删除已被证伪的「模型层级整体降一级」表述
- [x] 顾问 agent 的 model 字段**未改动**
- [x] 仓库任何文件都不含具体第三方型号
- [x] 一致性检查：仓库内无残留的具名 Fable 架构师叙事

## Comments

2026-07-25 — 已实现并通过双轴评审；验收清单逐项核对通过（回归证据见 tests/test_receipt_gate.py 7/7，决策记录见 docs/adr/0005）。
