# 01 — 拆出 runners.md，新增 lanes-other-hosts.md，路由行进 SKILL.md

Status: resolved

上游：[spec](../spec.md)，[ADR 0033](../../../docs/adr/0033-host-classes-and-runners-split.md)（「决策」1–7 有约束力），[ADR 0024](../../../docs/adr/0024-orchestration-files-by-lane-and-word-budgets.md)（决策 1、2、5 有约束力，决策 2 按 ADR 0033 决策 3 修订）。

## 契约

**Objective**：按 ADR 0033 决策 2–7（含 6a）重排编排技能文件。验收标准：

1. **逐句比对。** 基线是 `HEAD`（6.4.1）里的 `plugin/skills/orchestration/lanes-claude-code.md`。旧文件的每一句恰好出现在新的 `lanes-claude-code.md`、`runners.md`、`SKILL.md` 之一：无遗漏、无重复、无新增。例外只有四类：列明的删除、宿主条件标注、指针改写、拆分所需的结构标题（ADR 0033 决策 7，2026-10-18 补充）；每个例外逐条列出，删除还要说明不改变规则含义。脚本由车道自写，放在 `/tmp`。
2. **按规则归属拆分**（ADR 0033 决策 4）：runner 前置前言的规则进 `runners.md`；claude 车道派发提示词以路由行和读前言指令开头、`SendMessage`、路由门、claude 车道会话续用的时间来源留在 `lanes-claude-code.md`。报告按五条路径列出各自需要的规则及所在文件，证明第一次执行之前可达：Claude Code 的 claude 车道、Claude Code 的 runner、Cursor 的 `Task`、Cursor 经 Shell 的 codex runner、其他宿主。
3. `runners.md` 里只在 Claude Code 成立的机制——Bash 前台与后台两种等待、Bash 工具的 `timeout`、receipt gate、Grok deltas——位于按宿主条件标注的小节或句子里；`lanes-cursor.md` 的「The codex lane through Shell」与之不矛盾。
4. **路由行进 `SKILL.md`**（ADR 0033 决策 3）：「The route line」整节（格式代码块、三条要点、示例）移入 `SKILL.md` 的「The route」；`SKILL.md`、`lanes-cursor.md`、`lanes-other-hosts.md`、`runners.md` 中原指向 `lanes-claude-code.md`「The route line」的指针改指 `SKILL.md`。
5. **`SKILL.md`「Harness mechanics」** 改为四个按事件指路的指针（ADR 0033 决策 2）；兜底条款整段移出。
6. **新文件 `lanes-other-hosts.md`** 写全 ADR 0033 决策 5 的各条规则，以及它对 `SKILL.md` 的依赖（角色、档位、升级梯、契约、验收照常适用）。
7. **宿主条件**（ADR 0033 决策 6）：`SKILL.md`「User routing profile」的读档案指令限定为 Claude Code 与 Cursor，并指向 `lanes-other-hosts.md`；第二阶段、改道、升级梯各加一句宿主条件，指向 `lanes-other-hosts.md`。
7a. **并发隔离句**按 ADR 0033 决策 6a 拆开：runner 部分进 `runners.md`，claude 车道部分留在 `lanes-claude-code.md`；在逐句比对的例外清单中列为改写。
8. **`lanes-cursor.md`**：原指向 `lanes-claude-code.md` 的 runner 内容（第 3、16、21 行）改指 `runners.md`；路由行指针改指 `SKILL.md`。改后 `lanes-cursor.md` 不再链接 `lanes-claude-code.md`。
9. **`README.md`**：第 59–62 行指向 runner 内容的链接改指 `runners.md`；第 62、65 行指向 claude 车道与路由门的保持；第 123 行常见问题按 ADR 0033 决策 5 改写（其他宿主读 `lanes-other-hosts.md`，不读候选表）。
10. **中文孪生**：`docs/zh/skills/orchestration/` 下 `SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md` 同步，新建 `runners.md`、`lanes-other-hosts.md`；中文与英文逐段语义一致，术语按 `CONTEXT.md`。
11. `grep -rn "lanes-claude-code.md" plugin/ docs/zh/ README.md` 的每个命中都指向 claude 车道或路由门内容，不指向 runner 流程或路由行。
12. 新增与改写的文字遵守 `AGENTS.md`「Wording of shipped text」与「Canonical notation」：只写读者据以行动的规则；不写本仓历史、ADR 编号、日期、"未实测"之类状态；不点名 Grok Build 的未验证行为，只写规则（如"agent 文件写死的型号在该宿主上不能运行时……"）。

**Files**：`plugin/skills/orchestration/SKILL.md`、`plugin/skills/orchestration/lanes-claude-code.md`、`plugin/skills/orchestration/lanes-cursor.md`、新建 `plugin/skills/orchestration/runners.md`、新建 `plugin/skills/orchestration/lanes-other-hosts.md`；`docs/zh/skills/orchestration/` 下对应五个孪生；`README.md`。

**Interfaces**：
- `lane-preamble.md`、`lane-preamble-report.md`、`handoff-lane.md`、`routing-profile.md` 不移动、不改名、不改内容；runner 按相对路径读前言，agent 文件按插件根路径点名前言。
- `plugin/hooks/route-gate.py` 的路由行解析不变，所以路由行格式逐字保留。
- `SKILL.md` 的章节名 "User routing profile" 保留（ADR 0024 决策 6 未结）。

**Constraints**：
- 移动的文字只移动，不改规则含义；新增规则只来自 ADR 0033 决策 5–6。
- 决策类型门五项、契约五部分、"Reports are claims, not evidence" 留在 `SKILL.md`；不拆 `SKILL.md` 的路由、契约、验收三节。
- `SKILL.md` 第 40 行（同模派发的宿主分支）与第 60 行（grok lane 表格单元）不动。
- 不改 `plugin/agents/**`、`plugin/hooks/**`、`plugin/scripts/**`、`tests/**`、版本字段与说明书。
- 不做 git 写操作（add、commit、stash、checkout 都不做）。

**Verification**：
- 逐句比对脚本（`/tmp` 下，车道自写；报告附脚本路径与输出）。
- `python3 tests/test_zh_mirror.py`
- `python3 tests/test_shipped_wording.py`
- `grep -rn "lanes-claude-code.md" plugin/ docs/zh/ README.md` 与 `grep -n "lanes-claude-code" plugin/skills/orchestration/lanes-cursor.md`（后者应无命中）。
- `git diff --check`

## Comments

- 2026-10-18 派发：claude 车道同模派发，`worker-h` + `opus`（`Route: role=worker tier=same-model dial=opus-5-5[high] basis=same-model`）。
- 2026-10-18 worker 报告：五条路径可达性逐条列出；逐句比对 en 265 个基线单元，176 进 `runners.md`、73 留 `lanes-claude-code.md`、5 进 `SKILL.md`、11 为列明例外，例外 23 条（`/tmp/hc-exceptions-{en,zh}.json`）；`test_zh_mirror.py` 19/19、`test_shipped_wording.py` 49/49、`git diff --check` 0；`lanes-cursor.md` 不再链接 `lanes-claude-code.md`。词数：SKILL 3425→3513，lanes-claude-code 5155→1607，runners 3522，lanes-other-hosts 560，lanes-cursor 1352→1351。
- 2026-10-18 主代理 Tier 1：读 `lanes-other-hosts.md` 全文与 `SKILL.md`、`lanes-cursor.md`、`README.md` 的 diff，与决策 5、6 对应；读比对脚本 `/tmp/hc-sentence-check.py` 并重跑，en、zh 均 PASS。worker 自报的遗留：`runners.md` 第 3 节 `TaskStop` 一句只在 Claude Code 成立但未标注；`SKILL.md` 几处 "the lanes file" 对 runner 路径现指 `runners.md`，未改措辞。
- 2026-10-18 Tier 3（`gpt-6.1-sol[medium]` 验收形状，codex 会话 `01a14e1f-2bb8-75a2-ab36-2a294997e1b9`）：首轮不通过，两点——`runners.md:69` 的 `TaskStop` 句缺宿主条件；例外清单的"结构标题"不在三类之内。
- 2026-10-18 返工（同一 worker 会话）：两种语言的第 69 行都加了 "In Claude Code,"，复扫没有其他漏标。结构标题按决策类型门处理：ADR 0033 决策 7 补第四类例外，只限三个标题。
- 2026-10-18 复验（同一 advisor 会话续用）：通过，置信度高，接受第四类例外及其边界。工单 01 验收通过。
