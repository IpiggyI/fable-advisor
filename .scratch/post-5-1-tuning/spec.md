# 5.1.0 后续调整：报告模式脏基线、车道标题、伴生安装器、首轮池与 senior 门

Status: ready-for-agent

日期：2026-09-16。目标版本 5.2.0（runner 契约与 doctrine 语义均向后兼容，minor）。前置条件：工作树里未提交的 5.1.0 先提交、推送并在两侧安装；该步骤需用户单独授权，不属本 spec。词表见 `CONTEXT.md`（本轮已加：首轮档位、拨盘新记法、cursor lane、正典 / 活体、伴生安装器、升级梯）。

## Problem Statement

椰椰在 5.1.0 的使用中遇到四件事：

1. **只读调查被工作树拦住。** 让 grok lane 或 codex lane 以报告模式派一个 explorer 时，只要工作树有未提交改动，主代理就拒绝，理由是 runner 会把非空工作树判成 `unexpected_diff`，于是降级到 claude lane 的内置 explorer，丢掉跨厂商复核。一次只读调查不应该要求先 stash。
2. **车道会话分不清。** codex 与 grok 的会话列表按 prompt 首行显示，而每条车道的 prompt 都以同一段前言开头（"**Posture.** You own the deliverables…"），列表里全是同一句话。
3. **用户级文件靠手抄。** 路由档案、Cursor pin 规则、Cursor 门禁脚本的正典在本仓，另有两份旧规则的编辑源在 prompts 仓库；活体全靠人从仓库拷到 `~/.claude/`、`~/.cursor/`。两侧活体已经落后：旧规则里还写着 "advisor (default senior)"，仍在给主代理下指令。
4. **主代理"杀鸡用牛刀"。** 它频繁把任务派给 Fable 与 Astra。原因不全在模型：档案写了 advisor 默认 senior、角色默认 effort；doctrine 允许按判断首轮直派 senior；模型本身不具备判断其他模型能力的能力。椰椰不想把这个决定留给模型，要在档案里写死，并且档案要能随时调整。

## Solution

1. runner 开跑前记一次工作树是否已脏（`dirty_baseline`）；报告模式且开跑前已脏时不再判 `unexpected_diff`，只读沙箱是唯一防线。implement 模式不变。
2. spec 新增可选键 `title`；prompt 首行是这句标题，缺省用 slug；旧的 `[fable-advisor] <slug>` 行退役。同批完成工单 10：报告模式前置只读的报告前言，不再前置 worker 前言。
3. 新增**伴生安装器**：仓库检出内的一个脚本，把三件正典覆盖到指定家目录的活体，并删除清单里已退役的旧规则；`--check` 供测试与自检。正典位置不变，不进 `plugin/`，不挂插件 hook。
4. doctrine 与档案分工：doctrine 只保留机制——light 与 standard 是首轮池、两档自由选、senior 只经升级梯的门或用户声明到达、新记法 `model[a*, b, c]`、升级梯 R1–R4；档案承载全部取值，先按椰椰 2026-09-16 的表写出，之后椰椰改格即生效。codex 白名单加回 `gpt-5.6-sol`，为 gpt-6-sol 铺路。

## User Stories

1. 作为主代理，我想在工作树有未提交改动时仍能以报告模式派 grok / codex 的 explorer，以便只读调查不被工作树状态拦住。
2. 作为主代理，我想在 receipt 里看到 `dirty_baseline`，以便在披露里说明这次报告模式的脏检测被跳过。
3. 作为架构师，我想 implement 模式的 `no_diff` 与 `unexpected_diff` 语义保持不变，以便已有的验收习惯不用改。
4. 作为椰椰，我想在 codex 与 grok 的会话列表里一眼认出每条车道在做什么，以便回看与 resume 时不用逐个打开。
5. 作为架构师，我想在 spec 里写一句 `title`，以便车道会话首行是这句话。
6. 作为架构师，我想 `title` 可省略、省略时首行是 slug，以便旧 spec 不用改就能跑。
7. 作为报告模式的车道，我想读到一份只读的报告前言，而不是要求我持有 Files、以 `WORKER REPORT` 结尾的 worker 前言，以便前言不自相矛盾。
8. 作为架构师，我想 runner 在任一前言文件缺失时不 spawn 且退出非零，以便执行侧契约不会静默丢失。
9. 作为椰椰，我想在插件更新后跑一条命令就把三件用户级文件覆盖到活体，以便不再手抄。
10. 作为椰椰，我想安装器默认只写当前用户的家目录，并能用参数多指一个家目录，以便同一命令在本机一次写 WSL 与 Windows 两侧、在别的机器只写一侧。
11. 作为椰椰，我想安装器删除两份已退役的旧规则活体，以便旧填充表不再影响主代理。
12. 作为椰椰，我想安装器覆盖时不做新旧裁决、不留 `.bak`，以便活体永远等于正典。
13. 作为椰椰，我想安装器只检测 `~/.cursor/hooks.json` 里有没有门禁条目并在缺失时警告，以便它不改我分叉过的 hooks 配置。
14. 作为椰椰，我想用可选参数把同一批文件写到 prompts 仓库的备份目录，以便备份不用另一套流程。
15. 作为仓库维护者，我想漂移测试直接调用安装器的 `--check`，以便测试与安装器的比对逻辑只有一份。
16. 作为仓库维护者，我想 prompts 仓库退出漂移测试，以便备份缺席或落后不使测试失败。
17. 作为主代理，我想 doctrine 明确 light 与 standard 之间自由选择、senior 只经门到达，以便我不再凭判断首轮直派 senior。
18. 作为主代理，我想 doctrine 用四条规则写清返工、提升、换型号与升档的顺序，以便同一问题不会在同一型号上连升三次 effort。
19. 作为主代理，我想 senior 的门与决策类型门的"同一问题两次失败"重合，以便到门口时 advisor 的 verdict 顺带裁定是否上 senior。
20. 作为椰椰，我想档案里每格的拨盘用 `model[a*, b, c]` 写出、`*` 标默认，以便主代理默认选便宜档、又能在格内按需选更高 effort。
21. 作为椰椰，我想改一个格子、跑一次安装器就完成调整，不改 doctrine、不改插件，以便档案支持随时调整。
22. 作为椰椰，我想档案记录基准数据与声明日期，以便日后重估时知道当时依据。
23. 作为主代理，我想 Cursor 表按机制映射：GPT 行经 codex runner、grok 的 medium / high 经 grok runner、Claude 行只取 allowlist 有的 slug、composer 在 explorer @ light 首位，以便 Cursor 侧不再退回 "`explore` inherit"。
24. 作为主代理，我想 doctrine 给 Cursor 自家模型一个车道名（cursor lane），以便披露时不把 composer 算进 claude lane。
25. 作为架构师，我想 codex 白名单接受 `gpt-5.6-sol` 且默认 `high`，以便按档案派 sol 不会 `spec_invalid`。
26. 作为架构师，我想 sol 请求失败时不静默换成 luna，以便我点名的型号只在 receipt 里以失败出现，不被替换。
27. 作为仓库维护者，我想每个改动的运行时 Markdown 在同一提交里更新中文孪生，以便 `test_zh_mirror` 持续通过。
28. 作为仓库维护者，我想 `SKILL.md` 词数不超过 1960，以便 ADR 0012 / 0015 的预算不被这次增句突破。
29. 作为仓库维护者，我想一份 ADR 记下这批决定并标注对 ADR 0011、0014 决策 11、0015 决策 4 的修订，以便未来读者知道为什么。
30. 作为椰椰，我想 README 的升级段说明 5.2.0 新增的 spec 键、receipt 字段与安装器，以便更新后知道要多跑哪一步。
31. 作为椰椰，我想从 5.2.0 起每个版本都有一份 HTML 版本说明书，写清这个版本的完整行为和相对上一版本的改动点，以便不用翻 ADR 与 diff 就知道装上的是什么。
32. 作为椰椰，我想版本说明书的样式与 `outputs/` 里现有的 show-me HTML 相近（自包含、中文、分节、表格），以便阅读体验一致。

## Implementation Decisions

### runner 契约（两条 runner 同改）

1. **脏基线。** runner 在 spawn CLI 之前跑一次 `git status --porcelain`，非空即 `dirty_baseline: true`，两条 runner、两种模式都在 receipt 里记这个布尔字段；开跑前 `git status` 本身失败时记 `null` 并继续。报告模式下 `dirty_baseline: true` 时不判 `unexpected_diff`；`empty_report` 与 `complete` 的判定不变；`changed_files` 照常记录运行后观察到的路径。implement 模式的 `no_diff`、`git_status_failed` 语义不变。运行后 `git status` 失败仍是 `git_status_failed`。
2. **标题。** spec 新增可选顶层键 `title`：非空字符串，其他类型或空串记 `spec_invalid`。prompt 第一行是标题原文（纯文本，不加 Markdown 标记），空一行，再前言，再五部。省略 `title` 时第一行是 slug。`[fable-advisor] <slug>` 行退役。receipt 不新增字段。
3. **前言按 `mode` 分流（工单 10 并入）。** implement 模式前置现有 worker 前言；报告模式前置一份新的报告前言：只读、Files 是读取范围不是写权限、回答 Objective、以证据（explorer）或 verdict（advisor）形状结尾，不含 `WORKER REPORT`。runner 内联的 report-mode overlay 文本删除。任一模式所需前言文件缺失即退出非零、不 spawn。报告前言与 worker 前言同目录，二者都是执行侧契约的单源。
4. **sol 回白名单。** codex 白名单加 `gpt-5.6-sol`，默认 effort `high`。启动前回退只保留 astra → luna；sol 与 luna 一样不回退。修订 ADR 0014 决策 11。gpt-6-sol 发布后只改型号名。

### 伴生安装器

5. **形态。** 仓库检出内的一个 Python 脚本（两侧都有 python，插件 hook 已依赖它）。它不进 `plugin/`，不作为插件 hook 运行；用户在每侧插件更新后手动运行一次。这是新增交付物类别，`AGENTS.md` 的产物类别表加一行。
6. **清单。** 三件正典 → 活体：路由档案 → `~/.claude/docs/`；Cursor pin 规则 → `~/.cursor/rules/`；Cursor 门禁脚本 → `~/.cursor/hooks/`。`retire` 列表：`~/.claude/rules/fable-advisor.md`、`~/.cursor/rules/fable-advisor.mdc`，存在即删除。正典位置不变（`docs/agents/`、`cursor-hooks/`）。中文备份不安装。
7. **参数。** 默认家目录为当前用户；`--home <目录>` 可重复，逐个写入；`--check` 只比对不写，任一活体缺失或字节不同即退出非零并列出；`--also <目录>` 把同一批英文正典写到指定备份目录（prompts 仓库的快照用法）。
8. **策略。** 无条件覆盖，不比较新旧，不留 `.bak`。`~/.cursor/hooks.json`：只检测 `preToolUse` 里是否有指向门禁脚本的条目，缺失或文件不存在时打印警告，不修改。输出每个目标的动作（installed / unchanged / removed / warning）。
9. **测试与文档。** `test_user_level_archive.py` 的活体比对改为调用 `--check`（每个存在的家目录各一次），prompts 副本退出比对；中文孪生存在性检查保留。`plugin-release.md` 在两侧更新步骤后加"跑安装器"一步并给出本机双家目录的命令；`cursor-lane-gate.md` 与 `AGENTS.md` 的"手动拷贝"改为"跑安装器"。修订 ADR 0011（活体不再手动拷；权威副本位置不变）。

### doctrine（技能正文）

10. **首轮池与 senior 门。** Stage 1 改为：档位在 light 与 standard 之间按判断自由选择，无前置条件；senior 只经升级梯的门或用户声明到达。删除"a lot, with costly mistakes → senior, or a race of two fills"一句作为词数抵扣（竞赛条款保留在 Parallelism 段）。
11. **升级梯。** Escalation 段改写为四条：R1 返工票（同会话、同拨盘）；R2 提升（返工失败且归因能力：新会话 + 接管包；一次提升是同型号升 effort 或换型号）；R3 同型号只提升一次（例外：更高各格没有别的型号）；R4 执行时出现较大问题可跳过返工票直接换型号，记一次失败。senior 的门：首轮池内两次能力归因的失败，或用户声明；与决策类型门"同一问题两次失败"重合，advisor 的 verdict 顺带裁定。契约缺口的路径（修正契约、同车道会话）不变。
12. **记法。** `dial` 定义改为 `model[a*, b, c]`：格内该型号可选的 effort，全部首轮可选，`*` 标默认；无 effort 维度的型号裸写。`|`（仅升级）记法退役。修订 ADR 0015 决策 4。
13. **角色默认 effort 句删除。** 每格显式写 effort 后，"worker medium / explorer medium / advisor high"的默认句退役。
14. **词数。** `SKILL.md` 改后不超过 1960 词；新增句由第 10、13 条的删除抵扣。
15. **Claude Code 车道文档。** 报告模式段加 `dirty_baseline` 语义与前言分流；spec 字段列表加 `title`；"先干净再派"限定为 implement 模式；白名单加 sol、回退范围注明。
16. **Cursor 车道文档。** 加 cursor lane：Cursor 家族的 pin 是 cursor lane，只在 Cursor 宿主存在；加 grok runner 经 Shell 可用（机制同 codex runner，标注未在 Cursor 实跑）。不加 Task 派发标题句（`description` 已是 UI 名）。
17. **中文孪生。** 改动的每个运行时 Markdown 与新增的报告前言在同一提交更新 `docs/zh/` 孪生。

### 路由档案（先写，椰椰之后随时改）

18. **结构。** 声明日期与锚定模型 → 首轮池说明（前两列自由选，第三列有门）→ Claude Code 表 → Cursor 表 → 升级梯引用（指向技能，不复述）→ Resource preferences（含基准数据）→ 调整方法（改格、跑安装器；技能在档案变化时重读，不改 doctrine 不改插件）。
19. **Claude Code 表初值**（椰椰 2026-09-16 声明；候选顺序 = 车道默认顺序 grok › codex › claude，specialty 只作平手裁决）：

    | 角色 \ 档位 | light | standard | senior |
    |---|---|---|---|
    | explorer | grok-4.6[medium] › gpt-5.6-luna[high] › haiku-4-5 | grok-4.6[xhigh] › gpt-5.6-luna[max] › sonnet-5[high*, xhigh] | gpt-5.6-sol[high*, xhigh] › opus-5[high*, xhigh] |
    | worker | grok-4.6[medium*, high] › gpt-5.6-luna[xhigh] › sonnet-5[high] | grok-4.6[xhigh] › gpt-5.6-sol[high*, xhigh] › gpt-6-astra[low] › opus-5[high*, xhigh] | gpt-6-astra[medium*, high] |
    | advisor | gpt-6-astra[low] › fable-5-1[low] | gpt-6-astra[medium] › fable-5-1[medium] | gpt-6-astra[high*, xhigh] › fable-5-1[high*, xhigh] |

    advisor 的默认格：决策形状用 standard，验收形状用 light；升到 senior 只在 verdict 自报低置信或用户声明时。claude 车道的每个拨盘对应现有 agent 文件（explorer-h/xh、worker-md/h/xh、advisor-l/md/h/xh），haiku 无 effort 维度。
20. **Cursor 表。** 按机制映射同一份取值：GPT 行全部经 codex runner（Shell，报告模式或实现模式）；grok 的 medium / high 经 grok runner（Shell）、xhigh 可用 allowlist 的 grok slug 钉 Task；Claude 行只取本轮 allowlist 里有的 slug 变体（当前 opus-5 只有 high、fable 只有 xhigh，因此 fable 只出现在 senior 格，standard 的 advisor 首选 astra[medium] 经 codex runner）；explorer @ light 首位是 composer-2.5-fast 经 `explore`（cursor lane），其后 grok-4.6[medium]、luna[high]；allowlist 缺席的 slug 跳过并在披露里说明。表内写明 Cursor slug 来自本轮 allowlist，不持久化可能过期的 slug。
21. **Resource preferences。** 保留现有速度 / 价格 / 能力 / specialty 四条与两条声明规则；新增 2026-09-16 声明的依据：不同型号间的能力差距大于同型号不同 effort 之间的差距（同一测试集：opus-5[high] 73%±2%，opus-5[medium] 69%±1%，sonnet-5[high] 48%±5%，sonnet-5[medium] 40%±3%）。
22. **中文备份**同步改写，仍不安装。

### 词表、ADR、版本

23. `CONTEXT.md` 新词条已写入（本轮）：首轮档位、拨盘新记法、cursor lane、正典 / 活体、伴生安装器、升级梯。
24. 新 ADR 0018 一份，分条记以上决定，并标注修订：ADR 0011（活体安装方式）、ADR 0014 决策 11（sol）、ADR 0015 决策 4（`|` 记法退役）。
25. 版本 5.2.0：两处版本字段；README 升级段写明新增的 spec 键 `title`、receipt 字段 `dirty_baseline`、sol 白名单、报告前言、伴生安装器。

### 版本说明书（从 5.2.0 起每版一份）

26. **形态。** 一个自包含的中文 HTML 文件，样式与 `outputs/` 里现有的 show-me 文件相近：内联样式、`lang="zh-CN"`、编号的二级标题、表格与要点框。手写，不生成。
27. **位置与类别。** 进仓库、随版本号命名，放在专门的说明书目录下（不放 `outputs/`，那是本机未跟踪的产物目录）。属交付物（对用户描述行为），编排姿态下经 worker 写；`AGENTS.md` 的产物类别表加这一类。不进 `plugin/`，不随插件发布。
28. **内容两部分。** 第一部分是本版本的完整说明：角色 / 档位 / 车道 / 姿态、runner 的 spec 键与 receipt 字段与错误类、doctrine 要点（首轮池、升级梯、决策类型门、验证三层）、用户级文件与伴生安装器的用法、测试清单。第二部分是相对上一版本的改动点：逐条写改了什么、为什么、对应的 ADR 与工单。5.2.0 的上一版本是 5.1.0。
29. **发布流程。** `plugin-release.md` 在版本号 bump 之前加一步"写本版说明书"；说明书完成是发布票的前置条件。

## Testing Decisions

好测试只看外部行为：runner 的行为在进程边界看（假 CLI、假 git、真实 spec 文件、真实 receipt），安装器的行为在命令行边界看（临时家目录、真实文件），不看内部函数。

- **runner：沿用 `test_runner_contract.py` 的假 CLI / 假 git 模式**，新增用例：
  - 报告模式 + 开跑前已脏 + CLI 不写 → `complete` 且 `dirty_baseline: true`；报告模式 + 开跑前干净 + CLI 写文件 → `unexpected_diff` 且 `dirty_baseline: false`；implement 模式 + 已脏 → 行为与今天一致。假 git 需区分开跑前与运行后两次调用（计数或状态文件）。
  - `title` 给出 → prompt 首行等于它、第二行为空、之后是前言；省略 → 首行是 slug；prompt 里不再出现 `[fable-advisor]`；`title` 为空串或非字符串 → `spec_invalid` 且不 spawn。
  - 报告模式 prompt 含报告前言、不含 `WORKER REPORT`；implement 模式 prompt 含 worker 前言、不变；报告前言缺失 → 退出非零、不 spawn、stderr 指名文件。
  - `model: gpt-5.6-sol` 省略 effort → 提交 `high`；sol 在建立会话前失败 → 不回退、`model_used` 仍是 sol。
- **安装器：新测试在命令行边界**，用临时目录当家目录：空家目录安装 → 三件活体与正典逐字节一致、输出 installed；改动一份活体后 `--check` → 非零并列出该文件，再安装 → 覆盖、输出 installed；`retire` 路径预置文件 → 被删除、输出 removed；`--also` → 备份目录得到同一批英文文件；`hooks.json` 不存在或无门禁条目 → 输出 warning、退出 0；两个 `--home` → 两处都写。
- **漂移测试** `test_user_level_archive.py`：活体比对改为调用 `--check`；中文孪生存在性检查保留；prompts 路径删除。
- **既有测试不变**：`test_zh_mirror.py`（新报告前言的孪生须存在）、`test_lane_family_gate.py`、`test_receipt_gate.py`。
- **文本检查**：`SKILL.md` 词数 ≤ 1960（`wc -w`）；退役短语在 `plugin/`、`README.md`、`docs/zh/` 零命中：`[fable-advisor] `、`escalation-only`、`first-round options |`、`default senior`、`role default`。
- **行为验证（装上 5.2.0 之后）**：在有未提交改动的工作树上以报告模式派一次 grok explorer，receipt `complete`、`dirty_baseline: true`；codex / grok 会话列表首行显示标题；两侧跑安装器后 `--check` 通过、两份旧规则活体消失。

## Out of Scope

- 内容哈希基线（运行前后逐文件比对、`changed_files` 取差集）：未选；implement 模式仍要求干净工作树。
- 插件 `SessionStart` hook 自动安装、Cursor 原生伴生插件、脚本修改 `~/.cursor/hooks.json`。
- 全局提示词与 prompts 仓库里两行入口版规则的内容；prompts 仓库只作备份目录。
- receipt gate、handoff lane、Cursor pin 门禁脚本的规则本身。
- Cursor Task 派发的标题句（`description` 已存在）。
- 核实 `gpt-5.6-sol` 在椰椰的 Codex 计划里仍可调用；核实 Cursor 是否加载插件 hooks。
- 上游同步。

## Further Notes

- **姿态**：本仓有任务件，编排姿态。协调件（本目录、ADR、`CONTEXT.md`、`AGENTS.md`、`docs/agents/`、版本字段）主代理直接写；交付物（`plugin/`、`tests/`、`cursor-hooks/`、`README.md`、`docs/zh/`、新安装器脚本）经 worker。doctrine 散文同模派发；其余按椰椰本轮口头声明的新表在首轮池里派，默认 grok 车道。
- **已记录的假设（带失效条件）**：Cursor allowlist 为 2026-09-16 的四个 slug（换代即重看 Cursor 表）；codex 0.154.0、grok 1.0.30 的帮助文本与目录（版本变化即重探 `--reasoning-effort`、白名单）；基准数据为椰椰声明、未复测（新一代模型即失效）；senior 门取"两次失败"是推荐项、椰椰未单独确认（实施前若有异议改第 11 条）。
- **顺序**：先由椰椰授权提交、推送 5.1.0 并两侧安装，再开本批工单；5.2.0 的发布与两侧安装器运行同样另行授权。
- **工单**：见 `issues/01`–`08`。01 runner 契约（第 1、2、4 条 + 契约测试 + 车道文档对应句）；02 报告前言分流（第 3 条，含工单 10 的验收项）；03 伴生安装器与漂移测试（第 5–9 条）；04 doctrine 与 Cursor 车道文档（第 10–14、16、17 条）；05 路由档案与中文备份（第 18–22 条）；06 ADR 0018、README 升级段、`AGENTS.md` 类别表（第 24、25、27 条）；07 版本说明书 5.2.0（第 26–29 条）；08 发布 5.2.0。
- **5.1.0 已于 2026-09-16 提交（`83ce044`）、推送并在两侧安装**；门禁脚本活体同步到 5.1.0 版；`.scratch/post-5-1-tuning/` 与 `CONTEXT.md` 的新词条未随 5.1.0 提交。
- 来源：本轮 grilling（2026-09-16）；`.scratch/role-pool-posture/issues/10-report-mode-preamble.md`；codex-advisor 仓库的伴生安装器（`install-agents.sh`）作为形态参照，覆盖策略与之相反。

## Comments

### 2026-09-16 — 实施记录（工单 01–08 全部完成）

- 姿态：编排。01、03、06-README、07 grok 车道（Cursor 钉 `cursor-grok-4.6-xhigh`，requested, not confirmed）；02 复用 01 会话；04 同模派发；05、06 的 ADR 与 `AGENTS.md`、`CONTEXT.md` 词条架构师亲写。每票 Tier 1 验收（复跑测试 + 路径限定 diff），runner 与安装器另做 Tier 2 读码。
- Code review（两轴，各一条 codex runner 报告模式车道，`gpt-6-astra[low]`）：Standards 4 项、Spec 4 项。处理：前言指针冲突（`lanes-cursor.md:7`、`SKILL.md:72`）→ 同模车道返工；`dirtyBaseline !== true` 缺 shortcut 标记 → runner 车道加注释；中文文件裸英文（说明书 overlay、报告前言 hunks、档案 specialty）→ 各自翻译；测试桩不检真前言 → 新增 `case_real_preamble_files`（注入 `WORKER REPORT` 可红）；说明书把 `advisor-h` 写成默认 → 改为"默认在档案"。未处理并记录：两条 runner 的重复形状（按 ADR 0009 两脚本独立，判断项）；安装器 `gate_present` 子串匹配的构造性误报（警告而非门禁）。
- 发布：见 `issues/08` 评论。
- 未验证项：说明书在浏览器中的渲染（Cursor 内置浏览器拒绝 `file://` 与 WSL 本地服务）；codex / grok 会话列表首行标题的用户可见效果；Cursor 是否加载插件 hooks（范围外）。
- 范围外遗留：`ONBOARDING.md`、`docs/fable-advisor-healthcheck-2026-09.md`、`docs/fable-advisor-orchestration-handoff-2026-09.md`、`outputs/`、`cursor-hooks/__pycache__/` 与 `tests/__pycache__/` 仍未跟踪；建议 `.gitignore` 加 `__pycache__/`。
