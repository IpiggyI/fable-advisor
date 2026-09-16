# Claude Code 中的 CLI 车道 —— runner

在 Claude Code 中派发车道之前阅读本文。主代理通过确定性 runner 直接驱动两个 CLI 生产者，没有 subagent 启动成本。`grok lane` 需要 [Grok CLI](https://x.ai/cli)；`codex lane` 需要 codex CLI 与 Node。`claude lane` 是普通的 subagent 派发，无 runner。两条 CLI 都缺失时，它让插件保持自包含。它的角色池按（角色，effort）每组一份 agent 文件随插件发布，派发时寻址为 `fable-advisor:<name>`，名字里的档位用缩写（`l`、`md`、`h`、`xh`）：`explorer-h`、`explorer-xh`、`worker-md`、`worker-h`、`worker-xh`、`advisor-l`、`advisor-md`、`advisor-h`、`advisor-xh`。frontmatter 的 `effort:` 仍写全称，只有文件名与 `name:` 用缩写。因为 effort 没有按次参数而 model 有，拨盘被拆成两半：文件定死 effort，派发时的 `model` 选定具体填充。所以 `explorer-*` 与 `worker-*` 根本不带 `model:` 键——派发时省略 `model`，拿到的会是会话模型，而不是填充表点名的那一档。`advisor-*` 都写 `model: fable`。把一个 `worker` 的 `model` 钉为会话模型，即同模派发。宿主内置的 `Explore` agent 仍是 light `explorer` 的一个填充，但它自己没有 effort——不给显式 `model` 时它跑在会话模型上（Claude API 上封顶为 Opus），因此未钉死的 `Explore` 按会话价格计费。`claude lane` 的报告在 `Task` 结果内返回；后台派发的报告从该任务的输出文件读取。

agent 文件只在会话启动时加载。会话中途新增或改名的文件无法派发——调用会以 `Agent type '<name>' not found` 失败——所以对这个角色池的改动只有在会话重启之后才生效。

`claude lane` 上的 effort 不是每次派发的参数。`Agent` 工具的入参是 `description`、`prompt`、`subagent_type`、`model`、`isolation`，在以 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 启动的会话里再多一个 `name`；没有 `effort` 实参。因此档位只有两条路能到达一次派发：agent 定义的 frontmatter `effort:`（`low | medium | high | xhigh | max`；存在哪些级别取决于模型），或 CLI 启动时的 `--effort`，后者设定整个会话。

**传不传 `name` 是决定派发种类的唯一分流开关，也决定 frontmatter 的 effort 是否根本有效。** 不传 `name`，这次派发是后台子代理：frontmatter `effort:` 生效。传 `name`，它是具名 teammate：frontmatter `effort:` 被忽略，档位回落到该模型在 `~/.claude/settings.json` 里的档位，而且是静默回落——派发过程里没有任何东西提示声明值被丢掉了。同一会话、同样两个 agent、两条路径实测——用的是退役前的文件名 `worker` 与 `fable-advisor`，这两个名字现已不存在，所以今天照名字复现不了这一组对照：`worker`（当时声明 `medium`）作为 teammate 得到 xhigh，在后台得到 medium；`fable-advisor`（声明 `high`）配 `model: sonnet` 作为 teammate 得到 medium，在后台得到 high。派发这个角色池时不要传 `name`，否则它的全部意义就没了。

本角色池用到的四个档位都在后台路径上实测生效：`low` 配 fable、`medium` 配 opus、`high` 配 opus 与 sonnet、`xhigh` 配 sonnet。也就是说机制在四个取值上都已核实，但入口并不等价：经**插件级** agent 文件真正跑过的只有 `medium` 与 `high`，插件级的 `low` 与 `xhigh` 是从项目级 agent 文件的实测外推的，而那是另一条加载路径。会话重启之后，用本角色池把这两档补测一遍。覆盖是双向的——opus 的设置档位是 xhigh，声明 `high` 与声明 `medium` 都压过了它；sonnet 的设置档位是 medium，声明 `xhigh` 也压过了它——所以这是真的覆盖，不是声明值碰巧撞上了默认值。

agent 定义**没写** `effort:` 时，档位跟它实际运行其上的那个模型在 `settings.json` 里的档位走，不是跟会话的 effort 走；只有子代理模型与会话模型相同时两者才重合。`claude-haiku-4-5` 根本没有 effort 这一维——它的记录里没有该字段。

观察点是 `~/.claude/projects/<项目>/<会话>/subagents/agent-*.jsonl`，其中每条 assistant 记录都带着实际生效的 `model` 与 `effort`。`/tasks` 不是这件事的观察点：它只列具名 teammate，显示成员名与状态，既不显示 model 也不显示 effort，而且完全不列后台子代理。

模型解析顺序：按次 `model` 优先，然后是 agent 文件的 `model:`，然后是 `CLAUDE_CODE_SUBAGENT_MODEL`，最后是主会话模型。

**Fable 作为 advisor 的计费走 usage credits，账户必须先启用它。** 已确立的有三件事。宿主自己这样说：`/advisor fable` 回答 "Fable 5.1 as the advisor bills to usage credits, which need to be set up for your account. Run /model fable to review and enable, then set it as the advisor."；`/model fable` 随后回答 "Set model to `Fable 5.1` … Draws from usage credits"，此后 `/advisor fable` 成功，`~/.claude/settings.json` 也多了一个 `advisorModel: "fable"` 键。启用之后，三次请求三次都整程跑在 `claude-fable-5-1` 上，没有 `model_changed` 标记。启用之前，九次请求里只有一次整程留在它上面；其余的要么起初跑 `claude-fable-5-1`、拿到工具结果后切到 `claude-sonnet-5`，要么从第一轮起就是 `claude-sonnet-5`。

**未确立的是：这道门禁是否就是那些降级的成因。** 它最多只是相关：这道门禁不是作用于每次派发的确定性预检——启用之前有一次派发整程跑在 fable 上，它的首条记录比 credits 启用时刻早十八分钟；另有一次的开头一段先跑在 fable 上才切走。成因按未证处理，不要用猜出来的机制去顶替它。

因此有两条未知仍然敞开。第一，那种「开头一段成功、随后切走」的模式没有解释。第二，启用之后的样本全是后台子代理：自启用 credits 起，具名 teammate 路径一个样本都没有，而启用前那次从第一轮就是 sonnet 的 teammate 运行不能沿用，所以 fable 在该路径上是否可达，目前未测。

修好之后普适规则依然成立：模型是请求值，不是执行保证，所以引用时按 ADR 0015 的 receipt 措辞写——提交值，不是观测值。因此约束一个 `advisor` 答案边界的，是「它的权威来自它读到的代码，而不是它运行其上的模型」，从不是关于哪个模型实际服务了它的假定。

两条 CLI 车道流程相同；以 codex 演练为典范，grok 的差异紧随其后。两条 runner 默认服务 `worker` 角色，并在 report mode 下服务只读角色（见下文「报告模式」）。

## 0. 前言到达每一条车道

两条 runner 都读取其 `mode` 所点名的前言——`implement` 用 `lane-preamble.md`，`report` 用 `lane-preamble-report.md`（相对它们自己的目录 `<plugin-root>/scripts/` 解析）——并将其原文前置到车道提示，排在五个部分之前。当前模式所需的前言缺失会使 runner 在拉起任何东西之前以非零退出——执行侧契约从不被静默丢掉。

## 1. 撰写 spec

在 `implement` 模式下，从干净的工作树开始——`git status --porcelain` 为空。runner 用 `git status` 检测车道的变更，因此预先存在的脏状态会让空跑看起来像做了工作（见下文 `no_diff`）。

把五部 spec 写成 JSON，写入目标仓库的 `.fable-advisor/pending/<slug>.json`：

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-6-astra", "effort": "medium", "service_tier": "fast", "idle_timeout_sec": 600
}
```

调谐字段可选，且失败即响——越界值或未知顶层键会被拒绝为 `spec_invalid`，从不被静默强制转换。receipt 记录 runner 提交给 CLI 的值。

- `model` — `gpt-6-astra`（默认）、`gpt-5.6-luna` 或 `gpt-5.6-sol`；codex 目录是静态白名单，因此已退役的名字是 `spec_invalid`。
- `effort` — `model_reasoning_effort`：`low | medium | high | xhigh | max`。默认随模型：astra → `medium`，luna → `max`，sol → `high`。一个任务用哪个拨盘，由填充表决定。
- `title` — 可选；提示第一行，原文纯文本，不加 Markdown 标记。省略时该行是 spec 文件去掉 `.json` 的基名。
- `service_tier` — 省略则用 Codex 自己的默认；`"fast"` 是 Codex 的速度模式：大约快 1.5 倍，ChatGPT credit 消耗大约为 2.5 倍，智力不损失。不适用于 API-key 计费。
- `idle_timeout_sec` — 静默截止（默认 600 秒）：*最后*一个事件之后多久杀掉停滞的 CLI 子进程。一直在吐事件的车道要跑多久就跑多久；被切断的只有静默，而该路径会跳过核验，因此在这里被切断的车道会完全失去它的核验证据。
- `timeout_sec` — 对整次运行的可选绝对上限；无默认值，省略即不设上限。
- `resume_session_id` — 先前的 codex session id；见下文「返工票」。
- `mode` — `implement`（默认）或 `report`；见下文「报告模式」。

**回退。** 若 astra 在会话建立之前失败（`preparation_stalled`，或尚无 session id 的 `codex_failed`），runner 按 luna 的默认 effort 在 luna 上重试一次；receipt 显示 `model_requested: gpt-6-astra`、`model_used: gpt-5.6-luna`，以及非空的 `fallback_reason`。一旦会话已存在则不回退——半成品运行不会在另一模型上重做。sol 与 luna 从不回退。验收一次发生过回退的运行时，用你自己的话复述降级；receipt 负责披露，你负责承认。

## 2. 运行 runner

本 skill 的基目录是 `<plugin-root>/skills/orchestration`，因此 runner 在上两级：

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. 等待 runner

车道完成于 **runner 进程退出** —— 不是事件流出现 `end` 事件时，也不是一次 sleep 到期时。等待方式只有两种，没有第三种：

- 在前台运行 runner，让 Bash 在退出时返回。
- 若已后台化，`Read` 后台 Bash 调用所报告的输出文件，并反复读取直到下文的完成证据出现。`TaskOutput` 已正式弃用，改用该 `Read`；弃用并不等于今天不可用，但等待协议按 `Read` 来写。

完成证据是 pending 文件消失，或 receipt 出现在 `.fable-advisor/receipts/` 下。绝不要用 `sleep N` 再 `ls .fable-advisor/pending/` 充当等待——固定睡眠会在 runner 已经退出之后继续烧完整段间隔。对于并行车道，逐条 block 每个后台任务，或在同一条消息里前台运行各 runner。

有三个互相独立的时钟压在一次派发上，每一个都能单独结束它：

- **runner 自己的静默截止**（`idle_timeout_sec`，默认 600 秒）在事件流静默这么久之后杀掉 CLI 子进程、跳过核验，并留下一份 `idle_timeout` receipt。显式给出的 `timeout_sec` 在其之上再加一道绝对上限，留下 `timeout` receipt；不给则 runner 不设任何总量限制。
- **宿主 Bash 工具的 `timeout`**（默认 600000 毫秒，最大 3600000 毫秒）杀掉前台调用。runner 来不及写下任何东西，因此根本没有 receipt，而 pending spec 留在原地。既然 runner 默认不设上限，这就是前台派发的真正天花板：预计要跑很久的票据需要显式传入更大的 Bash `timeout`。
- **后台读取** 不杀任何东西，自身也没有截止：对任务输出文件做一次 `Read` 返回目前已写入的内容，车道可能仍在运行，因此一次读取不等于一次等待——反复读取直到完成证据出现，并依据该证据裁决（pending 文件已消失、receipt 已出现），而不是依据输出长度。这是唯一没有上限的路径；单次前台调用永远不可能超过 60 分钟。

让 runner 自己跑完，总是比杀掉它更便宜。CLI 子进程以 detached 方式拉起，处在它自己的进程组中，因此它能在一个瞄准 runner 进程组的信号下存活。runner 捕获 SIGTERM 与 SIGINT，杀掉子进程树并写下一份 `interrupted` receipt——但对 runner 的一次 SIGKILL 仍会留下 CLI 继续运行、继续改动仓库，且完全没有 receipt。

## 4. 裁决 receipt

runner 把 receipt 打印到 stdout，并写入 `.fable-advisor/receipts/<spec_hash>.json`：

- `error_class` — `complete | spec_invalid | codex_unavailable | preparation_stalled | idle_timeout | timeout | interrupted | codex_failed | verification_failed | no_diff | unexpected_diff | empty_report | git_status_failed`。
- `codex_session_id` — 绑定到所拉起进程的事件流，不受并发会话串扰；在恢复运行上它等于被恢复的 id。
- `model_requested`、`model_used`、`fallback_reason`（无回退时为 null）、`resumed_from`（无恢复时为 null）、`end_to_close_ms`（终止事件到进程 close；未见终止事件时为 null——这是诊断，不是门禁）、`max_idle_ms`（CLI 流上相邻两个事件之间的最长间隔，从子进程拉起量到最后一个事件；未观察到任何事件时为 null——这是诊断，不是门禁：一次 `idle_timeout` 之后它说明静默截止是不是定得太紧，正常跑完的运行上它显示还剩多少余量）、`idle_timeout_sec` 与 `timeout_sec`（本次实际生效的值；未设绝对上限时 `timeout_sec` 为 null）。三层，不是两层：`model_requested` 是 spec 请求的值；`model_used` 与 `effort` 是 runner 提交给 CLI 的值（发生回退时，是重试那次的值）；runner 不读取 CLI 运行事件来获知实际执行的配置，因此那一层仍未知——引用 receipt 的 model 或 effort 时，写 "submitted, not observed"。
- `dirty_baseline` — 开跑前一次 `git status --porcelain` 非空为 `true`，空为 `false`，该次 `git status` 本身失败为 `null`（运行继续）。两种模式、两条 runner 都记录。
- `changed_files`，外加核验命令的实际退出码与输出尾部。

`no_diff` 意味着 `files` 非空且 implement 模式下没有任何变更；pending 文件保留。在普通 spec 上这是一次静默空跑——去查。在返工票上，当车道发现缺陷无法复现时，这是预期答案：读报告、删除 pending 文件，并说明。`git_status_failed` 意味着 runner 无法判定改了什么；它不是 `complete`。

`idle_timeout` 与 `timeout` 意味着某个时钟切断了这条车道，而不是它的工作有错——而且因为两条路径都跳过核验，receipt 里没有可供裁决的核验证据。被切断会话的数据在磁盘上完好，所以干净的恢复方式是一张返工票，在 `resume_session_id` 中携带该 receipt 的 session id：车道恢复运行并跑完它自己的核验。由你自己手工核验一条被切断车道的工作树，不是恢复路径。

CLI 车道验收 = `error_class: complete`、非空 session id、可对照工作树抽查的核验输出，**并且** diff 通过 [SKILL.md](SKILL.md) 中的分层验收。缺失或非 complete 的 receipt 即未完成。第 3 层是 `advisor` 的 acceptance 形状；由哪种填充来答，是填充表中 `advisor` 那一行。

receipt 由机械强制执行：插件 Stop hook（**receipt gate**）在 `.fable-advisor/pending/` 下任何 spec 缺少 `complete` receipt 时阻止结束。一旦 `complete`，runner 自行删除 pending spec。若你放弃或改道一项 pending 任务，删除其 pending 文件并显式说明——绝不让 gate 成为唯一知情者。gate 强制的是 receipt 的存在；其内容仍由你裁决。

把 `.fable-advisor/` 加入目标仓库的 `.gitignore`——receipt 内嵌命令输出。receipt 按 spec 哈希键控，因此带不同 spec 文件的并行 runner 调用不会在 receipt 上碰撞——但同一工作树上的两个执行者会互相覆盖对方的改动，不同的 pending 文件名不是隔离。一次「挑选更强 diff」的竞速需要每位选手一个隔离工作目录（`git worktree add`），各自持有自己的 pending spec 并收到自己的 receipt，runner 的 `--cwd` 指向该 worktree。

## 返工票

返工票是一份新的五部 pending 文件，携带 `resume_session_id` —— 被返工那次运行的 `codex_session_id`（或 `grok_session_id`）。runner 调用 `codex exec resume <id>`（grok：`--resume <id>`），因此车道保留它已经付过的上下文；receipt 记录 `resumed_from`，其 session id 等于被恢复的那个。Objective = 缺陷，Files = 原范围，Verification = 失败的那条检查——里面不写修复方案（形态见 [SKILL.md](SKILL.md)）。返工票也失败时，归因决定（SKILL.md「升级」）：契约缺口在修正契约下保留 `resume_session_id`；能力失败则按 SKILL.md 升级梯做一次提升（同型号升 `effort`，或换型号；`senior` 档位只经其门到达）、新会话——省略 `resume_session_id`，并把原契约、先前车道的报告及其 receipt 交给接管契约。

## 报告模式

`mode` 是两条 runner 上的可选键：`implement`（默认，上文所述语义）或 `report`。报告模式把只读角色——`explorer` 或 `advisor`——派到 Grok 或 GPT 家族，且不期望 diff：

- CLI 以只读工具集运行；`files` 是读取范围，可为空；`verification` 可为空。
- CLI 由报告前言交代，而不是 `worker` 前言。
- 工作树无变更是正常结果，且为 `complete`；receipt 额外携带 `mode` 与 `report`（CLI 的最终消息，即车道的答案）。
- 开跑前干净、跑完后脏的工作树是错误类 `unexpected_diff`，绝不是 `complete`：只读角色写了文件是失败，不是彩头。当 `dirty_baseline` 为 `true` 时不判 `unexpected_diff`；`empty_report` 与 `complete` 的判定照常，`changed_files` 仍记录运行后的观察值。此时只读工具集是唯一防线。
- 工作树干净但收集到的报告文本为空或仅空白，是错误类 `empty_report`，绝不是 `complete`：只读角色什么都没说，就还没有作答。pending spec 保留。
- 报告模式下的优先级：先 `unexpected_diff`（车道弄脏的树），再 `empty_report`，然后 `complete`。
- receipt gate 照常适用：没有 `complete` receipt 的 report-mode pending spec 与其他任何 pending 一样阻塞会话。

未知的 `mode` 值是 `spec_invalid`。pending/receipt 流程、等待协议和 `resume_session_id` 不变。

## Grok 差异

`scripts/run-grok.mjs` —— 同一 CLI 契约（`--spec`、`--cwd`），同一前言，同一 pending/receipt 流程，同一 receipt gate，同一等待协议，同一 `mode` 取值。

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec 键：五个部分加上可选的 `model`、`effort`、`mode`、`title`、`idle_timeout_sec`、`timeout_sec` 和 `resume_session_id`。
- `effort` — 可选，白名单 `low | medium | high | xhigh`；越界值是 `spec_invalid`。省略则不发送 effort 标志，因此 CLI 自己的默认生效；receipt 记录 runner 提交给 CLI 的值（省略时为 null），从不是 CLI 实际跑的值。这就是在不换车道的情况下给 grok `worker` 拨档位的方式。
- `model` — 默认省略：未设置则不发送 `-m` 标志，因此 CLI 跑自己的默认并跟踪实时目录（当前为 grok-4.6，2026-09），世代更换时 spec 零改动。仅在有意挑选 `grok models` 列出的非默认目录条目时才设置。当目录可读时，`model` 对照每一个列出的条目校验——不在目录中的模型是 `spec_invalid`。目录不可读不是 `grok_unavailable`：runner 记录一条诊断、跳过校验，由真正的运行决定可用性。
- 错误类镜像 `codex lane`（`grok_unavailable | grok_failed | …`，外加 `no_diff`、`unexpected_diff`、`empty_report` 和 `git_status_failed`）。receipt 携带同样的 `model_requested` / `model_used` / `fallback_reason` / `resumed_from` / `end_to_close_ms` / `max_idle_ms` / `idle_timeout_sec` / `timeout_sec` 字段（`fallback_reason` 保持 null——`grok lane` 没有定义模型回退），并额外记录 grok 结束事件中的 `usage` 与 `total_cost_usd`。`grok_session_id` 由 runner 注入（`--session-id`），而非从流中嗅探。

## 派发，而非探测

切勿预先探测 CLI 的认证状态（例如 `grok models` 登录快照之类）：grok CLI 只在真正运行时刷新登录，且用户侧的提供商配置可以完全绕过认证，因此登出快照不是该车道宕机的证据。预检最多可检查安装（`which grok`）。把 spec 路由出去，让 runner 的 receipt 决定——`*_unavailable` 触发 [SKILL.md](SKILL.md) 中的改道规则。
