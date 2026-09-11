# 01: runner —— grok spec 的 `effort` 入参

**What to build:** 架构师在 grok lane 的 pending spec 里写 `effort`，runner 就以 `--effort <v>` 起 grok CLI 并把实际使用值记进 receipt；越界值在 spawn 之前被拒为 `spec_invalid`；省略则不传该 flag、交 CLI 默认。行为与 codex lane 的 `effort` 处理方式一致（fail-loud、receipt 可审计）。

**Blocked by:** None（可立即开始）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "runner 契约" 节。约束性事实：grok CLI 1.0.25 的 `--effort` / `--reasoning-effort` 取值为 `xhigh, high, medium, low`（2026-09-11 实测）。

- [x] grok spec 接受可选顶层键 `effort`，白名单 `{low, medium, high, xhigh}`；其他值 → `error_class: spec_invalid`，不 spawn
- [x] 合法值以 `--effort <v>` 出现在 grok 子进程 argv 中；省略时 argv 不含该 flag
- [x] receipt 记录实际使用的 `effort`（省略时为 `null`）
- [x] `tests/test_runner_contract.py` 新增三态用例（合法 / 越界 / 省略），沿用既有假 CLI 经 PATH 注入的写法；`python3 tests/test_runner_contract.py` 全绿
- [x] codex lane 的 `effort` 语义与默认值不变（回归用例仍绿）

## Comments

2026-09-11 — 已实现（codex lane，gpt-6-astra[medium]，隔离 worktree `lane/runner-contract`，receipt `complete`，会话 `01a0911d-2119-7a23-933b-74dbc124b460`）。契约测试 12/12；diff +59 行，架构师读完 Tier 2（车道自写的测试）。runner 契约的 advisor 验收在 02 落地后对合并 diff 做一次。
