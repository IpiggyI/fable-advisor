# 0024 — 编排技能按车道机制分文件，每个文件设词数预算并由测试强制

- **Status**: proposed（2026-09-29 椰椰要求按审查清单的建议执行；P11 采纳 (a)、(b1)、(c)，(b2) 暂缓；时点为 6.0.0 推送之后的 6.1.0。决策类型门经 `gpt-6-astra` medium advisor 裁决：修改后接受，置信度高，五点意见已并入决策 2、4、6 与实施契约；2026-10-02 发布的 6.1.0 包含 ADR 0026 至 0029，不含 P11，P11 的时点待椰椰重定；决策 4 的词数预算已被 [ADR 0030](./0030-global-plan-route-gate-reuse-window.md) 决策 9 取消，2026-10-04 椰椰决定，其余决策不变）
- **Date**: 2026-09-29
- **影响范围**: `plugin/skills/orchestration/SKILL.md` 的宿主指针；`plugin/skills/orchestration/lanes-claude-code.md` 拆出新文件 `plugin/skills/orchestration/runners.md`；`plugin/skills/orchestration/lanes-cursor.md` 的指针；`docs/zh/skills/orchestration/` 的对应孪生；新增 `tests/test_word_budget.py`；`README.md` 若引用被拆文件；版本 6.1.0 与说明书。
- **关联**: 修订 [ADR 0012](./0012-orchestration-skill-progressive-disclosure.md) 决策 1、2（分层只按宿主一条轴），复核其决策 5；[ADR 0022](./0022-orchestration-load-on-events.md) 决策 5 的 2210 词上限改由测试预算承接；[ADR 0020](./0020-one-executor-per-check-list.md) 决策 6 与 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 11 的"新规则必须到达每个主代理"仍成立。任务件 `.scratch/doc-healthcheck-6-0/review.md` 的 P11、R15、RI2、PS3；实施契约 `.scratch/doc-healthcheck-6-0/p11-contract.md`。

## 背景

ADR 0012 按宿主拆分编排技能：`SKILL.md` 放与宿主无关的准则，`lanes-claude-code.md` 与 `lanes-cursor.md` 放宿主专属机制。此后两份文件逐版膨胀（`git show` 加 `wc -w` 逐提交计数）：

- `SKILL.md`：2026-08-20 拆分后 1896 词，6.0.0 为 2160 词，工作树 2206 词。上限从约 1.9k 依次上调到 1950、1960、2110、2160、2210；2026-09-13 到 09-28 上调四次。
- `lanes-claude-code.md`：2026-08-20 788 词，6.0.0 为 3661 词，五周涨到 4.6 倍，没有预算。

原因有三：

1. 分层只有宿主一条轴。跨宿主的新规则只能进 `SKILL.md`（ADR 0020 决策 6、ADR 0021 决策 11 都写明"不能沉进某个 harness 分支文件"），于是每次靠上调上限落地。
2. `lanes-claude-code.md` 同时承载 Claude Code 的 claude 车道机制和两个宿主共用的 runner 流程。只派 claude 车道的会话要读 runner 流程；Cursor 使用 runner 的会话经 `lanes-cursor.md` 的指针，又要读 Claude Code 的 claude 车道细节。Claude Code 主代理首次派发前约读 7,090 词，Cursor 使用 runner 时约 8,290 词（按节计数推得，不是实测）。
3. 测量经过、观测日期和维护待办没有明确去处，反复进入随插件发布的文本。6.0.0 的审查清单 P04、P09 是现有实例。

## 决策

1. **分层规则。** `SKILL.md` 只收跨车道、跨宿主的共性规则。只属于一条车道或一个宿主的机制，放进该车道或宿主的文件。测量样本、观测经过和维护待办放进 ADR 或任务件，不进随插件发布的文本。
2. **按车道机制拆分 `lanes-claude-code.md`。** 按内容拆，不按行号切：
   - `lanes-claude-code.md` 只留 Claude Code 的 claude 车道机制，在 Claude Code 第一次派 claude 车道之前读。
   - 新文件 `runners.md` 收 runner 导语、第 0–4 节、"Rework tickets"、"Report mode"、"Grok deltas"、"Dispatch, not probes"，两个宿主都在第一次运行 runner 之前读。
   - 按规则归属拆，不整节搬运。第 0 节里 runner 前置前言的规则进 `runners.md`；claude 车道派发提示词以读前言的指令开头这条规则留在 `lanes-claude-code.md`。验收时逐条核对：每条车道需要的规则，在该车道第一次执行之前可达。
   - runner 流程里只在 Claude Code 成立的机制（Bash 前台返回与读后台输出文件两种等待、Bash 工具的 `timeout`、receipt gate）留在 `runners.md`，按宿主条件分节。放回 claude 车道文件会让只用 runner 的会话漏读。
   - `SKILL.md` 的宿主指针改为按车道机制指路，写成"第一次运行 runner 之前读"这类事件句。`lanes-cursor.md` 的指针改指 `runners.md`。
   - `lane-preamble.md` 与 `lane-preamble-report.md` 不移动：runner 按相对路径读取它们，agent 文件按插件根路径点名它们。
3. **不拆 `SKILL.md` 的路由、契约、验收三节。** 多数触发本技能的事件最后都要派发，派发同时用到这三节；拆出来就是必须全部加载的薄壳，总负担不降。决策类型门、契约五部分与"报告是声明、不是证据"的锚点留在 `SKILL.md`。
4. **词数预算由测试强制。** `plugin/skills/orchestration/` 下每个 `.md` 文件设预算，取拆分后的实测值加少量余量，写在 `tests/test_word_budget.py` 里。它取代 ADR 与工单里的人工 `wc -w` 核对，也承接 ADR 0022 决策 5 的 2210 词上限。`SKILL.md` 的初始预算不超过 2210。测试要求文件集合与预算条目完全一致：目录里出现没有预算的新文件，测试失败。上调任一预算要同时改测试并记 ADR，ADR 写明考虑过哪些内容下沉、为什么不能下沉。不得为满足预算把跨车道、跨宿主的共性规则下沉。
5. **逐句比对。** 拆分只移动已经定稿的文字。验收时逐句比对：旧文件的每一句恰好出现在一个新文件里。允许的例外只有三类：列明的删除、必要的宿主条件标注、指针改写。
6. **ADR 0012 决策 5 的前提待复核。** 该决策保留章节名 "User routing profile"，理由是仓外用户规则按名引用它。2026-09-29 检索 WSL 侧全局提示词，只点名档案路径，没有这个章节名；Windows 侧未查。实施时检索范围是两侧实际加载的全部仓外规则及其引用链，不只全局提示词。两侧都不按名引用，该决策退役，并同步 ADR 0012 的状态行与反向指针；任一入口无法检查，就保留该决策。

## 未采纳

- 把 `SKILL.md` 的路由、契约、验收三节各拆成文件：见决策 3。
- 失败路径单独成文件（审查清单 P11 的 (b2)）：候选的读取时机"第一次验收失败"漏了升级梯 R4 的重大执行问题与契约缺口。这些入口理清之前不拆。
- 继续只给 `SKILL.md` 设上限、靠人工核对：上限五周上调四次，`lanes-claude-code.md` 增长最快却没有上限。

## 复盘条件

- 对照任务（在已安装的 6.1.0 上执行，任务件 P11 列出四项）任一失败 → 重议指针措辞或分文件方式。
- 主代理未读 `runners.md` 就运行 runner，或未读 claude 车道文件就派 claude 车道，累计两次 → 按 ADR 0012 的复盘条件把关键句收回 `SKILL.md`。
- 任一预算上调申请 → 先按决策 1 判断下沉，并在 ADR 里写明理由。
- 宿主增删，或两个宿主的 runner 机制合流 → 重估分文件方式。
