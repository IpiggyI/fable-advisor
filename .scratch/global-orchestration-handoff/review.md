# 全局编排交接清单的审查意见

Status: needs-info

日期：2026-09-13。审查对象：[待执行清单](spec.md)。本文件发布修改建议，供椰椰确认；发布意见不代表批准实施，也不修改原清单的状态。插件规则、业务代码、用户配置和部署副本均未修改。

## 审查结论与依据

清单覆盖了主要问题，但应先修正事实、拆开不同的行为变更，再作为执行依据。优先处理配置默认值、报告恢复、验收触发和部署说明；减少验证与调整权限边界的建议单独列于本文后部。

审查依据包括以下文档及 2026-09-13 读取的官方资料：

- [插件交接文档](../../docs/fable-advisor-orchestration-handoff-2026-09.md)。
- [ADR 0014：角色池与姿态](../../docs/adr/0014-role-pool-posture.md)。
- [全局提示词工作副本](/mnt/d/Development/Local/prompts/current-prompts/CLAUDE.en.md)及[用户路由档案](/mnt/d/Development/Local/prompts/current-prompts/docs/fable-advisor-routing.md)。
- [OpenAI：重新思考 Astra 的技能与提示词](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra.md)。
- [Claude Code：子代理](https://code.claude.com/docs/en/sub-agents)、[模型配置](https://code.claude.com/docs/en/model-config)及[工具参考](https://code.claude.com/docs/en/tools-reference)。
- [Cursor：子代理](https://cursor.com/docs/subagents)。
- [OpenAI：Codex 速度选项](https://developers.openai.com/codex/speed.md)。

OpenAI 文章支持精简描述、按需加载和减少重复催促，同时提醒：

> Guidance that helps Sol or Luna may overconstrain GPT-6 Astra.

本插件服务多个模型。建议保留明确的任务契约和质量标准，优先删除重复要求、错误机制描述和没有实际作用的停顿，不直接把 Astra 的能力判断推广到所有执行者。

## 对现有条目的修改意见

### R01：D1、D2 应分开记法、默认值和首轮限制

位置：`spec.md:73`、`:74`；[当前路由档案](/mnt/d/Development/Local/prompts/current-prompts/docs/fable-advisor-routing.md)第 13、15、16 行；[ADR 0014](../../docs/adr/0014-role-pool-posture.md)第 135 行。

原文：

> efforts outside the bracket are reached only by escalation after a failed rework ticket or by user declaration

> claude-fable-5-1[high* / xhigh]

问题：第一句把执行者返工规则扩大到了所有角色；第二句仍允许 Fable 首轮选择 `xhigh`，不符合本次要求。运行器的 Luna 默认 `max` 也不能覆盖用户档案中显式指定的 `high`。旧的“Luna 只值得 max”策略落点已被 ADR 0014 废止。

建议：分别表达用户可选范围、默认值和首轮限制。默认值按角色保留，升级条件另行说明。以下为沿用现有角色默认值的提案，尚待确认：

| 模型及角色 | 建议记法 | 首轮范围 |
|---|---|---|
| Luna 的现有轻量角色 | `[high* / xhigh / max]` | 三档均可选择。 |
| Astra 执行者 | `[medium* / high / xhigh]` | 可选 `medium`、`high`。 |
| Astra 顾问 | `[medium / high* / xhigh]` | 可选 `medium`、`high`。 |
| Fable 顾问 | `[medium / high* / xhigh]` | 可选 `medium`、`high`。 |

影响：避免移动配置时顺带改变角色默认值，或引入所有角色都必须先经历返工失败的新门禁。表格表达用户策略，不代表模型 API 的完整支持范围。

### R02：A3、D4 应区分用户首选、角色配置和执行观测

位置：`spec.md:27`、`:76`；[worker.md](../../plugin/agents/worker.md)第 5、18 行。

原文：

> frontmatter `effort` 即该角色的 `*`

> 车道内升级只能换 `model` 或另建 agent 文件

问题：用户首选、角色文件配置和宿主实际应用值属于三个层次。仅换模型不会自动改变 `worker.md` 中固定的 `effort: medium`。

官方子代理文档确认：从 Claude Code `v2.1.198` 起，内置 Explore 继承模型，但 Claude API 有 Opus 上限；角色文件可以覆盖推理强度，`--agents` 定义也支持 `effort`。本机版本符合上述版本条件，但本轮没有运行真实探索场景。

建议：先确定显式配置的调用方式，再决定是否需要新增探索角色。若新增，理由应是稳定的取证契约和可控配置；不必先要求用户选择一个尚未验证必要性的默认别名。不能把“当前按次调用参数未提供 effort”推广成“所有入口都只能写角色文件”。

影响：减少不必要的角色文件，避免把请求配置写成已经生效的事实。

### R03：A5 不应默认重派；B10 可更新等待机制

位置：`spec.md:29`、`:46`；[lanes-claude-code.md](../../plugin/skills/orchestration/lanes-claude-code.md)第 49–60 行。

原文：

> 报告缺失用同一契约重派，不用 `resume` 催

> TaskOutput(task_id, block=true)

问题：写入可能已经完成，只是报告没有取回。重派原契约可能重复修改。Claude Code 官方工具文档已将 `TaskOutput` 标为弃用，并推荐读取任务输出文件。

建议：先读取已有输出，确认任务状态和工作区，再按具体缺口恢复；只有确实需要重新执行时才重派。按宿主实际入口更新等待说明，不把“不催报”写成跨宿主定律。弃用不等于当前不可用，兼容说明应保留这个区别。

影响：避免重复执行和固定等待浪费。`B10` 中 `README.md` 最低支持版本仍需单独核验，不能由本机当前版本推出。

### R04：A6、A9、C14 应完整修正机制表述

位置：`spec.md:30`、`:33`、`:66`；[lanes-claude-code.md](../../plugin/skills/orchestration/lanes-claude-code.md)第 25、70、109 行；[当前路由档案](/mnt/d/Development/Local/prompts/current-prompts/docs/fable-advisor-routing.md)第 20 行。

原文：

> The receipt records the values actually used.

> Cursor exposes `Shell` and a `Task` model allowlist; Claude Code exposes `Bash` and the runner scripts.

当前路由档案原文：

> Where a cell does not specify an effort, use the role default above.

建议：统一修正所有把提交配置表述为实际观测的句子，不能只补第 70 行。分别描述请求值、提交值和执行观测值；未观测到的层保持未知。宿主判别优先依据当前宿主身份和工具参数结构，不能仅凭 `Bash`、`Shell` 或是否有 `model` 参数判断。

`C14` 引用的旧句已不存在，应围绕当前句子检查角色默认值如何映射到 Cursor 的实际模型选项。Cursor 官方文档描述了自定义子代理的模型配置；插件加载入口的历史限制不能未经实测就推广到所有入口，也不能凭通用文档直接删除现有显式指定要求。

影响：消除文档内部矛盾，避免把部分入口的能力结论写成宿主的永久限制。本条不要求修改运行器代码。

### R05：B4 不应把作者自查称为第二位读者

位置：`spec.md:40`；[worker.md](../../plugin/agents/worker.md)第 14 行；[ADR 0014](../../docs/adr/0014-role-pool-posture.md)第 100 行。

原文：

> Read your own diff as its second reader before you report

建议：改为普通作者自查要求，或者依赖统一执行者契约。作者自查不能满足“另一位读者”的要求。ADR 0014 决策 10 没有规定三条披露，因此无需为删除披露重复而追加一个并不存在的决策变更理由。

影响：减少重复，同时避免误算独立审查已经完成。

### R06：C13 只能删重复列，不能删状态含义

位置：`spec.md:65`；[triage-labels.md](../../docs/agents/triage-labels.md)第 5–11 行。

原表头：

> Label in mattpocock/skills | Label in our tracker | Meaning

建议：删除重复的标签映射列，保留“状态、含义”两列。原表第三列解释五个状态的不同用途。

影响：压缩表格而不丢失状态使用规则。直接列出五个取值会丢掉这部分语义。

### R07：C8、C9 应保留发布边界的机制依据

位置：`spec.md:60`、`:61`；[plugin-release.md](../../docs/agents/plugin-release.md)第 12、45–55 行。

原文：

> marketplace.json sets `"source": "./plugin"`

> copies that directory wholesale

> does not honor `.pluginignore` or `export-ignore`

建议：删除目录枚举，保留以上发布边界及其依据。将可选抽查改为针对本次发布内容的检查，不把“不可能进缓存”当作已验证事实。

影响：减少无益细节，同时保留排查发布内容错误所需的信息。版本目录存在不能单独证明实际加载了正确内容；删除检查的影响另见敏感建议表。

### R08：A7、C6 的部分待定项已有依据

位置：`spec.md:31`、`:58`；[cursor-lane-gate.md](../../docs/agents/cursor-lane-gate.md)第 38–48 行；[plugin-release.md](../../docs/agents/plugin-release.md)第 3 行；[提示词仓库指南](/mnt/d/Development/Local/prompts/AGENTS.md)第 29、30 行。

原文：

> Canonical rule: `cursor-hooks/fable-lane-pin.mdc`.

> The installed marketplaces on **both** sides point at GitHub (`IpiggyI/fable-advisor`), not at this working tree

建议：保留插件仓库作为 Cursor 模型指定规则的编辑源，提示词仓库副本注明部署用途。当前 提示词仓库指南没有再次声明自己是该规则的权威源。`README.md` 安装地址建议与本分叉仓库 的部署目标一致，保留上游署名和链接。

删除整个 `user-rules/` 会同时删除 `zh/fable-lane-pin.mdc`。`A7` 必须处理这份中文备份及其引用，不能只删除两组漂移检查。

影响：减少重复决策，明确维护来源，并避免留下指向已删除备份的部署说明。

## 建议补入清单的遗漏项

| 编号 | 位置及原文 | 调整建议及影响 |
|---|---|---|
| N01 | [SKILL.md](../../plugin/skills/orchestration/SKILL.md)第 100–106 行：“Every dispatch carries five parts”，并统一要求验证命令。 | 按角色区分契约。执行者需要改动与验证证据；探索者和顾问可以返回来源与判断。报告模式已经允许验证命令为空，根文档应与之相容，避免给只读问题制造测试任务。适用检查仍须完成。 |
| N02 | [SKILL.md](../../plugin/skills/orchestration/SKILL.md)第 76–141 行完整承载路由、返工、契约、并行和验收细则；`B1` 只压缩描述。 | 将仅在派发或验收时需要的细则按需加载，根文件保留姿态、责任边界和准确指针。不要把“35 词以内”变成新的硬门禁。 |
| N03 | [全局提示词](/mnt/d/Development/Local/prompts/current-prompts/CLAUDE.en.md)第 3、33、81 行分别要求披露、检查点和“a verification plan listing each step and its executable check in order”。 | 合并重复的阶段说明。简单改动说明验证方法即可，依赖复杂或风险较高时再列逐步计划。减少重复输出，不删除必要检查。 |
| N04 | [全局提示词](/mnt/d/Development/Local/prompts/current-prompts/CLAUDE.en.md)第 60、64 行分别规定函数超过 30 行便“propose a split”、参数超过五个便“wrap into an object”。 | 数字仅作为观察线索，取消机械对应的动作。是否调整应依据职责或接口问题，避免在无关任务中提出重构。 |
| N05 | [lanes-claude-code.md](../../plugin/skills/orchestration/lanes-claude-code.md)第 29 行称 `fast` 用于“trading quality for speed”。 | 按 OpenAI 官方说明改成增加额度消耗以提高速度，避免混淆服务档位和推理强度。 |
| N06 | `A3` 考虑并入报告前言工单；[现有工单 10](../role-pool-posture/issues/10-report-mode-preamble.md)第 9 行明确涉及两条运行器的前言加载。 | 保持为后续独立范围。文档审查不能顺带授权业务代码实施；不能只改描述就宣称报告前言已完成分流。 |

## 单列：安全、权限边界或减少验证

本节每项均为待确认建议。确认普通文字精简不自动批准本节的行为变更。

| 编号 | 对应条目及原文位置 | 建议与潜在影响 |
|---|---|---|
| Q01 | `S1`；[SKILL.md](../../plugin/skills/orchestration/SKILL.md)第 129 行要求“before declaring a multi-step deliverable done”，第 139 行另要求“correctness-critical work, and same-family diffs”。 | 拆开“取消按步数触发的终审”和“缩小同族改动审查范围”两个决定。可以考虑取消纯粹按步数触发的终审，但保留高风险、明确要求评审及现有同族条件。主代理仍须检查实际改动，不能仅靠文件统计替代。 |
| Q02 | 新增；[SKILL.md](../../plugin/skills/orchestration/SKILL.md)第 96 行要求高风险任务在偏好未声明时询问用户。 | 仅在资源限制或用户偏好会改变选择时询问；已有默认策略能够决定时继续执行必要评审。减少路由确认，不扩大操作授权。 |
| Q03 | `B3`、`S4`；[worker.md](../../plugin/agents/worker.md)第 27 行：“no swallowed catches, no TODOs left behind”。 | 分开处理验证催促、错误处理约束及未完成事项。前言并未等价覆盖全部错误处理要求；“不留 TODO”也可能误伤范围外已有事项。不能把两条全部删除统称为验证要求不变。 |
| Q04 | 新增；[全局提示词](/mnt/d/Development/Local/prompts/current-prompts/CLAUDE.en.md)第 70 行要求至少记录异常处理和外部调用：“at minimum log error handling (catch blocks) and external calls”。 | 在合适边界记录可诊断的失败，避免每层捕获、每次成功调用重复记录。保留显式失败和禁止记录敏感数据的要求。此项会减少部分诊断输出。 |
| Q05 | `A4`、`S3`；[lane-preamble.md](../../plugin/skills/orchestration/lane-preamble.md)第 1 行：“machine-level … rules do not apply to this task”。 | 支持补强调用方保留操作的传递。姿态豁免不能扩大权限，验证命令和后续委派同受约束。遇到保留操作时报告具体缺口，并继续不受影响的工作。 |
| Q06 | `A7`、`C9`；清单建议删除旧规则漂移检查和缓存排除检查。 | 先明确迁移后的校验对象，保留模型指定规则的漂移检查。删除检查属于验证覆盖变化，不能仅为消除旧检查失败而删除。 |
| Q07 | `A8`、`C15`；[提示词仓库部署指南](/mnt/d/Development/Local/prompts/AGENTS.md)第 51 行：“Keep reviewed prior copies for recovery”。 | 保留可用恢复版本，将其余备份清理列为独立可选项。旧中文文档注明“不参与加载”，删除它不会减少当前提示词上下文。用户目录删除需要单独授权。 |
| Q08 | 新增；[发布步骤](../../docs/agents/plugin-release.md)第 21 行：“git add -A && git commit && git push origin main”。 | 改为显式暂存本次发布文件并检查暂存差异，避免带入现有交接稿、清单和 `outputs/`。此项调整发布操作边界，不授权执行提交或推送。 |
| Q09 | 新增；[SKILL.md](../../plugin/skills/orchestration/SKILL.md)第 118 行建议两个执行者竞争同一契约；[宿主说明](../../plugin/skills/orchestration/lanes-claude-code.md)第 81 行仅强调不同待执行文件。 | 明确工作目录和执行记录也要隔离。不同文件名不能防止两个执行者覆盖同一份交付物。此项为文档层面的并行写入边界补充，本轮未审查运行器实现。 |
| Q10 | `A1`、`S2`；[SKILL.md](../../plugin/skills/orchestration/SKILL.md)第 14 行：“Exploration, searches, and log-grepping go to an explorer”。 | 支持允许已知小范围查询由主代理直接读取。影响是减少强制派发、由主代理判断上下文成本；不改变已生效的编排姿态下交付物必须经执行者修改的规则。 |

## 支持保留或精简的项目

- 支持 `A1`、`A2` 的迁移方向，按本文对有界直读、配置来源和行为边界的限定处理。
- 支持 `B1`、`B2` 缩短描述；若 `S1` 发生变化，角色描述中的验收触发条件必须同步，避免再次双写。
- 支持 `B5`、`B6` 删除固定价格排名和 Claude 主代理视角残句，支持 `B7`、`B8`、`D3` 将模型偏好留在用户配置；模型支持范围和运行器默认值仍作为机制事实维护。
- 支持 `B9` 删除过时目录树和不再适用的模板残句，保留现有决策入口。
- 支持 `C1` 至 `C5` 压缩 `README.md` 重复细节，但保留安装前置条件、必要兼容性说明及仍需执行的迁移动作。
- `C7` 的版本规则应区分破坏兼容、向后兼容的语义变化及纯文字修正，不能把所有语义变化一概定为次版本更新。最终版本根据获批范围决定。
- 支持 `C10`、`C11` 去重，但保留权威文件路径、两侧部署路径和更新步骤。
- `C12` 的“从未使用过”尚无充分证据，不据此直接批准删除整个流程。
- 保留 `B11` 中有明确范围的姿态边界和已有故障依据的等待、登录态说明；若现行宿主接口变化，更新对应操作方式。
- 保留 `S5`、`S6` 的执行记录门和显式模型指定门，以及 `S7` 交接车道的亲自验证要求。本轮不对其代码实现或实际隔离效果作通过结论。
- “核心规则（1–14）”在当前全局工作副本中已经没有，无需重复立项。

## 官方与上游更新的取舍

已核对上游提交 [`4d6cc62164619a279b076439e1af5439892b958a`](https://github.com/DannyMac180/fable-advisor/commit/4d6cc62164619a279b076439e1af5439892b958a)的[技能正文](https://github.com/DannyMac180/fable-advisor/blob/4d6cc62164619a279b076439e1af5439892b958a/skills/orchestration/SKILL.md)。上游仍采用固定 Fable 架构师和强制终审，不能直接替换本分叉仓库 的角色池与姿态策略。

本轮明确可吸收的更新主要来自官方文档：Astra 的提示词精简原则、Claude Code 的探索继承及配置语义、任务输出读取方式，以及 Codex 的速度选项说明。Cursor 自定义角色文档与插件加载入口的差异仍须限定结论范围，不能未经真实入口验证就移除已有模型指定要求。

## 证据与验证边界

- 发布前重新读取了原清单。源仓库 `HEAD` 为 `ec36345`；工作树已有未跟踪的本清单目录、两份交接文档和 `outputs/`。这些内容保留。本文件是此次发布新增的唯一文件。
- 审查读取了插件技能、角色文档、相关 ADR、仓内部署文档、提示词仓库工作副本及已定位的两侧用户文件。外部链接和宿主能力结论以 2026-09-13 的读取结果为依据；后续版本或配置变化时，重新核对对应结论。
- `claude --version` 返回 WSL `2.1.270`、Windows `2.1.267`。这只证明已安装版本，不证明插件功能、模型分配或真实入口加载正确。
- 两次协作调用显式请求了 Luna `max`、Astra `high`。宿主回执未暴露可独立核验的实际模型及推理强度，不把请求值当作执行证明。
- 没有审查业务代码、运行插件测试或执行真实宿主行为场景。执行记录字段的赋值语义来自交接文档已有调查，本轮核对的是文档一致性，未重新审查运行器赋值代码。
- 本次发布仅检查文档结构、本地链接目标、原文摘录和改动范围。文档检查不能证明建议实施后的行为，也不能证明实际效率提升。

确认后，按获批编号修订原清单并拆分实施范围。本文不授权提交、推送、发布插件或修改用户目录。
