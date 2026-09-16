# 01: `SKILL.md` 承接全局编排入口

**What to build:** `plugin/skills/orchestration/SKILL.md` 按 [spec.md](../spec.md) 的 A1、A2、A3a、A4、A5、A9、B1、B5、B6、B8、B10、D1、N01、Q01a、Q09 修订。只改这一个文件；`docs/zh/` 孪生由工单 06 处理。

**Status:** ready-for-agent

**Blocked by:** 无

## 验收标准（全部为必须）

行号以 `ec36345` 的文件为准。

1. **A1** 第 12 行删句 "A code block longer than an interface signature is a contract not yet delegated."。第 14 行整段改为派发判据：读取范围宽、可独立并行、或只需结论进主线程时派 explorer；已知文件内的有界查询主代理直接读；代码块长度与单次工具调用都不是派发条件。删 "A full-file read here bills twice: re-read every turn, and re-read by the lane." 一句。第 16 行不动。
2. **A2** 第 65 行与第 88–96 行 "User routing profile" 合并为一处：填充表与专长备注在调用方指令指定的用户路由档案里（不写本机路径，不写"user's rules"）；首次分配模型前读取；档案变化或已滑出上下文时重读；未指定或读不到时报告缺口，不假定内容。"Volatile state"、"The handoff declaration"、"The low-confidence escape hatch" 三段原样保留。文件中不再出现 "user's rules"。
3. **A3a** 第 62 行 claude lane 行：`the harness explorer` 改为带显式按次 `model` 的内置 explorer（Claude Code 内置 Explore 省略 `model` 时继承会话模型，Claude API 上限 Opus，并继承会话 effort）。
4. **A4** 第 104 行 Constraints 定义末尾补：`and the operations the caller keeps in its own session; these bind the lane, its subagents, and its verification commands`。
5. **A5** 第 141 行删 "A subagent idle without its report is not a blocker: verify the workspace evidence and move on."，前半句保留。
6. **A9** 第 69 行改为：按所在宿主与其工具参数结构判断，不凭单个工具名或是否有 `model` 参数；判定后读对应 lanes 文件。两个指针行不动。
7. **B1** 第 3 行 `description` 压到约 35 词，只说何时用，例如：`Roles (explorer / worker / advisor), tiers, lanes and posture for delegated work. Use when deciding how to carry out a deliverable change, dispatching or accepting any subagent or CLI lane, or consulting the advisor.` 35 词是目标，不是硬限。
8. **B5** 第 62 行删 "highest unit price"，保留同族与共享额度两条披露。
9. **B6** 第 82 行 "stating the downgrade (no cross-vendor review)" 改 "stating any loss of cross-vendor review"；第 118 行 "two non-Anthropic fills buy a *third* perspective" 改 "two fills from families other than the main agent's buy a *third* perspective"。
10. **B8** 第 80 行删 "and a lane's cheaper model or lower effort is reached only by user declaration, or when the task is simple and that family is wanted anyway"，保留 "each lane priced at its default dial; dial positions never enter the lane-level comparison"。
11. **B10** 第 29 行 "Depth is not limited." 后补宿主事实：Claude Code 把子代理嵌套上限设在主会话下三层。
12. **D1** 第 65 行 `dial` 定义改为：`a dial is written model[first-round options | escalation-only], * marks the default; options after | are reached by a worker only through escalation after a failed rework ticket, and by any role only on user declaration`。
13. **N01** 第 105 行 Verification 按角色区分：worker 为验收证据命令，至少一条目标未达成即失败的检查；explorer / advisor 为期望的证据或裁决形状，可为空。
14. **Q01a** 第 129 行删第六项 "before declaring a multi-step deliverable done: this one takes the advisor's **acceptance** shape"。第 131 行 "The others take the **decision** shape" 改为全部取决策形状，并加一句：验收形状经 Tier 3 到达（第 139 行），不按步数触发。第 139 行 Tier 3 原文不动。
15. **Q09** 第 118 行竞赛句后补：两个执行者在同一工作树会互相覆盖，竞赛须各自隔离工作目录与执行记录；隔离方式见 lanes 文件。
16. 词数：`wc -w` ≤ 1950。
17. 文件中不再出现以下字串：`user's rules`、`highest unit price`、`longer than an interface signature`、`bills twice`、`is not a blocker`、`means Cursor`、`non-Anthropic`、`declaring a multi-step deliverable done`。

## 保留项

- 第 31–40 行委派边界、第 27 行姿态选择器、第 36 行 "a one-line fix is no exception"、第 96 行逃生门、第 134–139 行三级验收原文不动。
- 不新增文件，不改其他文件。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
wc -w plugin/skills/orchestration/SKILL.md
rg -n "user's rules|highest unit price|longer than an interface signature|bills twice|is not a blocker|means Cursor|non-Anthropic|declaring a multi-step deliverable done" plugin/skills/orchestration/SKILL.md ; echo "exit=$?"   # 期望无输出、exit=1
rg -n "first-round options|escalation-only|keeps in its own session|three layers|reads the matching|routing profile" plugin/skills/orchestration/SKILL.md
git diff --stat -- plugin/skills/orchestration/SKILL.md
```
