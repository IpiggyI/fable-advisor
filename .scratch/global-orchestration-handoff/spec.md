# 承接全局提示词"编排协作"入口：最终调整方案

Status: ready-for-agent

日期：2026-09-13。本文件是综合 GPT 审查（[review.md](review.md)）后的最终方案，取代同日的初版清单。每条保留原编号，标注最终处置。末节五个决定椰椰已于 22:21 全部按推荐确认：D2 取值照写；Q01 只做（a）；C6 改 `IpiggyI/fable-advisor`；N02、Q02 不做；A8 由椰椰自行执行。工单见 `issues/01`–`09`。本轮不修改业务代码（`plugin/scripts/**`、`plugin/hooks/*.py`、`cursor-hooks/*.py`）。

## 输入

- 交接文档：`/mnt/d/Development/Local/prompts/docs/plans/fable-advisor-orchestration-handoff-2026-09.md`。
- 讨论结论：`/mnt/d/Development/Local/prompts/.agent-discuss/advisor-global-orchestration/final.md`。
- 新全局提示词工作副本：`/mnt/d/Development/Local/prompts/current-prompts/CLAUDE.en.md`；用户路由档案：`/mnt/d/Development/Local/prompts/current-prompts/docs/fable-advisor-routing.md`。
- 官方资料（2026-09-13 读取）：[Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)；[Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)；[Claude Code tools reference](https://code.claude.com/docs/en/tools-reference)；[Codex speed](https://developers.openai.com/codex/speed)。
- GPT 审查：`review.md`（R01–R08、N01–N06、Q01–Q10）。

## 基线与本轮复核

- 仓库 `HEAD` = `ec36345`；工作树未跟踪项为本目录、`outputs/`。保留。
- 两侧已安装缓存均为 `5.0.0`；`claude --version` WSL `2.1.270`、Windows `2.1.267`（GPT 报告）。
- 活体未跟上工作副本：`~/.claude/CLAUDE.md` 为 14:15 版；`~/.claude/rules/fable-advisor.md` 与 `~/.cursor/rules/fable-advisor.mdc` 仍是完整 v5 规则；`~/.claude/docs/fable-advisor-routing.md` 两侧都不存在。
- 对 GPT 外部主张的复核（官方文档原文）：`TaskOutput` 已标弃用，推荐 `Read` 任务输出文件；内置 Explore 自 v2.1.198 起继承主会话模型，Claude API 上限 Opus，用户或项目级同名 `Explore` agent 可覆盖并保留自己的 `model`；子代理 `effort` 只在 agent 文件或 `--agents` 定义中设置，默认继承会话，取值随模型而异；模型解析顺序自 v2.1.251 起为按次参数 → frontmatter → 环境变量；子代理嵌套上限为主会话下三层；`/tasks` 自 v2.1.242 起显示子代理模型与 effort；Codex fast 模式是提速 1.5 倍、额度消耗 2.5 倍，不降低智能。
- `model_used` 来源：`run-codex.mjs:653`、`:703`、`run-grok.mjs:606` 赋值为提交给 CLI 的 spec 或重试 spec 的 `model`。
- 路由档案第 20 行已改为 "Where a cell does not specify an effort, use the role default above."，初版 C14 引用的句子不存在。

## 处置一览

执行 = 按初版执行；修订 = 按本节文字执行；转出 = 属 prompts 仓库或用户目录，本仓只给文本；保留 = 不改；待定 = 需椰椰决定。

### 一、承接全局改动（交接六项）

- [ ] **A1 执行**（Q10 支持）。`SKILL.md:12` 删 "A code block longer than an interface signature is a contract not yet delegated"（`README.md:31` 同句同删）；`:14` 改为判据：读取范围宽、可独立并行、或只需结论进主线程时派 explorer；已知文件内的有界查询主代理直接读；代码块长度与单次工具调用不是派发条件；删 "bills twice" 论证句。编排姿态下交付物必须经 worker 的规则（`:31-40`）不动。
- [ ] **A2 执行**。`SKILL.md:65`、`:90`、`README.md:22` 改为调用方指定的用户路由档案；补读取契约（首次分配模型前读；变化或滑出上下文时重读；缺失则报告缺口、不假定内容）；`SKILL.md:88-96` 与 `:65` 合并。
- [ ] **A3 拆分**（R02、N06）。
  - **A3a 执行（文档）**：`SKILL.md:62`、`lanes-claude-code.md:3`、`lanes-cursor.md:8` 写明 explorer 派发须带显式按次 `model`（来自路由档案）；Claude Code 内置 Explore 继承会话模型（Opus 封顶）与会话 effort，不带 `model` 即会话价格。
  - **A3b 单独工单，暂不实施**：是否新增 `plugin/agents/explorer.md`，先在真实会话核对"内置 Explore + 按次 `model`"能否满足只读取证契约与 effort 控制；核对结果决定是否需要 agent 文件及其默认值。不预选默认别名；不并入工单 10（`.scratch/role-pool-posture/issues/10-report-mode-preamble.md` 涉及 runner 代码）。
- [ ] **A4 执行**（Q05 支持）。`SKILL.md:104` Constraints 补 "and the operations the caller keeps in its own session; these bind the lane, its subagents, and its verification commands"；`lane-preamble.md:1` 补 "Constraints' reserved operations still bind you and any subagent you spawn; when a step needs one, report it under GAPS with your evidence instead of performing it or claiming the check passed"。前言保持三段。
- [ ] **A5 修订**（R03）。删 `SKILL.md:141` 后半句 "A subagent idle without its report is not a blocker: verify the workspace evidence and move on"。`lanes-cursor.md` 生命周期段补：后台派发的完成通知不是报告；报告缺失时先读输出文件与工作区确认状态，再按缺口恢复；确需重新执行才重派，不用 `resume` 催。`lanes-claude-code.md` 补 claude 车道子代理的报告在 Task 结果内返回，后台派发读任务输出文件。
- [ ] **A6 修订**（R04）。统一修正把提交值写成实际值的句子：`lanes-claude-code.md:25`（"The receipt records the values actually used"）、`:70`、`:109`（"the receipt records the value actually used"）、`README.md:61`。三层表述：请求值（spec）、提交值（runner 传给 CLI 的参数，含回退后）、观测值（runner 不读，保持未知）。`lanes-cursor.md` Task 派发处加 "pin 是请求值，Cursor 不暴露执行元数据，报告时标 requested, not confirmed"。可加一句：Claude Code `/tasks` 显示子代理模型与 effort（v2.1.242 起），是用户侧观测入口。不改 runner。
- [ ] **A7 修订**（R08、Q06）。删 `user-rules/` 中 Claude 与 Cursor 两份规则存档及其 `zh/` 孪生；`user-rules/zh/fable-lane-pin.mdc` 迁到 `cursor-hooks/zh/fable-lane-pin.mdc`；`tests/test_user_level_archive.py` 删两组规则条目、改中文列表路径，保留 pin 规则对活体与 prompts 副本的漂移检查；更新 `docs/agents/cursor-lane-gate.md:38`、`AGENTS.md:27-29`（改一句：候选与偏好在 prompts 仓库的用户路由档案，本仓不留副本）。pin 规则权威归插件仓库（prompts 指南第 30 行只描述内容，未声称权威）；prompts 副本注明部署用途（转出一句）。
- [ ] **A8 转出，可选**（Q07）。用户目录清理由椰椰单独授权执行：`~/.claude/docs/fable-advisor-rule.zh.md`（自注"不参与加载"，删除不减少上下文）；`.bak-*` 文件按 prompts 指南 "Keep reviewed prior copies for recovery" 至少保留一份可恢复版本。旧规则活体按"部署路由档案 → 换入口 → Cursor 真实会话确认 → 撤旧规则"顺序撤下。
- [ ] **A9 修订**（R04）。`SKILL.md:69` 改为按所在宿主与工具参数结构判断，不凭单个工具名或是否有 `model` 参数；判定后读对应 lanes 文件。

### 二、按 Astra 文审查

- [ ] **B1 执行**。`SKILL.md:3` 描述压短，目标约 35 词，不设硬门（N02 提醒）。
- [ ] **B2 执行**。`fable-advisor.md:3`、`worker.md:3` 描述压短；若 Q01 通过，fable-advisor 描述与正文中的验收触发同步改，避免双写。
- [ ] **B3 修订**（Q03）。删 `worker.md:26`（验证催促，前言已覆盖）；`:27` 改为限定自己改动的一句 "No swallowed errors or placeholders in your own diff"，不再称"验证要求不变"，而是"删催促、保留并限定错误处理约束"。
- [ ] **B4 修订**（R05）。`worker.md:12-16` 压成一行普通自查 "Re-read your diff before you report"，不称 second reader。三条披露的来源是 `.scratch/role-pool-posture/spec.md` 而非 ADR 0014 决策 10，无需 ADR 追记。
- [ ] **B5 执行**。`SKILL.md:62`、`worker.md:16`、`README.md:64` 删 "highest unit price"。
- [ ] **B6 执行**。`SKILL.md:82` 改 "stating any loss of cross-vendor review"；`:118` 改 "two fills from families other than the main agent's"。
- [ ] **B7 执行**（同 D3）。删 `lanes-claude-code.md:35` 整段；`:28` 白名单与按模型默认值保留。
- [ ] **B8 执行**。`SKILL.md:80` 删 Luna 半句，保留 "each lane priced at its default dial"。
- [ ] **B9 执行**。`docs/agents/domain.md:12` 模板句删；`:14-29` 目录树删；决策入口段保留。
- [ ] **B10 升级为执行**（R03）。`lanes-claude-code.md:47-61` 等待协议按官方工具参考更新：`TaskOutput` 已弃用，改读任务输出文件，保留"弃用不等于不可用"的兼容说明；`README.md:67` 模型解析顺序改为按次参数 → frontmatter → `CLAUDE_CODE_SUBAGENT_MODEL`（v2.1.251 起）；`SKILL.md:29` "Depth is not limited" 后补宿主事实（Claude Code 嵌套上限三层）。`README.md:59` 最低版本 2.1.170 仍未核验，保留并标注。
- **B11 保留**。`SKILL.md:36`、`lane-preamble.md:1` 授权句、`lanes-claude-code.md:54` 与 `:116-118`。上游提交 `4d6cc62` 仍是固定 Fable 架构师与强制终审，不吸收（GPT 已核）。

### 三、部署文档细节

- [ ] **C1 执行**。`README.md:49-52` 删 `/model fable` 代码块。
- [ ] **C2 执行**。`README.md:62-64` 每条压两句加链接；保留安装前置、兼容性说明、迁移动作。
- [ ] **C3 执行**。`README.md:95` 压五行加链接。
- [ ] **C4 执行**。`README.md:82-89` 与 `:119-124` 合并。
- [ ] **C5 执行**。`README.md:134` 只留 v5.0.0 段加 ADR 链接。
- [ ] **C6 修订**（R08）。`README.md:38-39` 安装地址改为本分叉的部署目标 `IpiggyI/fable-advisor`，保留上游署名与链接。
- [ ] **C7 执行**。`plugin-release.md:10` 改为三类规则：破坏兼容 → major；向后兼容的语义变化 → minor；纯文字 → patch。
- [ ] **C8 修订**（R07）。`plugin-release.md:12` 删目录枚举，保留 "`source: ./plugin`"、整目录复制、不认 `.pluginignore` / `export-ignore` 三句机制依据。
- [ ] **C9 修订**（R07、Q06）。`plugin-release.md:45-53` 删三行 `test ! -d`；抽查改为针对本次发布内容的 grep；保留 `ls` 版本目录。不把"不可能进缓存"写成已验证事实。
- [ ] **C10 执行**。`cursor-lane-gate.md:16-26`、`:28` 去重，保留权威路径、两侧部署路径、更新步骤。
- [ ] **C11 执行**。`cursor-lane-gate.md:36-44` 删对 `fable-lane-pin.mdc` 全文的复述。
- **C12 保留**。`issue-tracker.md:27-36` Wayfinding 段；"未使用"证据不足（GPT）。
- [ ] **C13 修订**（R06）。`triage-labels.md:5-11` 删重复的映射列，保留"状态 / 含义"两列。
- [ ] **C14 转出**。路由档案第 20 行现句 "Where a cell does not specify an effort, use the role default above." 在 Cursor 侧与 effort 钉在 slug（`lanes-cursor.md:14`）不兼容。给 prompts 仓库文本："In Cursor the effort is the slug suffix; pick the slug variant whose effort fits the cell; when this turn's allowlist has one variant, it is the dial, named in the disclosure."
- **C15 并入 A8**。

### 四、推理强度记法

- [ ] **D1 修订**（R01）。`SKILL.md:65` 的 `dial` 定义改为 "`model[first-round options | escalation-only]`, `*` marks the default; options after `|` are reached by a worker only through escalation after a failed rework ticket, and by any role only on user declaration"。`CONTEXT.md` 拨盘词条同步。
- [ ] **D2 修订、转出**（R01）。分开可选范围、默认值、首轮限制。给 prompts 仓库的取值草案（待椰椰确认）：
  - Luna（worker / explorer @ light）：`gpt-5.6-luna[high* / xhigh / max]`，三档首轮可选，默认沿用档案的 `high`；runner 默认 `max` 只在 spec 省略 effort 时生效，不覆盖档案。
  - Astra worker @ senior：`gpt-6-astra[medium* / high | xhigh]`。
  - Astra advisor：`gpt-6-astra[medium / high* | xhigh]`。
  - Fable advisor：`claude-fable-5-1[medium / high* | xhigh]`。
  - grok light：`grok-4.6[medium* / high | xhigh]`；grok standard：`grok-4.6[high / xhigh*]`。
  - Opus worker @ standard：`claude-opus-5[medium / high*]`（现档案值 `high`）。
- [ ] **D3 执行**（同 B7）。
- [ ] **D4 修订**（R02）。`lanes-claude-code.md` 补：Task 按次参数没有 `effort`；claude 车道的 effort 来自 agent 文件 frontmatter 或 `--agents` 定义，省略则继承会话；`worker.md` 的 `effort: medium` 与 `fable-advisor.md` 的 `effort: high` 即该角色在此车道的默认。`lanes-cursor.md:14` 补"括号映射到 slug 变体"（与 C14 同义）。

### GPT 补入项

- [ ] **N01 执行**。`SKILL.md:100-106` 契约第 5 部按角色区分：worker 为验收证据命令，至少一条目标未达成即失败的检查；explorer / advisor 为期望的证据或裁决形状，可为空（与报告模式 `verification` 可空一致）。
- **N02 可选，默认不做**。`SKILL.md:76-141` 派发细则再拆按需文件。收益约省 1.2k 词，风险是 ADR 0012 复盘条件"指针被跳读"。椰椰要求时另开票。
- **N03、N04 转出**。全局提示词第 3、33、81 行阶段说明合并；第 60、64 行数字阈值改为观察线索。属 prompts 仓库。
- [ ] **N05 执行**。`lanes-claude-code.md:29`、`README.md:62` 的 `service_tier: "fast"` 语义改为"提速 1.5 倍、额度消耗 2.5 倍，不降低智能；API key 计费时不适用"。
- **N06 采纳**。A3 不并入工单 10。

## 单列：安全、权限边界或减少验证

- [ ] **Q01 / S1 修订、待定**。拆成两个决定：（a）取消决策类型门第六项里"按多步触发"的强制终审（`SKILL.md:129`、`fable-advisor.md:3`、`README.md:106`）；（b）Tier 3（`SKILL.md:139` 正确性关键、同族 diff）与"用户明确要求评审"保留不动。建议只做（a）。主代理仍按 Tier 1 / 2 读实际改动，不以文件统计替代。
- **Q02 可选，默认保留**。`SKILL.md:96` 低置信度逃生门收窄为"仅当资源限制或偏好会改变选择时询问"。属 ADR 0006 决策，触发稀少，本轮不改。
- [ ] **Q03 / S4 修订**。同 B3。
- **Q04 转出**。全局提示词第 70 行日志要求。属 prompts 仓库。
- [ ] **Q05 / S3 执行**。同 A4。
- [ ] **Q06 修订**。同 A7、C9：保留 pin 规则漂移检查；删除的检查在工单里写明"验证覆盖变化"。
- **Q07 转出**。同 A8。
- [ ] **Q08 执行**。`plugin-release.md:21` 由 `git add -A && git commit && git push origin main` 改为显式暂存发布文件并 `git diff --cached --stat` 复核后再提交；注明 `outputs/` 未忽略、`.scratch/` 受跟踪，`-A` 会把在途稿一并带入。不授权执行提交或推送。
- [ ] **Q09 执行**。`lanes-claude-code.md:81`、`lanes-cursor.md:15` 补：同一工作树里两个执行者会互相覆盖；竞赛须各自隔离工作目录与执行记录（Claude Code 用 `git worktree`；Cursor 用隔离 worktree 的派发类型），不同 pending 文件名不构成隔离。文档层补充，未审查 runner。
- [ ] **Q10 / S2 执行**。同 A1。
- **S5、S6、S7 保留**。receipt gate、Cursor 显式指定门、handoff 亲自验证。本轮不对其实现作通过结论。

## 待椰椰决定

1. **D2 取值**：上表六行是否照此写入 prompts 仓库路由档案（尤其 Luna 默认 `high`、grok standard 默认 `xhigh`）。
2. **Q01**：是否只做（a）取消按步数触发的终审。
3. **C6**：README 安装地址改 `IpiggyI/fable-advisor` 是否同意。
4. **可选项**：N02（再拆 SKILL.md）、Q02（收窄逃生门）是否做；默认不做。
5. **A8**：用户目录清理是否由椰椰自行执行；本仓不动。

已由审查解决、不再询问：A3 默认别名（推迟到 A3b 核对后）；A7 pin 规则权威（插件仓库）。

## 工单拆分与顺序（确认后）

有上游任务件即编排姿态；椰椰声明"直接改"则主代理直接改。

1. `01-skill-doctrine`：`SKILL.md`（A1、A2、A4 契约句、A5、A9、B1、B5、B6、B8、B10 深度句、D1、N01、Q01a、Q09）。同模派发。
2. `02-lanes-and-preamble`：`lanes-claude-code.md`、`lanes-cursor.md`、`lane-preamble.md`（A3a、A4、A5、A6、B7、B10、D4、N05、Q09）。同模派发。
3. `03-agents`：`fable-advisor.md`、`worker.md`（B2、B3、B4、B5、Q01a 同步）。同模派发。
4. `04-readme`：`README.md`（A1、A2、A6、B5、B10、C1–C6、N05）。grok 车道。
5. `05-repo-docs-and-archive`：`AGENTS.md`、`docs/agents/*`、`user-rules/` 删除与 pin 中文备份迁移、`tests/test_user_level_archive.py`（A7、B9、C7–C11、C13、Q08）。grok 车道。
6. `06-zh-mirror`：`docs/zh/**` 孪生同批更新。grok 车道。
7. 协调件（主代理亲写）：`CONTEXT.md` 拨盘词条；ADR 0015 记录填充表改为调用方指定档案、第六项处置、拨盘记法、存档退役、explorer 待核；版本两处。
8. 后续独立票：`A3b` explorer 核对；prompts 仓库转出项（C14、D2、N03、N04、Q04、A7 副本注记）。

版本建议 5.1.0（A4 前言语义、doctrine 语义变化、存档退役；向后兼容）。提交、push、两侧 `claude plugin update` 另行授权。

## Comments

### 2026-09-13 — 实施记录（工单 01–07 完成，08、09 待办）

- 姿态：编排。01–03 同模派发（`generalPurpose`，inherit）；04、05、06 grok 车道（`cursor-grok-4.6-xhigh`）；07 架构师亲写。全部在同一工作树并行，文件范围互不相交。
- 01 车道为满足 ≤ 1950 词额外删了六句同文重复句（见 ADR 0015 实施节），验收接受；词数上限随返工改为 1960，终值 1952。
- advisor 验收形状（`fable-advisor`，`claude-fable-5-1-thinking-xhigh`，本轮 allowlist 唯一 Fable 变体）：ACCEPT-WITH-REWORK。返工两处：`README.md:84-86` 合并片段对决策类型门重复下指令（C4）→ 04 车道 `resume` 修正；`SKILL.md:136` Tier 3 只列两触发而 `fable-advisor.md:25`、`CONTEXT.md:14` 列三触发（契约自身不一致）→ 按 Q01(b) 以三项为准，01 车道 `resume` 补导语，06 中文孪生同步。
- 验证：`test_zh_mirror` 7/7、`test_lane_family_gate` 16/16、`test_user_level_archive` 5/5（三处 pin 活体逐字节一致）、`test_receipt_gate` 8/8、`test_runner_contract` 15/15；`git diff --check` 干净；退役短语在 `plugin/`、`README.md`、`docs/zh/`、`CONTEXT.md`、`AGENTS.md`、`docs/agents/` 零命中；六对中英文件标题数一致。`git diff HEAD --stat`：27 files, +143 / −397。
- 未做：提交、push、两侧 `claude plugin update`、两种姿态与 explorer 的真实场景（须在 5.1.0 上跑）、工单 08、工单 09 转出项。均待椰椰授权或执行。
- 范围外披露：工作树另有两个未跟踪文件 `docs/fable-advisor-healthcheck-2026-09.md`、`docs/fable-advisor-orchestration-handoff-2026-09.md`（review.md 的相对链接目标），不在任何工单 Files 内，处置待椰椰定。

## 验证

- 静态：`python3 tests/test_zh_mirror.py`、`python3 tests/test_lane_family_gate.py`、调整后的 `python3 tests/test_user_level_archive.py`、`git diff --check`；grep 确认退役短语消失（"lives in the user's rules"、"highest unit price"、"actually used"、"TaskOutput(task_id"、"trading quality for speed"）。
- 行为（须在更新后的插件上跑，静态不能替代）：两种姿态各一个小任务看谁改交付物；explorer 带显式 `model` 派发并对照 `/tasks`；一次含保留操作的模拟契约看执行者是否报 GAPS 而非执行；报告缺失场景先读输出文件再决定。
