# 04: doctrine——首轮池、senior 门、升级梯、新记法；Cursor 车道文档

**What to build:** 任一主代理读技能正文后知道：light 与 standard 是首轮池、两档自由选；senior 只经升级梯的门或用户声明到达；返工、提升、换型号、升档的顺序是 R1–R4；拨盘记法是 `model[a*, b, c]`。Cursor 侧知道 composer 属 cursor lane、grok runner 可经 Shell 使用、explorer / advisor 派发首行指向报告前言。词数不超过 1960。

**Blocked by:** None (can start immediately)。doctrine 散文，同模派发。

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 10–14、16、17 条；`CONTEXT.md` 词条 首轮档位 / 拨盘 / 升级梯 / cursor lane；ADR 0015 决策 4（本票退役其 `|` 记法）。范围：`SKILL.md`、`lanes-cursor.md` 及二者中文孪生。

- [x] Stage 1：档位在 light 与 standard 之间按判断自由选择、无前置条件；senior 只经升级梯的门或用户声明；删除 "a lot, with costly mistakes → senior, or a race of two fills"（竞赛条款留在 Parallelism 段）
- [x] Escalation 段改写为升级梯：R1 返工票（同会话、同拨盘）；R2 提升（返工失败且归因能力：新会话 + 接管包；同型号升 effort 或换型号）；R3 同型号只提升一次，例外为更高各格没有别的型号；R4 执行时较大问题可跳过返工票直接换型号、记一次失败；senior 的门 = 首轮池内两次能力归因的失败或用户声明，与决策类型门"同一问题两次失败"重合；契约缺口路径不变
- [x] `dial` 定义改为 `model[a*, b, c]`（全部首轮可选、`*` 默认、无 effort 型号裸写）；`|` 记法句删除
- [x] 角色默认 effort 句（worker medium / explorer medium / advisor high）删除
- [x] `lanes-cursor.md`：Cursor 家族的 pin 是 cursor lane（只在 Cursor 宿主存在）；grok runner 经 Shell 可用，机制同 codex runner，标注未在 Cursor 实跑；explorer / advisor 的 Task 派发首行指向报告前言
- [x] `SKILL.md` 词数 ≤ 1960（`wc -w`）
- [x] 退役短语在 `plugin/` 零命中：`escalation-only`、`first-round options |`、`default senior`、`role default`
- [x] 两份中文孪生同提交；`python3 tests/test_zh_mirror.py` 绿；中英文二级标题数一致

## Comments

### 2026-09-16 — 实施记录（同模派发，inherit）

- 首轮落地：`SKILL.md` Stage 1 / Escalation / dial 记法改写，1959 词；`lanes-cursor.md` 加 cursor lane、报告前言指针、grok runner 经 Shell；两份孪生同改；`test_zh_mirror` 14/14；标题数一致。
- 为守词数车道额外删了三句（Stage 1 的角色输出映射、逃生口的排除句、R1 的 "never a hand fix" 括注），各有同文他处覆盖，验收接受。
- 验收项 3 的"角色默认 effort 句"在 `SKILL.md` 本就不存在，无可删。
- 车道上报范围外不一致五处：`SKILL.md` 接管句、`lanes-cursor.md` 返工句 / 首段车道清单 / "Two differences" 引出句 → 修正契约同会话处理；`lanes-claude-code.md:107` "higher-tier worker" → 工单 02 车道回报后追加；`plugin.json` description → 并入工单 06。
- 修正契约落地：接管句改为 "A raise (ladder R2) runs under a takeover contract: contract shape, not tier."；`lanes-cursor.md` 首段列 cursor lane、Rework 项按升级梯、grok runner 段独立成段；孪生同改；1958 词；架构师复核 `wc -w` 与 diff。工单 04 验收完成。
