# 0015 — 承接全局提示词的编排入口：填充表改为调用方指定档案、决策类型门第六项退役、拨盘记法入仓

- **Status**: accepted（2026-09-13 用户确认 GPT 审查后的最终方案，五项待定"全部按推荐"）
- **Date**: 2026-09-13
- **影响范围**: `plugin/skills/orchestration/`（`SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md`、`lane-preamble.md`）、`plugin/agents/`（`fable-advisor.md`、`worker.md`）、`README.md`、`docs/zh/**`、`user-rules/**`（删除）、`cursor-hooks/zh/fable-lane-pin.mdc`（迁入）、`tests/test_user_level_archive.py`、`docs/agents/**`、根目录 `AGENTS.md` / `CONTEXT.md`；版本 5.1.0。不改 runner 与 hook 代码。
- **关联**: [ADR 0006](./0006-pareto-lane-routing-inhouse-promotion.md)（机制入库、判断入用户规则——本次判断的落点从用户规则改为按需档案）、[ADR 0011](./0011-cursor-lane-family-gate-user-level.md)（用户级存档与漂移检测——本次只保留 pin 规则一项）、[ADR 0012](./0012-orchestration-skill-progressive-disclosure.md)（词数预算——本次沿用 ≤ 1950）、[ADR 0013](./0013-delivery-contract-not-build-instructions.md)（前言单源——本次加一句边界从句）、[ADR 0014](./0014-role-pool-posture.md)（决策类型门清单——本次退役第六项；填充表位置——本次改）。任务件与审查记录 `.scratch/global-orchestration-handoff/`（`spec.md`、`review.md`、`issues/01`–`09`）；上游交接 `/mnt/d/Development/Local/prompts/docs/plans/fable-advisor-orchestration-handoff-2026-09.md`。

## 背景

用户的全局提示词（prompts 仓库 `current-prompts/CLAUDE.en.md`）把常载的 Scout Doctrine 换成一段通用的 Collaboration（主代理职责、三角色、委派输入输出、模型与 effort 的选择与核验），并在 Platform Adapter 加了两条入口：交付物改动、超出有界事实查询的调查、重要决策、交付验收以及任何子代理调用前先读 `fable-advisor:orchestration`；分配模型前先读 `~/.claude/docs/fable-advisor-routing.md`。用户级规则 `~/.claude/rules/fable-advisor.md` 与 Cursor 副本缩成两行入口，填充表迁到按需档案。

这让插件的四处前提失效：

1. `SKILL.md` 成本段的两句无条件委派（代码块长于接口签名即未派发的契约；探索一律派 explorer）会加载给准备直接改代码的实现姿态主代理，与第 23 行"可直接改"和全局第 8 条"编辑者先读代码"冲突；全局删掉 Scout Doctrine 后，"何时派 explorer"的判据没有落点。
2. `SKILL.md:65`、`:90` 与 `README.md:22` 写填充表"在用户规则里"，而它已在调用方指定的按需档案里；插件不能写死本机路径。
3. `user-rules/` 存档与 `tests/test_user_level_archive.py` 的比较对象已变成两行入口，prompts 仓库成为偏好的唯一编辑源，存档成了第二个编辑源。
4. 前言的"machine-level rules do not apply"与 grok / codex 车道同时读到的授权边界句并列，没有明说调用方保留的操作（破坏性命令、提交、部署、回滚、破坏性数据库操作、用户门禁）仍约束执行者。

同期按 OpenAI《Rethinking skills and prompts for GPT-6 Astra》（2026-09-11）做了一轮体检：技能与 agent 描述过长、复述门清单；`worker.md` 复述全局已有的验证催促与错误处理规则；`lanes-claude-code.md` 残留拨盘判断（ADR 0014 备注已把拨盘判断收进用户档案）；"highest unit price"是型号排名残留；`TaskOutput` 已被官方标弃用；README 的模型解析顺序是 v2.1.251 前的旧顺序；`service_tier: "fast"` 被写成"以质量换速度"，官方定义是提速 1.5 倍、额度 2.5 倍、不降智能。GPT 对初版清单的审查（`review.md`）修正了八条、补了六条、单列了十条敏感项，用户确认后形成最终方案。

## 决策

1. **填充表位置改为调用方指定的用户路由档案。** `SKILL.md` 的 "User routing profile" 段定义读取契约：首次分配模型前读取；档案变化或滑出上下文时重读；未指定或读不到时报告缺口、不假定内容。插件不持有本用户的排序与机器路径。`user-rules/` 存档及其中文孪生删除；`tests/test_user_level_archive.py` 只保留 Cursor Task pin 规则的存在、中文孪生与漂移检查。pin 规则权威留本仓 `cursor-hooks/fable-lane-pin.mdc`，中文备份迁到 `cursor-hooks/zh/`，prompts 仓库那份记为部署快照。
2. **成本段改为判据。** 删"代码块长于接口签名即未派发的契约"；"探索派 explorer"改为：读取范围宽、可独立并行、或只需结论进主线程时派 explorer，已知文件内的有界查询主代理直接读，代码块长度与单次工具调用不是派发条件。编排姿态下交付物一律经 worker 的边界（ADR 0013 §4、ADR 0014 决策 1）不动。
3. **决策类型门第六项退役。** "宣告多步交付物完成前"不再是门的一项；advisor 的验收形状经验证 Tier 3 到达，不按步数触发。Tier 3 的导语补第三个触发"用户要求评审"（advisor 验收时发现与 `fable-advisor.md`、`CONTEXT.md` 不一致，返工补齐），正文不动。这是一项减少强制验证的决定，由用户在 GPT 单列（Q01）后确认，只做"取消按步数触发"这一半。
4. **拨盘记法入仓，取值留档案。** `dial` 写作 `model[first-round options | escalation-only]`，`*` 标默认；`|` 之后的档位 worker 只经返工失败后的升级到达，任一角色只经用户声明到达。取值（Luna `[high* / xhigh / max]`、Astra worker `[medium* / high | xhigh]`、Astra 与 Fable advisor `[medium / high* | xhigh]`、grok light `[medium* / high | xhigh]`、grok standard `[high / xhigh*]`、Opus `[medium / high*]`）由用户写进 prompts 仓库的路由档案；runner 的省略默认值（luna → `max`）是机制事实，不覆盖档案。`lanes-claude-code.md` 的"quality-first / Escalate to high"段删除。
5. **调用方保留的操作经契约与前言传递。** 契约第 4 部 Constraints 定义加"调用方留在自己会话里的操作"，约束车道、其子代理与验证命令；前言姿态段加一句：这些保留操作仍约束执行者及其子代理，需要时在 GAPS 报告并继续不受阻的部分，不执行、不谎称通过。前言仍是三段。
6. **执行记录三层表述。** `model_requested` 是 spec 请求值；`model_used` 与 `effort` 是 runner 提交给 CLI 的值（回退后为重试值，`run-codex.mjs:653`、`:703`，`run-grok.mjs:606`）；runner 不读 CLI 运行事件，实际执行配置保持未知，引用时写 "submitted, not observed"。Cursor 侧 pin 是请求值，标 "requested, not confirmed"。只改文档，不改 runner。
7. **explorer 入口只做文档要求，agent 文件待核。** claude 车道的 explorer 派发须带显式按次 `model`；内置 Explore 省略时继承会话模型（Claude API 上限 Opus）与会话 effort。是否新增 `plugin/agents/explorer.md` 推到工单 08：先在真实会话核对"内置 Explore + 按次 `model`"是否满足取证契约与 effort 控制，再决定，不预选默认别名。
8. **宿主事实更新。** 等待协议按官方工具参考改为 `Read` 任务输出文件（`TaskOutput` 已弃用，弃用不等于不可用）；README 模型解析顺序改为按次参数 → frontmatter → `CLAUDE_CODE_SUBAGENT_MODEL`（v2.1.251 起）；`SKILL.md` 深度句补 Claude Code 嵌套上限三层；`service_tier: "fast"` 语义改正；竞赛须各自隔离工作树，不同 pending 文件名不构成隔离；宿主判别改为按所在宿主与工具参数结构，不凭单个工具名。
9. **报告生命周期按宿主写。** 完成通知不是报告；报告缺失先读输出文件与工作区确认状态，再按缺口恢复，确需重跑才重派，不用 `resume` 催。`SKILL.md:141` 的跨宿主句删除。
10. **描述与规则去重。** 技能描述压到约 35 词（目标，不是硬限）；两个 agent 描述压短，不再复述门清单与路由理由；`worker.md` 三条披露改为一行自查（不称 second reader）、验证催促句删除、错误处理句限定到自己的 diff；"highest unit price" 三处删除；Claude 主代理视角残句改写。
11. **仓内文档细节。** README 安装地址改为本分叉 `IpiggyI/fable-advisor` 并保留上游署名；`/model fable` 块、v3–v4 升级史删除；Requirements 与 Cursor 段压缩为指针；发布步骤改显式暂存加 `git diff --cached --stat`（`.scratch/` 受跟踪、`outputs/` 未忽略，`-A` 会带入在途稿）；版本规则三类；缓存抽查删 `test ! -d`；`domain.md` 删模板句与目录树；`triage-labels.md` 删重复映射列。
12. **版本 5.1.0。** 前言语义、doctrine 语义、存档退役，均向后兼容。

## 未采纳

- 再把 `SKILL.md` 拆出派发细则文件（GPT N02）：省约 1.2k 词，但 ADR 0012 复盘条件"指针被跳读"风险仍在，暂不做。
- 收窄低置信度逃生门（GPT Q02）：ADR 0006 决策，触发稀少，不改。
- 删 `docs/agents/issue-tracker.md` 的 Wayfinding 段：仓内无 `map.md` 只证明尚未用，不证明不用。
- 同族多步改动的 Tier 3 条件不放宽（Q01 的另一半）。
- 把三条披露删除记为 ADR 0014 决策 10 的变更：那三条来自 `.scratch/role-pool-posture/spec.md`，不是 ADR 决策。

## 实施

工单 `.scratch/global-orchestration-handoff/issues/01`–`07`。编排姿态：01–03（doctrine 散文）同模派发；04、05、06 grok 车道；07 协调件架构师亲写。advisor 验收形状（Fable，Cursor 本轮 allowlist 唯一 Fable 变体为 xhigh）裁决 ACCEPT-WITH-REWORK：一处返工（README 合并片段对同一门下两次指令）、一处契约不一致（Tier 3 触发条数）返工补齐；两处返工复用原车道会话；返工后 `SKILL.md` 1952 词，词数上限相应改为 1960。终态：五个测试脚本全绿，`git diff --check` 干净，退役短语零命中，六对中英文件标题数一致。为满足 ≤ 1950 词，01 车道在契约之外删了六句与文中其他段落重复的句子（Stage 1 尾句、Stage 2 handoff 条件成员句、"senior 亦可首选"、"契约没说怎么做不是缺口"、姿态段"门约束两种姿态"、档案条目须带前置条件与失效条件句），各有同文他处覆盖，验收时接受；最后一句的要求（档案条目带日期与失效条件）随档案归 prompts 仓库维护。

## 复盘条件

- 工单 08 核对结果：内置 Explore 加按次 `model` 若不能钉住 effort 或取证形状不稳 → 新增 `explorer.md`，默认值届时定。
- 决策 3 之后，编排姿态下同族多步改动漏判累计 ≥2 次 → 重议 Tier 3 触发或恢复按步数项。
- `SKILL.md` 再增长到 1950 词以上 → 重议 N02 拆派发文件。
- 任一宿主提供子代理实际模型 / effort 的机器可读入口 → 更新决策 6 的三层表述，考虑 receipt 增加观测字段。
- prompts 仓库未按决策 4 的记法更新档案 → 括号记法在档案里无对应，重议记法是否入仓。

## 备注

- 官方依据（2026-09-13 读取）：Claude Code sub-agents（Explore 继承与 Opus 上限、effort 只在 agent 文件或 `--agents`、解析顺序、嵌套三层、`/tasks` 显示模型与 effort）、tools reference（`TaskOutput` 弃用）、Codex speed（fast 模式语义）、OpenAI Astra 提示词文。
- 部署顺序归 prompts 仓库与用户：先部署 `fable-advisor-routing.md` 到两侧 `~/.claude/docs/`，再换全局入口，Cursor 真实会话确认后撤旧规则活体。本 ADR 不授权提交、推送、发布或改用户目录。
- 转出项（prompts 仓库文本、用户目录清理）见工单 09。

## 追记（2026-09-16）：工单 08 核对结果，决策 7 定案

核对在 Claude Code 2.1.273（WSL）真实会话完成，会话模型 `claude-opus-5`、档位 xhigh，装的插件仍是 5.0.0。证据取自子代理转写 `~/.claude/projects/<项目>/<会话>/subagents/agent-*.jsonl` 与同名 `.meta.json`：meta 记请求模型，转写每条 assistant 记录带实跑 `model` 与 `effort`。完整记录见 `.scratch/global-orchestration-handoff/issues/08-explorer-probe.md` 的 `## Comments`。

**测到的三件事。** 一，按次 `model` 生效：内置 Explore 带 `model: sonnet` 实跑 `claude-sonnet-5`，不带时实跑会话模型。二，子代理 effort 不继承会话，而是取"它实际运行的那个模型"的配置档位（本机 `~/.claude/settings.json` 的 `effortLevel` 与 `modelSettings`）；只有子代理模型与会话模型相同时两者才相等。三，内置 Explore 持有 Bash，探针实际用它跑了 `rg`，因此角色表承诺的 explorer 只读权限在内置 Explore 上不成立。成本侧，同一取证契约下 sonnet/medium 用 1,964 输出 token、3 次工具调用，opus/xhigh 用 4,566 输出 token、7 次工具调用，证据质量相同。

**决策 7 定案：新增 `plugin/agents/explorer.md`，但不写 effort 声明。** 采纳 advisor 的 C 裁定。理由是能力边界而非成本：`tools: Read, Grep, Glob` 关掉 Bash 写入口，与 `fable-advisor.md` 的既有约定一致；正文承载只读取证契约，收敛实测到的报告形状漂移（有的自加小标题，有的用绝对路径）。不写 `effort:` 的理由见下一条。落地改动在工单 10，本 ADR 不授权提交、推送、发布。

**新的未决项：agent 文件的 `effort:` 与 `model:` 是否被执行。** 四次涉及 agent 文件的派发中，转写的 `effort` 没有一次等于文件声明值，每次等于实跑模型的设置档位；`fable-advisor.md` 的 `model: fable` 有两次整程落在 `claude-sonnet-5`，一次跑到中途从 fable 切走。因此 `lanes-claude-code.md:5` 称 `worker.md` 的 `effort: medium` 与 `fable-advisor.md` 的 `effort: high` 是"role defaults on this lane"，这一说法待证，不能再复制到第三个文件。限定条件：本轮会话设了 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`，派发走 teammate 路径而非经典 Task 子代理路径，该结论未在经典路径验证。`/tasks` 判不了这一项——团队模式下它不显示模型与档位（见下条），所以唯一的分辨手段是在未开该变量的会话里重跑同批探针。

**证伪的仓内表述（工单 10 必改）。** 其一，`lanes-claude-code.md:3`、`:5` 与 `SKILL.md:62` 的"继承会话 effort"改为"取实跑模型的配置档位"。其二，`lanes-claude-code.md:5` 的"`/tasks` 显示每个子代理的实际模型与 effort，是用户侧观测点"实测不成立：三个 sleeper 运行中执行 `/tasks`，输出只有成员名与状态（`@probe-g2-worker-frontmatter: Running Sleep for 600 seconds`），既无模型也无档位。该观测限定在开了 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 的团队模式；官方文档另有限定——档位只在子代理定义或其 fork 的技能设了 `effort` 时才显示，因此对内置 Explore 的派发本来也不显示。改法：不再称它为用户侧观测点，改指子代理转写。

**复盘条件更新。** 原"工单 08 核对结果"一条结清。新增两条：在未开 agent-teams 的会话里重跑同批探针，若 frontmatter 的 `effort:` 生效 → 给 `explorer.md` 补档位声明并改回 `lanes-claude-code.md:5`；若 `fable-advisor` 派发继续落在 Sonnet 而非 Fable → 填充表的 advisor 条目失去前置条件，须在路由档案重议。原"任一宿主提供子代理实际模型 / effort 的机器可读入口"一条已触发：Claude Code 的子代理转写就是该入口，决策 6 的三层表述可据此加一句——claude 车道的实跑模型可观测，但 meta 的请求值与实跑值会不一致。

**未测项。** 插件级同名 `Explore` 能否覆盖内置未测，须先发布并安装 5.1.0；官方文档只保证用户级与项目级覆盖，且优先级表把插件 `agents/` 列为最低一级，本会话所见插件 agent 均带命名空间前缀（`fable-advisor:worker`），因此不能假定覆盖成立。工单 10 的 doctrine 句子按"新增一个具名 agent"写，不依赖覆盖。
