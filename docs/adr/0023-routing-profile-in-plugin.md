# 0023 — 路由档案随插件发布

- **Status**: accepted（2026-09-28 椰椰要求内置并确认四项实施决定；实施决定经 `gpt-6-astra` medium advisor 裁决；2026-09-29 椰椰要求安装器不再处理旧版游离文件，决策 3、6 相应修订，同经 advisor 裁决）
- **Date**: 2026-09-28
- **影响范围**: `docs/agents/fable-advisor-routing.md` 移到 `plugin/skills/orchestration/routing-profile.md`，中文译本移到 `docs/zh/skills/orchestration/routing-profile.md`；`plugin/skills/orchestration/SKILL.md` "User routing profile" 段与中文孪生；`scripts/install-user-level.py`、`tests/test_install_user_level.py`、`tests/test_user_level_archive.py`；`README.md`；`plugin/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` 的描述；`docs/manuals/6.0.0.html`；`AGENTS.md`、`CONTEXT.md`。并入未发布的 6.0.0，不另开版本号。
- **关联**: 取代 [ADR 0017](./0017-routing-profile-edit-source.md) 决策 1、2、4、5；取代 [ADR 0015](./0015-global-orchestration-entry.md) 决策 1 中"填充表在调用方指定的档案、插件不持有"的部分；取代 [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md) 决策 2 中"持久判断写用户级规则文件"的部分；撤销 [ADR 0018](./0018-post-5-1-tuning.md) 决策 5 中安装器的退役清单。任务件 `.scratch/tiers-and-routing-6-0/issues/06-routing-profile-in-plugin.md`。codex-advisor 早已如此（该仓 ADR 0004）。

## 背景

6.0.0 之前，填充表是用户级档案：编辑源在 `docs/agents/`，伴生安装器把它复制到两侧 `~/.claude/docs/fable-advisor-routing.md`，技能只读"调用方指令点名"的档案，用户的全局提示词负责点名。一张表因此有编辑源、两份活体、一份 prompts 仓库快照和一行全局指令五个落点。2026-09-28 核对时两侧活体仍是旧表（安装器 `--check` 退出 1），就是这种维护压力的实例。

椰椰要求"模型路由表不再游离在外而是内置到插件中，减少维护压力"。这一条在交接到本仓时丢失：`docs/fable-advisor-tier-and-consult-handoff-2026-09.md:107` 把"不随插件发布（ADR 0017）"写成既定事实，6.0.0 的 spec 没有收录，ADR 0021 沿用了 ADR 0017。

## 决策

1. **档案是插件文件。** 位于 `plugin/skills/orchestration/routing-profile.md`，技能用同目录链接读取；中文译本是镜像孪生，不发布。
2. **只有一个来源。** 不保留"调用方指令点名的档案优先"。读不到时报告缺口，不假定内容；首次分配前读取、变化或滑出上下文时重读，不变。
3. **没有活体。** 安装器不再复制档案，也不再维护退役清单，不删除任何文件。6.0.0 之前的档案活体只在本机两侧存在，迁移时手动删除一次（决策 6）；旧规则文件两侧已不存在（2026-09-29 核对）。
4. **改档案就是发版。** 改格、更新声明日期、发布插件、两侧更新；改格算次版本。运行中的会话重启前仍用旧档案。
5. **并入 6.0.0。** 6.0.0 尚未推送，两侧装的是 5.2.0。
6. **迁移顺序。** 两侧更新并核对新版内容；停止旧会话；删除全局提示词里点名档案路径的一行；启动新会话，逐侧确认读取插件档案；然后手动删除两侧活体并逐侧断言已不存在，再运行安装器刷新 Cursor 文件，最后删除 prompts 仓库快照。任一检查失败即停。5.2.0 的技能只读调用方点名的档案，所以顺序不能颠倒。

## 代价

- 档案随插件发给所有安装者，其中有本分叉的型号排名。这是 ADR 0017 决策 4 当初不进 `plugin/` 的理由，椰椰接受这一代价。
- 改一个格子要发版加两侧更新，取代"编辑加运行安装器"。
- 档案成为 `plugin/**` 下的交付物：编排姿态下经 `worker` 修改。

## 未采纳

- 插件带默认路径、调用方仍可点名覆盖：两个来源，维护压力不减。
- 另开 6.1.0：6.0.0 未发布，没有必要多一个版本。
- 安装器保留退役清单、每次运行都检查旧路径：这些文件只在本机存在，手动删一次就不会再出现，长期维护清单没有收益。

## 复盘条件

- 同一档案一周内因取值调整发版 ≥2 次 → 重议"改格算次版本"或改为补丁版本。
- 任一侧新会话在迁移后仍读取 `~/.claude/docs/fable-advisor-routing.md` → 全局指令或活体清理没做完，按决策 6 补做。
- 本机以外出现 6.0.0 之前的档案活体或旧规则文件 → 决策 3 的前提"只在本机存在"不成立，重议是否恢复退役清单。
