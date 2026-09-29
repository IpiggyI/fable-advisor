# 06：路由档案随插件发布

Status: ready-for-agent
Blocked by: —

**要做什么：** 路由档案成为插件文件。技能直接读插件内的档案，不再依赖调用方指令点名路径；伴生安装器不再复制档案，也不再处理旧文件，两侧的活体副本在迁移时手动删除一次；两侧装上 6.0.0 之后，全局提示词删掉 "Model allocation" 一行。以后改档案就是改插件文件、发版、两侧更新。

**负责的要求：** 椰椰 2026-09-28："模型路由表不再游离在外而是内置到插件中，减少维护压力"。这一条在交接到本仓时丢失：`docs/fable-advisor-tier-and-consult-handoff-2026-09.md:107` 把"路由表是用户级档案，不随插件发布（ADR 0017）"写成既定事实，`../spec.md` 没有收录。codex-advisor 已按此实现（该仓 ADR 0004）。

**推翻的既定决定：** ADR 0017 决策 1、2、4、5；ADR 0015 决策 1 中"填充表在调用方指定的档案、插件不持有"的部分；ADR 0006 决策 2 中"持久判断写用户级规则文件"的部分。ADR 0017 决策 4 的理由是"随插件发布会把本分叉的排名发给安装者"；椰椰接受这一代价。

## 决定

- **D1 位置。** `plugin/skills/orchestration/routing-profile.md`。中文译本迁到 `docs/zh/skills/orchestration/routing-profile.md`，成为镜像孪生。
- **D2 读取。** `SKILL.md` "User routing profile" 段用同目录链接 `[routing-profile.md](routing-profile.md)`，保留"首次分配前读取、变化或滑出上下文时重读"。不保留"调用方指令点名的档案优先"：只有一个来源。读不到时报告缺口，不假定内容。技能文字消除不了旧全局指令，所以全局指令的清理在 D5。
- **D3 并入 6.0.0。** 6.0.0 未推送（本地 `main` 领先 `origin/main` 两个提交），两侧装的是 5.2.0。不另开版本号；说明书 `docs/manuals/6.0.0.html` 补写这一变化。
- **D4 活体退役。** 安装器 `MANIFEST` 删去档案一项；`RETIRE` 清单与 `process_retire` 删除，安装器不删除任何文件；`--also` 只写两份。（2026-09-29 修订：原为把档案加进 `RETIRE`，见 Comments。）
- **D5 顺序。** 推送后，两侧更新并核对新版内容；任一侧失败，保留旧提示与旧档案。两侧成功后，停止旧会话（`docs/agents/plugin-release.md` 第 6 步：重启才生效）；删除 prompts 仓库 `CLAUDE.en.md`、`CLAUDE.zh.md` 与两侧线上 `~/.claude/CLAUDE.md` 的 "Model allocation" 一行；启动新会话，逐侧确认读取的是插件档案；再手动删除两侧活体，逐侧断言已不存在；然后运行安装器刷新 Cursor 文件；最后删除 prompts 仓库 `current-prompts/docs/fable-advisor-routing.md` 与 `.zh.md` 快照。任一检查失败即暂停后续删除。两侧装上 6.0.0 之前不能删全局那一行：5.2.0 的技能只读调用方点名的档案。
- **D6 代价。** 档案随插件发给所有安装者；改一个格子要发版加两侧更新，取代"编辑加运行安装器"。

## 范围（Files）

- 移动并改写首段与 "Adjusting this profile" 一节：`docs/agents/fable-advisor-routing.md` → `plugin/skills/orchestration/routing-profile.md`；`docs/agents/fable-advisor-routing.zh.md` → `docs/zh/skills/orchestration/routing-profile.md`。
- `plugin/skills/orchestration/SKILL.md` "User routing profile" 段与中文孪生。
- `README.md` 第 22、51、126 行附近。
- `scripts/install-user-level.py`；`tests/test_install_user_level.py`；`tests/test_user_level_archive.py`。
- `docs/manuals/6.0.0.html`。
- `README.md` 第 107 行（"user routing profile's decision"）。
- 协调件：`AGENTS.md`（Companion installer、User routing profile 两节与第 46 行镜像说明）；`CONTEXT.md`；ADR 0023（新）与 ADR 0017、0015、0006 状态行注记；`../spec.md` MAN-2、REL-2、REL-3；工单 05（依赖、第 6 行、安装器一项）。
- D5 的外部目标（prompts 仓库、两侧 `~/.claude/CLAUDE.md`、两侧活体档案）只由获授权的主会话执行。
- 不改 `docs/agents/plugin-release.md`：D5 是一次性迁移，写在工单 05、`../spec.md` REL-3 与说明书的升级步骤；通用发布流程不变。

**执行方式：** 椰椰直接要求补上，主代理实施姿态直接改。提交、推送、两侧更新、运行安装器、改全局提示词都需椰椰当次授权（REL-2）。

## 验收

- [ ] 全部测试通过：`test_zh_mirror.py`、`test_user_level_archive.py`、`test_install_user_level.py`、`test_lane_family_gate.py`、`test_receipt_gate.py`、`test_runner_contract.py`、`test_runner_lifecycle.py`；`git diff --check` 干净。
- [ ] 安装器测试在"档案仍被复制"或"安装器多写任何文件"时失败（断言目标目录的实际文件集合）；家目录里预先存在的无关文件在安装后原样保留。（2026-09-29 修订："活体档案未被删除"一项随 D4 取消。）
- [ ] `SKILL.md` 与中文孪生的档案链接指向存在的文件。
- [ ] 全仓扫描：`docs/agents/fable-advisor-routing`、"the caller's instructions name"、"the caller names"、"调用方指令指定"、"调用方指令指名" 在交付物、`AGENTS.md`、`CONTEXT.md` 零命中（ADR 与 `.scratch/` 历史记录除外）；退役路径字面量 `.claude/docs/fable-advisor-routing.md` 只允许出现在 ADR、`.scratch/` 任务件、旧版说明书与 6.0.0 说明书的迁移说明（不兼容点与升级步骤）（2026-09-29 修订）。
- [ ] 说明书：`html.parser` 完整解析；新增内容写明档案位置、改档案的流程与 D5 的升级步骤。
- [ ] 发布后（归工单 05）：逐侧独立断言活体档案已不存在，不以 `--check` 通过代替（安装器不处理这份文件，`--check` 通过不说明它已删除）；一次新会话的模型分配读取的是插件缓存里的 `routing-profile.md`；真实家目录的 `test_user_level_archive.py` 在安装器运行后再跑一次。

## Held for batch acceptance

- 发布后一项归工单 05 的 REL-3。

## Comments

### 2026-09-28 — 决策咨询与实施（主代理，实施姿态）

决策咨询：`gpt-6-astra` / `medium`（档案 advisor 映射的决策形状；提交值，未观测），会话 `01a0e7f7-c4e1-79e0-84d1-71f3677618cd`。裁决"修改后采纳"，置信度高：D1、D4、D6 合理；D2、D3 成立；D5 须改为重启后逐侧确认再删除；补齐 `AGENTS.md:46`、`README.md:107`、spec MAN-2 / REL-2 / REL-3、工单 05；安装器测试第 176 行允许退役文件残留时 `--check` 通过，发布后须逐侧单独断言。全部采纳，唯一例外是不改 `docs/agents/plugin-release.md`（理由见范围一节）。

实施：两份档案用 `git mv` 移动（重命名已暂存，未提交）；`SKILL.md` 第 88 行与中文孪生；档案"Adjusting this profile"一节（改格算次版本）；`README.md` 第 22、51、107、126 行；安装器 `MANIFEST` / `RETIRE` / `--also` 帮助；两个测试；两个清单文件的描述（"user-side fill table" 改为随插件发布的档案）；说明书第 9、12、16 节与两张变化卡片（未重新截图）；ADR 0023 与 0017、0015、0006 状态注记；`AGENTS.md`、`CONTEXT.md`、spec、工单 05。

检查：`test_install_user_level.py` 8/8；`test_zh_mirror.py` 16/16；`test_user_level_archive.py` 4/4（真实家目录，`--check` 只读）。变异检查：安装器仍复制档案 → 4 项失败；安装器不删除活体档案 → 1 项失败。

阻塞项：`SKILL.md` 为 2206 词（`wc -w`），超过 TR-9 的 2160；正文（不含 frontmatter）2115 词。超出来自 ADR 0022 扩写的技能描述（HEAD 为 2160）。按 S4 停下回报，由椰椰决定。

### 2026-09-28 — 椰椰决定

- 词数：上限调到 2210，记入 ADR 0022 决策 5；spec TR-9、S4 与工单 05 同步。`SKILL.md` 现为 2206 词。
- ADR 0023 四项子决定（并入 6.0.0、不保留点名覆盖、改格算次版本、一周两次的复盘条件）全部确认，状态改为 accepted。

### 2026-09-29 — 计划：安装器不再处理旧版游离文件（待 advisor 裁决）

来源：椰椰 2026-09-29 要求移除对旧版本游离文档（如 `fable-advisor-routing.md`）的处理。理由：这些文档只在本机存在，一次性删掉后不会再出现，不需要维护处理逻辑。

现状（2026-09-29 只读检查）：两侧的 `~/.claude/rules/fable-advisor.md` 与 `~/.cursor/rules/fable-advisor.mdc` 都已不存在。两份档案活体仍在：WSL `~/.claude/docs/fable-advisor-routing.md`（6314 字节，2026-09-16）与 `/mnt/c/Users/Shy/.claude/docs/fable-advisor-routing.md`（6314 字节，2026-09-18）。两侧 `~/.claude/CLAUDE.md:132` 仍点名这份活体，两侧装的仍是 5.2.0，所以活体现在不能删。`plugin/**` 里没有这类处理，处理逻辑只在伴生安装器、它的测试和文档里。

决定的改动：
- D4 改为：安装器 `MANIFEST` 删去档案一项；删除 `RETIRE` 清单与 `process_retire`，安装器不再删除任何文件；`--also` 只写两份。
- D5 的"再运行安装器删除活体"改为：手动删除两侧活体（一次性），逐侧断言文件已不存在，再运行安装器刷新 Cursor 文件。其余顺序不变。

范围：
- 交付物，经 `worker`：`scripts/install-user-level.py`（`RETIRE`、`process_retire`、`process_home` 里的循环、`--check` 帮助里的 "delete nothing"）；`tests/test_install_user_level.py`（`RETIRE`、`RETIRED_PROFILE` 及其断言、`retire_removed` 与它的 `check` 行、fresh-home 用例的描述；`len(installed) == 2` 已覆盖"不写档案"）；`README.md:51`，以及 `README.md:126` 中 v6.0.0 一句里点名活体路径与"安装器会删除活体"的从句（更早版本的说明逐字保留）；`docs/manuals/6.0.0.html` 第 461 行退役列表、第 465 与 467 行两个表格行、第 470 行的 `removed` 前缀、第 496 行测试说明、第 690 与 752 行、升级步骤第 6 步。
- 协调件，主代理直接写：`AGENTS.md:25`；`CONTEXT.md:144`；ADR 0023 决策 3、6（未跟踪，原地修订并在状态行注明日期）；ADR 0018 状态行补反向指针（决策 5 的退役清单由 ADR 0023 撤销）；本工单 D4、D5 与验收第 38、40 行；工单 05 第 29 行；规格 REL-2（加"手动删除两侧活体"一步）与 REL-3。
- 本工单验收第 42 行（发布后逐侧单独断言活体已不存在）不变。

验收：
- `grep -rn -E "RETIRE|process_retire|fable-advisor-routing|rules/fable-advisor" scripts/ tests/` 零命中。
- 测试全部退出 0：`test_install_user_level.py`、`test_user_level_archive.py`（真实家目录，`--check` 只读）、`test_zh_mirror.py`、`test_lane_family_gate.py`、`test_receipt_gate.py`、`test_runner_contract.py`、`test_runner_lifecycle.py`；`git diff --check` 干净。
- 一次性核对（不入库）：在临时家目录预置三个旧路径文件，运行安装器与 `--check`。通过标准：三个文件原样保留，输出没有 `removed` 与 `still present`。
- 说明书经 `html.parser` 完整解析。

### 2026-09-29 — advisor 裁决与处置

决策咨询：`gpt-6-astra` / `medium`（现行档案决策形状的 `standard` 格；提交值，未观测），会话 `01a0eb15-d848-7d73-9f98-82a7af53cb68`。裁决"修改后同意"，置信度高。五点全部采纳：

1. 范围补齐：本工单第 6 行的"并删除两侧的活体副本"与第 42 行"允许退役文件残留"的依据一并修改；第 42 行的发布后逐侧断言保留。
2. 顺序统一：工单 05 第 29 行原先把"确认新会话读取插件档案"放在"删除全局提示词那一行"之前，与 D5 相反。统一为 D5 的顺序：两侧更新并核对；停止旧会话；删除全局提示词那一行；启动新会话，逐侧确认读取插件档案；手动删除两侧活体；逐侧断言不存在；运行安装器刷新 Cursor 文件。任一步失败即停。
3. 防回归：`len(installed) == 2` 只数输出行，`--also` 用例只遍历预期文件。改为断言临时家目录与 `--also` 目录里实际存在的文件集合恰好是预期的两件，这样静默多写一个文件也会失败，而且测试不需要点名任何旧路径。
4. 验收替代：第 38 行取消"活体档案未被删除"，"不写档案"由第 3 点的文件集合断言承担；第 40 行保留扫描，把例外写明为 ADR、任务件与说明书中的一次性迁移步骤。
5. 证据：一次性核对之外，入库一条通用回归测试：家目录里预先存在的无关文件在安装与 `--check` 之后原样保留（用中性文件名，不用旧路径）；再用一次临时变异（安装器多写一个文件）证明文件集合断言会失败，变异不入库。

交付物由 claude 车道 `worker-h` 实施（椰椰 2026-09-29 要求本次 worker 一律用 Claude 模型；现行档案 worker `light` 格的 Claude 候选是 `sonnet-5[high]`）。

### 2026-09-29 — advisor 第二、三轮

同一会话续接两轮（`gpt-6-astra` / `medium`，提交值，未观测）。第二轮"修改后同意"，指出 ADR 0023 决策 6 仍写"两侧更新并重启之后，才删除全局提示词"，与 D5 的"停止旧会话，删除，再启动新会话"不一致；已把决策 6 改为与 D5 相同的顺序。第三轮"同意"，置信度高：ADR 0023 决策 6、本工单 D5 与工单 05 第 29 行的顺序一致。两轮都只覆盖协调件；`scripts/`、`tests/`、`README.md` 与说明书由 worker 并行修改，交付后另行验收。

### 2026-09-29 — 安装器改动的实施与验收

实施：claude 车道 `worker-h`，型号 `sonnet`（提交值，未观测）。改动相对派发前快照：`scripts/install-user-level.py` 删除 `RETIRE`、`process_retire` 与调用循环，`--check` 帮助改为 "compare only; write nothing"；`tests/test_install_user_level.py` 删除旧路径常量与 `retire_removed`，每个写入临时家目录的用例断言实际文件集合，`--also` 用例断言目录内文件集合，新增"预先存在的中性文件在安装与 `--check` 后原样保留"用例；`README.md:51` 与 `:126` 的 v6.0.0 一句（v5.2.0 起逐字未动）；`docs/manuals/6.0.0.html` 的伴生安装器一节、测试说明、两张卡片与升级步骤第 6 步。

检查（各跑一次）：变异（安装器多写一个文件）使安装器测试失败，已还原；`test_install_user_level.py` 8/8；`test_user_level_archive.py` 4/4（真实家目录，只读 `--check`）；`test_zh_mirror.py` 16/16；`test_lane_family_gate.py` 18/18；`test_receipt_gate.py` 8/8；`test_runner_contract.py` 19/19；`test_runner_lifecycle.py` 退出 0；`scripts/`、`tests/` 旧路径扫描零命中；预置旧路径文件的一次性核对通过；说明书 `html.parser` 解析通过；`git diff --check` 干净；快照之后被改的文件只有四个交付物与主代理的协调件。

验收（Tier 3，同族 diff）：`gpt-6-astra` / `low`（现行档案验收形状的 `light` 格；提交值，未观测），会话 `01a0eb45-e93c-7251-b3a3-0c9e6c52aa75`。第一轮"有条件通过"：预置文件用例缺文件集合断言（违反契约 3a）、说明书第 6 步缺停止条件、主代理契约漏列其余测试与全目录扫描。前两点经同一 worker 会话返工修复，第三点由主代理补跑。第二轮"验收通过"，置信度高。

遗留：两侧活体的一次性手动删除归工单 05（D5 顺序），需椰椰当次授权。
