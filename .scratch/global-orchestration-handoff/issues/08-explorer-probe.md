# 08: explorer 入口核对（A3b）

**What to build:** 在更新到 5.1.0 的插件上，于 Claude Code 真实会话核对"内置 Explore + 按次 `model`"能否满足只读取证契约与 effort 控制，据结果决定是否新增 `plugin/agents/explorer.md`。

**Status:** needs-info

**Blocked by:** 07（发布）；用户授权两侧 `claude plugin update`

## 核对项

1. 高档主会话（Fable 或 Opus，高 effort）派内置 Explore 并带按次 `model`（如 `sonnet`）：`/tasks` 显示的模型是否为指定值；effort 是否仍为会话值（官方文档：子代理 effort 默认继承会话，只能在 agent 文件或 `--agents` 定义中覆盖）。
2. 同一任务不带 `model`：`/tasks` 显示是否为会话模型（Claude API 上限 Opus）。
3. 若 effort 继承导致明显浪费，或取证报告形状不稳定，则新增 `explorer.md`：`tools: Read, Grep, Glob`、`effort: medium`、正文只读取证契约；`model:` 默认值届时按路由档案定，不预选。官方文档另记：用户或项目级同名 `Explore` agent 可覆盖内置并保留自己的 `model`，插件级是否同样生效需实测。
4. Cursor 侧：`explore` 加显式 slug 已满足要求，不另建。
5. 新增 agent 文件时同步 `docs/zh/agents/explorer.md`、`SKILL.md:62`、`lanes-claude-code.md:3`，并与工单 `.scratch/role-pool-posture/issues/10-report-mode-preamble.md` 的报告前言单源协调，但不合并实施。

## 产出

核对记录（模型、effort 的证据来源与截图或 `/tasks` 文本）写入本文件 `## Comments`；结论进 ADR 0015 追记。

## Comments

### 2026-09-16 核对记录（第一轮）

**环境与偏差。** 宿主 Claude Code 2.1.273（WSL），会话模型 `claude-opus-5`，会话档位 `effort=xhigh`。已装插件仍是 5.0.0（`~/.claude/plugins/cache/fable-advisor/fable-advisor/5.0.0/`），仓内工作树是未发布的 5.1.0。**偏差说明**：工单要求"在更新到 5.1.0 的插件上"核对，本轮未满足这一前置——07 未提交推送，两侧 `claude plugin update` 未授权。核对项 1、2 测的是宿主机制（按次 `model` 解析、子代理 effort 取值），与插件版本无关，故照常执行；核对项 3 中"插件级同名 agent 是否覆盖内置"确实依赖新装插件，本轮未测。

**证据来源。** 比 `/tasks` 更强的机器可读入口：`~/.claude/projects/<项目>/<会话>/subagents/agent-*.meta.json` 记请求模型，同名 `agent-*.jsonl` 每条 assistant 记录带 `model` 与 `effort` 字段。用户目录无 `~/.claude/agents/`、本仓无 `.claude/agents/`，故 probe A/B/C 用的是真内置 Explore，无用户级或项目级覆盖干扰。

**核对项 1（带按次 `model`）。** probe-a：`subagent_type: Explore` + `model: sonnet`，同一只读取证契约。meta `"model": "sonnet"`；转写 `model=claude-sonnet-5`、`effort=medium`。→ 按次 `model` 生效；**effort 不是会话值 xhigh**，与工单假设（子代理 effort 默认继承会话）不符。

**核对项 2（不带 `model`）。** probe-b：转写 `model=claude-opus-5`、`effort=xhigh`，等于会话模型与会话档位。对照 probe-c（显式 `model: opus`，与会话同）：`claude-opus-5`、`xhigh`。

**机制。** 规则不是"显式 `model` 就重置 effort"，而是**子代理 effort 跟它实际运行的那个模型的配置档位走**。本机 `~/.claude/settings.json` 有 `"effortLevel": "medium"` 与 `"modelSettings": {"claude-opus-5": {"effortLevel": "xhigh"}}`；opus 取 xhigh，其余模型取 medium，三次观测全部吻合。只有当子代理模型与会话模型相同时，它才等于"会话 effort"。因此 `lanes-claude-code.md:3`、`:5` 与 `SKILL.md:62` 的"继承会话 effort"是不准确的表述（本机设置下可复现；换一台机器的 `effortLevel` 取值会变，结论的形式是"跟模型配置走"，不是"一定是 medium"）。

**成本对比（同一契约，A 对 B）。** output tokens 1,964 对 4,566；cache_read 122,762 对 207,487；cache_creation 98,468 对 136,842；工具调用 3 次对 7 次。两份证据都正确。叠加 Sonnet 与 Opus 的单价差，不钉模型的 explorer 贵约一个量级而产出等价 —— 工单"effort 继承导致明显浪费"的判据成立，但成因是模型档位，不是 effort 继承本身。

**报告形状。** 三次都交付了 `FINDINGS` / `GAPS`、`file:line`、逐字引用，实质稳定；装饰层不稳：probe-b 自行加了 `**(a)** / **(b)**` 小标题并改用引号，probe-c 用绝对路径而非仓相对路径。契约写死了格式仍出现漂移。

**权限边界（工单未列，本轮发现）。** 内置 Explore 不是只读角色：它持有 Bash（probe-a、probe-b 实际用 Bash 跑 `rg`/`grep`），Bash 可经重定向写文件。"explorer = 只读"这一角色属性在内置 Explore 上不成立，只靠提示词约束。

**未决冲突：frontmatter `effort` 是否真的生效。** probe-d（`fable-advisor` agent，frontmatter `effort: high`，按次 `model: sonnet`）转写 `effort=medium`；probe-e（同 agent，不带按次 `model`，实跑 `claude-fable-5-1`）转写仍 `effort=medium`。两次都等于该模型的设置档位，不等于 frontmatter 的 `high`。官方文档（2026-09-16 读取 https://code.claude.com/docs/en/sub-agents）的 frontmatter 表写 `effort` "Overrides the session effort level"。→ 两种解释：转写的 `effort` 字段记的是设置解析值而非实际下发值；或 2.1.273 上 agent 文件的 `effort` 未生效。`worker.md` 的 `effort: medium` 与 `fable-advisor.md` 的 `effort: high` 都压在同一机制上，`lanes-claude-code.md:5` 称它们是"role defaults on this lane"，此说待证。待用户粘贴一次 `/tasks` 文本（probe-f：Explore + sonnet，定义无 effort；probe-g：`worker`，定义 `effort: medium`，实跑 opus 而设置为 xhigh）以对照显示值。

**官方文档核对（2026-09-16 读取，code.claude.com/docs/en）。**
- 模型解析四级：按次 `model` → frontmatter `model:`（`inherit` 取主会话模型）→ `CLAUDE_CODE_SUBAGENT_MODEL` → 主会话模型（v2.1.251 起为此顺序）。与 probe-a/b/c 一致。
- effort 无按次参数，只有 frontmatter `effort`；子代理默认继承会话 —— 本轮观测显示实际按模型档位取值，与文档表述不一致。
- `/tasks`：显示子代理所用模型；**仅当子代理定义或其 fork 的技能设了 `effort` 时才附带显示档位**（v2.1.242 起）。→ 对内置 Explore 的派发，`/tasks` 根本不显示 effort，工单核对项 1 想用 `/tasks` 观测 effort 这条路对内置 Explore 不通，转写字段是更强的入口。
- 覆盖与优先级：文档只写"用户级或项目级同名 `Explore` 覆盖内置并保留自己的 `model`"；优先级表 plugin 的 `agents/` 最低（第 5 级）。本会话观察：插件 agent 以命名空间出现（`fable-advisor:worker`），内置 `Explore` 无前缀。→ 插件级同名覆盖不能假定成立，本轮未实测（需先发布并安装 5.1.0）。

### 2026-09-16 核对记录（第二轮：agent 文件的 model 与 effort）

**环境限定。** 本会话设了 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`，所有派发走 teammate 路径（meta `"taskKind": "in_process_teammate"`），不是官方文档描述的经典 Task 子代理路径；另设 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`；环境无 `CLAUDE_CODE_SUBAGENT_MODEL`。核对项 1、2 的模型解析结论与官方四级顺序一致，可外推；下面 frontmatter 与模型替换两项只在 teammate 路径实测过，**未在经典路径验证**。失效检查：在未设 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 的会话里重跑 probe-d / probe-g / probe-h。

**frontmatter `effort` 与转写不符，四次一致。**

| 派发 | agent 文件声明 | 按次 `model` | 实跑模型 | 转写 `effort` | 该模型的设置档位 |
|---|---|---|---|---|---|
| probe-d | `fable-advisor`：`effort: high` | sonnet | `claude-sonnet-5` | medium | medium |
| probe-e | 同上 | 无 | `claude-fable-5-1` → `claude-sonnet-5` | medium | medium |
| probe-g | `worker`：`effort: medium` | 无 | `claude-opus-5` | xhigh | xhigh |
| advisor 决策派发 | `fable-advisor`：`effort: high` | 无 | `claude-sonnet-5` | medium | medium |

转写的 `effort` 没有一次等于 agent 文件的声明值，每次都等于"实际运行模型"的设置档位。两种解释未分辨：转写字段记的是设置解析值而非下发值；或插件 agent 的 `effort:` 在此路径不生效。注意 `/tasks` 按官方说明只在"子代理定义或其 fork 的技能设了 `effort`"时显示档位，显示的可能同样是声明值 —— 它能暴露两者不一致，未必能判定哪个是执行值。

**模型替换反常。** advisor 决策派发 meta 记 `model: fable`（frontmatter 值），十轮 assistant 记录全部是 `claude-sonnet-5`；probe-h（同 agent，最小任务）meta 记 `fable`，实跑 `claude-sonnet-5`；probe-e 前两轮 `claude-fable-5-1`，后三轮切到 `claude-sonnet-5`。→ agent 文件的 `model:` 进了 spawn 记录，实际执行可被替换，且能在一次派发中途改变。成因未证，候选两条：端点侧容量回退；该路径不完整执行插件 agent 的 frontmatter。既有相关事实：`lanes-cursor.md:9` 已记 Cursor 侧"Agent frontmatter `model:` is not honored for plugin-loaded agents"。对填充表的影响：advisor 名义走 Fable 5.1，本轮三次里两次整程落在 Sonnet 5。

**advisor 裁定（决策形状，选项 A / B / C）。** 结果 C：新建 `plugin/agents/explorer.md` 并限 `tools: Read, Grep, Glob`，关掉内置 Explore 带 Bash 的能力口子，与 `fable-advisor.md` 的既有约定一致；但在 frontmatter effort 问题查清前，该文件与 doctrine 都不写 effort 声明。决定性风险：第二次写下宿主未必执行的档位声明，会把一个待查问题变成成文的假规则。裁定同时指出：`lanes-claude-code.md:3`、`:5` 与 `SKILL.md:62` 的"继承会话 effort"无论选哪项都要改，核对项 1、2 已独立证伪它。

**核对项 4、5 的处置。** 第 4 项（Cursor 侧不另建）维持原判，本轮未做任何 Cursor 改动。第 5 项的同步清单（`docs/zh/agents/explorer.md`、`SKILL.md:62`、`lanes-claude-code.md:3`）连同实测新增的两处（`lanes-claude-code.md:5` 的 effort 与 `/tasks` 两句、三处英文句的中文孪生）一并写进工单 10；与 `.scratch/role-pool-posture/issues/10-report-mode-preamble.md` 的报告前言保持单源引用，不合并实施。

**结论。** 采纳 C，写入 ADR 0015 追记；落地改动写成工单 10（`.scratch/global-orchestration-handoff/issues/10-explorer-agent-and-effort-sentences.md`），不在本工单实施。

**仍待用户的两件事。** 第一，一次 `/tasks` 文本，须在派发运行中截取，用于对照 effort 的显示值与转写值（第三轮已取得，见下）。第二，在未开 agent-teams 的会话里重跑 probe-d / probe-g / probe-h，判定 frontmatter 是否在经典路径生效。两者都不改变 C 的裁定，只决定工单 10 之后能否恢复 effort 声明。

### 2026-09-16 核对记录（第三轮：`/tasks` 的实际显示）

三个 sleeper（`probe-f2-explore-sonnet` 内置 Explore 加按次 `model: sonnet`；`probe-g2-worker-frontmatter` 插件 `worker`、不带按次 `model`、定义写 `effort: medium`；`probe-h2-explore-inherit` 内置 Explore、不带 `model`）运行中，用户执行 `/tasks`，原样输出：

```
 @team-lead
     @probe-h2-explore-inherit: Running Sleep for 600 seconds
     @probe-g2-worker-frontmatter: Running Sleep for 600 seconds
     @probe-f2-explore-sonnet: Running Sleep for 600 seconds
     @probe-h-model-repeat: idle
     @advisor-explorer-decision: idle
     @probe-g-tasks-worker: idle
     @probe-f-tasks-explore: idle
     @probe-e-effort-frontmatter: idle
     @probe-d-effort-pin: idle
     @probe-c-opus: idle
     @probe-b-inherit: idle
     @probe-a-sonnet: idle
```

同期三者的转写记录：`probe-f2` = `claude-sonnet-5` / medium；`probe-g2` = `claude-opus-5` / xhigh；`probe-h2` = `claude-opus-5` / xhigh。

**结果：`/tasks` 只列成员名与状态，既不显示模型，也不显示 effort。** `lanes-claude-code.md:5` 的"`/tasks` shows each subagent's actual model and effort (since v2.1.242) — the user-side observation point for what a claude-lane dispatch is really running"在本环境不成立。限定条件：本会话开了 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`，`/tasks` 呈现的是团队花名册；未开该变量的经典 Task 路径是否按官方文档显示模型与档位，本轮未测。

三点后果。第一，核对项 1 设想的证据源在本环境取不到模型与 effort，子代理转写是唯一可用入口；前两轮结论基于转写，不受影响。第二，frontmatter `effort` 是否下发的争点无法用 `/tasks` 判定，只能靠未开 agent-teams 的会话重跑 probe-d / probe-g / probe-h 来定，该项仍未决。第三，工单 10 第 5 条追加一句：`/tasks` 的表述按实测收窄，注明团队模式下只显示名称与状态，不要把它写成"用户侧观测点"。

### 2026-09-16 核对记录（第四轮：经典 Task 路径，未开 agent-teams）

**环境。** 另开一个会话，环境只有 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` 与 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`，**未设 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`**；宿主 2.1.273，会话模型 `claude-opus-5`，`~/.claude/settings.json` 为 `effortLevel: medium` 加 `modelSettings.claude-opus-5.effortLevel: xhigh`，无 `CLAUDE_CODE_SUBAGENT_MODEL`。已装插件仍是 5.0.0（`agents/fable-advisor.md`: `model: fable` / `effort: high` / `tools: Read, Grep, Glob` / `readonly: true`；`agents/worker.md`: `model: opus` / `effort: medium`）。这一轮兑现第二轮"仍待用户的第二件事"：在未开 agent-teams 的会话重跑 frontmatter 探针。

**任务与取证。** 七个探针跑同一条极小只读任务（读 `plugin/.claude-plugin/plugin.json` 报 `version`），只变 `subagent_type` 与按次 `model`；七个都正确返回 `5.1.0`，每个一次工具调用。证据取自本会话 `subagents/agent-*.meta.json` 与同名 `.jsonl` 的每条 assistant 记录。

| 探针 | `subagent_type` | 按次 `model` | 定义声明 | 实跑模型 | 转写 `effort` | 该模型的设置档位 |
|---|---|---|---|---|---|---|
| c1 | 内置 `Explore` | sonnet | 无 effort | `claude-sonnet-5` | medium | medium |
| c2 | 内置 `Explore` | 无 | 无 effort | `claude-opus-5` | xhigh | xhigh |
| c3 | 内置 `Explore` | haiku | 无 effort | `claude-haiku-4-5-20251001` | **无 effort 字段** | 无档位 |
| c4 | `fable-advisor:worker` | 无 | `model: opus`、`effort: medium` | `claude-opus-5` | **medium** | xhigh |
| c5 | `fable-advisor:fable-advisor` | 无 | `model: fable`、`effort: high` | `claude-fable-5-1` → `claude-sonnet-5` | **high** | medium |
| c6 | `fable-advisor:fable-advisor` | sonnet | `effort: high` | `claude-sonnet-5` | **high** | medium |
| c7 | 内置 `Explore` | fable | 无 effort | `claude-fable-5-1` → `claude-sonnet-5` | medium | medium |

**frontmatter `effort` 在后台子代理派发上生效，三次全中。** c4 实跑 opus 而转写 medium（opus 的设置档位是 xhigh）；c5、c6 转写 high（sonnet 与 fable 的设置档位都是 medium）。三次都等于 agent 文件的声明值，都不等于运行模型的设置档位。c1、c2、c3 三个无声明的派发则等于运行模型的设置档位。→ 优先级是 **frontmatter `effort` 高于运行模型的设置档位**；第一轮"跟模型配置档位走"的机制描述只在"定义未声明 effort"时成立，其样本（probe-a/b/c）全是内置 `Explore`，正好都无声明。

**第二轮的争点判定完毕，分裂点是派发种类，不是环境变量。** 第五轮把归因订正了，此处按订正后的表述记：第二轮那四个反例全是**具名 teammate 派发**（`taskKind: in_process_teammate`），teammate 上 frontmatter `effort` 不生效；本轮七个是**后台子代理派发**（`requestShape: background`），声明生效。两者可以在同一个会话里并存，`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 只决定 teammate 派发是否可用，不改变后台子代理的行为 —— 证据见第五轮。第二轮列的两种解释由此分辨：转写字段记的是实际下发值，teammate 路径确实没下发。

**meta.json 形状随派发种类变，可作判别入口。** 后台子代理的 meta 是 `{"agentType", "description", "toolUseId", "spawnDepth": 1, "requestShape": "background", "requestNonInteractive": true, ["model"]}`，无 `taskKind`，`agentType` 记 agent 类型（`Explore`、`fable-advisor:worker`），文件名是 `agent-<agentId>.meta.json`，`model` 只在带按次 `model` 时出现（c1、c3、c6、c7 有，c2、c4、c5 无），记的是按次请求值。teammate 的 meta 有 `"taskKind": "in_process_teammate"`，`agentType` 记的是**成员名**（如 `probe-d-effort-pin`）而不是 agent 类型，文件名是 `agent-a<成员名>-<hash>.meta.json`，`model` 每次都有且记解析后的模型（`probe-b-inherit` 无按次 `model` 也记 `opus`）。引用 meta 的 `model` 前须先看是哪一种。

**fable → sonnet 的替换与 agent-teams 无关，也与插件 frontmatter 无关。** c5（frontmatter `model: fable`）与 c7（内置 `Explore` 加按次 `model: fable`）都是第一条 assistant 记录 `claude-fable-5-1` 且带 `tool_use`，工具结果回来后第二条切成 `claude-sonnet-5` 收尾；两次都无 `fallbackModel` 字段、无 `isApiErrorMessage`、无 system 错误记录。c6 显式请求 sonnet 全程不切。→ 第二轮列的候选"该路径不完整执行插件 agent 的 frontmatter"被 c7 排除（c7 走内置 agent、按次参数，同样被替换）；只剩端点侧回退这一类候选，成因仍未证，且本轮转写不给回退标记（第五轮在对方会话的记录里找到了 `diagnostics.cache_miss_reason` 标记）。合并三个会话的样本（见第五轮）：请求 fable 共 7 次，**没有一次整程跑在 fable 上**；4 次首轮真跑 `claude-fable-5-1`、拿到工具结果后切 sonnet，3 次从头就是 sonnet。对填充表的影响不变：advisor 名义走 Fable 5.1，实际只有首轮在 Fable 上。

**两处附带事实。** 第一，Haiku 4.5 的派发转写完全没有 `effort` 字段（c3 四条记录都无），"给每个角色写 effort 声明"对无档位模型是空操作。第二，`perTurnEffort` 字段只出现在 `claude-fable-5-1` 的记录上（c5 为 high、c7 为 medium，都等于同记录的 `effort`），其余六个探针全为 null。

**本轮未测。** 一、经典路径下 `/tasks` 的实际显示（需在派发运行中由用户截取，本轮探针都是秒级完成）。二、插件级同名 `Explore` 能否覆盖内置，仍待 5.1.0 安装。三、按次 effort 参数不存在：`Agent` 工具的入参只有 `model`，无 effort，"不同推理强度"只能经 agent 定义或模型设置档位达成。

### 2026-09-16 核对记录（第五轮：跨会话对照，分裂点归因订正）

**为什么有这一轮。** 第四轮把 effort 的分裂归因于 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`。同机另开一个设了该变量的会话（`6581a876`，宿主与设置同）跑完同一组七个探针后回传的结果与第四轮几乎逐行一致：c4 = opus/medium、c5 = fable→sonnet/high、c6 = sonnet/high、c1 = sonnet/medium、c2 = opus/xhigh、c3 = haiku/无 effort 字段。也就是说，在设了该变量的会话里，frontmatter `effort` **照样生效**。该会话同时报告它的七个 meta 里没有 `taskKind` 键，并据此认为这个键区分不出两条路径。

**订正后的归因：分裂点是派发种类，不是环境变量。** 本会话对全项目的 `subagents/*.meta.json` 做了一次 grep：`"taskKind":"in_process_teammate"` 共 15 处，集中在第二、三轮那个会话（`5bf87aa7`，12 处）与另两个更早会话；第四轮我自己的七个、第五轮对方的七个都没有这个键。把 `5bf87aa7` 的 12 条 teammate 记录重抽一遍：

| teammate | meta.model | 实跑模型 | 转写 effort | 该模型设置档位 | 定义声明 effort |
|---|---|---|---|---|---|
| probe-a-sonnet | sonnet | `claude-sonnet-5` | medium | medium | 无（内置 Explore） |
| probe-b-inherit | opus | `claude-opus-5` | xhigh | xhigh | 无 |
| probe-c-opus | opus | `claude-opus-5` | xhigh | xhigh | 无 |
| probe-d-effort-pin | sonnet | `claude-sonnet-5` | medium | medium | high（advisor） |
| probe-e-effort-frontmatter | fable | fable-5-1 → sonnet-5 | medium | medium | high（advisor） |
| probe-f-tasks-explore | sonnet | `claude-sonnet-5` | medium | medium | 无 |
| probe-f2-explore-sonnet | sonnet | `claude-sonnet-5` | medium | medium | 无 |
| probe-g-tasks-worker | opus | `claude-opus-5` | xhigh | xhigh | medium（worker） |
| probe-g2-worker-frontmatter | opus | `claude-opus-5` | xhigh | xhigh | medium（worker） |
| probe-h-model-repeat | fable | `claude-sonnet-5` | medium | medium | high（advisor） |
| probe-h2-explore-inherit | opus | `claude-opus-5` | xhigh | xhigh | 无 |
| advisor-explorer-decision | fable | `claude-sonnet-5` | medium | medium | high（advisor） |

12 条全部 `effort = 运行模型的设置档位`，六条有声明的（probe-d、e、g、g2、h、advisor-decision）一条都没取到声明值。→ **具名 teammate 派发不下发 agent 文件的 `effort`；后台子代理派发（`requestShape: background`）下发。** 两种派发能在同一会话并存，环境变量只决定 teammate 派发是否可用。第四轮"经典路径 vs teams 路径"的措辞作废，按"后台子代理 vs teammate"重述。

**对方那句"taskKind 区分不出两条路径"只对它自己的样本成立。** 它的七个探针走的是 `Agent` 工具的后台派发，与我的七个同种，所以两边 meta 键集相同、结论相同 —— 它没有派过 teammate，因此测不到 teammate 路径。这一句已按本机 15 条实据订正，不写进结论。

**对方带回的两点增量（转述，未经本会话复核）。** 第一，它的 c5 第二段记录带 `diagnostics.cache_miss_reason = {"type":"model_changed","cache_missed_input_tokens":12781}` —— 这是第四轮说"转写不给回退标记"的反例，模型切换在转写里有可查标记，位置是 `diagnostics`，不是 `fallbackModel`。第二，它的 c7（内置 `Explore` 加按次 `model: fable`）**两段都是 `claude-sonnet-5`，fable 一次没跑到**，而我的 c7 首轮真跑了 fable。同一派发种类、同一参数、同一分钟内，实跑模型不一致 → 支持"端点侧回退"这一类候选，反对"宿主按规则替换"。

**合并后的 fable 样本（7 次请求）。** 首轮真跑 `claude-fable-5-1` 再切 sonnet：teammate probe-e、我的 c5、我的 c7、对方 c5，共 4 次。从头就是 sonnet：teammate probe-h、teammate advisor-decision、对方 c7，共 3 次。整程跑在 fable 上：0 次。

**对既有结论的影响。** 第三项裁定 C（新建 `plugin/agents/explorer.md`、限 `tools: Read, Grep, Glob`）不受影响，理由是权限口子，与 effort 无关。但 C 的附加条件"该文件与 doctrine 都不写 effort 声明"的依据（"宿主未必执行的档位声明"）现在只对 teammate 派发成立，对后台子代理派发（`Agent` 工具的默认形状，也是 doctrine 里 claude 车道的派发形状）已证伪 —— 是否恢复 effort 声明属于改动既定方案，按决策类型门须先过 advisor，本轮不改，只把证据留给工单 10。`lanes-claude-code.md:3`、`:5` 与 `SKILL.md:62` 的"继承会话 effort"仍要改，且改写须按派发种类限定：后台子代理派发下，有 `effort` 声明时取声明值、无声明时取运行模型的设置档位；具名 teammate 派发一律取运行模型的设置档位，声明无效。

### 2026-09-16 核对记录（第六轮：档位可控性、派发分流参数、fable 成因）

**为什么补记这一轮。** 本轮证据一度只存在于会话对话里，未落盘，随后两次让 context-clean 的读者拿到错前提：advisor 在决策形状里判"`xhigh` 从未直接测试"（实际 g4 直接命中），在验收形状里判"`:9` 的同一会话对照是推断"（实际另一会话在其自身会话内跑了两条路径）。故补记，供后续读者据此判定，不必回看对话。

**档位可控性：四档全部直接命中。** 建四个只声明 `effort`、不声明 `model` 的项目级 agent 文件（`.claude/agents/probe-eff-{low,medium,high,xhigh}.md`，`tools: Read`），由一个无头会话（`claude -p --model sonnet --effort low --permission-mode dontAsk`，会话 `0b5d9469`）派发，任务同为读 `plugin/.claude-plugin/plugin.json` 报 `version`：

| 探针 | 定义声明 | 按次 `model` | 实跑模型 | 转写 `effort` | 该模型设置档位 |
|---|---|---|---|---|---|
| g1 | `effort: low` | fable | `claude-fable-5-1` ×2，**未切换** | low | medium |
| g2 | `effort: medium` | opus | `claude-opus-5` ×2 | medium | xhigh |
| g3 | `effort: high` | opus | `claude-opus-5` ×2 | high | xhigh |
| g4 | `effort: xhigh` | sonnet | `claude-sonnet-5` ×2 | xhigh | medium |

四次全部等于声明值，四次全部与该模型的设置档位不同——双向覆盖（opus 被压低两次，sonnet 被抬高一次），不是撞上默认值。补充两个插件级样本：f1（`fable-advisor`，声明 high，按次 opus）得 `claude-opus-5` / high；f2（同 agent，按次 haiku）得 `claude-haiku-4-5-20251001`，四条记录全无 `effort` 字段。→ **插件级只直接测过 `medium` 与 `high`（c4、c5、c6、f1）；`low` 与 `xhigh` 只在项目级测过，插件级是外推。**

**agent 文件的加载时机。** 上述四个文件在本会话中途新建，本会话六次派发全部报 `Agent type 'probe-eff-low' not found`（可用清单里没有它们）；同样的文件，另起的无头会话全部加载成功。→ agent 定义只在会话启动时加载，改完须重启。探针文件测完已删除，`.claude/` 目录不留。

**派发分流参数（另一会话提供，工具形状为其自报）。** teammate 与后台子代理用的是**同一个 `Agent` 工具**，参数为 `description`（必填）、`prompt`（必填）、`subagent_type`、`name`、`model`（枚举 `sonnet|opus|haiku|fable`）、`isolation`，另有已废弃并被忽略的 `mode`、`team_name`。**没有 `effort` 参数。** `name` 是唯一分流开关：传了走 teammate，不传走后台子代理。该参数只在设了 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 的会话存在——本会话（未设）的 `Agent` 入参里确实没有 `name`，可作旁证。

**同一会话内的两条路径对照（这是 `lanes-claude-code.md:9` "same session" 的证据）。** 会话 `6581a876` 在其自身会话内先跑后台子代理派发、再跑具名 teammate 派发，用同样两个插件 agent：

| agent 定义 | 声明 `effort` | 传 `name`（teammate） | 不传 `name`（后台子代理） |
|---|---|---|---|
| `fable-advisor:worker` | `medium` | xhigh（= opus 设置档位） | medium（= 声明值） |
| `fable-advisor:fable-advisor` + 按次 `model: sonnet` | `high` | medium（= sonnet 设置档位） | high（= 声明值） |

同会话、同插件、同 agent 文件，唯一变量是 `name`。teammate 侧模型钉定精确生效（t-haiku、t-sonnet、t-opus 三个实跑模型均与请求一致），但档位一律回落到模型设置档位，且回落静默。

**`/tasks` 的原样输出（teammate 存在时，由用户执行）。**

```
     Team: session-6581a876 (9)
   ❯ @team-lead
     @t-advisor: idle
     @t-worker: idle
     @t-fable: idle
     @t-opus: idle
     @t-sonnet: idle
     @t-haiku: idle
     @probe-alpha: idle
     @probe-beta: idle
```

只有成员名与状态：无模型列、无 effort 列、无任务描述、无 token 计数。该会话同期的七个后台子代理一个都不在列。→ teammate 路径上的档位回落在界面层完全不可见，唯一观测入口是 `subagents/agent-*.jsonl`；后台子代理派发在界面层没有任何观测点。teammate 跑完保持 idle 并可再次发消息唤醒，不会自动消失。

**fable 降级的成因：账户侧 usage credits 门禁，已解决。** 宿主自报：`/advisor fable` 返回 "Fable 5.1 as the advisor bills to usage credits, which need to be set up for your account. Run /model fable to review and enable, then set it as the advisor."；`/model fable` 返回 "Set model to `Fable 5.1` … Draws from usage credits"。启用后 `~/.claude/settings.json` 新增 `advisorModel: "fable"` 键。启用后三个样本全部整程 `claude-fable-5-1`、无 `model_changed`：本仓 advisor 验收派发 38 条 assistant 记录全为 fable（effort 与 perTurnEffort 均 high）；另一会话两个与启用前失败样本逐字同参数的对照探针（d1 对照 c5、d2 对照 c7）各 2 段全为 fable。→ 第四、五轮"请求 fable 共 9 次、4 次中途切走、4 次从头 sonnet、1 次整程"是**启用前**的历史计数，不再描述当前行为；第五轮"支持端点侧回退、反对宿主按规则替换"的机制判断被确认（条件一变行为即变，规则替换预测不出这个），补上的是触发条件。两条残余未知：启用前有一次派发第一段真跑在 fable 上才切走，硬性计费预检解释不了，成因未验证；启用 credits 后具名 teammate 路径零样本，该路径上 fable 是否可达现为未测。

**g1 反例经另一会话独立核实。** 该会话读本机文件核对（非转述）：`0b5d9469` 会话的 `agent-a07c3b08daa84b969`（meta 记 `agentType: probe-eff-low`、`model: fable`、无 `taskKind`，即后台子代理派发）两段 assistant 记录时间为 `2026-09-16T10:05:59.447Z` 与 `10:06:00.590Z`，模型均 `claude-fable-5-1`、effort 均 `low`、均无 `model_changed`；`~/.claude/settings.json` mtime 为 `10:24:11Z`。整程成功样本比 credits 启用早 18 分 11 秒，故 credits 门禁不可能是逐次生效的确定性预检。双方就"强相关、成因未证、软门禁与概率性门禁无法分辨"达成一致。该会话另确认 g1–g4 四个探针的 effort（low / high / xhigh / medium）全部等于各自项目级定义的声明值，与 c4、c6 方向一致。

**teammate 路径的 fable 样本：用户裁定不补跑。** 这一格按"启用 credits 后未测"归档，是有意留白而非疏漏；后续若要关闭它，最小派发是具名 teammate 加 `model: fable`、读一个文件报一个字段，再看转写两段的 `model`。
