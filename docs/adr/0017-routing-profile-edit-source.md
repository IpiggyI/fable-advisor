# 0017 — 用户路由档案的编辑源改到本分叉协调件；prompts 仓库降为备份

- **Status**: accepted（2026-09-16 用户声明本仓为主、`D:\Development\Local\prompts` 仅作备份，并选定路径 `docs/agents/`；决策 1、2、4、5 已被 [ADR 0023](./0023-routing-profile-in-plugin.md) 取代）
- **Date**: 2026-09-16
- **影响范围**: `docs/agents/fable-advisor-routing.md`（+ `.zh.md`）、根目录 `AGENTS.md` / `CONTEXT.md`、`tests/test_user_level_archive.py`；不改 `plugin/`、不改 runner / hook。活体仍是 `~/.claude/docs/fable-advisor-routing.md`。
- **关联**: [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md) 决策 2（判断不进仓库 doctrine——本次保持：不进 `plugin/`）；[ADR 0011](./0011-cursor-lane-family-gate-user-level.md)（仓内存档、活体用户级、漂移检测——本次把同一模式扩到路由档案）；[ADR 0015](./0015-global-orchestration-entry.md) 决策 1（本仓不留填充表副本——本次修订为：本分叉留编辑源，调用方仍指名活体路径）。

## 背景

ADR 0015 决策 1 把填充表从用户规则挪到调用方指定的按需档案，并写「本仓不留副本」，是为了避免 `user-rules/` 与 prompts 仓库变成两个编辑源。编辑源当时落在 prompts 仓库。用户随后把档案拷进本仓 `docs/`，并声明本分叉为主、prompts 仅备份。`docs/` 根目录与 chatgpt 转写、过期交接稿混放，且不在 `AGENTS.md` 的产物类别表里（不明即交付物）。

## 决策

1. **编辑源在本分叉 `docs/agents/fable-advisor-routing.md`。** 中文备份同目录 `fable-advisor-routing.zh.md`，不进 `docs/zh/`（那是 `plugin/**/*.md` 的孪生保留区）。该路径属协调件，编排姿态下主代理可直接改。
2. **活体不变。** 技能读的是调用方指名的档案，本机即 `~/.claude/docs/fable-advisor-routing.md`（两侧）。`plugin/skills/orchestration/SKILL.md` 的「调用方指令点名、读不到报缺口」一字不改，不写死仓内路径。
3. **prompts 仓库降为字节一致的备份**，与 pin 规则的 prompts 副本同类。`D:\Development\Local\prompts\current-prompts\docs\fable-advisor-routing.md`（+ `.zh.md`）不再当编辑源。
4. **不进 `plugin/`。** 填充表仍是一名用户的判断，随插件发布会把本分叉的排名发给安装者。ADR 0006 决策 2 仍然有效。
5. **漂移检测扩到这份档案的英文正典**：仓内存档 vs 两侧活体 vs prompts 备份。中文备份只检查存在与含中文，不装到 `~/.claude/docs/`。

## 未采纳

- 留在 `docs/` 根：无产物类别，与转写混放。
- 放进 `cursor-hooks/`：那是 Cursor 活体门禁；本档案含 Claude Code 表，部署目标是 `~/.claude/docs/`。
- 放进 `plugin/`：违反发布边界。
- 恢复 `user-rules/`：刚在 5.1.0 退役的第二编辑源。

## 复盘条件

- 仓内存档与活体或 prompts 备份反复漂、且未走「先改本仓再拷」→ 重估是否改回单一活体编辑。
- 上游同步把这份用户档案带进公开 fork 的默认树 → 按 [ADR 0001](./0001-upstream-sync-fork.md) 把它标成本地硬化、不回灌上游。
