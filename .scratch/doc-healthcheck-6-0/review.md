# 仓库产出体检与去冗清单（6.0.0 发布前，第二版）

Status: ready-for-human

第二版日期：2026-09-29。第一版日期：2026-09-27，审查对象是 `HEAD` `50e1151`（6.0.0 发布提交）。第二版以当前工作树为基准：`HEAD` `50e1151` 加上未提交的 ADR 0022、ADR 0023 批次（技能描述改为按事件加载；路由档案移入插件，见工单 06）。审查依据不变：`D:\Document\Prompts\Agent 文档与指令体检提示词.md`（下称"体检"）与 `D:\Document\Prompts\会话残留清理与去冗提示词.md`（下称"去冗"）。第二版按椰椰 2026-09-29 的要求分为两部分，并收录椰椰补充的议题 P11。本文件只记录清单；记录不代表批准实施。本轮没有按清单修改交付物、活体副本或用户目录，也没有暂存或提交。"本轮另行处理的改动"一节记录椰椰单独要求的改动，它不属于审查发现。

## 〇、阅读说明

### 两部分的边界

- **第一部分，本仓库自身内容**：不随插件发布的全部内容。包括 `AGENTS.md`、`CLAUDE.md`、`CONTEXT.md`、`README.md`、`docs/**`（含中文镜像 `docs/zh/**`、ADR、版本说明书、`docs/agents/**`）、`.scratch/**`、`cursor-hooks/**`、`scripts/**`、`tests/**`、`.claude-plugin/marketplace.json`、`.gitignore` 和未跟踪产出。`README.md` 在 GitHub 上对外可见，但它不在插件包里，所以归第一部分。
- **第二部分，发布到外面去的插件内容**：`plugin/**`。依据：`.claude-plugin/marketplace.json:14` 写 `"source": "./plugin"`。已安装的 5.2.0 插件缓存 `~/.claude/plugins/cache/fable-advisor/fable-advisor/5.2.0/` 里是 `.claude-plugin`、`agents`、`hooks`、`scripts`、`skills`，外加宿主的 `.in_use` 标记（2026-09-29 `ls -a`），与 `plugin/` 的内容对应。
- 第二部分多一条审查标准：插件文本不携带本仓内容。本仓内容指本仓路径、ADR 与工单编号、本机"两侧"、维护待办和测量经过。安装者在别的仓库里读不到这些文件，也无法照做；这些文字却随每次加载进入上下文。依据：椰椰 2026-09-29 的要求；去冗·失效或错层内容（"只服务维护、溯源或历史记录，却混入其他读者入口的内容"）；体检·七（"检查可复用内容是否意外固化个人路径、账户状态、单次任务细节或某个模型的特定行为"）。
- 第二部分条目的"最小修改"只改 `plugin/**`。本仓文件只以"对照"的身份出现在证据里。
- 一个问题要同时改插件文件和本仓文件时，拆成一条 P 条目和一条 R 条目，两条互相指向。
- 中文孪生：第二部分每改一个 `plugin/**/*.md`，同一提交要改 `docs/zh/` 下的孪生。这条规则统一记在 R13，各 P 条目不再重复。

### F09 里的两个 `AGENTS.md`

第一版 F09 的方案 C 涉及两个不同的 `AGENTS.md`，第一版没有分开写。

- 插件文本里的 "The repo's AGENTS.md names the artifact class it serves." 指插件运行时所在仓库的 `AGENTS.md`。别的用户在自己的仓库里使用插件时，这句指他们自己仓库的 `AGENTS.md`；插件在本仓运行时，这句才指本仓的 `AGENTS.md`。这一半见 P08。
- "在 `AGENTS.md` 写明触发类别 `plugin/skills/**`、`plugin/agents/**`"指本仓根目录的 `AGENTS.md`。这一半见 R09。

### 编号对照

第二版给第一部分编 R，给第二部分编 P，括号内是第一版编号。Comments 里的裁定仍用第一版编号。

| 第一版 | 第二版 | 说明 |
|---|---|---|
| F01 | R01 | |
| F02 | P01 | |
| F03 | P02、R02 | 拆成插件与本仓两半 |
| F04 | P03 | |
| F05 | P04、R03 | 拆成插件与本仓两半 |
| F06 | P05、R04 | 英文在插件，中文孪生与 `CONTEXT.md` 在本仓 |
| F07 | R05 | |
| F08(a) | R06 | |
| F08(b) | P06 | 并入 `SKILL.md:29` 的同类句 |
| F08(c) | 已消除 | 工作树已改写 `SKILL.md:88` |
| F08(d) | R07 | |
| F08(e) | P07 | |
| F08(f) | R08 | |
| F09 | P08、R09 | 拆成插件与本仓两半 |
| F10 | R10 | 建议从方案 A 改为方案 B |
| S1 | PS1 | 替代措施在 R03 |
| S2 | PS2 | |
| S3 | RS1 | |
| S4 | RS2 | |
| S5 | RS4 | |
| S6 | RS5 | |
| I1 | PI1 | |
| I2 | RI1 | |
| U1–U6 | U1–U6 | 在第一部分 |
| — | R11、R12、R13、R14、R15、RS3、RI2、RI3、P09、P10、P11、P12、PS3 | 第二版新增 |

### 第一版到第二版的变化

- 复核：第一版 18 处带路径前缀的原文引用，由脚本逐条比对当前工作树，全部仍在原行（2026-09-29）。其余位置逐行打印核对，结论仍成立。工作树只改写了这些文件的个别行，行数不变，所以行号没有漂移。
- 已消除：第一版 F08(c)。工作树把 `SKILL.md:88` 改写为 "live in [routing-profile.md](routing-profile.md), the user's routing profile shipped with this skill"，"never this repo" 已不存在。
- 事实更新：
  - 路由档案从 `docs/agents/fable-advisor-routing.md` 移到 `plugin/skills/orchestration/routing-profile.md`，行号不变。它从本仓内容变成插件内容，相关条目移到第二部分。
  - `SKILL.md` 现为 2206 词（`wc -w`），上限 2210（ADR 0022 决策 5）。
  - 插件缓存现有 4.0.0、5.0.0、5.1.0、5.2.0 四个版本目录。
  - ADR 反向指针：工作树里最新的两份 ADR（0022、0023）已回写反向指针。R10 的建议因此从方案 A 改为方案 B。
  - 任务件状态行重新计数，见 R05。

### 覆盖范围

- 第一版已覆盖，结论并入各条：通读 `plugin/skills/orchestration/` 的六个运行时文件与 `plugin/agents/` 的九个文件；路由档案；Cursor pin 规则与中文备份；`AGENTS.md`、`CLAUDE.md`、`CONTEXT.md`、`README.md`；`docs/agents/` 下五份流程文档；ADR 0021 全文；工单 03、05 全文。按结构或检索核对 `docs/zh/**`、`docs/manuals/6.0.0.html`、全部 ADR 的状态行与"关联"行、`.scratch/**` 的状态行。代码只作核实证据。
- 第二版新读：ADR 0012 全文；ADR 0020 决策 6、ADR 0021 决策 11、ADR 0022、ADR 0023 全文；工单 06 全文；`routing-profile.md` 全文；`SKILL.md` 第 54–95 行；`lanes-claude-code.md` 第 1–31 行；`lanes-cursor.md` 全文；`scripts/install-user-level.py` 与 `tests/test_install_user_level.py` 全文；`docs/manuals/6.0.0.html` 的伴生安装器一节与升级步骤；两份审查提示词原文。
- 第二版核实：`plugin/**` 里本仓路径、ADR 编号与本机描述的检索；各节词数（脚本按标题切分计数）；`SKILL.md` 与 `lanes-claude-code.md` 的逐提交词数（`git show` 加 `wc -w`）；两侧仓外档案、旧规则文件与全局提示词的存在检查（只读）。
- 未读：`lanes-claude-code.md` 第 33–145 行（runner 各节）只按节计数，没有逐句审；本会话读过已安装 5.2.0 版的同名章节。`docs/upstream-sync/**`、`docs/manuals/5.2.0.html`、多数 ADR 与 `.scratch/**` 正文仍未读。

### 总体结论

- 第二部分（插件）：运行时准则结构清楚。需要修改的实质问题有五类：agent 文件的自述与路由档案争夺路由权（P01）；Cursor 下 Grok 的到达方式有两种说法（P02）；claude 车道没有规定前言的送达，影响待探针验证（P03）；插件文本携带本仓内容（P04、P08、P09）；`SKILL.md` 与 `lanes-claude-code.md` 逐版膨胀，阅读路径没有按车道分叉（P11）。
- 第一部分（本仓）：Cursor pin 规则的英文正典已过时，而且已经装到两侧（R01）。其余是术语、任务件状态、ADR 反向指针、词表与规格的一致性问题。

### 条目字段

每条写：位置；原文（逐字）；依据（体检或去冗的条款）；证据状态（已核实、推断或待验证）；影响；最小修改；产物类别；来历；验证。

---

## 第一部分：本仓库自身内容

### 1.1 需要修改的发现

按影响与改动风险排序。

#### R01（F01）Cursor pin 规则的英文正典仍点名已退役的 `fable-advisor`

位置：`cursor-hooks/fable-lane-pin.mdc:10`。对照 `cursor-hooks/zh/fable-lane-pin.mdc:7`、`cursor-hooks/fable-lane-family-gate.py:33`。

原文：

> - `fable-advisor`: pass an explicit, non-inherit `model` from this turn's allowlist. A `preToolUse` hook denies missing, empty, or `inherit`.

中文备份第 7 行已经写"任一 `advisor-*` agent（`advisor-l`、`advisor-md`、`advisor-h`、`advisor-xh`）"。门禁脚本按前缀 `advisor-` 判定（`ADVISOR_PREFIX = "advisor-"`）。

依据：体检·六（"失效引用""多处维护同一规则造成的漂移"）；去冗·失效或错层内容（"前提已不成立的要求"）。

证据状态：
- 已核实：英文正典最后修改于 `04a332a`（2026-09-11）。中文备份修改于 5.1.0 的 `83ce044`（2026-09-16）；同一版本按 ADR 0016 决策 8 退役了裸名 `fable-advisor`。WSL 与 Windows 两份活体都与英文正典逐字节相同（2026-09-27 用 `cmp` 核对）。
- 推断：Cursor 以裸名呈现插件 agent。2026-08-18 观测到的 `subagent_type` 是 `fable-advisor`（`.scratch/cursor-lane-family-gate/issues/01-unpinned-fable-advisor-not-denied.md:17`）；新名字没有观测记录。

影响：这条规则设了 `alwaysApply`，每个 Cursor 会话都加载。它点名一个已不存在的 agent，却没有点名门禁实际守护的四个 `advisor-*`。推断后果有两个。第一，未钉 `model` 的 `advisor-*` 派发得不到事先提醒，要先被门禁拒绝一次再重试。第二，模型可能按规则去派发已不存在的 `fable-advisor`。另外，工单 05 的安装器若照现状运行，会把这份过时文本再装一次。

最小修改：第 10 行改为与中文备份等义的英文，其余行不动。建议文本：

> - Any `advisor-*` agent (`advisor-l`, `advisor-md`, `advisor-h`, `advisor-xh`): pass an explicit, non-inherit `model` from this turn's allowlist. A `preToolUse` hook denies missing, empty, or `inherit`; it matches the `advisor-` prefix, so a later dial is covered too.

若 O2 专题决定退役 `advisor-l`（见 PI1），中英两份同时删去它。

产物类别：本仓交付物（`cursor-hooks/**`），经 `worker`。刷新活体要运行安装器，见 RS2。

来历：第一版新发现。规格第十五节只核对了"pin 规则不含档位或型号"，没有核对 agent 名。

验证：`grep -n '`fable-advisor`' cursor-hooks/fable-lane-pin.mdc` 没有命中；安装器运行后 `python3 tests/test_user_level_archive.py` 退出 0；若采纳 RI1，新增的内容比对测试先在现状上失败，修改后通过。

#### R02（F03 本仓部分）README 的 Grok 到达说法，以及 Cursor 实跑记录

> 2026-09-29：本条的修改方向已被椰椰的更正推翻（Cursor 下 Grok 是本家模型，只经钉型号的 `Task` 到达，不跑 grok runner）。README 保持原文，不做 Cursor 实跑。见 Comments 与 ADR 0025。

位置：`README.md:26`、`:92`。插件部分见 P02。

原文：

> `README.md:26` | grok lane | Grok family (catalog default, currently grok-4.7) | `scripts/run-grok.mjs` runner (Claude Code); pinned-model dispatch (Cursor) |

> `README.md:92` The grok and claude lanes are Task dispatches with an explicit `model`; the GPT family is reached by running the **codex runner through the Shell tool**, with no receipt gate.

依据：体检·六（"规则冲突"，同一事实有两种说法）。

证据状态：已核实。

影响：P02 修改插件文本后，README 仍让 Cursor 用户把 Grok 的 `medium`、`high` 当钉型号 `Task` 派发；allowlist 没有这两个变体时，它们会被跳过。

最小修改：
- `README.md:26`、`:92` 按 P02 的新说法同步：Cursor 下 Grok 的 `medium`、`high` 经 Shell 运行 grok runner，`xhigh` 经钉型号的 `Task`。
- 在 Cursor 里实跑一次 grok runner，结果记入工单 05 或新工单。跑通后，P02 再改 `lanes-cursor.md:25` 的 "Not yet exercised in Cursor."。

产物类别：README 是本仓交付物，经 `worker`；工单是协调件。

来历：复核遗留。见工单 03 Comments 第 92–94 行的 advisor verdict，以及规格第 641 行。

验证：文字部分可在本机检查。Cursor 实跑只能由椰椰在 Cursor 执行；结果回报前标为未核实。

#### R03（F05 本仓部分）README 的回退说法过时；测量样本与探针的去处

位置：`README.md:63`；`docs/adr/0016-effort-per-agent-file-role-pool.md:70`；`.scratch/tiers-and-routing-6-0/issues/05-release-6-0-0.md` 的 REL-4。插件部分见 P04。

原文：

> `README.md:63` Heads-up: if a pinned Claude model isn't available on your account, Claude Code silently falls back to your session model — the pattern degrades quietly rather than erroring.

依据：体检·六（"过时事实"）；去冗·处置·迁移（"仍有保存价值但放错层的内容，移到授权范围内已有的合适载体"）。

证据状态：已核实。2026-09-27 的观测是：在未开通 usage credits 的配置下，`fable` 派发被拒（HTTP 429）。

影响：README 让用户预期"静默回退"，最新观测却是明确报错。

最小修改：
- `README.md:63` 改为下面的文本。它只陈述有证据的 Fable 情形：

> If a pinned Claude model isn't available on your account, the dispatch can fail (for example, Fable without usage credits enabled) or run on another model; `message.model` in the subagent transcript shows what ran.

- P04 从插件删掉的测量样本与外推留在 ADR 0016（第 70 行已记外推），不另建文档。
- 插件级 `low`、`xhigh` 强度探针写进工单 05 REL-4 的验收清单，见 PS1。

产物类别：README 是本仓交付物，经 `worker`；ADR 与工单是协调件。

来历：第一版新发现。ADR 0016 记下了探针需要，此后没有执行记录。

验证：README 的新文本与 P04 的新文本一致；工单 05 REL-4 列出探针。

#### R04（F06 本仓部分）中文孪生与 `CONTEXT.md` 把强度称作"档位"

位置：
- 中文孪生：`docs/zh/skills/orchestration/lanes-claude-code.md:3`、`:7`、`:9`、`:11`、`:13`；`docs/zh/skills/orchestration/lanes-cursor.md:14`；`docs/zh/agents/explorer-h.md:14`、`explorer-xh.md:14`、`worker-h.md:11`、`worker-xh.md:11`；`docs/zh/agents/advisor-xh.md:14`、`:20`。
- 词表：`CONTEXT.md:32`。
- 英文部分见 P05。

原文：

> `docs/zh/agents/worker-h.md:11` 档位来自上面的 frontmatter，模型来自派发时的 `model` 参数

> `CONTEXT.md:32` 接管卡住任务的是 worker 的高档位加一份接管契约，不是另一个角色。

依据：体检·六（"散落的同一概念"，此处是同一概念有多种叫法）；`docs/agents/domain.md` 的 "Use the glossary's vocabulary"。`CONTEXT.md:39-44` 定义：档位（tier）按型号划分；拨盘（dial）是型号加强度。

证据状态：文本已核实（2026-09-29 逐行计数：中文 `lanes-claude-code.md` 五行共 9 处，其余每行 1 处）；影响为推断。

影响：6.0.0 起档位按型号划分，升档要换型号（R2、R3）。把强度称作"档位"，容易把"加强度"读成"升档"。R3 限制同一型号只提升一次，混读会让升级梯走偏。中文读者受影响最大。

最小修改：
- 中文孪生里指强度的"档位"改为"强度"；"固定的 effort 档"改为"固定的强度"。
- `CONTEXT.md:32` 的"高档位"改为"下一档"。

产物类别：中文孪生是本仓交付物，与 P05 同批派发；`CONTEXT.md` 是协调件。

来历：复核遗留。见工单 03 第 97、99 行，工单 05 第 68 行 code-review 的判断项，规格第 641 行。

验证：逐个检查中文孪生里"档位"的剩余命中，每个都指 tier；`python3 tests/test_zh_mirror.py` 退出 0。

#### R05（F07）任务件状态行没有终态

位置：`docs/agents/triage-labels.md` 的标签表；`docs/agents/issue-tracker.md` 的 `Wayfinding operations` 一节（用 `resolved`）；`.scratch/**` 的状态行。

原文：

> `triage-labels.md` | `ready-for-agent` | Fully specified, ready for an AFK agent  |

依据：体检·四（"没有完成标准"）；体检·六（"过时事实"，状态与事实不符）。

证据状态：
- 已核实（2026-09-29 重新计数）：`.scratch/` 里有 21 个状态行。18 个是 `ready-for-agent`，其中包括 5.0.0 已发布的 `.scratch/role-pool-posture/spec.md` 和更早的 `.scratch/model-routing-and-receipt-gate/spec.md`。2 个是 `needs-info`：本文件，以及 `.scratch/global-orchestration-handoff/review.md`（对应的 5.1.0 已经发布）。1 个是 `ready-for-human`：`.scratch/orchestration-lazy-load/proposal.md`（对应的 ADR 0022 已 accepted）。45 张工单里有 38 张没有状态行。
- 推断：下面的风险场景。仓内没有它实际发生的记录。

影响：按 `Status: ready-for-agent` 找工作的代理会拿到已完成的工单，例如分诊流程、AFK 代理和 `Wayfinding` 的 frontier 规则；它们只有读完 Comments 才能分辨。

最小修改：
- 在 `triage-labels.md` 加一个终态。建议复用 `Wayfinding` 已定义的 `resolved`，写明"工作已落地并验收时设置"。
- 入口同步：`AGENTS.md:13` 与 `docs/agents/triage-labels.md:3` 都写 "five canonical roles"，一并改为包含终态的写法。
- 把已完成规格与工单的状态行改为 `resolved`。`tiers-and-routing-6-0` 的规格、工单 05、工单 06 仍在进行，保持原状。
- 没有状态行的旧工单不逐张补；它们所属规格的状态行标为终态即可。

产物类别：协调件，主代理直接写。

来历：第一版新发现。

验证：`grep -rn "^Status:" .scratch/` 的结果与各任务的实际状态一致。

#### R06（F08(a)）`AGENTS.md:35` 转述了首轮准入，并且漏了一个条件

位置：`AGENTS.md:35`。对照 `plugin/skills/orchestration/SKILL.md:76`。

原文：

> The profile's columns are the three tiers: new work starts in `mainstay`, may start in `crux` when a key difficulty is already identified, and reaches `rescue` only after a capability failure in `crux` or a user declaration (see `CONTEXT.md`).

`SKILL.md:76` 的条件是 "an identified key difficulty or mutually constraining conditions"，这段转述漏了后半。工作树已改写这一段的前半（档案改为随插件发布），这句转述仍在。这一段的职责是说明档案在哪里改、改完做什么。

依据：去冗·不必要的重复维护（"同一规则或事实在多处独立维护，却没有阅读或执行上的必要性"）。

证据状态：已核实。

最小修改：改为 "The profile's columns are the three tiers (`CONTEXT.md`, "档位")."。

产物类别：协调件。

验证：`AGENTS.md` 不再转述准入条件。

#### R07（F08(d)）`CONTEXT.md:58` 的车道清单漏了 cursor lane

位置：`CONTEXT.md:58`、`:71`。对照 `CONTEXT.md:73-75`。

原文：

> 到达一个供应商的机制：grok lane、codex lane、claude lane、handoff lane。

`CONTEXT.md:73-75` 定义了 cursor lane；`CONTEXT.md:71` 的"把同模派发当成第五条车道"也因此与第 73 行矛盾。

依据：体检·六（"规则冲突"）。

证据状态：已核实。

最小修改：第 58 行补"Cursor 宿主另有 cursor lane"；第 71 行"第五条车道"改为"另一条车道"。

产物类别：协调件。

#### R08（F08(f)）README 的最低版本与解析顺序的前提不一致

位置：`README.md:57`、`:65`。

原文：

> `:57` **Claude Code ≥ 2.1.170.**

> `:65` Model resolution order in Claude Code (v2.1.251+): per-invocation `model` parameter → agent frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → session model.

5.1.0 之前的 README 把 `CLAUDE_CODE_SUBAGENT_MODEL` 排在每次派发的 `model` 之前（`git show 83ce044^:README.md` 第 67 行）；ADR 0015 第 19 行记录顺序在 v2.1.251 改变。在 2.1.170 到 2.1.250 之间，若设置了这个环境变量，档案给出的每次派发 `model` 都会被覆盖。

依据：体检·六（"过时事实"）。

证据状态：仓内记录一致；官方更新日志本轮没有重读，属推断。

最小修改：把最低版本提到 2.1.251，或写明环境变量这个条件。

产物类别：本仓交付物，经 `worker`。

#### R09（F09 本仓部分）本仓 `AGENTS.md` 写明同模派发的触发类别（已裁定：方案 C）

位置：`AGENTS.md:41-42`（"Delegation boundary by artifact class" 一节）；`docs/adr/0013-delivery-contract-not-build-instructions.md:71`（决策 4）。插件部分见 P08。

原文：

> `docs/adr/0013-delivery-contract-not-build-instructions.md:71` 类别口径入 `SKILL.md`（机制），本仓库的路径映射入 `AGENTS.md`。

这里的 `AGENTS.md` 是本仓根目录的文件。P08 让插件文本改为指向"所在仓库的 `AGENTS.md`"。本仓是插件的开发仓，需要在自己的 `AGENTS.md` 里写出触发类别；否则 P08 落地后，同模派发在本仓不再触发。

依据：ADR 0013 决策 4 的分工；体检·七（"只把不属于通用流程的细节移到配置、参数或条件分支"）。

证据状态：已核实：`AGENTS.md:41` 的交付物清单列了 `plugin/**`，但没有写同模派发的触发类别。

最小修改：
- 在 `AGENTS.md` 的产物类别一节加一句：编排姿态下，`plugin/skills/**` 与 `plugin/agents/**` 的准则散文走同模派发；按类别触发，不按文字看起来是否核心。
- 需一并裁定：`plugin/skills/orchestration/routing-profile.md` 是否属于这一类。ADR 0023 把档案移进 `plugin/skills/**`，按上句的写法它也会被纳入。建议不纳入，写成"`plugin/skills/**`（`routing-profile.md` 除外）"。理由：档案记的是椰椰声明的取值，改档案是誊写声明，不是写准则。
- ADR 0013 追记一行：决策 4 的路径映射已写进本仓 `AGENTS.md`。
- 第一版列出的重复位置 `CONTEXT.md:70`、`README.md:62` 按裁定不动。

产物类别：`AGENTS.md` 与 ADR 是协调件，主代理直接写。

来历：部分复核。2026-09-12 体检交接第 4 条针对的是 prompts 仓库规则文件里的同一专指，那份文件已不存在。

验证：`AGENTS.md` 含新句。对照任务（修改阶段执行）：P08 落地后，在本仓编排姿态下修改一个 `plugin/agents/*.md`，主代理选择同模派发。

#### R10（F10）ADR 修订关系缺反向指针（建议改为方案 B）

位置：被修订 ADR 的状态行。

证据状态：已核实（2026-09-29 重新计数）。
- 缺反向指针至少 16 处。第一版列出 12 处：0014 修订 0005、0006、0011、0013；0015 修订 0006、0014；0018 修订 0011、0014、0015；0020 修订 0013；0021 修订 0018（决策 4、6、7、10、12）与 0020（头部版本说明、决策 6）。第二版补 4 处：0022 修订 0015 决策 10（`0022:6`）；0013 撤回 0012 决策 6 的经济豁免（`0013:71`）；0017 修订 0015 决策 1（`0017:6`）；0018 把 0013 的前言单源分成两份（`0018:18`）。
- 计数方法的局限：第一版只解析"关联"行。第二版用宽口径脚本扫描全部 ADR 正文，得到约 35 个候选对，多数来自同一行里的并列引用，需要逐份人工确认。所以 16 是下限。
- 有反向指针 7 处（2026-09-29 本轮改动后）：0003（指向 0004）；0018 第 16 行（指向 0019）；0006、0015、0017（指向 0023）；0021（指向 0022）；0018 状态行（指向 0023，由本轮游离文件改动补写）。后五处是 2026-09-28 以来的写法。

依据：体检·六（"结合实际适用范围、加载顺序和权威关系判断"）；全局规则 7（两种写法并存时选一种，优先较新者，并说明理由）。

影响：`docs/agents/domain.md` 让代理 "read the ADRs that touch the area you're about to work in"。只读 ADR 0018 的代理会把首轮池和 senior 门当成现行决定。

最小修改（二选一）：
- 方案 B（建议）：先逐份确认完整的修订关系清单，再给每个被修订的 ADR 状态行补"（决策 N 已由 ADR 00XX 修订）"，与 ADR 0003、0023 的写法一致。在 `docs/agents/domain.md` 加一句：新 ADR 修订旧 ADR 时，同时在旧 ADR 的状态行补反向指针。理由：最新两份 ADR 已经这样写，这是较新的写法；方案 A 会与它冲突。代价：以后每份修订旧 ADR 的新 ADR 都要回写。
- 方案 A：在 `docs/agents/domain.md` 加检索规则，不回写。第一版建议这个方案，理由是当时以只记在新 ADR 里为主（12 比 2）。第二版这个比例已变，最新批次改为回写。

产物类别：协调件。

来历：第一版新发现。

验证：方案 B 按确认后的清单逐条检查反向指针，`domain.md` 含新句；方案 A 检查 `domain.md` 的新句。

#### R11（新）`CONTEXT.md:53` 的 _Avoid_ 与 ADR 0023 冲突

位置：`CONTEXT.md:53`。对照 `plugin/skills/orchestration/routing-profile.md:19-25`（型号排名）、ADR 0023 决策 1。

原文：

> `CONTEXT.md:53` _Avoid_: 把型号排名写进仓库 doctrine（`plugin/` 内的技能与 agent 正文）；把填充表当成胜任性筛选（它只在胜任集合内做选择）；写"在用户规则里"；在技能正文里写死本机路径。

依据：体检·六（"规则冲突"）；去冗·失效或错层内容（"前提已不成立的要求"）。

证据状态：已核实。

影响：ADR 0023 把含型号排名的档案放进 `plugin/skills/orchestration/`。按这条 _Avoid_ 的字面，档案本身就是被禁止的写法。后来的代理可能据此把排名移出插件，或者在改档案时误判为违规。

最小修改：第一项改为"把型号排名写进 doctrine 正文（`SKILL.md`、车道文档、agent 文件），排名只在路由档案"，其余三项不动。

产物类别：协调件，主代理直接写。

来历：新发现。工单 06 改了 `CONTEXT.md:52`，没有改第 53 行。

验证：`CONTEXT.md:53` 的新文本与 ADR 0023 决策 1 一致。

#### R12（新，P09 的本仓部分）`AGENTS.md` 接收档案里的两条维护规则

位置：`AGENTS.md:35`（"User routing profile" 一节）。插件部分见 P09。

原文：

> `AGENTS.md:35` Edit that file (a deliverable under `plugin/**`), then release and update both sides (see "Plugin release & local update").

对照 `routing-profile.md:76` 的 "Update the declaration date in the first paragraph when a table changes." 与 `:77` 的 "a changed cell is a minor version"。

依据：去冗·处置·迁移（"移到授权范围内已有的合适载体"）。

证据状态：已核实：`AGENTS.md` 没有写"改格算次版本"和"更新首段声明日期"；ADR 0023 决策 4 写了前一条。

影响：P09 删除档案的维护一节后，这两条规则只剩 ADR 0023 一处。维护者按 `AGENTS.md` 改档案时会漏掉它们。

最小修改：`AGENTS.md:35` 第一句后补 "A changed cell is a minor version, and the declaration date in the profile's first paragraph changes with it."。

产物类别：协调件。

来历：新发现。

验证：`AGENTS.md` 含这两条规则。

#### R13（新）中文孪生同步

位置：`docs/zh/skills/orchestration/**`、`docs/zh/agents/**`。

依据：`AGENTS.md` 的 "Chinese mirror of runtime docs"（"A change to a runtime `.md` updates its twin in the same commit."）。

内容：第二部分下列条目改动 `plugin/**/*.md`，每条都要在同一提交里改对应的孪生。
- P01：九个 agent 文件。
- P02：`SKILL.md`、`lanes-cursor.md`。
- P03、P04：`lanes-claude-code.md`。
- P05：`lanes-cursor.md` 与五个 agent 文件。
- P06：`SKILL.md`、`lanes-claude-code.md`。
- P07：`lanes-cursor.md`。
- P08：`SKILL.md`、`routing-profile.md`。
- P09、P10：`routing-profile.md`。
- P11 若采纳：被拆文件的删节、指针修改与新建文件，都要同步孪生。

产物类别：中文孪生是本仓交付物，与对应的 P 条目同批派发。

来历：新条目，由两部分分开写而来。

验证：`python3 tests/test_zh_mirror.py` 退出 0（只查一一存在）；按第一版做法逐文件比对标题、列表、表格与段落数。

#### R14（新）规格仍按 ADR 0023 之前的档案位置与安装器职责书写

位置：`.scratch/tiers-and-routing-6-0/spec.md:29`、`:394`、`:412`、`:414`、`:476`、`:480`。

原文：

> `spec.md:29` | 伴生安装器 | `scripts/install-user-level.py`；`tests/test_user_level_archive.py`、`tests/test_install_user_level.py` | 基线 | 把档案装到活体；`--check` 比对 | 03、05 |

> `spec.md:394` ### 路由档案（编辑源 `docs/agents/fable-advisor-routing.md` 与中文备份）

> `spec.md:412` - **RP-10 保留内容。** … 调整方法（改这里、跑伴生安装器、更新声明日期）。

> `spec.md:414` - **RP-12 中文备份。** `.zh.md` 同步为中文，内容一致，不安装。

> `spec.md:476` 3. **伴生安装器（现有接缝）。** 档案改完后，装进一个临时家目录，再对它跑 `--check` 退出 0；…

> `spec.md:480` … 中文副本（`docs/zh/`、`docs/agents/fable-advisor-routing.zh.md`）同样零命中现行中文译法：…

依据：体检·六（"过时事实""失效引用"）。

证据状态：已核实。工单 06 只改了规格的 MAN-2、REL-2、REL-3。第 480 行是工单 05 全仓扫描仍在引用的验收范围，其中的 `docs/agents/fable-advisor-routing.zh.md` 已不存在（移到 `docs/zh/skills/orchestration/routing-profile.md`，已在 `docs/zh/` 范围内）。

影响：按规格核对 6.0.0 的代理会以为档案仍在 `docs/agents/`、安装器仍复制档案；工单 05 的扫描会引用一个不存在的路径。

最小修改：
- 第 29、394、412、414、476 行记录的是当时的计划，不改写。在规格 Comments 追加一条：ADR 0023 与工单 06 已取代这些行里的档案位置与安装职责。
- 第 480 行是现行验收入口，原地删去 `docs/agents/fable-advisor-routing.zh.md`。

产物类别：协调件。

来历：新发现；第 394、414、480 行由 GPT-6-Astra 第一轮补充。

验证：规格 Comments 含这一条；第 480 行不再含旧路径。

#### R15（新，P11 的本仓部分）为 P11 记新 ADR

位置：`docs/adr/`（新 ADR）；`docs/adr/0012-orchestration-skill-progressive-disclosure.md` 的决策 1、2、5。插件部分见 P11。

依据：`docs/agents/domain.md`（`docs/adr/` 是唯一的决策存放处）；决策类型门（"committing to … a refactor strategy"）。

内容：若采纳 P11，新 ADR 记录分层规则、拆分方式、各文件预算与复盘条件，修订 ADR 0012 决策 1、2；复核 ADR 0012 决策 5 的前提（仓外规则按名引用 "User routing profile"），前提不成立就退役它；并在 ADR 0012 状态行补反向指针（见 R10）。

产物类别：协调件，主代理直接写。

来历：新条目。GPT-6-Astra 第一轮指出新 ADR 属本仓内容，从 P11 移到这里。

验证：新 ADR 存在，ADR 0012 状态行指向它。

### 1.2 单列：涉及安全、权限边界或减少验证的建议

#### RS1（S3）`AGENTS.md` 产物类别表补三类路径

- 现状：`AGENTS.md:41-42` 没有列 `.agent-discuss/**`、`docs/upstream-sync/**`、`CLAUDE.md`。`SKILL.md:38` 规定 "An unclear class is a deliverable"，所以编排姿态下，讨论记录与上游同步摘要都要经 `worker` 写。
- 建议：把这三类归入协调件。
- 放宽的边界：主代理可以直接写这些路径，它们失去第二读者。这些文件不随插件发布，也不被测试。需椰椰确认。

#### RS2（S4）运行伴生安装器

- 安装器写两侧的 `~/.cursor/rules/fable-lane-pin.mdc` 与 `~/.cursor/hooks/fable-lane-family-gate.py`（WSL 家目录与 `/mnt/c/Users/Shy`）。这是仓外写入，工单 05 已列为需授权。
- "本轮另行处理的改动"落地后，安装器不再删除任何文件。
- 建议 R01 在工单 05 运行安装器之前落地，一次装好。

#### RS3（新）一次性删除两侧的路由档案活体与全局提示词里的路径指令

- 对象（2026-09-29 只读检查）：WSL 的 `~/.claude/docs/fable-advisor-routing.md`（6314 字节，2026-09-16）；Windows 的 `/mnt/c/Users/Shy/.claude/docs/fable-advisor-routing.md`（6314 字节，2026-09-18）；两侧 `~/.claude/CLAUDE.md:132` 的 "Model allocation" 一行；prompts 仓库的档案快照。旧规则文件 `~/.claude/rules/fable-advisor.md` 与 `~/.cursor/rules/fable-advisor.mdc` 在两侧都已不存在。
- 原顺序保护什么：已安装的 5.2.0 技能只读调用方点名的档案，两侧全局提示词点名的正是这两份活体。两侧装上 6.0.0 并重启之前删除，当前会话的模型分配会读不到档案。
- 做法：按工单 06 D5 的顺序执行。两侧装上 6.0.0 并重启，删除全局提示词那一行，逐侧确认新会话读取插件档案，然后手动删除两份活体，每侧单独断言文件已不存在。
- 这是仓外删除，git 无法恢复，需要椰椰当次授权。

#### RS4（S5）删除未跟踪文件（U1、U3、U4、U5）

- git 无法恢复未跟踪文件。`cmp` 证实只有 U1 的两份交接稿在 prompts 仓库有逐字节相同的原件。`outputs/*.html` 与 `ONBOARDING.md` 没有其他副本。`__pycache__/` 可由测试重新生成。
- 建议：删除前先移到仓外备份目录；或者只加入 `.gitignore`，不删除。

#### RS5（S6）`ONBOARDING.md` 的隐私

- 文件含 "Based on IpiggyI's usage over the last 30 days" 的个人用量统计，以及另外两个仓库的链接。提交到公开 fork 会公开这些信息。
- 建议：不提交。

### 1.3 单列：涉及功能逻辑、接口或测试覆盖的建议

这些项不作为文字清理直接执行。

#### RI1（I2）文档漂移测试只查存在

- 证据（已核实）：`tests/test_zh_mirror.py` 第 2 行写明只查 "One-to-one existence"。`tests/test_user_level_archive.py` 对 pin 规则中文备份只查三件事：非空、含中文、含"不是活体"。所以 R01 的中英漂移通过了全部测试。
- 建议：在 `test_user_level_archive.py` 加一条最小内容比对：英文正典与中文备份点名同一组 agent，两份都含 `advisor-` 前缀，都不把 `fable-advisor` 当 agent 名。不建议做全文翻译比对。
- 这是新增测试覆盖，需确认。
- 验证：新测试先在当前文件上失败（能抓到 R01），R01 修复后通过。

#### RI2（新，P11 的本仓部分）词数预算改由测试强制

- 证据（已核实）：`SKILL.md` 的上限只写在 ADR 与工单验收里，由人工 `wc -w` 核对；2026-09-13 到 2026-09-28 上调四次（1950、1960、2110、2160、2210，见 ADR 0015、0020、0021、0022）。`lanes-claude-code.md` 没有预算。
- 建议：若采纳 P11 的 (c)，新增一个测试，逐文件检查 `plugin/skills/orchestration/*.md` 的词数不超过各自预算。预算值写在测试里；上调预算要改测试并记 ADR。
- 这是新增测试覆盖，需确认。
- 验证：新测试在"某文件超出预算"的样本上失败，在现状上通过。
- 时点：随 P11 的预算定稿一起实施。

#### RI3（新，PI1 的本仓部分）`advisor-l` 退役时的本仓引用

- 前提：只在 O2 专题决定退役 `advisor-l`（PI1 方案 A）时执行。
- 本仓引用（已核实）：`README.md:28`、`:58`、`:107`；`CONTEXT.md:18`；`cursor-hooks/zh/fable-lane-pin.mdc:7`，以及 R01 修改后的英文正典。
- 中文孪生：删除 `docs/zh/agents/advisor-l.md`，同步 `docs/zh/skills/orchestration/lanes-claude-code.md:3` 的 agent 枚举。孪生残留时 `tests/test_zh_mirror.py` 会判为失败。
- 公开的 agent 名减少，属不兼容改动，需要版本号与 README 升级说明。门禁按前缀判定，不用改；自测用例里的 `advisor-l` 仍是合法的前缀样本。
- 验收：与 PI1 同批完成；`python3 tests/test_zh_mirror.py` 退出 0；现行文本里的 `advisor-l` 引用只剩有意保留的历史升级说明。

### 1.4 未跟踪产出的处置建议

| 编号 | 文件 | 事实 | 建议 |
|---|---|---|---|
| U1 | `docs/fable-advisor-healthcheck-2026-09.md`、`docs/fable-advisor-orchestration-handoff-2026-09.md` | 与 `/mnt/d/Development/Local/prompts/docs/plans/` 下的原件逐字节相同（2026-09-27 `cmp`）；内容已由 ADR 0015 至 0018 落地；其中的版本事实停在 4.2.0 与 5.0.0 | 删除，原件保留在 prompts 仓库；见 RS4 |
| U2 | `docs/fable-advisor-tier-and-consult-handoff-2026-09.md` | 本机唯一副本；讨论 `tiers-and-consult-iteration` 的 `request-001.md` 与 `final.md` 按路径和 SHA-256（`5c9ba715…`）引用它；其中的 advisor 部分（H8 至 H16）留给待开的 advisor 专题 | 保留原位，不提交（O1 已定）；advisor 专题关闭后再处置 |
| U3 | `outputs/*.html`（三份） | show-me 讲解页，日期为 2026-09-11、09-13、09-16，描述的是 5.x 行为；不是版本说明书 | 删除；或保留并把 `outputs/` 加入 `.gitignore`。若加入，`docs/agents/plugin-release.md:32` 的 "`outputs/` is not ignored" 要同步修改。见 RS4 |
| U4 | `ONBOARDING.md` | Claude Code 生成的团队入门模板，含 `_TODO_` 与个人用量统计 | 删除或移出仓库；见 RS4、RS5 |
| U5 | `tests/__pycache__/`、`cursor-hooks/__pycache__/` | 测试运行产物；`.gitignore` 没有 `__pycache__/` | 删除，并在 `.gitignore` 加 `__pycache__/` |
| U6 | `.agent-discuss/tiers-and-consult-iteration/`、`.agent-discuss/active` | O1 已定不提交；`active` 是讨论技能的便利指针，技能说明写明它不是事实来源 | 不处置 |

### 1.5 容易被误删的保留项

- `CONTEXT.md` 各 `_Avoid_` 里的退役名（light、standard、senior、首轮池、senior 门等）：它们防止旧词回流，是词表的职责。
- `README.md:126` 中 v5.2.0 及更早版本的升级说明：工单 03 规定逐字保留的历史记录。v6.0.0 一句由"本轮另行处理的改动"修改。
- `docs/agents/cursor-lane-gate.md:16` 对规范化局限的说明（零宽字符、全角字符）：这是写给维护者的已知边界。

### 1.6 待椰椰裁定（第一部分）

1. R01 至 R08、R11 至 R14：逐项确认。R15 随 P11 裁定。
2. R05：任务件终态是否用 `resolved`？
3. R09：路由档案是否排除在同模派发的类别之外？建议排除。
4. R10：选方案 B 还是方案 A？第二版建议 B。
5. RS1、RS4、RS5：逐项确认。RS2、RS3 的执行时点已写在工单 05、06，届时另行授权。
6. RI1、RI2：是否新增这两项测试？RI2 随 P11 裁定；RI3 随 O2 专题。
7. `README.md:130-132` 的 "Go deeper" 段是上游作者的订阅推广（原文写 "I write"），fork 的 README 是否保留？

---

## 第二部分：发布到外面去的插件内容（`plugin/**`）

`SKILL.md` 现为 2206 词，上限 2210（ADR 0022 决策 5）。改动它的条目写出词数变化与抵扣来源。

### 2.1 需要修改的发现

按影响与改动风险排序；P11 是椰椰补充的结构议题，放在最后。

#### P01（F02）agent 文件的自述替路由档案选拨盘，`advisor-h` 不再说明何时调用（已裁定：九个文件现在一起改）

位置：
- 替档案选拨盘：`plugin/agents/advisor-xh.md:3`、`:14`；`advisor-md.md:14`；`advisor-l.md:14`；`explorer-h.md:3`、`:14`；`explorer-xh.md:3`、`:14`；`worker-h.md:11`；`worker-xh.md:3`、`:11`。
- 失去调用时机：`plugin/agents/advisor-h.md:3`、`:14`。
- 对照：`plugin/skills/orchestration/routing-profile.md:36-39`（advisor 映射）、`:45-47`（Claude 拨盘到 agent 文件的映射）；`plugin/skills/orchestration/SKILL.md:88`（填充表在档案里）。

原文：

> `advisor-xh.md:3` Read-only advisor at effort xhigh: for a contested decision, a plan about to be overturned, or the same problem failing twice.

> `advisor-xh.md:14` Use this file when the cheaper advisors would be guessing: the same problem has failed twice, two established patterns contradict, a plan is about to be overturned, or a diff is correctness-critical with no cross-vendor reader available. Routine gates belong on `advisor-h`.

> `advisor-md.md:14` A correctness-critical decision belongs on `advisor-h`; a contested one, or the same problem failing twice, on `advisor-xh`.

> `worker-h.md:11` Use this file for contracts whose shape is already settled; `worker-xh` is for work where the implementation choices themselves are hard.

> `advisor-h.md:3` Read-only advisor at effort high: serves any `high` advisor dial the routing profile names, in the decision or the acceptance shape.

档案原文：

> `routing-profile.md:37` Decision shape: `mainstay` at `medium`.

依据：体检·一（"是否接管了本应由用户、其他文档或既有工作流负责的事情"，此处是 agent 文件接管了档案的路由职责）；体检·三（"skill 的描述或文档引用是否清楚交代何时适用"）；体检·六（"规则冲突"）。

证据状态：
- 已核实：上述冲突文本。本会话的派发工具列表显示的正是这些描述；除 `advisor-h` 与 `worker-md` 外，列出的 5.2.0 描述与仓库现行描述逐字相同。
- 推断：主代理按描述而不按档案选拨盘的频率；单独复制 `advisor-h` 使用时的调用率。

影响：Claude Code 每个会话的派发工具都列出九个描述。描述点名具体情形时，就与档案争夺路由权。例如，推翻计划属于决策类型门，档案给的是 `mainstay` 的 `medium`（Claude 候选对应 `advisor-md`）；`advisor-xh` 的描述却正好点名这个情形，可能让一次 `mainstay` 决策绕过档案映射，直接用上 xhigh 拨盘。反方向的问题在 `advisor-h`：6.0.0 把它的描述改成只说"服务档案点名的 high 拨盘"，不再说明何时调用。用户只把 `advisor-h.md` 复制进 `~/.claude/agents/` 单独使用时（README 称 Lite mode），没有档案，主代理没有调用它的理由。

最小修改：九个文件用同一种描述。描述写角色做什么、调用方何时用这个角色；拨盘交给档案。advisor 的建议文本：

> Read-only advisor at effort high: a second reader at the decision-type gate (before committing) or for acceptance review (after). Which advisor effort answers is the routing profile's decision. Advises only.

正文把 "Use this file when …""… belongs on …" 一类句子换成 "Which dial reaches this file is the routing profile's decision."。保留与强度相关的行为句，例如 `advisor-xh.md:20` 的 "read the callers too"、`:30` 的 "A verification that cannot fail when the intent is wrong is not evidence either"、`explorer-xh.md:22` 的 "both anchors and which one the runtime actually reaches"。

产物类别：插件准则散文，走同模派发，按 Tier 3 验收。孪生见 R13。

来历：复核遗留。工单 03 Comments 第 98 行与规格第 641 行已记录。

验证（依赖模型行为，留待修改阶段执行）：
- 对照任务 1（单独复制）：新会话只在 `~/.claude/agents/` 放 `advisor-h`，任务是"为一个接口选定 API 形状"。通过标准：主代理在定案前派发 advisor。
- 对照任务 2（带档案）：一次推翻既定计划的决策。通过标准：选中的 advisor 拨盘符合档案的决策形状映射，不是 `advisor-xh`。
- 机械检查：`grep -n -E "belongs on|Use this file when|default explorer" plugin/agents/*.md` 没有命中。

相关单列项：PS2、PI1。

#### P02（F03 插件部分）Cursor 下 Grok 的到达方式有两种说法

> 2026-09-29：本条的修改方向已被椰椰的更正推翻。改为以 `SKILL.md:60` 与 `lanes-cursor.md:3` 的原说法为准，修改档案的 Cursor 调用入口句，并删去 `lanes-cursor.md` 的 grok runner 一段。见 Comments 与 ADR 0025。

位置：`plugin/skills/orchestration/SKILL.md:60`；`plugin/skills/orchestration/lanes-cursor.md:3`。对照 `routing-profile.md:59`、`lanes-cursor.md:25`。本仓部分见 R02。

原文：

> `SKILL.md:60` the Grok family through the grok runner (Claude Code) or a pinned dispatch (Cursor)

> `lanes-cursor.md:3` The grok lane, the claude lane, and the cursor lane (Cursor's own models) are native: a subagent dispatch pins its own model.

> `routing-profile.md:59` `grok-4.7` `medium` and `high` through the grok runner via Shell, `xhigh` through a model-pinned `Task`

> `lanes-cursor.md:25` The grok runner runs the same way. … Not yet exercised in Cursor.

依据：体检·六（"规则冲突"，同一事实有两种说法）；体检·四（"缺少必要验证"，档案路由到从未实跑的路径）。

证据状态：
- 已核实：文本冲突。版本说明书 6.0.0 自己把它记为已知不一致。三处冲突现在都在插件内（档案随 ADR 0023 移入插件）。
- 推断：当前 Cursor allowlist 里有哪些 Grok 变体。最后一次快照是 2026-09-16，只有 xhigh；PRB-3 没有回报。

影响：Cursor 的主代理按 `SKILL.md` 与 `lanes-cursor.md`，会把 Grok 的 `medium`、`high` 当钉型号 `Task` 派发；档案却让它们经 Shell 走 grok runner。若 allowlist 仍只有 xhigh 变体，这两个强度会被跳过。另外，档案把 Cursor 下 worker `mainstay` 的默认拨盘 `grok-4.7[high]` 路由到一条准则自己标为"未实跑"的路径。

最小修改：
- `SKILL.md:60` 改为 "the Grok family through the grok runner (Claude Code, or Shell in Cursor) or a pinned dispatch (Cursor)"。加 4 词，由 P06 抵扣。
- `lanes-cursor.md:3` 把 grok 从"原生"列表拿出，按档案第 59 行写明：Grok 的 `medium`、`high` 经 Shell 运行 grok runner（见同文件下文），`xhigh` 经钉型号的 `Task`。
- Cursor 实跑跑通后（记录见 R02），再改 `lanes-cursor.md:25` 的 "Not yet exercised in Cursor."。

产物类别：插件准则散文，走同模派发。

来历：复核遗留。见工单 03 Comments 第 92–94 行的 advisor verdict，以及规格第 641 行。

验证：文字部分可在本机检查；Cursor 实跑见 R02。

#### P03（F04）Claude Code 的 claude 车道没有规定前言路径的送达

位置：`plugin/agents/explorer-h.md:10`、`explorer-xh.md:10`、`worker-h.md:9`、`worker-md.md:9`、`worker-xh.md:9`；`plugin/skills/orchestration/SKILL.md:72`；`plugin/skills/orchestration/lanes-claude-code.md:29-31`。

原文：

> `explorer-h.md:10` Your operating contract — authority boundary, gap protocol, report shape — is `<plugin-root>/skills/orchestration/lane-preamble-report.md`. If the dispatch prompt did not open with it, read it before anything else.

> `SKILL.md:72` Runners prepend the one `mode` names; a Cursor dispatch points at the one its role needs. Restate neither.

> `lanes-claude-code.md:29` ## 0. The preamble reaches every lane

依据：体检·四（"对顺序敏感、易出错或必须一致的操作，保留精确步骤和判据"，此处缺少送达前言的步骤）；另外第 0 节标题写"每条车道"，正文只写两个 runner。

证据状态：
- 已核实：上述三处文本。插件缓存 `~/.claude/plugins/cache/fable-advisor/fable-advisor/` 现有 4.0.0、5.0.0、5.1.0、5.2.0 四个版本目录（2026-09-29）。
- 待验证：子代理实际怎样解析 `<plugin-root>`。Cursor 侧的主代理能否得到 `<plugin-root>` 的实际路径，同样未验证。

影响（推断）：准则只规定了两种送达方式，即 runner 前置与 Cursor 指路。Claude Code 的 claude 车道派发没有规定。子代理看不到技能的基础目录，只能自己搜索这个文件。缓存里有四个版本，它可能读到旧版前言，也可能跳过前言；这样缺口上报与报告格式都不受约束。`explorer-*` 只有 Read、Grep、Glob 三个工具。

最小修改：在 `lanes-claude-code.md` 的 claude 车道段或第 0 节加一句：

> A claude-lane dispatch prompt opens with the absolute path of the preamble its role needs, taken from this skill's base directory.

第 0 节正文补上 claude 车道；或者把标题改为只指 runner。`SKILL.md` 不动。

产物类别：插件准则散文。

来历：第一版新发现。

验证（先验证，再修改）：派发一次 `explorer-h`，提示词不带前言路径，读子代理转写，看它读了哪个前言文件、有没有读。修改后再派一次，提示词带路径。通过标准：转写显示读取了当前版本的前言，报告符合前言规定的回答形状。

#### P04（F05 插件部分）`lanes-claude-code.md` 混入测量经过、过时的 Fable 事实、维护待办和仓内 ADR 编号

位置：`plugin/skills/orchestration/lanes-claude-code.md:9`（后半）、`:11`、`:19-25`。对照 `docs/adr/0021-tiers-mainstay-crux-rescue.md:52`、`.scratch/tiers-and-routing-6-0/issues/02-grok-default-and-claude-aliases.md:56`、`docs/adr/0016-effort-per-agent-file-role-pool.md:70`。本仓部分见 R03。

原文：

> `:9` Measured on the same session, same agents, both paths — under the pre-retirement file names `worker` and `fable-advisor`, which no longer exist, so this pair is not reproducible by name today: …

> `:11` … plugin-level `low` and `xhigh` are extrapolated from project-level agent files, which is a different load path. Probe those two through this pool once the session has restarted.

> `:19` … Before enabling, only one of nine requests stayed on it for a whole run; the rest either started on `claude-fable-5-1` and switched to `claude-sonnet-5` once tool results came back, or were `claude-sonnet-5` from the first turn.

> `:21` … one pre-enablement dispatch ran wholly on fable — its first record timestamped eighteen minutes before credits were switched on …

> `:25` The general rule survives the fix: a model is a request, not an execution guarantee, so cite it in the receipt wording of ADR 0015 — submitted, not observed.

依据：去冗·失效或错层内容（"只服务维护、溯源或历史记录，却混入其他读者入口的内容"）；体检·四（"是否把局部任务扩大成全量调查、反复验证"，此处 "Probe those two…" 把维护待办交给每个读者）；体检·六（"过时事实""失效引用"）；第二部分的本仓内容标准（ADR 0015 不随插件发布，安装者读不到）。

证据状态：
- 已核实：第 9 行后半 61 词，第 11 行 131 词，第 19–25 行 326 词（其中第 25 行 58 词），合计约 518 词，占该文件 3661 词的 14%。已跟踪文件与 `.memory/tasks/` 里都找不到插件级 `low`、`xhigh` 探针已执行的记录。2026-09-27 的观测是：在未开通 usage credits 的配置下，`fable` 派发被拒（HTTP 429）。
- 推断：删去这些叙事不改变派发行为。

影响：`SKILL.md:67` 要求 Claude Code 的主代理在首次派发前读这份文件，所以这 518 词进入每个派发会话。"Probe those two…"是一条维护待办，自 5.1.0 起没有关闭；它以祈使句出现在所有仓库的运行时准则里，可能把主代理拉去做与任务无关的探针。Fable 叙事早于 429 观测。第 25 行让安装者去查一份他们读不到的 ADR；这句要表达的规则 "submitted, not observed" 本身就在同一句里。

最小修改：
- 保留规则句：派发不带 `name`；frontmatter `effort:` 双向覆盖运行模型的设置档位；没写 `effort:` 的 agent 跟随运行模型的设置；haiku 没有强度维度；观测点是子代理转写。
- 第 9 行删去从 "Measured on the same session" 到该句例子结束的测量叙事。
- 第 11 行改为一句："Frontmatter `effort:` overrides the running model's configured level in both directions."
- 第 19–25 行改为：

> Fable as the advisor needs usage credits enabled on the account. When a `fable` dispatch fails, treat it as an unavailable candidate and re-route (SKILL.md "Re-routing"). A model is a request, not an execution guarantee: cite a receipt's model as submitted, not observed, and read `message.model` in the subagent transcript for what ran.

- 新文本只写运行条件、失败处置与观测方法，不写观测经过与日期，也不把单次观测（2026-09-27 当次配置返回 HTTP 429）写成必然行为。
- 测量样本、外推与探针的去处见 R03 与 PS1。

产物类别：插件准则散文，走同模派发。

来历：第一版新发现；第 25 行的 ADR 引用是第二版按本仓内容标准新增。

验证：修改前后对比 `wc -w`；用 `grep` 确认保留的规则句都在，`plugin/**/*.md` 里没有 "ADR 0015"。对照任务：主代理读修改后的文件后派发 claude 车道；通过标准是派发不带 `name`，模型取自档案。

#### P05（F06 英文部分）强度被称作 tier 或 dial

位置：`plugin/skills/orchestration/lanes-cursor.md:14`；`plugin/agents/explorer-h.md:14`、`explorer-xh.md:14`、`worker-h.md:11`、`worker-md.md:11`、`worker-xh.md:11`。本仓部分见 R04。

原文：

> `lanes-cursor.md:14` An ad-hoc model pin carries a fixed effort tier

> `worker-h.md:11` the dial comes from the frontmatter above, and the model comes from the per-dispatch `model` parameter

依据：体检·六（"散落的同一概念"）；`CONTEXT.md:39-44` 的定义（档位按型号划分，拨盘是型号加强度）。

证据状态：文本已核实；影响为推断。

影响：6.0.0 起档位按型号划分。把强度称作 tier 或 dial，容易把"加强度"读成"升档"，与升级梯 R3 冲突。

最小修改：
- "a fixed effort tier" 改为 "a fixed effort"。
- 五个 agent 文件的 "the dial comes from the frontmatter above" 改为 "the effort comes from the frontmatter above"。

产物类别：插件准则散文，走同模派发。

来历：复核遗留（同 R04）。

验证：`grep -rn -E "effort tier|the dial comes from" plugin/` 没有命中。

#### P06（F08(b) 扩充）`SKILL.md` 里两句 Claude Code 专属事实

位置：`plugin/skills/orchestration/SKILL.md:62`、`:29`。对照 `lanes-claude-code.md:3`。

原文：

> `SKILL.md:62` Unpinned, Explore runs the session model (Opus-capped on the Claude API) with no effort dial.

> `SKILL.md:29` Claude Code caps subagent nesting at three layers below the main session.

依据：ADR 0012 决策 1（`SKILL.md` 只放与宿主无关的准则）；去冗·不必要的重复维护；体检·三（"特定分支的细节按条件读取"）。

证据状态：已核实。第 62 行这句与 `lanes-claude-code.md:3` 重复，Claude Code 的主代理首次派发前会读到那里。第 29 行这句只在 Claude Code 成立，车道文件里没有它。

最小修改：
- 从 `SKILL.md` 删去第 62 行这句，减 15 词。
- 把第 29 行这句移到 `lanes-claude-code.md`（claude 车道段），`SKILL.md` 减 11 词。
- 合计减 26 词，抵扣 P02 的加 4 词。

产物类别：插件准则散文，走同模派发。

来历：第 62 行是第一版 F08(b)；第 29 行是第二版新增。

验证：`wc -w` 对比；`lanes-claude-code.md` 含两句事实各一次。

#### P07（F08(e)）`lanes-cursor.md:29` 写 "Two rules:"，后面有四条

位置：`plugin/skills/orchestration/lanes-cursor.md:29`，后面的规则在第 31–34 行。

依据：去冗·语义冗余（"仅复述相邻结构的计数或编号范围"，此处计数还与结构不符）。

证据状态：已核实。

最小修改：改为 "Rules:"。

产物类别：插件交付物。

#### P08（F09 插件部分）`SKILL.md:40` 点名"本插件自己的准则散文"，档案第 67 行复述（已裁定：方案 C）

位置：`plugin/skills/orchestration/SKILL.md:40`；`plugin/skills/orchestration/routing-profile.md:67`。本仓部分见 R09。

原文：

> `SKILL.md:40` It serves one artifact class in the orchestrating posture, the plugin's own doctrine prose (skill and agent text); the class triggers it, not how central the text feels.

> `routing-profile.md:67` Same-model dispatch (doctrine prose in the orchestrating posture) stays a `generalPurpose` dispatch with `model` omitted, outside this table.

依据：体检·七（"只把不属于通用流程的细节移到配置、参数或条件分支"）；去冗·归属层（"当前读者是否需要在这里看到它"）；第二部分的本仓内容标准（这条规则只在本仓生效，却随插件发给所有安装者）；ADR 0013 决策 4 的分工。

证据状态：文本已核实；`SKILL.md:40` 第二句 28 词。

影响：随插件发布到所有仓库的核心准则里，有一条只在本仓生效的规则。档案第 3 行说档案放取值和格内规则，第 67 行却复述准则。

最小修改（方案 C，已裁定）：`SKILL.md:40` 保留机制句与两个宿主的做法，把第二句换成 "The repo's AGENTS.md names the artifact class it serves."（9 词），减 19 词。这句的 `AGENTS.md` 泛指插件运行时所在仓库的文件。删去 `routing-profile.md:67`。

产物类别：插件准则散文，走同模派发。

来历：部分复核（同 R09）。

验证：`SKILL.md` 不含 "the plugin's own doctrine prose"；档案不含 "Same-model dispatch"。

#### P09（新）档案的 "Adjusting this profile" 一节是本仓维护步骤

位置：`plugin/skills/orchestration/routing-profile.md:74-78`；`:3` 的 "and replaces the 2026-09-16 profile"。对照 `AGENTS.md:35`（本仓已有同一流程）。本仓部分见 R12。

原文：

> `routing-profile.md:76` 1. Edit the cell here, in `plugin/skills/orchestration/routing-profile.md`. This file is the only source; its Chinese translation `docs/zh/skills/orchestration/routing-profile.md` does not ship. Update the declaration date in the first paragraph when a table changes.

> `routing-profile.md:77` 2. Release the plugin (`docs/agents/plugin-release.md`) and update it on both sides; a changed cell is a minor version. A running session keeps the old profile until it restarts.

> `routing-profile.md:78` 3. Nothing else changes: no doctrine edit, no installer run, and no instruction outside the plugin names this file.

依据：第二部分的本仓内容标准；去冗·失效或错层内容（"只服务维护、溯源或历史记录，却混入其他读者入口的内容"）；去冗·处置·迁移（"移到授权范围内已有的合适载体"）。

证据状态：已核实。这一节 83 词，三句点名了本仓路径、本仓发版文档、本机"两侧"、伴生安装器和全局指令。`SKILL.md:88` 要求主代理在首次分配模型前读档案，所以这 83 词进入每个分配模型的会话。

影响：安装者在别的仓库里读到一套无法执行的维护步骤；主代理每次分配模型都读这一节，却用不上它。

最小修改：
- 删去第 74–78 行整节，只保留一句对安装者有用的条件："A running session keeps the old profile until it restarts."，移到第 3 行首段末尾。
- 第 3 行删去 "and replaces the 2026-09-16 profile"。声明日期保留，它是"模型换代时重评"的锚点。
- 仍需要的两条维护规则迁到本仓 `AGENTS.md`，见 R12。
- 净减约 79 词（删 83 词加第 3 行 6 词，保留句 10 词）。

产物类别：插件交付物（档案）。派发方式取决于 R09 对档案类别的裁定：不属同模派发类别时经 `worker`。

来历：新发现。

验证：`grep -n -E "docs/agents|both sides|installer" plugin/skills/orchestration/routing-profile.md` 没有命中。

#### P10（新）`SKILL.md` 与档案重复陈述同一批规则

位置：`plugin/skills/orchestration/routing-profile.md:8`、`:9`、`:69-72`。对照 `SKILL.md:78`、`:88`、`:90`、`:92`。

原文：

> `routing-profile.md:9` The first candidate in a cell is the default. With no declaration and no specialty that fits, take the first candidate at its `*` dial.

> `SKILL.md:78` **Stage 2 — choosing inside the cell.** The first candidate is the default, at its `*` dial absent declarations.

另外三组：档案第 8 行的拨盘记法对应 `SKILL.md:88`；档案第 71 行的易变状态对应 `SKILL.md:90`；档案第 72 行的 handoff 声明对应 `SKILL.md:92`。

依据：去冗·不必要的重复维护（"同一规则或事实在多处独立维护，却没有阅读或执行上的必要性。按实际读取路径合并到合适位置"）。

证据状态：已核实：四组现在语义一致。ADR 0023 之前，档案是用户级文件，技能必须自带这些机制，档案的复述不影响技能；ADR 0023 决策 2 规定只有插件内这一份档案，两份文件总是一起发布、在同一时刻读取，复述不再有独立加载的理由。

影响：同一规则改一处漏一处就会漂移；主代理分配模型时两处都读。按下面的删除范围计算，档案净减约 125 词（含标题）。

最小修改：
- 档案第 8 行只保留表格语法 "`›` separates candidates."，拨盘记法以 `SKILL.md:88` 为准。
- 删去档案第 9 行。
- 删去档案第 69–72 行整节（"Verbal declarations"）。
- 机制留在 `SKILL.md`。档案首段 "this file carries the user's values and the in-cell choosing rules those values depend on" 不动，因为三条刻意的顺序、擅长点与车道默认顺序仍在档案。

产物类别：插件交付物（档案），派发方式同 P09。

来历：新发现。

验证：逐句核对：被删的每条规则都能在 `SKILL.md` 找到等义句。

#### P11（新，椰椰 2026-09-29 补充议题）`SKILL.md` 与 `lanes-claude-code.md` 过重且逐版膨胀：精简与拆分（需裁定）

位置：`plugin/skills/orchestration/SKILL.md`（2206 词，其中 frontmatter 约 90 词）；`plugin/skills/orchestration/lanes-claude-code.md`（3661 词）。对照：`SKILL.md:67`；`lanes-cursor.md:3`、`:20`；`routing-profile.md`（1224 词）。

原文：

> `SKILL.md:67` Identify the harness by the host you run in and its tools' parameter structure, never by one tool name or a `model` parameter's presence; read the matching lanes file before the first dispatch:

> `lanes-cursor.md:20` … The spec, the pending/receipt flow, the wait protocol (block on the Shell process, never a fixed sleep), the receipt fields, `resume_session_id`, and `mode: "report"` for read-only roles are exactly as in [lanes-claude-code.md](lanes-claude-code.md) …

依据：
- 体检·三："常驻内容保留必要共性，特定分支的细节按条件读取；引用应说明何时读、读来解决什么问题。避免每次任务都读全部材料，也避免为缩短主文件拆出必须全部加载的薄壳。评估实际阅读路径与总负担，不只看入口长度。"
- 去冗·不必要的重复维护；去冗·失效或错层内容。
- ADR 0012 背景的分支判据（"只被部分运行到达的引用材料应下沉到指针之后"）；ADR 0022 决策 5（"ADR 0021 的复盘条件'逼近上限时先按 ADR 0012 判断沉降，不继续上调'仍适用于正文"）。

证据状态：
- 已核实（词数由 `git show` 加 `wc -w` 逐提交计数；上限取自 ADR 原文）：
  - `SKILL.md`：2026-08-20 按 ADR 0012 拆分后 1896 词；5.1.0（2026-09-16）1959 词；2026-09-21 2106 词；6.0.0（2026-09-27）2160 词；工作树 2206 词。上限依次是约 1.9k（ADR 0012）、1950（ADR 0015）、1960（ADR 0015 返工）、2110（ADR 0020 决策 6）、2160（ADR 0021 决策 11）、2210（ADR 0022 决策 5）。2026-09-13 到 09-28 上调了四次。
  - `lanes-claude-code.md`：2026-08-20 788 词；09-06 1406 词；09-11 2128 词；09-16 3258 词；09-21 3710 词；6.0.0 3661 词。五周涨到 4.6 倍，没有预算。
  - 上调理由的共同点：ADR 0020 决策 6 与 ADR 0021 决策 11 都写新规则"必须到达每个主代理，不能沉进某个 harness 分支文件"。ADR 0012 只有按宿主拆分这一条轴，跨宿主的新规则因此都落进 `SKILL.md`。
  - 阅读路径：`SKILL.md:67` 要求首次派发前读宿主对应的车道文件；`SKILL.md:88` 要求首次分配模型前读档案。Claude Code 的主代理第一次派发前读 `SKILL.md`、`lanes-claude-code.md` 与档案，约 7,090 词。Cursor 的主代理使用 codex runner 时，`lanes-cursor.md:20` 又把它指向 `lanes-claude-code.md`，约 8,290 词。
  - 分节词数（按标题切分，不含标题行）：`lanes-claude-code.md` 开头到第 27 行（claude 车道机制加测量经过）1101 词；第 0–4 节 runner 流程 1725 词；"Rework tickets" 131 词；"Report mode" 311 词；"Grok deltas" 269 词；"Dispatch, not probes" 73 词。`SKILL.md`："Routing" 293 词，"User routing profile" 181 词，"The delivery contract" 329 词，"Parallelism" 78 词，"Verification" 292 词，其余各节 36–151 词。
  - 加载方式：本会话（2026-09-29）调用技能时，宿主只注入了 `SKILL.md` 正文；同目录文件要另行读取。
- 推断：各类会话实际用到哪些部分的比例。仓内没有统计。

影响：
- `lanes-claude-code.md` 把两类读者的内容放在一份首次派发前必读的文件里。只派 claude 车道的会话要读 runner 机制；Cursor 使用 runner 的会话要读 Claude Code 的 claude 车道细节。
- 预算只约束 `SKILL.md`，而且新规则每次都靠上调预算落地；`lanes-claude-code.md` 没有预算，增长最快。
- 测量经过、维护待办这类内容没有明确的去处规则，所以反复进入运行时文件（P04、P09 是现有实例）。

最小修改（(a)、(b)、(c) 分别裁定）：

(a) 精简：只删错层与重复内容，不改行为。它就是 P02、P04、P06、P08、P09、P10 的合集，估算效果如下。
- `lanes-claude-code.md` 净减约 450 词（P04）。
- `SKILL.md` 净减约 41 词：P02 加 4 词，P06 减 26 词，P08 减 19 词，2206 词降到约 2165 词。
- 档案约减 200 词（P09、P10）。
- "Wait for the runner"（560 词）与 "Judge the receipt"（703 词）本轮没有逐句审，是否还有可删内容，留给实施阶段单独判断。

(b) 拆分：只在阅读路径确实分叉的地方拆。
- (b1)（建议）`lanes-claude-code.md` 按车道机制拆成两份。按内容拆，不按行号机械切分：
  - Claude Code 的 claude 车道文件：开头到第 25 行的 claude 车道内容，P03、P04、P06 之后约 680 词。只在 Claude Code 派 claude 车道之前读。
  - 两个宿主共用的 runner 文件：第 27 行的 runner 导语、第 0–4 节、"Rework tickets"、"Report mode"、"Grok deltas"、"Dispatch, not probes"，约 2,540 词。Claude Code 与 Cursor 都在第一次运行 runner 之前读。`lanes-cursor.md:3`、`:20`、`:25` 改为指向它。
  - runner 文件里只在 Claude Code 成立的机制，留在 runner 文件里按宿主条件分节，不移回 claude 车道文件：那份文件只在派 claude 车道之前读，只用 runner 的会话会漏读。已知的 Claude Code 专属处：第 72、73 行的两种等待方式（Bash 前台返回、读后台输出文件）；第 84 行 Bash 工具的 `timeout`；第 85 行的后台读取；第 107 行的 receipt gate（Cursor 没有，见 `lanes-cursor.md` 的 "No receipt gate"）。
  - `SKILL.md:67-70` 的宿主指针改为按车道机制指路，词数约持平。
- (b2)（暂缓）失败路径单独成文件：把 `SKILL.md` 的 "Escalation — the ladder"（155 词）与 "Rework tickets"（53 词）移出。暂缓的原因：候选的读取时机"第一次验收失败"漏了 R4 的重大执行问题与契约缺口，这些入口理清之前不拆。
- 不建议：把 `SKILL.md` 的路由、契约、验收三节各拆成文件。多数触发技能的事件最后都要派发，派发同时用到这三节；拆出来就是体检·三所说"必须全部加载的薄壳"，总负担不降。

(c) 防止再膨胀：
- `plugin/skills/orchestration/` 下每个文件都设词数预算，取拆分后的实测值加少量余量，由测试强制（本仓部分见 RI2），取代 ADR 与工单里的人工核对。
- 分层规则（记入新 ADR，见 R15）：`SKILL.md` 收跨车道、跨宿主的共性规则；只属于一条车道或一个宿主的机制放进该车道的文件；测量样本、观测经过和维护待办放进 ADR 或任务件，不进随插件发布的文本。任一预算上调之前，先在 ADR 里写明考虑过哪些内容下沉、为什么不能下沉。

阅读路径估算（按节计数推得，不是实测）：

| 会话 | 现在 | (a) 加 (b1) 之后 |
|---|---|---|
| Claude Code，只派 claude 车道 | 约 7,090 词 | 约 3,870 词 |
| Claude Code，只用 runner | 约 7,090 词 | 约 5,730 词 |
| Claude Code，两类都用 | 约 7,090 词 | 约 6,410 词 |
| Cursor，使用 runner | 约 8,290 词 | 约 6,930 词 |
| Cursor，不用 runner | 约 4,630 词 | 约 4,390 词 |

(b2) 暂缓，不计入估算。

风险与约束（写进实施契约）：
- `lane-preamble.md` 与 `lane-preamble-report.md` 不移动：runner 按相对路径读取它们（`lanes-claude-code.md` 第 0 节），agent 文件写的是 `<plugin-root>/skills/orchestration/lane-preamble-report.md`。
- 决策类型门留在 `SKILL.md`：它约束任何主代理，技能可能只为一个决策点加载。
- `SKILL.md` 保留契约五部分与"报告是声明、不是证据"的一行锚点，跳读指针时仍有最低约束。拆分后指针可能被跳读（ADR 0012 已记这一风险），见 PS3。
- 每个新文件都要有中文孪生（R13），`tests/test_zh_mirror.py` 会检查。
- ADR 0012 决策 5（章节名 "User routing profile" 保留，因为仓外用户规则按名引用它）的前提需要复核：WSL 侧全局提示词只点名档案路径，没有这个章节名（2026-09-29 检索）；Windows 侧没有查。处理见 R15。
- 这是重构策略决定。按决策类型门先问 advisor；决策记录见 R15。
- 顺序：先落地 (a) 与其他 P 条目的文字修改，再做 (b)。(b) 只移动已经定稿的文字；验收时逐句比对，旧文件的每一句都恰好出现在一个新文件里。允许的例外只有三类：列明的删除、必要的宿主条件标注、指针改写。

验证：
- 机械检查：各文件词数不超过新预算；逐句比对脚本通过；`python3 tests/test_zh_mirror.py` 退出 0。
- 对照任务（依赖模型行为，留待修改阶段，在已安装的新版本上执行）：
  1. Claude Code 新会话，任务只需派一个 claude 车道 explorer。通过标准：转写显示读了 claude 车道文件，没有读 runner 文件。
  2. Claude Code 新会话，派一个 codex 车道 worker。通过标准：运行 runner 之前读了 runner 文件；收到 receipt 后按 receipt 验收。
  3. Cursor 新会话，经 Shell 派 codex 车道。通过标准：读了 runner 文件，没有读 Claude Code 的 claude 车道文件；按 Cursor 的条件等待（Shell 工具的时钟）并自行判读 receipt。
  4. 对照任务 2 与 3 合并判读：两个宿主各自读到本宿主的等待方式与门禁说明，没有照搬另一个宿主的机制。

产物类别：插件准则散文，走同模派发。本仓配套：R15（ADR）、RI2（预算测试）、R13（孪生）。

来历：新发现，椰椰 2026-09-29 补充议题。

#### P12（新）两个 runner 的 shortcut 注释带 ADR 编号

位置：`plugin/scripts/run-codex.mjs:785`、`plugin/scripts/run-grok.mjs:757`。

原文（两处相同的结尾）：

> … replace when: a report-mode lane writes under dirty_baseline true or when git is unavailable, or implement mode misreports because of pre-existing dirt twice (ADR 0018 / 0019 review conditions).

依据：第二部分的本仓内容标准（ADR 不随插件发布）；去冗·语义冗余（"无新增含义的括号限定"）。

证据状态：已核实。括号前的 "replace when" 已写完整的可观测触发条件，括号只指出条件的出处。

影响：随插件发布的代码带着安装者读不到的 ADR 编号。影响小：注释不进入代理上下文，只有读代码的人会看到。

最小修改：两处都删去 " (ADR 0018 / 0019 review conditions)"，shortcut 标记的三个字段保持完整。只改注释，不改行为。

产物类别：插件交付物（代码注释），经 `worker`。

来历：新发现。第一版把它列为保留项；GPT-6-Astra 第一轮指出保留与第二部分的边界标准冲突，改为发现。

验证：`grep -n "ADR" plugin/scripts/run-codex.mjs plugin/scripts/run-grok.mjs` 没有命中；`python3 tests/test_runner_contract.py` 退出 0。

### 2.2 单列：涉及安全、权限边界或减少验证的建议

#### PS1（S1）从准则删除插件级强度探针的待办（P04 的一部分）

- 原规则保护什么：确认插件级 agent 文件的 `low`、`xhigh` frontmatter 真的生效。ADR 0016 第 70 行把这两个值标为外推。
- 替代措施：工单 05 的 REL-4 计划用已安装插件逐个派发 Claude 拨盘，其中包含 `explorer-xh`、`worker-xh`、`advisor-xh`（xhigh）。工单 02 已证实子代理转写带 `effort` 字段，所以 xhigh 会被 REL-4 覆盖。`low` 只由 `advisor-l` 使用，不在 REL-4 里；若 O2 保留 `advisor-l`，REL-4 要补一次 `advisor-l` 派发。
- 建议：先由 R03 把探针写进工单 05 的验收清单，再从准则删除。不直接删除。

#### PS2（S2）删除 `advisor-xh` 对"正确性关键且无跨厂商读者"的自选（P01 的一部分）

- 原规则保护什么：同族 diff 属于正确性关键时，自动用最高强度的 Claude advisor。
- 改后：Tier 3 验收用哪个拨盘由档案决定。档案的验收形状默认是 `gpt-6-astra[low]`，属跨厂商；verdict 自报低置信度时升 `crux`。
- 失去的保护：codex 车道不可用、验收落到 Claude 候选时，不再自动用 xhigh。
- 替代选项：在档案的 "Advisor mapping" 加一条，例如"正确性关键的验收用 `crux`"。这是档案取值，由椰椰决定。

#### PS3（新，P11 的一部分）拆分后跳读指针的风险

- 原结构保护什么：`lanes-claude-code.md` 在首次派发前整篇必读，runner 的等待协议与 receipt 验收规则一定进入上下文。
- 拆分后：只读了 claude 车道文件就去运行 runner 的主代理，会漏掉等待协议与 receipt 验收规则。若采纳 (b2)，漏读失败路径文件的主代理可能按错误的梯级升级。
- 仍有的保护：Claude Code 的 receipt gate hook 在缺少 `complete` receipt 时阻止结束（机械门禁；Cursor 没有）；`SKILL.md` 保留契约五部分与"报告是声明、不是证据"的锚点。
- 建议：指针写成"第一次运行 runner 之前读"这类事件句；用 P11 的对照任务 2、3 验证；发现两次跳读，就按 ADR 0012 的复盘条件把关键句收回主文件。

### 2.3 单列：涉及功能逻辑、接口或测试覆盖的建议

#### PI1（I1）`advisor-l` 在档案里没有映射（已裁定：交给 O2）

- 证据（已核实）：`routing-profile.md:47` 只把 `[medium]`、`[high]`、`[xhigh]` 映射到 `advisor-md`、`advisor-h`、`advisor-xh`；三档 advisor 格都没有 Claude 的 `low` 候选。`advisor-l` 仍随插件发布，描述 "the cheap second reader for a bounded check — does this diff match its contract" 会招来档案外的使用。
- 方案 A（退役）：删 `plugin/agents/advisor-l.md`，修改插件内的引用 `lanes-claude-code.md:3`。公开的 agent 名减少，属不兼容改动，触发决策类型门。本仓的引用与版本处理见 RI3。
- 方案 B（保留为备用拨盘）：描述写 "serves any `low` advisor dial the routing profile names"，与 P01 的统一描述一致；并按 PS1 补一次 `low` 探针。
- 已知后果：6.0.0 发布后若 O2 决定退役，需要升到 7.0.0。

### 2.4 容易被误删的保留项

- `SKILL.md:76` 的 "no usage ratio"（不设使用比例）：这是椰椰确认的决定（规格用户故事 5、TR-2），不是会话残留。
- `lanes-claude-code.md:9` 的规则句 "Dispatch this role pool without `name`, or its whole point is gone."：P04 只删测量叙事，不删这条规则。
- 档案第 25 行的 `sonnet-5` 占位说明：临时状态，带失效条件。
- 档案第 43 行的 "currently `grok-4.7` (observed 2026-09-27)"：带日期的现行事实，日期是失效判断的锚点，对安装者有用。
- ~~`lanes-cursor.md:25` 的 "Not yet exercised in Cursor."~~：2026-09-29 随椰椰的更正整段删除，见 P02 的标注。
- `SKILL.md` 决策类型门的五项原文：工单 03 要求与基线逐字相同。

### 2.5 待椰椰裁定（第二部分）

1. P02 至 P07、P09、P10、P12：逐项确认。
2. P11：(a)、(b1)、(c) 分别是否采纳？建议全部采纳；(b2) 暂缓。
3. P11 的时点：并入 6.0.0（推送前落地），还是 6.0.0 推送之后作为 6.1.0 单独发布？"推送前落地"的裁定早于这个议题，需要重新决定。建议 6.1.0，理由有三：P11 只移动已经定稿的文字；它的对照任务要在已安装的新版本上跑；6.0.0 的发布清单已经很长。
4. PS2：是否在档案里加"正确性关键的验收"这一取值？
5. PS3：是否接受上述缓解措施？

---

## 执行顺序（跨两部分）

1. 先做核实：P03 的前言解析探针；若采纳 RI1，新测试先在现状上失败。
2. 前置协调件，主代理直接写，在插件批次之前完成：R03 把探针写进工单 05 REL-4（PS1 的替代措施）；R09 在本仓 `AGENTS.md` 写明同模派发的触发类别；R12 把档案的两条维护规则迁进 `AGENTS.md`。
3. 第一批，插件准则散文，走同模派发并按 Tier 3 验收：P01 至 P10，以及 R13 的对应孪生。P09、P10 的派发方式取决于 R09 对档案类别的裁定。`SKILL.md` 净减约 41 词（2206 降到约 2165）。
4. 第二批，经 `worker`：本仓的 R01，R02、R03、R08 的 README 部分，RI1 的测试，`.gitignore`（U5）；插件的 P12（代码注释）。
5. 其余协调件由主代理直接写：R04 的 `CONTEXT.md` 部分、R05、R06、R07、R10、R11、R14。
6. P11 若采纳：先按决策类型门问 advisor 并记 ADR（R15），再在第一批之后单独成批；RI2 的预算测试随预算定稿一起实施；时点按 2.5 第 3 项的裁定。
7. 工单 05 的授权步骤（推送、两侧更新、RS2 的安装器、RS3 的一次性删除）排在 R01 之后。
8. 未跟踪产出按 RS4、RS5 的答复处置。

## 本轮另行处理的改动：移除伴生安装器对旧版游离文件的处理

这一节记录椰椰 2026-09-29 单独要求的改动，不属于审查发现。

- 位置：`plugin/**` 里没有这类处理。处理逻辑在本仓的伴生安装器 `scripts/install-user-level.py`（`RETIRE` 清单与 `process_retire`），以及它的测试和文档。
- 现状（2026-09-29 只读检查）：两侧旧规则文件已不存在，只剩两份路由档案活体；已安装的 5.2.0 与两侧全局提示词仍在使用它们。
- 范围：
  - 本仓交付物，经 `worker`：`scripts/install-user-level.py`；`tests/test_install_user_level.py`；`README.md:51`，以及 `README.md:126` 的 v6.0.0 一句；`docs/manuals/6.0.0.html` 的伴生安装器一节与升级步骤。
  - 协调件，主代理直接写：`AGENTS.md:25`；`CONTEXT.md:144`；ADR 0023 决策 3、6；ADR 0018 的状态行（决策 5 的退役清单）；工单 06；工单 05 第 29 行；规格 REL-3。
- 一次性删除：见 RS3，排在工单 05 的迁移步骤里，需椰椰当次授权。
- 进度：已实施并验收（2026-09-29）。worker 用 Claude 模型（`sonnet`）；GPT-6-Astra 的 Tier 3 验收经一次返工后通过。记录见工单 06 的 Comments。一次性删除仍按 RS3 等待授权。

## 与 GPT-6-Astra 的对齐

通道：已安装 5.2.0 插件的 codex runner，报告模式。型号 `gpt-6-astra` 由椰椰指定；强度 `medium` 取自现行路由档案的决策形状（`standard` 格）。receipt 里的型号与强度是提交值，不是观测值。

第一轮（2026-09-29，三个请求并行）：

| 范围 | 会话 | 结论 | 处置 |
|---|---|---|---|
| 〇与第一部分 | `01a0eb15-cdae-7be1-8285-c83d46c57e29` | 修改后同意，置信度中，7 点 | 全部采纳：边界依据改引 `marketplace.json`；R05 补入口同步；R10 改为"至少 16 处"；R13 补 P11 的删节与指针；R14 补三行并原地修正第 480 行；执行顺序把 R03、R09、R12 提前，RI2 随 P11；第 7 点（`plugin/**` 不在第一部分的读取范围）在第二轮补入范围 |
| 第二部分与 P11 | `01a0eb15-d32e-7f03-9838-3c119328750b` | 修改后同意，置信度高，9 点 | 全部采纳：P01 改为"绕过档案映射"；P02、R02 按档案第 59 行写；P04 新文本去掉观测经过；P09 保留重启句；P10 改为 125 词；P11 按内容拆并标明宿主机制，(b2) 暂缓，分层规则改写，新 ADR 移到 R15；PI1 的本仓引用移到 RI3；shortcut 注释从保留项改为发现 P12 |
| 游离文件改动计划 | `01a0eb15-d848-7d73-9f98-82a7af53cb68` | 修改后同意，置信度高，5 点 | 全部采纳，见工单 06 的 Comments |

第二轮（2026-09-29，续接上面三个会话）：

| 范围 | 结论 | 处置 |
|---|---|---|
| 〇与第一部分 | 修改后同意，置信度高，2 点 | 全部采纳：R10 的已有反向指针改为 7 处；RI3 补中文孪生的删除与镜像测试 |
| 第二部分与 P11 | 修改后同意，置信度高，2 点；P12 成立；P11 的总体策略可以定案 | 全部采纳：P04 不把单次观测写成必然行为（R03 的 README 文本同步）；P11 的宿主专属机制留在 runner 文件里按宿主分节，逐句比对允许宿主条件标注与指针改写，对照任务补"两个宿主各自读到本宿主约束"的判读 |
| 游离文件改动计划 | 修改后同意，置信度高，1 点；只覆盖协调件，交付物另行验收 | 采纳：ADR 0023 决策 6 的顺序改为与工单 06 D5 一致 |

第三轮（2026-09-29，续接同一组会话，只核对第二轮的处置）：

| 范围 | 结论 |
|---|---|
| 〇与第一部分 | 同意，置信度高。R10、RI3、R03 三处修改到位；限定范围内没有必须修改的问题 |
| 第二部分与 P11 | 同意，置信度高。P04、P11 两处到位；重构策略可以定案；实施后的加载行为仍待 P11 所列对照任务验证 |
| 游离文件改动计划 | 同意，置信度高。ADR 0023 决策 6、工单 06 D5 与工单 05 第 29 行的顺序一致；说明书属并行修改，交付后另行核对 |

结论：本文件第二版与 GPT-6-Astra 已沟通一致（2026-09-29）。这只确认清单与方案文本；各条目仍按"待椰椰裁定"逐项确认后实施。

## Comments

### 2026-09-27 — 椰椰的四项裁定

（本条用第一版编号，对照见"〇、阅读说明"。）

- 修复时机：推送前落地。本清单批准的修复在工单 05 推送 6.0.0、运行安装器之前完成，随 6.0.0 一起发布。F01 必须先于工单 05 的安装器。
- F02：九个 agent 文件现在一起改，不等 O2。`advisor-l` 的描述也按统一写法修改，去掉替档案选拨盘的句子；它退役与否仍由 O2 决定。
- I1：`advisor-l` 交给 O2。因此 F01 的 pin 规则枚举保留 `advisor-l`；S1 中 `low` 强度探针的去留也随 O2 决定。已知后果：6.0.0 发布后若 O2 决定退役，需要升到 7.0.0。
- F09：选方案 C。`SKILL.md:40` 保留机制句与两个宿主的做法，第二句换成指向 `AGENTS.md` 的一句（减 19 词）；`AGENTS.md` 写明触发类别；删去档案第 67 行；ADR 0013 追记一行。

其余条目（F03 至 F08、F10、S1 至 S6、I2、U1 至 U6）等待逐项答复。

### 2026-09-29 — 椰椰的新要求

- 审查文档分成两部分：本仓库自身内容；发布到外面去的插件内容。插件部分不混入本仓内容。本文件第二版按此重排。
- 文档调整完成后，先与 GPT-6-Astra 沟通一致，才能开始修改。
- 单独改动：移除对旧版本游离文档（如 `fable-advisor-routing.md`）的处理。理由：这些文档只在本机存在，一次性删掉后不会再出现，不需要维护处理逻辑。见"本轮另行处理的改动"。
- 补充议题：`SKILL.md`、`lanes-claude-code.md` 单个文件过重，而且每次迭代都在膨胀，词数上限已经上调多次；按渐进式加载的需要精简与拆分。收为 P11。
- 对 F09 的疑问已在"〇、阅读说明"里分开写明两个 `AGENTS.md`。

### 2026-09-29 — 与 GPT-6-Astra 沟通一致

三轮咨询，三个范围各用一个会话续接。第一、二轮都是"修改后同意"，意见全部采纳；第三轮三份都是"同意"，置信度高。过程与处置见"与 GPT-6-Astra 的对齐"。按椰椰的要求，沟通一致是开始修改的前提，不代表各条目已获批准；各条目仍等椰椰逐项确认。

### 2026-09-29 — 椰椰：按建议执行，不再逐项询问

椰椰要求按本清单的建议直接实施，中途不再询问。各待裁定项的处置如下。提交、推送、两侧更新、运行安装器与仓外删除仍是授权关口，本轮做到关口之前为止。

第一部分（§1.6）：
1. R01 至 R08、R11 至 R14：采纳，按各条"最小修改"实施。R15 随 P11。
2. R05：终态用 `resolved`。逐个核实工作已落地并验收后，才改对应的状态行。
3. R09：路由档案不属于同模派发的类别。
4. R10：方案 B。完整的修订关系清单先由 explorer 逐份确认。
5. RS1：采纳。RS4：删除两个 `__pycache__/`，并在 `.gitignore` 加 `__pycache__/`；U1、U3、U4 原地保留、不暂存，移除列入授权清单。RS5：不提交 `ONBOARDING.md`。RS2、RS3：按工单 05、06 另行授权。
6. RI1：新增。RI2：随 P11。RI3：随 O2 专题。
7. README "Go deeper" 段：清单没有建议，本轮不动，保持待裁定。

第二部分（§2.5）：
1. P02 至 P07、P09、P10、P12：采纳。P08 的档案一半（删去 `routing-profile.md:67`）并入 P09、P10 的档案契约，避免与 `SKILL.md` 批次共用文件。
2. P11：采纳 (a)、(b1)、(c)；(b2) 暂缓。(a) 就是 P02、P04、P06、P08、P09、P10，随本批落地。
3. P11 的时点：6.0.0 推送之后，作为 6.1.0。本轮只做协调部分：决策类型门咨询、R15 的 ADR（`proposed`）、P11 的实施契约。
4. PS2：档案取值由椰椰声明，本轮不加，保持待裁定。
5. PS3：接受所列缓解措施。

执行方式：工作树有未提交改动，codex 与 grok 车道的实施模式要求干净工作树，所以交付物全部走 claude 车道的 worker。准则散文用同模派发；其余交付物用普通 worker。同族 diff 的 Tier 3 验收用 GPT-6-Astra 的报告模式。

### 2026-09-29 — 椰椰更正：Cursor 下 Grok 是本家模型

- 椰椰原话："cursor里不会跑grok runner，grok是cursor的本家模型"。
- 影响：P02、R02 的修改方向被推翻。审查清单原以档案第 59 行为准，实际写错的是档案。处置：
  - `SKILL.md:60` 与 README 第 26、92 行恢复原文；`lanes-cursor.md:3` 恢复 Grok 为原生车道。
  - `lanes-cursor.md` 删去 grok runner 经 Shell 一段，§2.4 的对应保留项随之取消。
  - 档案 "Cursor candidates" 的调用入口句改为 Grok 经钉型号的 `Task`，声明日期改为 2026-09-29。
  - 工单 05 不再加 Cursor 实跑一项。
  - `docs/manuals/6.0.0.html` 的对应段落与已知限制一行另派 worker 修改。
  - 决定记为 ADR 0025，它取代 ADR 0018 决策 9 的 grok runner 部分；ADR 0018 状态行已补反向指针。

### 2026-09-29 — 椰椰声明：`sonnet` 已更新到 Sonnet 5.5

- 中文档案上午的修改就是新取值。英文档案已同步：锚定型号与两处排名改为 `sonnet-5-5`，删去占位说明，两个 explorer `crux` 格为 `sonnet-5-5[medium*, high]`。
- Claude Code 没有 `medium` 强度的 explorer 文件，档案的映射行写明 `sonnet-5-5[medium]` 经 `explorer-h` 以 `high` 运行。是否新增 `explorer-md`，待椰椰决定。
- 说明书第 550、679 行同步。

### 2026-09-29 — 实施记录（主代理）

已落地（工作树，未暂存、未提交）：

- 协调件，主代理直接写：
  - R05：`triage-labels.md` 加终态 `resolved`；逐个核实后，10 个已发布任务件的状态行改为 `resolved`。
  - R06、R09、R12、RS1：`AGENTS.md`。
  - R04、R07、R11：`CONTEXT.md` 的对应行；grok lane 词条按 ADR 0025 改写。
  - R03：工单 05 REL-4 补插件级 `xhigh`、`low` 探针。
  - R14：规格第 480 行与 Comments。
  - R10：`docs/agents/domain.md` 加回写规则；14 份被修订的 ADR 状态行补反向指针。修订关系清单由 grok 车道 explorer 逐份读出（会话 `478d2179-8075-466e-b4ce-43dea778e981`），主代理抽查 5 条引文属实。
  - ADR 0013 追记（R09）；新 ADR 0025（Cursor 下 Grok）；ADR 0018 状态行补反向指针。
- 交付物，经 claude 车道 worker（工作树不干净，CLI 车道的实施模式不可用）：
  - 准则散文用同模派发（`worker-h` 配 `opus`）：P01、P03、P04、P05、P06、P07、P08 的 `SKILL.md` 一半，以及 R04、R13 的孪生。
  - 普通 worker（`worker-h` 配 `sonnet`）：档案 P08 的另一半、P09、P10；R01、RI1、R03 与 R08 的 README 部分、P12、U5；`docs/manuals/6.0.0.html` 与本批对齐。
- P03 先验证再修改：`explorer-h` 配 `haiku` 三次派发。提示词不带路径、只带 "Preamble: <路径>" 标签时，都没有读前言；以祈使句"先读 <绝对路径>"开头时读了。插件文本因此写成"以读前言的指令开头，只给路径标签不够"，Cursor 的 Invocation 一条同样改写（Cursor 下未实测）。
- 词数：`SKILL.md` 2206 降到 2160；`lanes-claude-code.md` 3661 降到 3271；`lanes-cursor.md` 1202 降到 1181；档案 1224 降到约 990。

验收：

- 每批按 Tier 1 核对 worker 的检查证据，主代理亲读档案与三份技能文件的 diff。
- Tier 3：GPT-6-Astra 报告模式，`low`（会话 `01a0ebdd-4bcf-7fd1-b29b-c733d6b4cfa0`，已提交，未观测）。结论为返工，两点：
  - `lanes-claude-code.md:3` 的指代歧义：返工后复核通过。
  - 中英档案不一致：起因是椰椰上午在中文档案写入的 Sonnet 5.5 取值，按椰椰声明同步英文后消除。
- 没有经过 Tier 3 的部分：`docs/manuals/6.0.0.html` 的全部改动（约 +50/−38 行，包括删去两行已知限制、改写 ADR 0022 与 2110→2160 两张历史卡片、第 441 行点名本仓的类别路径），以及档案的 Sonnet 增量。这些只有 worker 的自查证据（Tier 1），说明书 diff 主代理没有亲读。椰椰要求停止额外测试，本轮不再补做，属遗留风险。
- 测试（工作树）：`test_runner_contract` 19/19、`test_runner_lifecycle` 退出 0、`test_zh_mirror` 16/16、`test_receipt_gate` 8/8、`test_install_user_level` 8/8；`git diff --check` 干净。`test_lane_family_gate` 16/18、`test_user_level_archive` 3/5，失败项都是两侧 pin 规则活体仍为旧文本，要等工单 05 运行安装器后才能通过。

P11（6.1.0）的准备：

- ADR 0024（`proposed`）已写。
- 决策类型门：GPT-6-Astra `medium`（会话 `01a0ebd5-96f6-7043-8208-bd3449f63943`），结论为修改后接受，置信度高；五点意见已并入 ADR 0024 与 `p11-contract.md`。

未做与待定：

- 授权关口：提交与推送 6.0.0、两侧更新、RS2 安装器、RS3 一次性删除、U1/U3/U4 的移除。
- 椰椰的取值或决定：PS2（正确性关键的验收拨盘）、README "Go deeper" 段、PI1/RI3（O2 专题）、是否新增 `explorer-md`。
- 依赖模型行为的对照任务：P01 两项、P11 四项。
