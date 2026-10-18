# Claude Code 中的 claude lane

在 Claude Code 中第一次派发 `claude lane` 之前阅读本文。`claude lane` 是普通的子代理派发，无 runner。两条 CLI 都缺失时，它让插件保持自包含。它的角色池按（角色，effort）每组一份 agent 文件随插件发布，派发时寻址为 `fable-advisor:<name>`，名字里的强度用缩写（`l`、`md`、`h`、`xh`）：`explorer-md`、`explorer-h`、`explorer-xh`、`worker-md`、`worker-h`、`worker-xh`、`advisor-l`、`advisor-md`、`advisor-h`、`advisor-xh`。frontmatter 的 `effort:` 仍写全称，只有文件名与 `name:` 用缩写。因为 effort 没有按次参数而 model 有，拨盘被拆成两半：文件定死 effort，派发时的 `model` 选定具体填充。所以 `explorer-*` 与 `worker-*` 根本不带 `model:` 键——派发时省略 `model`，跑的是 `CLAUDE_CODE_SUBAGENT_MODEL`，该变量未设时跑会话模型，而不是填充表点名的那个填充；因此路由门拒绝不带 `model` 的本角色池派发（「路由门」规则 2）。`advisor-*` 都写 `model: fable`。把一个 `worker` 的 `model` 钉为会话模型，即同模派发。宿主内置的 `Explore` agent 自己没有 effort——不给显式 `model` 时它跑在会话模型上（Claude API 上封顶为 Opus），因此未钉死的 `Explore` 按会话价格计费。`claude lane` 的报告在 `Task` 结果内返回；后台派发的报告从该任务的输出文件读取。Claude Code 把主会话之下的子代理嵌套限制为三层。

agent 文件只在会话启动时加载。会话中途新增或改名的文件无法派发——调用会以 `Agent type '<name>' not found` 失败——所以对这个角色池的改动只有在会话重启之后才生效。

`claude lane` 上的 effort 不是每次派发的参数。`Agent` 工具的入参是 `description`、`prompt`、`subagent_type`、`model`、`isolation`，在以 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 启动的会话里再多一个 `name`；没有 `effort` 实参。因此强度只有两条路能到达一次派发：agent 定义的 frontmatter `effort:`（`low | medium | high | xhigh | max`；存在哪些级别取决于模型），或 CLI 启动时的 `--effort`，后者设定整个会话。

**传不传 `name` 是决定派发种类的唯一分流开关，也决定 frontmatter 的 effort 是否根本有效。** 不传 `name`，这次派发是后台子代理：frontmatter `effort:` 生效。传 `name`，它是具名 teammate：frontmatter `effort:` 被忽略，强度回落到该模型在 `~/.claude/settings.json` 里设置的强度，而且是静默回落——派发过程里没有任何东西提示声明值被丢掉了。派发这个角色池时不要传 `name`，否则它的全部意义就没了。

frontmatter 的 `effort:` 双向覆盖运行模型所设置的强度。

agent 定义**没写** `effort:` 时，强度跟它实际运行其上的那个模型在 `settings.json` 里设置的强度走，不是跟会话的 effort 走；只有子代理模型与会话模型相同时两者才重合。

观察点是 `~/.claude/projects/<项目>/<会话>/subagents/agent-*.jsonl`，其中每条 assistant 记录都带着实际生效的 `model` 与 `effort`。`/tasks` 不是这件事的观察点：它只列具名 teammate，显示成员名与状态，既不显示 model 也不显示 effort，而且完全不列后台子代理。

模型解析顺序：按次 `model` 优先，然后是 agent 文件的 `model:`，然后是 `CLAUDE_CODE_SUBAGENT_MODEL`，最后是主会话模型。`CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 为真时，宿主去掉按次 `model`，子代理跑 `CLAUDE_CODE_SUBAGENT_MODEL`；该变量未设或为 `inherit` 时，跑主会话模型。别名所属家族与主会话模型相同时，跑主会话模型；否则在设了重定向变量 `ANTHROPIC_DEFAULT_*_MODEL` 时按变量解析。完整推导见「路由门」规则 2。

Fable 作为 advisor 需要账户启用 usage credits。`fable` 派发失败时，把它当作不可用的候选，按 SKILL.md「改道」改道。模型是请求值，不是执行保证：引用 receipt 的模型时写提交值，不是观测值；实际运行的模型看子代理转写里的 `message.model`。

后台子代理可以在运行中被纠偏。按派发结果返回的 `agentId` 调用 `SendMessage`，不需要 `name`，第一行是路由行（SKILL.md「路由」），消息在子代理下一次调用工具时送达；子代理正在执行一次很长的工具调用时（例如在前台运行 runner），消息要等那次调用返回。纠偏会改变契约：只在 Objective、Constraint 或 Verification 某一项被发现有错时发送，验收依据契约加这条消息。

`claude lane` 子代理的续用窗口（SKILL.md「会话续用」）从它的 `subagents/agent-<id>.jsonl` 里最后一条 assistant 记录的时刻算起。

同时进行的契约各在自己的工作目录里运行（`git worktree add`），`claude lane` 契约的 Files 与 Verification 命令指向其中。

## 路由与前言

`claude lane` 派发没有 runner 替它前置前言。它的提示第一行就是路由行本身；第二行是一条指令：先于其他一切，按绝对路径读取其角色所需的前言——`worker` 读 `lane-preamble.md`，`explorer` 或 `advisor` 读 `lane-preamble-report.md`——路径取自本技能的基础目录。只写一行裸路径标签不够。发给本角色池子代理的每条 `SendMessage` 消息，第一行同样是路由行。

### 路由门

插件的 `PreToolUse` 钩子 `hooks/route-gate.py`（**路由门**，`route gate`）校验每一次 `subagent_type` 为 `fable-advisor:*` 的 `Agent` 派发，以及每一条发给本角色池子代理的 `SendMessage` 消息。未通过的调用被拒绝：`permissionDecision: deny`，理由写明缺了什么，并列出该角色、该档位的合法拨盘；改正调用后重新发出。路由门校验提交的配置；实际运行的型号仍以子代理记录里的 `message.model` 为准。每次受校验的调用都满足下列规则：

1. **角色。** 路由写的角色与 agent 文件一致：`explorer-*` 是 `explorer`，`worker-*` 是 `worker`，`advisor-*` 是 `advisor`。
2. **拨盘。** 本角色池的每次 `Agent` 派发都显式带 `model`，因为不带时型号还受 agent 文件的 `model:` 与 `CLAUDE_CODE_SUBAGENT_MODEL` 影响。单次派发的 `model` 优先于 `CLAUDE_CODE_SUBAGENT_MODEL`，路由门据此推出拨盘。例外只有一个：`CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 为真（`1`、`true`、`yes`、`on`）时，宿主从 `Agent` 的参数里去掉 `model`，派发因此不带它；路由门改按 `CLAUDE_CODE_SUBAGENT_MODEL` 推出拨盘，该变量未设或为 `inherit` 时按会话型号推出。别名按以下顺序解析：别名所属家族与会话型号相同时，跑会话型号；否则在设了重定向变量时按变量解析（`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`ANTHROPIC_DEFAULT_FABLE_MODEL`）；否则按档案锚点对应：`haiku` 对应 `haiku-5-5`，`sonnet` 对应 `sonnet-5-5`，`opus` 对应 `opus-5-5`，`fable` 对应 `fable-5-1`。会话型号按规则 5 读取；读不到时跳过家族这一步。规范化后不是锚点型号的，拒绝：在跑 `claude-sonnet-4-5` 的会话里，`sonnet` 跑的是 `claude-sonnet-4-5`，它不是锚点，所以这次派发被拒绝。强度取 agent 文件的 `effort:`。所以 `explorer-h` 配 `sonnet` 的路由写 `sonnet-5-5[high]`。路由写的拨盘与推出的拨盘相同。
3. **档位。** 该角色与拨盘出现在 Claude Code 表里，路由所写角色、档位的那一格。
4. **依据。** 高于 `mainstay` 时，依据是 SKILL.md 接受的一种，`ref` 非空。路由门只查依据存在且格式合规，不查真假。
5. **同模派发。** 只有 `worker-*` 派发可以写 `tier=same-model`，依据种类为 `same-model`。推出的型号与会话型号相同；会话型号取会话记录最后一条非合成 assistant 记录的 `message.model`，读不到就拒绝。合成记录指 `message.model` 为 `<synthetic>` 的 assistant 记录，例如宿主在 API 出错后会写一条。assistant 记录全是合成记录的会话记录，按没有 assistant 记录处理。路由门运行时，当前这条回复还没有写进会话记录，而会话的第一条回复之前没有 assistant 记录，所以在会话第一条回复里做的同模派发会被拒绝；要在任意一条别的回复之后再派。产物类别和依据的真假仍由主代理判断。
6. **不带 `name`。** 带 `name` 的本角色池派发一律拒绝，因为 `name` 会让 agent 文件的强度失效。
7. **`SendMessage`。** 发给本角色池子代理的消息，第一行是路由行。它的拨盘取目标的实际配置：目标记录里最后一条非合成 assistant 记录（见规则 5）的 `message.model`（规范化）与 `effort`；目标还没有 assistant 记录时，取它的 `meta.json`（`agentType` 与 `model`），按规则 2 推出。暂停、纠正等消息照样带路由；拒绝理由给出目标的拨盘，照抄即可。只带 `notify_when_idle`、不带消息的订阅放行。`meta.json` 里的 agent 类型不以 `fable-advisor:` 开头的目标放行。目标是名字、`main` 或别的会话时放行：本角色池派发时不带 `name`，所以按名字寻址的目标不在本角色池里。形如 agentId、却在本会话找不到记录的目标，拒绝。`TaskStop` 不受校验。
8. **拒绝。** 字段缺失、格式错误或互相矛盾时拒绝；路由档案读不出或解析失败也拒绝。路由门只拒绝，从不询问。

路由门覆盖不到：

- Cursor 钉型号的 `Task` 派发，含 `resume`：那里的路由只有文本规则（[lanes-cursor.md](lanes-cursor.md)）。
- 没有 Python 的机器：路由门放行，并向 stderr 写一行说明，与 receipt gate 相同。
- 内置代理（`general-purpose`、`Explore` 等）：它们不属于本角色池。
