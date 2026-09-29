# 编排技能按事件加载：提案

Status: ready-for-human

## 问题

`fable-advisor:orchestration` 经常在第一条消息后就被加载，而多数任务用不上委派。codex-advisor 的 `codex-advisor:orchestration` 有同样的问题。用户要的是：技能描述常驻，技能正文只在需要时读取。

## 证据（2026-09-19 至 2026-09-28 的 Claude Code 会话记录）

- 12 个会话加载了 `fable-advisor:orchestration`，9 个在第一条人类消息后就加载。
- 其中 6 个加载后没有任何派发（画 SVG、画 App Icon、合并分支、档位问答、仓库体检、一次缓存显示分析）。
- 13 个会话读了路由档案，9 个在第一条消息就读，5 个整个会话没有派发。
- 加载点都在几次定位工具调用之后、第一次改文件之前。模型思考内容不可见，因果关系是推断。

## 原因

1. 全局入口按任务类型触发：`~/.claude/CLAUDE.md:127`（源 `/mnt/d/Development/Local/prompts/current-prompts/CLAUDE.en.md:127`）写"交付物改动、超出有界事实查询的调查、重要决策、交付验收前先读并遵循"。几乎每个编码任务都命中。codex 侧 `~/.codex/AGENTS.md:127`（源 `current-prompts/AGENTS.en.md:127`）同文。
2. `CLAUDE.en.md:128` 的 "Model allocation: first read …" 容易被读成会话开始就读。
3. 技能描述同样宽：`plugin/skills/orchestration/SKILL.md:3` 写 "Use when deciding how to carry out a deliverable change"；codex-advisor `plugins/codex-advisor/skills/orchestration/SKILL.md:3` 写 "Use when a primary agent implements or delegates work"。

## 决策

保留全局入口（它解决了"忘记加载"），把触发条件从任务类型改成可观察的事件；两个技能描述同步收窄。

### A. fable-advisor 全局入口

替换 `CLAUDE.en.md:127-128`，`CLAUDE.zh.md:127-128` 同步翻译；部署时只替换两份线上 `~/.claude/CLAUDE.md`（WSL 与 `/mnt/c/Users/Shy/.claude/CLAUDE.md`）的这两行。

```
- Orchestration: `fable-advisor:orchestration` holds the delegation rules. Read and follow it only when one of these happens; otherwise do not load it:
  - the user asks you to orchestrate or delegate, or the task comes from an issue, spec, or task file;
  - you are about to dispatch any subagent or CLI lane, native roles included, or to accept one's delivery;
  - you reach one of these points: committing to an architecture, data migration, API shape, or refactor strategy; overturning an established plan; changing a public interface or a cross-module dependency; relaxing acceptance criteria; the same problem failing twice.
- Model allocation: when assigning a model to a dispatch, read the user routing profile `~/.claude/docs/fable-advisor-routing.md`; do not read it otherwise.
```

```
- 编排：`fable-advisor:orchestration` 存放委派规则。只在出现下列情况之一时读取并遵循它，其他情况不加载：
  - 用户要求你编排或委派，或任务来自 issue、spec 或任务文件；
  - 你即将派发任何子代理或 CLI 车道（包括原生角色），或即将验收它们的交付；
  - 你到达下列节点之一：确定架构、数据迁移、API 形态或重构策略；推翻既定计划；修改公共接口或跨模块依赖；放宽验收标准；同一问题第二次失败。
- 模型分配：为派发分配模型时，读取用户路由配置 `~/.claude/docs/fable-advisor-routing.md`；其他时候不读取。
```

三条触发的依据：
- 第一条对应技能的姿态选择器（`SKILL.md` Posture 段：用户声明或上游任务件决定编排姿态）。写"任务来自"而不写"仓库里有"，因为多数仓库都有 `.scratch/`。
- 第二条覆盖派发与车道验收。原"调查"一条删除：派 explorer 本身就是派发。验收只限子代理或车道的交付。
- 第三条是技能 `## Decision-type gate` 五项的抄录。不读技能就不知道门存在，所以触发清单必须在常驻层；代价是两处清单，门清单改动时要同步。

### B. codex-advisor 全局入口

替换 `AGENTS.en.md:127`，`AGENTS.zh.md:127` 同步翻译；部署时只替换两份线上 `~/.codex/AGENTS.md`（WSL 与 `/mnt/c/Users/Shy/.codex/AGENTS.md`）的这一行（两份线上文件在别处与源文件不同，只动这一行）。

```
- Orchestration: `codex-advisor:orchestration` holds the delegation rules. Read and follow it only when one of these happens; otherwise do not load it:
  - the user asks you to delegate or authorizes Architect mode;
  - you are about to spawn any subagent, native roles included, or to accept, rework, or escalate a delegated result;
  - the delivery is high-risk or the user asks for independent review, so it needs independent acceptance.
```

```
- 编排：`codex-advisor:orchestration` 存放委派规则。只在出现下列情况之一时读取并遵循它，其他情况不加载：
  - 用户要求你委派，或授权 Architect 模式；
  - 你即将派生任何子代理（包括原生角色），或即将验收、返工或升级一个委派结果；
  - 交付属于高风险，或用户要求独立审查，因此需要独立验收。
```

与 A 的差异及依据：
- 不含"任务来自任务文件"：codex-advisor `SKILL.md` 写明 "Model identity, a ticket, a specification, or an unaccepted proposal does not activate this mode"。
- 不含过程咨询：主代理的咨询姿态由 `SessionStart` hook 注入（ADR 0006："`SessionStart` injects the primary's posture"，`scripts/advisor-hooks.py` 的 `posture()`），咨询工具常驻，不依赖技能正文。
- 第三条对应 `SKILL.md` "High-risk delivery and explicit independent-review requests each require independent acceptance"。

### C. fable-advisor 技能描述

`plugin/skills/orchestration/SKILL.md:3`：

```
description: Roles (explorer / worker / advisor), tiers, lanes and posture for delegated work. Use before dispatching or accepting any subagent or CLI lane, when the user asks to orchestrate or a task comes from an issue, spec, or task file, or before committing to an architecture, migration, API, or refactor strategy.
```

中文孪生 `docs/zh/skills/orchestration/SKILL.md:3` 同步。去掉 "consulting the advisor"，避免与宿主自带的 `advisor` 工具混淆（推断，未验证）。记 ADR 0022；发版后才生效。

### D. codex-advisor 技能描述

`plugins/codex-advisor/skills/orchestration/SKILL.md:3`：

```
description: "Use when a primary agent is about to delegate work or to accept, rework, or escalate a delegated result, when the user authorizes Architect mode, or when a delivery needs independent acceptance. Not needed for direct work outside these cases."
```

中文孪生 `docs/zh/skills/orchestration/SKILL.md:3` 同步。记 codex-advisor ADR 0007；发版后才生效。

## 约束

- 不提交、不推送、不发版；prompts 仓库这几行本身是未提交改动，同文件其他未提交改动不动。
- 线上文件替换前按用户惯例留 `.bak-<原因>-<日期>` 备份。
- `current-prompts/rules/` 下的快照不在本次范围。

## 备选

1. 本提案：全局入口按事件触发 + 描述收窄。
2. 只删全局入口，靠描述触发：回到"忘记加载"。
3. 全局入口只保留第二条（派发时加载）：编排姿态与决策门会在未派发时漏读。

## 验证

- 文本：`python3 tests/test_zh_mirror.py`（两仓）、`git diff --check`；线上 `~/.claude/CLAUDE.md` 与 `CLAUDE.en.md` 全文一致；线上 `~/.codex/AGENTS.md` 只有第 127 行附近变化。
- 行为：部署后积累真实会话，重跑会话扫描。预期无委派任务不再加载技能、不再读路由档案；票据会话仍在第一次派发前加载。行为效果在真实会话出现前未验证。

## 第一轮裁决（gpt-6-astra xhigh，会话 01a0e7df-f3ba-7ce0-adbe-db36bc8c145c）

修改后采纳方案一。采纳：上游指令、任务件触发收窄到"即将编辑受任务件约束的交付物"、宽读取触发（`SKILL.md:14`）、handoff 车道、描述 C 补齐决策门。有争议：B、D 要求把过程咨询列为触发。

反证：主代理的咨询不依赖技能正文。
- 姿态：`advisor-hooks.py:44-62` 在 `SessionStart` 注入选好的姿态块与采纳块；ADR 0006 写明 native entries 携带委派者的姿态。
- 档位：咨询服务器自行选 advisor 档位，`consult_context.py:185-195` 从路由档案读 `ca_advisor_*`。
- 后果：完整姿态要求"多步任务定方案前咨询一次"，若咨询触发加载，codex 技能会在几乎每个多步任务开头加载，本提案对 codex 失效。
- 对策（新增 E）：改技能正文 `SKILL.md:131` 的无条件前置读取，而不是把咨询加进触发。

## 第二轮修订文本

### A′ fable-advisor 全局入口（替换 `CLAUDE.en.md:127-128`）

```
- Orchestration: `fable-advisor:orchestration` holds the delegation rules. Read and follow it only when one of these happens; otherwise do not load it:
  - the user or an upstream instruction asks for orchestration or delegation, or you are about to edit a deliverable that an issue, spec, or task file governs, with no instruction that fixes your posture;
  - you are about to start reading that is wide, splits into independent parallel parts, or is needed only for its conclusion;
  - you are about to dispatch any subagent or lane, native roles and the handoff lane included, or to accept one's delivery;
  - you reach one of these points: committing to an architecture, data migration, API shape, or refactor strategy; overturning an established plan; changing a public interface or a cross-module dependency; relaxing acceptance criteria; the same problem failing twice.
- Model allocation: when assigning a model to a dispatch, read the user routing profile `~/.claude/docs/fable-advisor-routing.md`; do not read it otherwise.
```

### B′ codex-advisor 全局入口（替换 `AGENTS.en.md:127`；不变）

```
- Orchestration: `codex-advisor:orchestration` holds the delegation rules. Read and follow it only when one of these happens; otherwise do not load it:
  - the user asks you to delegate or authorizes Architect mode;
  - you are about to spawn any subagent, native roles included, or to accept, rework, or escalate a delegated result;
  - the delivery is high-risk or the user asks for independent review, so it needs independent acceptance.
```

### C′ fable-advisor 技能描述（`SKILL.md:3`）

```
description: Roles (explorer / worker / advisor), tiers, lanes and posture for delegated work. Use when orchestration or delegation is requested; before editing a deliverable a task file governs; before wide, parallel, or conclusion-only reading; before dispatching or accepting any subagent or lane; or at a key decision: architecture, migration, API or refactor strategy, plan reversal, public-interface change, relaxed acceptance, a problem failing twice.
```

### D′ codex-advisor 技能描述（`SKILL.md:3`）

```
description: "Use when a primary agent is asked to delegate or is about to delegate work or to accept, rework, or escalate a delegated result, when the user authorizes Architect mode, or when a delivery needs independent acceptance. Not needed for direct work outside these cases."
```

### E codex-advisor 技能正文（`SKILL.md:131-132` 的首句）

原文：

```
Before using consultation, read the consultation mapping in the routing profile
and [consult-posture.md](references/consult-posture.md).
```

改为：

```
The `SessionStart` hook injects the primary's selected posture and adoption blocks,
native entries carry each delegate's, and the consultation server selects the
advisor dial itself. Only when no posture block is in your context, read the
consultation mapping in the routing profile and
[consult-posture.md](references/consult-posture.md).
```

其后 "Compare the caller's exact model identity …" 起的句子不变，成为缺少注入时的回退步骤。中文孪生同步；记入 codex-advisor ADR 0007。

## 第二轮裁决与落地

裁决（同一会话续用）：采纳 E，撤回把过程咨询列为触发的建议。另补四处：C′ 措辞补全决策门；E 把模型身份比较也并入回退条件；B′、D′ 增加"姿态块或采纳块缺失或不适用"的回退触发；验证描述改为"姿态完整有效的咨询本身不触发加载"。全部采纳，B′ 的回退触发单列为第四条。

落地（2026-09-28，未提交）：
- fable-advisor：`plugin/skills/orchestration/SKILL.md:3` 与中文孪生；`docs/adr/0022-orchestration-load-on-events.md`。
- codex-advisor：`plugins/codex-advisor/skills/orchestration/SKILL.md` 第 3 行与咨询段首句（E）、中文孪生；`docs/adr/0007-load-orchestration-on-events.md`。
- prompts 仓库：`CLAUDE.en.md`、`CLAUDE.zh.md`、`AGENTS.en.md`、`AGENTS.zh.md` 的编排入口。
- 线上：两侧 `~/.claude/CLAUDE.md` 与 `CLAUDE.en.md` 全文一致；两侧 `~/.codex/AGENTS.md` 只替换编排入口。四个线上文件替换前各留 `.bak-lazy-orchestration-20260928`。

待办：两个插件发版后描述与 E 才生效；部署后用 `scan-skill-loads.py` 复查真实会话。
