# 宿主分三类与 runner 拆分

Status: ready-for-agent

依据：[ADR 0033](../../docs/adr/0033-host-classes-and-runners-split.md)，执行 [ADR 0024](../../docs/adr/0024-orchestration-files-by-lane-and-word-budgets.md) 的 P11。旧实施契约 `.scratch/doc-healthcheck-6-0/p11-contract.md` 以 6.0.0 为基线、含已取消的词数预算测试，不再沿用；本目录取代它。

## 目标

一个宿主里的主代理只读本宿主需要的说明：

- Cursor 主代理不再经指针读 Claude Code 的 claude 车道机制与路由门。
- 其他宿主（如 Grok Build）不再读路由档案的候选表，只适用整体分级策略。
- 路由行格式归 `SKILL.md`，三类宿主共用。

## 计划

- 工单 01（`issues/01-split-and-other-hosts.md`）：拆分、新增其他宿主文件、指针、中文孪生、`README.md`。一个契约，同模派发（`AGENTS.md` "Delegation boundary by artifact class"）。
- 工单 02（`issues/02-release.md`）：说明书与版本字段、推送、两侧更新。依赖工单 01 验收与批次验收通过；推送与两侧更新需椰椰当次授权。
- 协调件由主代理直接写：ADR 0033、`CONTEXT.md` 的「其他宿主」词条、ADR 0024 与 ADR 0031 的状态行与反向指针。
- 依赖：02 依赖 01。没有并行契约，不需要隔离工作目录。

## Batch checks

- 全量测试：`for t in tests/test_*.py; do python3 "$t" || echo "FAIL $t"; done` 与 `node tests/test_runner_lifecycle_windows.cjs`（若在本机可运行）。覆盖工单 01；执行者：主代理；时点：工单 01 验收之后、工单 02 之前。结果：passed（2026-10-18，10 个 Python 测试全部退出 0：install_user_level 8/8、lane_family_gate 18/18、receipt_gate 11/11、route_gate 44/44、routing_profile_parity 29/29、runner_contract 24/24、runner_lifecycle PASS、shipped_wording 49/49、user_level_archive 5/5、zh_mirror 19/19；`test_runner_lifecycle_windows.cjs` 在 WSL 上 SKIP，需要 Windows Node，未执行；日志 `/tmp/hc-batch-*.log`）。
- 加载行为对照（依赖模型行为，不能由测试替代）：发布后在新会话中各派发一次——Claude Code 只跑 runner、Claude Code 只派 claude 车道、Cursor 跑 codex runner、其他宿主（Grok Build）派一次 advisor——读转写，确认读取的文件与本 spec 的目标一致。执行者：Claude Code 两项由主代理；Cursor 与 Grok Build 两项由椰椰执行并回报转写要点。时点：工单 02 两侧更新之后。结果：pending。

## Comments
