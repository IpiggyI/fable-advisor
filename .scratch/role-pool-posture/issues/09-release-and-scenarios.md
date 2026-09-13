# 09: 发布 5.0.0 + 两个姿态各一个真实场景

**What to build:** 两侧（WSL / Windows）安装的插件更新到 5.0.0 并读到新 doctrine；更新后各跑一次真实场景——编排姿态：一张有上游任务件的小票派给 grok worker@standard，记往返次数与 GAPS 内容；实现姿态：一次无任务件的 bug 排查，主代理派 explorer 后直接修，记 advisor 是否在决策类型门的点位被咨询——证据追加到 spec 的 Comments。

**Blocked by:** 01、02、03、04、05、06、07、08

**Status:** ready-for-agent

上游：`docs/agents/plugin-release.md`；`.scratch/role-pool-posture/spec.md` "Testing Decisions" 的行为场景。commit / push / 两侧 `claude plugin update` 需要用户当次授权。

- [x] `plugin/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` 的 version 同为 `5.0.0`
- [x] 四个测试脚本全绿：`python3 tests/test_runner_contract.py`、`python3 tests/test_lane_family_gate.py`、`python3 tests/test_zh_mirror.py`、`python3 tests/test_receipt_gate.py`
- [x] 全库结构化 grep：`plugin/**`、`README.md`、`docs/zh/**`、`cursor-hooks/**` 中旧名为零（历史 ADR 与 `.scratch/` 历史目录不追改）。README「Upgrading from v2?」changelog 仍叙述历史 `implementer` / advisor-only，属版本史，不改。
- [x] 用户授权后：commit、push `origin main`、两侧 `claude plugin marketplace update` + `claude plugin update`，缓存目录出现 `5.0.0/` 且不含 `docs/`、`.scratch/`。WSL 与 Windows 均从 4.2.0 升到 5.0.0；两边 CLI 都提示 Restart to apply changes。
- [ ] 两个姿态场景各跑一次，证据（派发次数、GAPS、advisor 咨询点位、receipt 路径）追加到 spec `## Comments`

## Comments

2026-09-13 — 发布半截已落地：`c5b52a7` 推到 `origin/main`；WSL Claude 2.1.270 与 Windows Claude 2.1.267 均 `4.2.0 → 5.0.0`；缓存 `5.0.0/` 只有 `agents/` `hooks/` `scripts/` `skills/`，有 `worker.md`、无 `implementer.md`。仓外用户规则已安装（见工单 08）。两边都提示 Restart。两个姿态场景未跑。
