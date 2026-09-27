# 03：三档、格内选择、升级梯与新路由表（端到端）

Status: ready-for-agent
Blocked by: 01, 02

**要做什么：** 主代理读到的技能正文、车道文档、两个 agent 文件、路由档案、词表、`AGENTS.md`，以及用户读到的 README 与两个清单描述，都用 `mainstay`、`crux`、`rescue` 讲同一套首轮准入、格内选择、换车道和升级梯；路由档案换成用户的新表、新排名、两条已声明假设和 advisor 映射；ADR 0021 记下本批决定。本票落地后仓库不再有任何地方把 light、standard、senior 当现行档位。

**负责的要求：** `../spec.md` 第八节 TR-1 至 TR-10、RP-1 至 RP-12、AG-1 至 AG-3、DOC-1 至 DOC-6（DOC-5 中 codex 车道行与安装说明的部分已由 01 完成）；第九节第 3、4、5 项（本票文件）。

**范围（Files）：**
- 技能与 agent 散文：`plugin/skills/orchestration/SKILL.md`、`plugin/skills/orchestration/lanes-claude-code.md`（返工段、内置 Explore 一句、grok 段 `model` 条；codex 段已由 01 改完，不再动）、`plugin/skills/orchestration/lanes-cursor.md`、`plugin/agents/worker-md.md`、`plugin/agents/advisor-h.md`，以及它们在 `docs/zh/` 下的孪生。
- 路由档案：`docs/agents/fable-advisor-routing.md`、`docs/agents/fable-advisor-routing.zh.md`。安装到真实家目录属工单 05。
- 记录：`CONTEXT.md`、`docs/adr/0021-*.md`（新建）、`AGENTS.md`。
- 对外说明：`README.md`（档位、准入、升级段落、grok 车道行与升级段；codex 车道部分已由 01 完成）、`plugin/.claude-plugin/plugin.json` 的 `description`、`.claude-plugin/marketplace.json` 的两处 `description`。版本字段属工单 05。

**执行方式：** 一张票，多份交付契约，按产物类别分派：
- 技能与 agent 散文用同模派发（claude 车道，`model` 设为会话模型）；同家族 diff，按验证 Tier 3 交 advisor 验收形状，优先跨厂商的拨盘。
- README 与两个清单描述是交付物，经 worker。
- 路由档案、`CONTEXT.md`、`AGENTS.md`、ADR 0021 是协调件，主代理直接写。
- 建议顺序：先写路由档案与 `SKILL.md`（取值与机制要互相对上），再写其余；ADR 0021 最后写，记录落地后的实测词数。

## 实施必读

- `../spec.md`：第二节（用户原话）；第三节全部，特别是 N9、N10、N11、U17；第六节；第八节"档位与路由机制""路由档案""agent 文件""其他文档"；第十一节；第十二节 S2–S5；第十四节。
- `plugin/skills/orchestration/SKILL.md`（基线，2106 词）："Roles and tiers"中的 Tiers 一句，"Routing — two stages"整节，"User routing profile"中提到档位的句子。
- `plugin/skills/orchestration/lanes-claude-code.md` 第 3 行（内置 Explore）与返工段（"the senior tier only through its gate"）；`lanes-cursor.md` 的"Rework."条（"the senior gate applies"）。
- `plugin/agents/worker-md.md`、`plugin/agents/advisor-h.md` 与中文孪生。
- `docs/agents/fable-advisor-routing.md` 与 `.zh.md`（基线）：现行结构与"Adjusting this profile"一节。
- `scripts/install-user-level.py`（`--home`、`--check`）；`tests/test_user_level_archive.py`（输出按行给出 `PASS` 或 `FAIL`）。
- `CONTEXT.md`："档位""拨盘""升级梯""填充表"词条。
- `docs/adr/0018-post-5-1-tuning.md`（决策 4、6、7、10、12）、`docs/adr/0020-one-executor-per-check-list.md`（头部版本说明、决策 6）、`docs/adr/0019-report-mode-skips-git-status-failed.md`；ADR 格式参照 0018–0020。
- `README.md`：第 5、20、78 行附近的段落与升级段；两个清单文件的 `description`。
- 工单 02 的观测表与结论（N11 的 grok 写法、RP-7 的别名说明、ADR 宿主事实）；工单 01 落地后的 runner 行为（README 升级段要写）。

## 验收

技能正文与车道文档
- [ ] `SKILL.md` 按 TR-1、TR-2、TR-4、TR-5、TR-6 写出档位、首轮准入、格内选择、换车道、升级梯；"Senior gate"整句（含"verdict 顺带裁定"）不存在；决策类型门五项文字与基线逐字相同（`git diff` 该节为空）。
- [ ] `SKILL.md` 不含新增的型号名、排名或拨盘值，不含 C3 收窄条件；`wc -w` ≤ 2160，超过按 S4 停下。
- [ ] `SKILL.md` Stage 2 不再有 Pareto 权衡句与"No declarations → the cheapest adequate fill"（N9）；TR-5 的换候选顺序按 D6、D7 写，并写明对单个候选不可用、codex runner 对某型号启动失败同样适用（U17）。
- [ ] 两份车道文档的返工段为下一档语义；内置 Explore 不再被称为任何档位的候选；grok 段 `model` 条按 N11 与工单 02 的结论改写。
- [ ] `worker-md`、`advisor-h` 的 `description` 与正文符合 AG-2、AG-3；九个 agent 文件名与 `effort` 不变。

路由档案
- [ ] Claude Code 表与 `../spec.md` RP-2 逐格一致（候选、顺序、强度、`*`），用脚本比对并把输出贴进 Comments；Cursor 部分与 RP-8 一致。
- [ ] RP-3 至 RP-7 的内容齐全（车道顺序与 explorer 例外及理由、三条排序理由、擅长点示例且注明非穷尽、能力链与价格链、≈ 与 ≤ 的读法、haiku 与 composer 不排级、`sonnet-5` 占位与失效条件、两条假设、advisor 映射、到达方式）。
- [ ] RP-9 退役内容零命中：`first-round pool`、`senior`、`Candidate order inside a cell is the lane default order`、`Specialty only breaks ties`、`Luna as a worker`、`grok-4.6`、`gpt-5.6-`、`opus-5[`、`73%`、`cheapest adequate`、`allowlist carries`、`On 2026-09-16 the allowlist`、`Fable appears only`；易变状态一条改为"没有声明时取格内第一个候选的 `*` 拨盘"（N9）；专长说明作为擅长点示例保留（N10）；RP-10 保留内容仍在；RP-11 未复述升级梯；声明日期 2026-09-26。
- [ ] 中文备份内容一致；`python3 tests/test_user_level_archive.py` 输出中 `chinese twin docs/agents/fable-advisor-routing.zh.md` 一行为 `PASS`（活体比对各行在 05 之前预期为 `FAIL`，整体退出码不作为本票判据）。
- [ ] `python3 scripts/install-user-level.py --home <临时目录>` 后 `--check --home <临时目录>` 退出 0；`python3 tests/test_install_user_level.py` 退出 0。

记录
- [ ] `CONTEXT.md` 三个词条按 DOC-2 改写；light、standard、senior、首轮池、senior 门进 `_Avoid_`。
- [ ] ADR 0021 按 DOC-3：第三节各条及依据；逐条点名修订的 ADR 0018 决策 4、6、7、10、12 与 ADR 0020 决策 6、头部版本说明；C3 收窄条件（不启用）；词数上限 2160 与落地实测词数；宿主事实与失效检查（含工单 02 的观测）；已否决项。
- [ ] `AGENTS.md` 按 DOC-4。

对外说明
- [ ] README 描述当前行为的段落与 `SKILL.md` 一致；grok 车道行按 N11 与工单 02 的结论改写；升级段新增 v6.0.0：档案列名改变、白名单型号改变、取消自动换模型、并入的 ADR 0019 与 0020 改动、"更新后运行伴生安装器"；旧版本段落不改。
- [ ] 三处清单 `description` 用新档位，删除"the senior tier is gated"。

全票
- [ ] 中文孪生同步；`python3 tests/test_zh_mirror.py` 退出 0。
- [ ] 中文副本零命中 `../spec.md` 第九节第 5 项列出的中文译法（`首轮池`、`帕累托`、`专长只作决胜项`、`最便宜的充分填充`、`格内候选顺序即车道默认顺序`、`专长只作平手裁决`、`最便宜的够用候选`、`一格只列 allowlist 里有的变体`、`Fable 只出现在 senior 格`、`2026-09-16 的 allowlist` 等）；`test_zh_mirror.py` 只查存在，不能代替这一项。
- [ ] 本票文件内零命中：`cheapest adequate`、`grok-4.6`（README 历史升级描述除外）；档位含义的 `light`、`standard`、`senior`，`first-round`、`senior gate`、`首轮池`、`senior 门`（`CONTEXT.md` 的 `_Avoid_` 与 README 历史升级描述除外；命中逐条判断并在 Comments 列出保留理由）。
- [ ] advisor 验收形状 verdict 写入 Comments；主代理保留最终判断。

## Held for batch acceptance

- 全仓文字扫描（`../spec.md` 第九节第 5 项）——工单 05 执行。2026-09-27 已执行：命中只剩允许的例外（见工单 05 Comments）。通过。
- 真实家目录的 `--check`（两侧）——工单 05 在用户授权运行安装器之后执行。

## Comments

### 2026-09-27 — 实施与验收（主代理）

派发（按已安装 5.2.0 技能与旧活体档案路由）：
- 技能与 agent 散文（`SKILL.md`、两份车道文档、`worker-md`、`advisor-h` 与五份中文孪生）：同模派发 `worker-h`，`model: opus`。一次修正契约：`lanes-cursor.md` 第 8 行"The tier is the dial the pin names"与 TR-1 不符，第 14 行"allowlist 只有一个变体时就用它"与 RP-8、D9 的"缺少的变体跳过并披露"冲突，两句改写（我的契约漏列，属契约缺口）。
- README 与三处清单描述：grok 车道 `grok-4.6[medium]`（旧档案 worker light），会话 `a28f5f83-77d8-4ca9-8096-b6f56618679c`，回执 `complete`。
- 路由档案、`CONTEXT.md`、`AGENTS.md`、ADR 0021：主代理直接写。

验收证据：
- `wc -w plugin/skills/orchestration/SKILL.md` = 2160（≤ 2160，零余量）。
- 决策类型门一节与基线逐字相同（worker 用 `diff` 比对，空输出）。
- `SKILL.md` 型号名集合与基线相同（大小写不敏感比对，worker 报告），未写车道顺序值与 explorer 例外。
- 表逐格比对（`/tmp/cmp_tables.py`，从规格 RP-2 表与 RP-8 文字解析）：英文档案 `Claude Code vs RP-2 diffs: [] | Cursor vs RP-8 diffs: [] | cells compared: 18`；中文备份同样零差异。
- 档案退役内容扫描（`first-round pool`、`senior`、`Candidate order inside a cell…`、`Specialty only breaks ties`、`Luna as a worker`、`grok-4.6`、`gpt-5.6-`、`opus-5[`、`73%`、`cheapest adequate`、`allowlist carries`、`On 2026-09-16 the allowlist`、`Fable appears only`，以及 `light`、`standard`）：零命中；中文备份的中文译法扫描零命中。
- 临时家目录：`install-user-level.py --home <tmp>` 后 `--check --home <tmp>` 退出 0；`test_install_user_level.py` `8/8 passed`；`test_user_level_archive.py` 的 `chinese twin docs/agents/fable-advisor-routing.zh.md` 行为 `PASS`。
- `python3 tests/test_zh_mirror.py`：`15/15 passed`。
- 本票文件扫描：英文命中只剩 `CONTEXT.md` 第 41、49 行（`_Avoid_` 条目）与 README 第 126 行（v6.0.0 升级说明里的旧列名与 v5.2.0 历史描述），均属例外；中文副本零命中。
- README：档位、准入、格内选择、升级段按 `SKILL.md` 改写；grok 行为 `currently grok-4.7`；升级段新增 v6.0.0（不兼容：列名、白名单、取消自动换型号、`fallback_reason` 恒为 `null`、并入 ADR 0019 与 0020、运行伴生安装器、ADR 0021）；v5.2.0 及更早段落逐字不变。三处清单 `description` 用新档位，删除"the senior tier is gated"，JSON 解析通过。
- ADR 0021：点名修订 ADR 0018 决策 4、6、7、10、12 与 ADR 0020 决策 6、头部版本说明；记录 C3 收窄条件（原文取自 `final.md` 第 51 行与 codex-advisor TR-6）；词数上限与实测 2160；宿主事实含工单 02 的观测。

Tier 3 advisor 验收：codex 车道报告模式 `gpt-6-astra[low]`（旧档案 advisor light 格，跨厂商；submitted, not observed），会话 `01a0e0f2-bec3-7bb1-b3ed-68ecd784df61`。verdict 摘要："暂不通过"，唯一问题：`SKILL.md:60` 车道表把 Cursor 的 Grok 写成钉型号派发，`lanes-cursor.md:3` 同样笼统归为原生子代理，与档案"`medium`/`high` 经 Shell 走 grok runner、`xhigh` 走 `Task`"不一致；其余指定项（首轮准入、第一个候选默认、换候选顺序、R2–R4、删除 senior 门、不换型号与 `fallback_reason`、两个 agent 自述、Explore 定位、`grok-4.7`、中英一致、决策类型门不变、词数 2160）都符合契约。

主代理判断：接受本票。依据：被指出的两句与基线逐字相同（`git show HEAD:` 核对）；5.2.0 的旧档案同样写着 Grok `medium`/`high` 经 Shell 走 grok runner，`lanes-cursor.md` 第 25 行也已说明 grok runner 可经 Shell 运行。这处不一致在本次之前就存在，不是本次引入；U8 规定 Cursor 本轮只更新路由表，`SKILL.md` 也没有词数余量。作为遗留项上报，不在本票修改。

其他遗留（worker 报告，范围外，未改）：
- `lanes-cursor.md` 第 14 行"An ad-hoc model pin carries a fixed effort tier"与中文"固定的 effort 档"用 tier/档 指强度。
- `worker-h`、`worker-xh`、`advisor-md`、`advisor-xh`、`advisor-l`、`explorer-h`（"The claude lane's default explorer"）仍有替档案做路由选择的句子；AG-2、AG-3 只覆盖 `worker-md` 与 `advisor-h`，规格第十五节把其他 advisor 文件列为范围外。
- 中文车道文档多处用"档位"指 effort（`lanes-claude-code.md` 第 3、7、9、11、13 行等），与 `CONTEXT.md` 的"档位"定义冲突；基线即如此。
