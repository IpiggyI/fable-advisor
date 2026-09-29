# 0018 — 5.2.0：报告模式脏基线、车道标题、伴生安装器、首轮池与 senior 门、版本说明书

- **Status**: accepted（2026-09-16 用户经 grilling 两轮确认；senior 门取"两次失败"为推荐值，用户未单独否决；决策 5 的退役清单已由 [ADR 0023](./0023-routing-profile-in-plugin.md) 撤销；决策 9 中"grok runner 经 Shell 在 Cursor 可用"已被 [ADR 0025](./0025-cursor-grok-pinned-task-only.md) 取代；决策 4 已被 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 9 修订；决策 6、7 已被 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 2、5 取代；决策 10 已被 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 4、7、8 与 [ADR 0023](./0023-routing-profile-in-plugin.md) 决策 4 修订；决策 12 的版本号已被 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 12 取代）
- **Date**: 2026-09-16
- **影响范围**: `plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`plugin/skills/orchestration/`（`SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md`、新增 `lane-preamble-report.md`）、`docs/zh/**` 孪生、新增 `scripts/install-user-level.py` 与其测试、`tests/test_user_level_archive.py`、`tests/test_runner_contract.py`、`docs/agents/fable-advisor-routing.md`（+ `.zh.md`）、`docs/agents/plugin-release.md`、`docs/agents/cursor-lane-gate.md`、根目录 `AGENTS.md` / `CONTEXT.md`、`README.md`、新增 `docs/manuals/5.2.0.html`；版本 5.2.0。
- **关联**: [ADR 0011](./0011-cursor-lane-family-gate-user-level.md)（本次修订决策 2 的"活体手动拷"）；[ADR 0013](./0013-delivery-contract-not-build-instructions.md)（前言单源——本次按 `mode` 分成两份单源）；[ADR 0014](./0014-role-pool-posture.md)（决策 11 "sol 不加回"——本次撤销；报告模式 `unexpected_diff`——本次加脏基线例外）；[ADR 0015](./0015-global-orchestration-entry.md)（决策 4 的 `|` 记法——本次退役；决策 1 的档案读取契约不变）；[ADR 0017](./0017-routing-profile-edit-source.md)（编辑源在本仓、不进 `plugin/`——本次保持，活体改由安装器写）；[ADR 0019](./0019-report-mode-skips-git-status-failed.md)（报告模式不再因运行后 `git status` 失败抛 `git_status_failed`）。任务件 `.scratch/post-5-1-tuning/`。

## 背景

5.1.0 装上后用户观察到四件事。一，报告模式派 grok / codex 的 explorer 在有未提交改动的工作树上被主代理拒绝：runner 用运行后的 `git status --porcelain` 判改动、没有运行前基线，报告模式下任何脏都是 `unexpected_diff`（`lanes-claude-code.md` 要求"先干净再派"）。二，两条 CLI 车道的 prompt 都以前言开头，codex / grok 会话列表按首行显示，全是同一句。三，用户级文件的编辑源分散（路由档案、pin 规则、门禁脚本在本仓；两份旧规则在 prompts 仓库），活体靠手抄，两侧活体仍是带旧填充表（"advisor (default senior)"）的 9-11 版。四，主代理频繁把任务派给 Fable 与 Astra；档案与 doctrine 都允许模型自行判断首轮上 senior，而模型不具备判断其他模型能力的能力。用户要把这个决定写进档案，并要求档案支持随时调整。

事实核验（2026-09-16）：`run-grok.mjs` / `run-codex.mjs` 只在运行后调用 `git status`；报告模式下 codex 以 `--sandbox read-only`、grok 以只读工具集运行，`unexpected_diff` 是第二道保险；codex `exec resume` 与 grok `--resume` 都接受 effort 覆盖，"换 effort 要换会话"是策略不是机制；codex 白名单只有 astra、luna；Cursor 本轮 allowlist 为 grok-4.6 xhigh、opus-5 high、fable-5.1 xhigh、composer-2.5-fast；`SKILL.md` 1959 词，上限 1960；codex-advisor 仓库以插件内的伴生安装器 `install-agents.sh` 安装用户级模板，策略是拒绝覆盖已改动的目标。

## 决策

1. **脏基线取"跳过"而非"差集"。** runner 在 spawn 前跑一次 `git status --porcelain`，receipt 记布尔 `dirty_baseline`（失败为 `null`）。报告模式且开跑前已脏时不判 `unexpected_diff`，只读沙箱是唯一防线；implement 模式语义不变，"先干净再派"只对 implement 模式成立。未采纳内容哈希差集（见未采纳）。报告模式下运行后 `git status` 失败是否仍抛 `git_status_failed`，见 [ADR 0019](./0019-report-mode-skips-git-status-failed.md)（本条原写「仍抛」，已撤销）。
2. **spec 新增可选键 `title`。** prompt 首行是标题原文，缺省用 slug；`[fable-advisor] <slug>` 行退役。只改 runner；Cursor 的 Task 派发已有 `description`，不加句子。
3. **前言按 `mode` 分成两份单源。** implement 前置 `lane-preamble.md`，report 前置 `lane-preamble-report.md`（只读、Files 是读取范围、回答 Objective、以证据或 verdict 形状结尾）；runner 内联的 report overlay 删除；任一缺失 fail-loud。承接工单 `role-pool-posture/issues/10`。Cursor 侧 explorer / advisor 派发首行指向报告前言。
4. **`gpt-5.6-sol` 回 codex 白名单**，默认 `high`，不回退（astra → luna 回退不变）。撤销 ADR 0014 决策 11；理由是用户为即将到来的 gpt-6-sol 铺路，届时只改型号名。
5. **伴生安装器。** 仓库检出内的 Python 脚本 `scripts/install-user-level.py`，清单三件正典（路由档案 → `~/.claude/docs/`、pin 规则 → `~/.cursor/rules/`、门禁脚本 → `~/.cursor/hooks/`）加 `retire` 两份旧规则活体；默认写当前用户家目录，`--home` 可重复；无条件覆盖、不留 `.bak`；`--check` 只比对；`--also` 写备份快照；`~/.cursor/hooks.json` 只检测门禁条目、缺则警告、不改。正典位置不变（ADR 0017 决策 1、4 保持），不进 `plugin/`，不挂插件 `SessionStart`。漂移测试改为调用 `--check`，prompts 仓库退出测试。修订 ADR 0011 决策 2："活体仍须手动拷"改为"活体由安装器写入"；权威副本位置与"不进 `plugin/hooks/`"不变。
6. **首轮池与 senior 门。** light 与 standard 是一个首轮池，两档按 Stage 1 判断自由选择，格内多个 effort 自由选、`*` 为默认；senior 只经升级梯的门（池内两次能力归因的失败）或用户声明到达，且这一列刻意换型号。"a lot, with costly mistakes → senior" 从 Stage 1 删除。
7. **升级梯 R1–R4。** R1 返工票同会话同拨盘；R2 返工失败且归因能力 → 提升（新会话 + 接管包；同型号升 effort 或换型号）；R3 同型号只提升一次，例外为更高各格没有别的型号；R4 执行时较大问题可跳过返工票直接换型号、记一次失败。senior 门与决策类型门"同一问题两次失败"重合，advisor 的 verdict 顺带裁定。
8. **记法 `model[a*, b, c]`。** 格内全部首轮可选；`|`（仅升级）退役——ADR 0015 决策 4 修订。角色默认 effort 句退役，每格显式写 effort。
9. **cursor lane。** Cursor 自家模型经钉模型派发到达的车道，只在 Cursor 宿主存在；进 `CONTEXT.md` 与 `lanes-cursor.md`，不进 `SKILL.md` 车道表。grok runner 经 Shell 在 Cursor 可用，机制同 codex runner，标注未实跑。
10. **路由档案先写后调。** 按用户 2026-09-16 的表写出 Claude Code 表与 Cursor 表（Cursor 按机制映射，composer 在 explorer @ light 首位，allowlist 缺席的变体跳过），advisor 默认格为决策 standard / 验收 light，Resource preferences 记基准数据；末节写调整方法（改格、跑安装器）。用户之后随时改格。
11. **版本说明书。** 从 5.2.0 起每版一份自包含中文 HTML（`docs/manuals/<version>.html`），两部分：本版完整说明、相对上一版改动点；是交付物，不随插件发布；`plugin-release.md` 在 bump 前加"写说明书"一步。
12. **版本 5.2.0**（runner 契约与 doctrine 均向后兼容，minor）。

## 未采纳

- 内容哈希基线（运行前后逐路径哈希取差集）：能同时修好 implement 模式的 `no_diff`，但用户选了更简单的跳过；触发条件见复盘。
- 报告模式在 HEAD 临时 worktree 跑：调查员读不到未提交改动，正是要调查的东西。
- 插件 `SessionStart` hook 自动安装：需要正典进 `plugin/`（违反 ADR 0017 决策 4），且 `${CLAUDE_PLUGIN_ROOT}` 在 SessionStart 为空的 bug 有先例（anthropics/claude-code #27145、#39550）。
- Cursor 原生伴生插件承载规则与 hook：第二条安装通道，与 Claude 兼容路径并存会双载 skills / agents（ADR 0010 顾虑），加载行为未验证。
- 安装器改 `~/.cursor/hooks.json`：两侧已分叉且混有其他插件的 hook。
- 安装器拒绝覆盖被改动的活体（codex-advisor 策略）：本仓活体只由安装器写，新旧不是需要裁决的事。
- senior 门取"一次失败即开"：与用户的典型路径（grok medium → xhigh → astra medium）不符。

## 复盘条件

- implement 模式因脏工作树误报 `no_diff` 或 `changed_files` 混入既有脏文件 ≥2 次 → 重议内容哈希基线。
- 报告模式在 `dirty_baseline: true` 或 git 不可用下车道实际写了文件（沙箱失守）→ 恢复脏检测，改用差集。见 [ADR 0019](./0019-report-mode-skips-git-status-failed.md)。
- 安装器覆盖了用户手改的活体导致丢失 ≥1 次 → 重议覆盖策略或加 `--dry-run`。
- Cursor allowlist 出现 sonnet / haiku / luna 变体 → 补 Cursor 表对应格。
- gpt-6-sol 上线 → 改白名单型号名与默认 effort；ADR 不另记。
- 主代理在首轮池内仍频繁取最贵拨盘 → 重议"池内自由选"，考虑把 `*` 改为硬默认。
- 版本说明书连续两版没人读 → 重议是否保留。

## 备注

- 5.1.0 于 2026-09-16 提交 `83ce044`、推送并两侧安装；门禁脚本活体同步；这是本 ADR 实施的基线。
- 编排姿态实施：工单 01、03 grok 车道（Cursor 钉 `cursor-grok-4.6-xhigh`，requested, not confirmed）；04 同模派发；05 架构师亲写；06 的 ADR 与 `AGENTS.md` 亲写、README 经 worker；07 经 worker；08 发布另行授权。
