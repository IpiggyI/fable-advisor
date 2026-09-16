# 06: ADR 0018、README 升级段、AGENTS.md 类别表

**What to build:** 未来读者能从一份 ADR 知道本批决定与理由，并看到对 ADR 0011、0014 决策 11、0015 决策 4 的修订；安装者从 README 升级段知道 5.2.0 新增了什么、更新后要多跑安装器；`AGENTS.md` 的产物类别表覆盖新安装器与版本说明书。

**Blocked by:** 01、02、03（README 与 ADR 记录实际落地的契约与安装器行为）

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 24、25、27 条。ADR 与 `AGENTS.md` 是协调件，架构师亲写；README 是交付物，经 worker。

- [x] ADR 0018：背景（四个问题）、决定分条（脏基线取 B、标题键、前言分流、sol 回白名单、伴生安装器形态与覆盖策略、首轮池与 senior 门、升级梯 R1–R4、记法退役 `|`、cursor lane、版本说明书）、未采纳（内容哈希基线、SessionStart hook、Cursor 原生伴生插件、脚本改 hooks.json）、复盘条件
- [x] ADR 0018 标注修订：ADR 0011（活体由安装器写入）、ADR 0014 决策 11（sol）、ADR 0015 决策 4（`|` 记法）
- [x] README 升级段：新增 spec 键 `title`、receipt 字段 `dirty_baseline` 与报告模式语义、sol 白名单、报告前言、伴生安装器用法一句；`Report mode` 要点句更新
- [x] `AGENTS.md`：交付物类别加安装器脚本与版本说明书目录；"User routing profile" 段的"copy onto both live paths"改为"跑安装器"
- [x] README 中退役短语零命中（`default senior`、`|` 记法）
- [x] `plugin/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` 的 description："escalation is one failed rework ticket plus attribution" 改为升级梯与 senior 门的一句（工单 04 车道发现的范围外不一致）

## Comments

### 2026-09-16 — 实施记录

- ADR 0018、`AGENTS.md`（发布流程、Companion installer 节、类别表、路由档案节）：架构师亲写。
- README 与两处 description：grok 车道（`cursor-grok-4.6-xhigh`，requested, not confirmed）。README 改 Tiers 句、车道表 codex 行、技能概述、伴生安装器段、codex 车道 bullet、Report mode bullet、Escalation 段、v5.2.0 升级段；两处 description 改为 "escalation climbs a ladder (rework ticket, then a raise) and the senior tier is gated"，`version` 未动。
- 验收：架构师复核 JSON 有效、退役短语零命中、diff 只含三个文件。车道披露：README 的 Escalation 段为守四句省略 R4（`SKILL.md` 保有）；安装器 bullet 未写 `--also`。二者接受。
