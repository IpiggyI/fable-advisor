# 0033 — 宿主分三类：Claude Code、Cursor、其他宿主；执行 ADR 0024 的 runner 拆分

- **Status**: accepted（2026-10-18 椰椰的要求与选择；决策类型门经 `gpt-6.1-sol[high]` advisor 裁决：修改后接受，置信度高，两点必要修改与一点建议已并入决策 5、6、6a；codex 会话 `01a14e0e-e55d-74a3-8b22-c318fb34b8e6`）
- **Date**: 2026-10-18
- **影响范围**:
  - `plugin/skills/orchestration/SKILL.md`：「Harness mechanics」改为按事件指路的四个指针；「The route」收入路由行格式；「User routing profile」与升级梯 R3 加宿主条件。
  - `plugin/skills/orchestration/lanes-claude-code.md`：拆出 runner 流程，只留 Claude Code 的 claude 车道机制；路由行格式移出。
  - 新增 `plugin/skills/orchestration/runners.md`：两个宿主共用的 runner 流程。
  - 新增 `plugin/skills/orchestration/lanes-other-hosts.md`：其他宿主的规则，取代 `SKILL.md` 里的兜底条款。
  - `plugin/skills/orchestration/lanes-cursor.md`：指针改指 `runners.md` 与 `SKILL.md`。
  - `docs/zh/` 下对应孪生；`README.md` 的链接与常见问题；`CONTEXT.md` 新增「其他宿主」词条。
  - 版本与说明书，按 `docs/agents/plugin-release.md`。
- **关联**: 执行 [ADR 0024](./0024-orchestration-files-by-lane-and-word-budgets.md) 决策 1、2、5，并修订决策 2 的一处；修订 [ADR 0031](./0031-haiku-5-5-rework-limit-other-hosts.md) 决策 4（兜底条款）；[ADR 0025](./0025-cursor-grok-pinned-task-only.md) 是 Grok deltas 只在 Claude Code 成立的依据。

## 背景

椰椰认为，一个宿主里的主代理读到另一个宿主的说明属于噪音。2026-10-18 按读取路径计数（`wc -w`）：

- Claude Code 主代理读到的 Cursor 内容只有几句：`SKILL.md` 第 40、60、70、73 行，`lanes-claude-code.md` 第 58、82 行，路由档案的 Cursor 表。
- Cursor 主代理经 `lanes-cursor.md` 第 3、7、16、21 行的指针读 `lanes-claude-code.md` 全文（5155 词），其中 claude 车道机制约 813 词、路由门 718 词、Grok deltas 282 词都与 Cursor 无关。这正是 ADR 0024 背景第 2 条描述的问题；ADR 0024 一直是 `proposed`，P11 的时点待定。

椰椰进一步提出第三类宿主：导入 Claude Code 的设置或插件、但内部运行与 Claude Code 不同的 harness。典型是 Grok Build：它只有自家 grok 一个型号家族，整体的分级策略对它有效，型号路由细则基本不生效；现在的兜底条款让它读 Claude Code 的候选表，这也是噪音。

本机 Grok Build（`grok 1.0.60`）的 `~/.grok/README.md` 写明（转述，未在 Grok Build 内实测）：它自动发现 Claude Code 插件的全部组件，包括 `agents/`、`skills/` 与 `hooks/hooks.json`；子代理默认继承父会话型号，agent 定义的 `model` 无条件覆盖；子代理工具名是 `task`。因此 `advisor-*` 写死的 `model: fable` 在 Grok Build 上可能派发失败；路由门匹配 `Agent|SendMessage`，在那里大概率不触发。

## 决策

1. **宿主分三类。** Claude Code、Cursor、其他宿主。其他宿主指加载本技能、但既不是 Claude Code 也不是 Cursor 的宿主，包括导入 Claude Code 设置或插件、自身运行方式不同的宿主。识别方式沿用 `SKILL.md`：看所在宿主与工具参数结构，不看单个工具名。
2. **`SKILL.md` 只留指针。** 「Harness mechanics」写成按事件指路：在 Claude Code 第一次派 claude 车道之前读 `lanes-claude-code.md`；第一次运行 runner 之前读 `runners.md`；在 Cursor 第一次派发之前读 `lanes-cursor.md`；在其他宿主第一次派发之前读 `lanes-other-hosts.md`。兜底条款整段移出 `SKILL.md`。
3. **路由行格式进 `SKILL.md`。** 「The route line」一节（格式、三条要点、示例）是三类宿主、全部车道共用的规则，按 ADR 0024 决策 1 归 `SKILL.md` 的「The route」。其他文件改指 `SKILL.md`。这修订 ADR 0024 决策 2 中路由行随 runner 流程进 `runners.md` 的隐含归属。
4. **按 ADR 0024 决策 2 拆分 runner 流程。** `runners.md` 收 runner 导语、第 0 节 runner 前置前言的规则、第 1–4 节、"Rework tickets" 的 runner 部分、"Report mode"、"Grok deltas"、"Dispatch, not probes"。claude 车道派发提示词、`SendMessage`、路由门、claude 车道会话续用的时间来源留在 `lanes-claude-code.md`。runner 流程里只在 Claude Code 成立的机制（Bash 前台与后台两种等待、Bash 工具的 `timeout`、receipt gate、Grok deltas）在 `runners.md` 里按宿主条件分节标注；椰椰本次没有选择把它们再拆出去，所以 Cursor 仍会读到这几节的标题与内容。
5. **其他宿主的规则（`lanes-other-hosts.md`）。**
   - 不沿用任何其他宿主的 runner、receipt gate、路由门或型号钉选；只通过宿主自己提供的入口派发。宿主加载的插件钩子不作依靠；路由是文本，没有机械校验。
   - 不读路由档案。角色、档位第一阶段（按难度与升级梯定档、依据种类）、契约与验收照常适用；`SKILL.md` 中依赖档案的部分——第二阶段在格内选择、改道的车道顺序、R2 的"不低于失败型号的排名"——由下面几条替代。
   - 档位按强度分（椰椰 2026-10-18 选定）：一个型号上，`mainstay` 用该入口的默认强度，`crux` 比默认高一级，`rescue` 用该入口能给的最高强度。入口不能设强度时，档位只决定契约形状、依据与升级梯，拨盘写裸型号。
   - 首次选择：默认用入口的默认型号；宿主提供多个型号时，只在任务落在某型号的专长上或用户声明时换用，并在披露中说明。
   - 改道：入口或型号不可用时，换宿主提供的另一个型号，档位与强度规则不变，并披露；没有可换的就报告用户。不是能力失败。
   - R2：升级按上面的强度规则提高到下一档；宿主提供多个型号时可按任务换型号，并披露。R3 按拨盘计数（椰椰 2026-10-18 选定）：同一拨盘最多升级一次；没有更高的强度时交给用户。
   - 路由行的 `dial` 写宿主实际的型号 id 加强度，或裸型号。
   - 会话续用：档案没有其他宿主的窗口，所以返工、修正契约与后续消息默认新开会话，携带缺陷、原契约、上轮报告；`SKILL.md` "Session reuse" 的超窗续用例外照样适用，其他各条不变。
   - agent 文件写死的型号在该宿主上不能运行时（如 `advisor-*` 的 `model: fable`），该文件视为不可用的入口：不派它，改用宿主自己的入口承担该角色，指向角色所需的执行侧契约，并在披露中说明（椰椰 2026-10-18 选定只写文档，不改 agent 文件）。
   - 执行侧契约照旧：派发提示词按绝对路径指向角色所需的前言。
6. **`SKILL.md` 的读档案指令加宿主条件。** Claude Code 与 Cursor 在第一次指派型号之前读路由档案；其他宿主不读，按决策 5 处理。这修订 [ADR 0023](./0023-routing-profile-in-plugin.md) 决策 2 的"首次分配前读取"：只对 Claude Code 与 Cursor 成立；"只有一个来源"不变。`SKILL.md` 的第二阶段、改道与升级梯各加一句指向 `lanes-other-hosts.md` 的宿主条件。
6a. **并发隔离句拆开归属。** `lanes-claude-code.md`「4. Judge the receipt」末段的"同时运行的契约各用独立工作目录"一句同时讲 runner 的 `--cwd` 与 claude 车道契约的 Files、Verification。runner 部分进 `runners.md`，claude 车道部分留在 `lanes-claude-code.md`，各自保留"同时运行的契约各用独立工作目录（`git worktree add`）"的主句；这是逐句比对中列明的改写。
7. **逐句比对。** 按 ADR 0024 决策 5：旧 `lanes-claude-code.md` 的每一句恰好出现在 `lanes-claude-code.md`、`runners.md`、`SKILL.md` 之一。例外只有：列明的删除、宿主条件标注、指针改写。`SKILL.md` 兜底条款被决策 5 的新规则取代，列为改写。另有第四类：拆分所需的结构标题——新文件与被拆文件的标题，以及 `lanes-claude-code.md` 中承接原第 0 节 claude 车道部分的小节标题；它们不含规则，只命名其下内容；第四类只覆盖这三个标题，不豁免正文的增删、重复或规则变化。ADR 0024 决策 5 的三类例外没有覆盖新建文件的标题，这是对它的补充（2026-10-18 验收中发现，经决策类型门裁决）。

## 未采纳

- **把 runner 里 Claude Code 专属的部分再拆成单独文件。** 能让 Cursor 完全读不到 Claude Code 内容，但只用 runner 的 Claude Code 会话要多读一个文件；椰椰本次未选。
- **路由档案按宿主拆分。** `plugin/scripts/routing-profile.mjs` 解析两张表并取并集，因为 runner 在两个宿主上都跑；Cursor 表的 worker 与 advisor 行沿用 Claude Code 行；ADR 0023 规定档案是单一发布文件。收益约 25 行，不抵改动面。
- **`SKILL.md` 第 40、60 行的宿主分支句下沉。** 收益很小，椰椰本次未选。
- **改 `advisor-*` 的 `model: fable`。** 会牵动 Claude Code 路由门与 Cursor 用户级门；椰椰选定本次只写文档。
- **词数预算测试。** ADR 0030 决策 9 已取消。

## 已知能力上限

- 其他宿主的路由只是文本，任何门都不校验。
- 路由档案没有其他宿主的会话续用窗口，所以其他宿主的返工与修正契约默认新开会话（决策 5），已付的上下文不复用。
- Grok Build 的行为来自其 README，未在 Grok Build 内实测：插件钩子是否运行、`advisor-*` 是否派发失败、`task` 工具能否设强度。

## 复盘条件

- 椰椰在 Grok Build 内实测到与「背景」所述不同的行为 → 按实测修订决策 5。
- 出现第二个有固定入口的其他宿主（如它自己的钉选机制或可用的门）→ 给它写专属 lanes 文件，不再走 `lanes-other-hosts.md`。
- 其他宿主上续用窗口缺失造成明显浪费 → 椰椰在路由档案声明其他宿主的窗口。
- ADR 0024 的复盘条件继续适用：主代理未读 `runners.md` 就运行 runner，或未读对应 lanes 文件就派发，累计两次 → 重议指针措辞。
