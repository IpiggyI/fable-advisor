# 0019 — 报告模式不因 `git_status_failed` 挡 `complete`

- **Status**: accepted（2026-09-17 用户在广州仓现场确认：三条 report 均为 `git_status_failed`，Grok 已写出报告；并要求改契约）
- **Date**: 2026-09-17
- **影响范围**: `plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`tests/test_runner_contract.py`、`plugin/skills/orchestration/lanes-claude-code.md` 与 `docs/zh/` 孪生、`README.md`
- **关联**: [ADR 0018](./0018-post-5-1-tuning.md) 决策 1（脏基线跳过 `unexpected_diff`；「运行后 `git status` 失败仍是 `git_status_failed`」——本次只对报告模式撤销）

## 背景

5.2.0 让报告模式在 `dirty_baseline: true` 时不再误判 `unexpected_diff`。运行后的 `git status` 失败仍对两种模式抛 `git_status_failed`。广州仓 `D:\Tellhow\Projects\Idea\GuangDong\GuangZhou` 是 SVN/IDEA 工程，没有 `.git`。2026-09-17 三次 report（schema 盘点、`SYSTEMPARAMSBUILD.xml`、JDBC）CLI 均 `exit_status: 0` 且写出 `report`，receipt 却是 `git_status_failed`、`dirty_baseline: null`，Cursor 背景命令因此退出码 1。

`git_status_failed` 在 implement 模式有对应物：runner 无法证明写过什么。报告模式的写保护是只读工具集；git 不可用时这条共享门没有可核对象。

## 决策

1. **报告模式不抛 `git_status_failed`。** 运行后 `git status` 失败时 `changed_files` 记空数组，`dirty_baseline` 保持开跑前记录（开跑前也失败则为 `null`），随后只判 `empty_report` 与 `complete`。优先级仍是 `unexpected_diff`（开跑前干净且跑完后观察到脏）→ `empty_report` → `complete`。
2. **implement 模式不变。** `no_diff` 与 `git_status_failed` 仍按 5.2.0。
3. **不把两种模式合成一种。** 只读工具集、报告前言、允许空 `files` / `verification`、无改动即 `complete`、脏基线跳过 `unexpected_diff`，这些差别保留。

## 未采纳

- 仅当 `dirty_baseline: null` 时跳过：开跑前 git 成功、运行后失败（锁、瞬时故障）仍会挡一份已写出的报告；与「报告不依赖 git」不一致。
- 报告模式连 `unexpected_diff` 一并取消：git 仓上开跑前干净、车道写了文件，仍应失败。

## 复盘条件

- 报告模式在 git 不可用或 `dirty_baseline: true` 下车道实际写了文件（沙箱失守）→ 恢复检测，改用差集或其它基线。
- implement 模式在无 git 的树上需要 `complete`（例如同样的 SVN 地区仓）→ 另议，不并进本条。
