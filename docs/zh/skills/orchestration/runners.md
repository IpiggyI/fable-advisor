# runner —— codex lane 与 grok lane

第一次运行 runner 之前阅读本文。主代理通过确定性 runner 直接驱动两个 CLI 生产者。`grok lane` 需要 [Grok CLI](https://x.ai/cli)；`codex lane` 需要 codex CLI 与 Node。两条 CLI 车道流程相同；以 codex 演练为典范，grok 的差异紧随其后。两条 runner 默认服务 `worker` 角色，并在 report mode 下服务只读角色（见下文「报告模式」）。

## 0. 路由与前言到达每一条车道

两条 runner 都读取其 `mode` 所点名的前言——`implement` 用 `lane-preamble.md`，`report` 用 `lane-preamble-report.md`（相对它们自己的目录 `<plugin-root>/scripts/` 解析）——并将其原文前置到车道提示，排在五个部分之前。当前模式所需的前言缺失会使 runner 在拉起任何东西之前以非零退出——执行侧契约从不被静默丢掉。runner 的路由就是它的 spec：键 `role`、`tier` 与 `basis`，拨盘取自 `model` 与 `effort`（第 1 节）。

## 1. 撰写 spec

在 `implement` 模式下，从干净的工作树开始——`git status --porcelain` 为空。runner 用 `git status` 检测车道的变更，因此预先存在的脏状态会让空跑看起来像做了工作（见下文 `no_diff`）。

把五部 spec 写成 JSON，写入目标仓库的 `.fable-advisor/pending/<slug>.json`：

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "role": "worker", "tier": "crux", "basis": {"kind": "key-difficulty", "ref": "…"},
  "model": "gpt-6-astra", "effort": "medium", "service_tier": "fast", "idle_timeout_sec": 600
}
```

路由键在两条 runner 上都必填：

- `role` — `implement` 模式取 `worker`；`report` 模式取 `explorer` 或 `advisor`。
- `tier` — `mainstay`、`crux` 或 `rescue`。runner 拒绝 `same-model`：同模派发是 `claude lane` 的拨盘。
- `basis` — `{"kind": …, "ref": …}`，高于 `mainstay` 时必填，在 `mainstay` 可省略：种类是 SKILL.md 对该角色、该档位接受的一种，`ref` 非空。
- 拨盘，即 `model` 加 `effort`，必须出现在档案里该角色、该档位的格里；格取 Claude Code 表与 Cursor 表的并集，因为 runner 在两个宿主上都会运行。codex runner 校验有效拨盘：省略的 `model` 或 `effort` 按下文的省略默认值计。grok runner 要求 `model` 与 `effort` 都显式写出（见「Grok 差异」）。

路由未通过这些校验的 spec，在 CLI 启动之前被拒绝为 `spec_invalid`。校验只查依据存在且格式合规，不查真假。

调谐字段可选，且失败即响——越界值或未知顶层键会被拒绝为 `spec_invalid`，从不被静默强制转换。receipt 记录 runner 提交给 CLI 的值。

- `model` — `gpt-6-astra`（默认）、`gpt-6-luna` 或 `gpt-6.1-sol`；codex 目录是静态白名单，因此其他名字都是 `spec_invalid`。
- `effort` — `model_reasoning_effort`：`low | medium | high | xhigh | max`。省略时，runner 按型号提交默认值：`gpt-6-astra` → `medium`，`gpt-6-luna` → `max`，`gpt-6.1-sol` → `high`；这是 runner 的省略默认，不是档案的默认。一个任务用哪个拨盘，由填充表决定。
- `title` — 可选；原文纯文本。runner 把提示第一行写成 `[车道] ` 加标题；省略标题时，用 spec 文件去掉 `.json` 的基名代替标题。CLI 的会话列表把这一行显示为会话名，标识让用户区分车道会话和普通会话。它的读者是用户：标题用用户的语言写一个名词短语，只由描述会话目标的词组成，不含数字编号和标点，不计标识不超过 12 个汉字或 6 个英文词，例如「令牌续期接口」。其余信息都写进五个部分。
- `service_tier` — 省略则用 Codex 自己的默认；`"fast"` 是 Codex 的速度模式：大约快 1.5 倍，ChatGPT credit 消耗大约为 2.5 倍，智力不损失。不适用于 API-key 计费。
- `profile` — 默认省略；只在用户明确要求使用某个 Codex profile 时填写。runner 把 `--profile <name>` 紧接在 `exec` 之后传入，Codex 据此在基础配置之上叠加 `$CODEX_HOME/<name>.config.toml`（例如该 profile 指定的供应商）；新会话与续接会话都如此。
- `idle_timeout_sec` — 静默截止（默认 600 秒）：*最后*一个事件之后多久杀掉停滞的 CLI 子进程。一直在吐事件的车道要跑多久就跑多久；被切断的只有静默，而该路径会跳过核验，因此在这里被切断的车道会完全失去它的核验证据。
- `timeout_sec` — 对整次运行的可选绝对上限；无默认值，省略即不设上限。
- `resume_session_id` — 先前的 codex session id；见下文「返工票」。
- `mode` — `implement`（默认）或 `report`；见下文「报告模式」。

**不换型号。** runner 从不换型号。会话建立之前的失败（`preparation_stalled`，或尚无 session id 的 `codex_failed`）只尝试一次并报告：receipt 带该错误类，`model_requested` 与 `model_used` 都是请求的型号。主代理按 [SKILL.md](SKILL.md) 的改道规则处理。

## 2. 运行 runner

本技能的基目录是 `<plugin-root>/skills/orchestration`，因此 runner 在上两级：

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. 等待 runner

车道完成于 **runner 进程退出** —— 不是事件流出现 `end` 事件时，也不是一次 sleep 到期时。

完成证据是 pending 文件消失，或 receipt 出现在 `.fable-advisor/receipts/` 下。

runner 工作期间，在 `.fable-advisor/running/<spec_hash>.json` 维护一个运行中标记（runner、pid、spec 路径、开始时间、阶段 `preparing | cli | verifying`、事件数），每 60 秒刷新一次。每次刷新同时向 stderr 写一行进度，例如 `[run-grok] running 4m00s; phase cli; 132 events; last event 0m12s ago`。runner 在它观察到的每条退出路径上都删除该标记；180 秒未刷新的标记属于已死的 runner。在标记仍新鲜的 spec 上启动的 runner 以状态 1 退出，不写 receipt，也不启动 CLI：同一份 spec 同一时间最多只有一个 runner。

CLI 主进程退出后，runner 停止运行计时器，最多等待两秒来排空后代继承的输出管道。到期后，runner 释放剩余管道、记录诊断，并依据已观察到的退出状态继续核验和生成 receipt。预检、Git 检查和核验命令使用同样的排空期限；仍在运行的核验命令不因此获得总运行时限。

超时或中断会先启动独立的两秒收尾期限，再尝试终止进程树。Windows 的 `taskkill` 另有两秒运行上限和两秒收尾期限。即使终止失败，两处等待也会结束。若诊断说明尚未观察到退出，恢复会话或派发另一个写入任务前，先确认并停止存活进程；失败 receipt 不证明进程树已清理。

让 runner 自己跑完，总是比杀掉它更便宜。CLI 子进程以 detached 方式拉起，处在它自己的进程组中，因此它能在一个瞄准 runner 进程组的信号下存活。runner 捕获 SIGTERM 与 SIGINT，杀掉子进程树并写下一份 `interrupted` receipt——但对 runner 的一次 SIGKILL 仍会留下 CLI 继续运行、继续改动仓库，且完全没有 receipt。

CLI 车道运行期间没有传递消息的通道：runner 只交付一次提示词。要在运行中纠偏，用 `kill <pid>` 停止它的 runner，pid 取自运行中标记：这只发送 SIGTERM，中断路径能完整走完。在 Claude Code 中，对 runner 的后台任务调用 `TaskStop` 同样先发 SIGTERM，但随后很快强制结束，可能截断 receipt 的写入。然后删除旧的 pending spec，用 `resume_session_id` 指向那份 `interrupted` receipt 的 session id，排入修正后的契约；车道带着原有上下文继续。

### 经 Bash 等待（仅 Claude Code）

等待方式只有两种，没有第三种：

- 在前台运行 runner，让 Bash 在退出时返回。这适合预计远在 Bash `timeout` 之内完成的票据。
- 把 runner 本身作为一次后台 Bash 调用（`run_in_background: true`）运行，然后结束本轮，或继续做互不依赖的工作。该进程退出时，宿主会唤醒会话；那时再裁决 receipt。runner 运行期间，receipt gate 允许本轮结束。

只有主会话以结束本轮的方式等待。子代理结束本轮就是把报告交还给上级，receipt gate 不在这种结束上运行，所以子代理在前台运行 runner。

不要自己写等待循环：不用 `sleep`、`while`、`until` 或 `pgrep` 轮询，前台不行，包进后台调用也不行。在 runner 外面包一层循环的后台调用，会把退出通知交给循环而不是 runner；`pgrep -f <pattern>` 会匹配到运行它的 shell 自身，所以基于它的循环永远不会结束。反复读取输出文件也不是等待；`TaskOutput` 也不是，它已正式弃用。

对于并行车道，在同一条消息里把每个 runner 各作为一次后台调用启动，或在同一条消息里前台运行各 runner。

有三个互相独立的时钟压在一次派发上，每一个都能单独结束它：

- **runner 自己的静默截止**（`idle_timeout_sec`，默认 600 秒）在事件流静默这么久之后杀掉 CLI 子进程、跳过核验，并留下一份 `idle_timeout` receipt。显式给出的 `timeout_sec` 在其之上再加一道绝对上限，留下 `timeout` receipt；不给则 runner 不设任何总量限制。
- **宿主 Bash 工具的 `timeout`**（默认 600000 毫秒，最大 3600000 毫秒）杀掉前台调用。runner 来不及写下任何东西，因此根本没有 receipt，而 pending spec 留在原地。既然 runner 默认不设上限，这就是前台派发的真正天花板：预计要跑很久的票据需要显式传入更大的 Bash `timeout`。
- **后台调用** 不杀任何东西，自身也没有截止：只有 runner 自己的截止约束它。可能超过 60 分钟的票据放到后台运行，因为单次前台调用永远不可能超过 60 分钟。

## 4. 裁决 receipt

runner 把 receipt 打印到 stdout，并写入 `.fable-advisor/receipts/<spec_hash>.json`：

- `error_class` — `complete | spec_invalid | codex_unavailable | preparation_stalled | idle_timeout | timeout | interrupted | codex_failed | verification_failed | no_diff | unexpected_diff | empty_report | git_status_failed`。
- `codex_session_id` — 绑定到所拉起进程的事件流，不受并发会话串扰；在恢复运行上它等于被恢复的 id。
- `model_requested`、`model_used`、`fallback_reason`（恒为 null）、`resumed_from`（无恢复时为 null）、`end_to_close_ms`（终止事件到进程自然触发 `close` 的时长；未见终止事件或管道被强制释放时为 `null`——这是诊断，不是门禁）、`max_idle_ms`（CLI 流上相邻两个事件之间的最长间隔，从子进程拉起量到最后一个事件；未观察到任何事件时为 null——这是诊断，不是门禁：一次 `idle_timeout` 之后它说明静默截止是不是定得太紧，正常跑完的运行上它显示还剩多少余量）、`idle_timeout_sec` 与 `timeout_sec`（本次实际生效的值；未设绝对上限时 `timeout_sec` 为 null）。三层：`model_requested` 是 spec 请求的值；`model_used` 与 `effort` 是 runner 提交给 CLI 的值；runner 不读取 CLI 运行事件来获知实际执行的配置，因此那一层仍未知——引用 receipt 的 model 或 effort 时，写 "submitted, not observed"。
- `dirty_baseline` — 开跑前一次 `git status --porcelain` 非空为 `true`，空为 `false`，该次 `git status` 本身失败为 `null`（运行继续）。两种模式、两条 runner 都记录。
- `role`、`tier` 与 `basis` — spec 提交的路由，原样记录。`lane_finished_at` — CLI 进程退出的时刻，在 runner 跑核验之前记录；它是续用窗口的时间来源（见「返工票」）。
- `changed_files`，外加每条核验命令的实际 `exit_code`、`output_tail`（合并输出的最后 2,000 个字符）与 `output_log`：相对于 `--cwd` 的路径 `.fable-advisor/receipts/<spec_hash>.verification-<n>.log`，文件里是该命令的完整输出；runner 写不出该文件时为 `null`。

一旦 `complete`，runner 自行删除 pending spec。

`no_diff` 意味着 `files` 非空且 implement 模式下没有任何变更；pending 文件保留。在普通 spec 上这是一次静默空跑——去查。在返工票上，当车道发现缺陷无法复现时，这是预期答案：读报告、删除 pending 文件，并说明。`git_status_failed` 意味着 implement 模式下 runner 无法判定改了什么；它不是 `complete`。报告模式不抛这个类：运行后的 `git status` 失败时 `changed_files` 为空，并保留已记下的 `dirty_baseline`，随后仍按 `empty_report` 与 `complete` 判定。

`idle_timeout` 与 `timeout` 意味着某个时钟切断了这条车道，而不是它的工作有错——而且因为两条路径都跳过核验，receipt 里没有可供裁决的核验证据。被切断会话的数据在磁盘上完好，所以在续用窗口之内（见「返工票」），干净的恢复方式是一张返工票，在 `resume_session_id` 中携带该 receipt 的 session id：车道恢复运行并跑完它自己的核验。由你自己手工核验一条被切断车道的工作树，不是恢复路径。

runner 是契约检查列表的执行者：CLI 退出之后由它自己跑 `verification`，所以车道被告知不要重复跑，receipt 里的输出就是那一次执行。检查失败时，从它的 `output_log` 读出失败用例，只重跑这些用例；为了查看失败而重跑整份列表，等于重复最贵的那一步。`complete` receipt 是它自己那张契约的证据——既不是对该契约的验收，也不是对整个任务的验收。

CLI 车道验收 = `error_class: complete`、非空 session id、可对照工作树抽查的核验输出，**并且** diff 通过 [SKILL.md](SKILL.md) 中的分层验收。缺失或非 complete 的 receipt 即未完成。第 3 层是 `advisor` 的验收形状；由哪种填充来答，是填充表中 `advisor` 那一行。

把 `.fable-advisor/` 加入目标仓库的 `.gitignore`——receipt 内嵌命令输出。receipt 按 spec 哈希键控，因此带不同 spec 文件的并行 runner 调用不会在 receipt 上碰撞——但同一工作树上的两个执行者会互相覆盖对方的改动，不同的 pending 文件名不是隔离。一次「挑选更强 diff」的竞速需要每位选手一个隔离工作目录（`git worktree add`），各自持有自己的 pending spec 并收到自己的 receipt，runner 的 `--cwd` 指向该 worktree。同时进行的契约用同样的隔离：各在自己的工作目录里运行（`git worktree add`），runner 的 `--cwd` 指向其中。worktree 的 `.fable-advisor/receipts/` 存着它的 receipt 与核验日志，所以删除 worktree 之前，先把它们另存出来。

### receipt gate（仅 Claude Code）

receipt 由机械强制执行：插件 Stop hook（**receipt gate**）在 `.fable-advisor/pending/` 下任何 spec 缺少 `complete` receipt、且没有新鲜运行中标记时阻止结束。新鲜标记允许本轮结束，因为后台 runner 退出时宿主会唤醒会话。若你放弃或改道一项 pending 任务，删除其 pending 文件并显式说明——绝不让 gate 成为唯一知情者。gate 强制的是 receipt 的存在；其内容仍由你裁决。

## 返工票

返工票是一份新的五部 pending 文件，携带 `resume_session_id` —— 被返工那次运行的 `codex_session_id`（或 `grok_session_id`）。runner 调用 `codex exec resume <id>`（grok：`--resume <id>`），因此车道保留它已经付过的上下文；receipt 记录 `resumed_from`，其 session id 等于被恢复的那个。Objective = 缺陷，Files = 原范围，Verification = 能覆盖失败用例和修复波及范围的最小可运行检查——里面不写修复方案（形态见 [SKILL.md](SKILL.md)）。返工票也失败时，归因决定（SKILL.md「升级」）：契约缺口在修正契约下保留 `resume_session_id`，以返工上限为限（SKILL.md「会话续用」）；能力失败则按 SKILL.md 升级梯升到下一档、新会话——省略 `resume_session_id`，并把原契约、先前车道的报告及其 receipt 交给接管契约。

车道会话的每一次续用都只在该车道的续用窗口之内进行（SKILL.md「会话续用」；取值在路由档案的「会话续用窗口」一节）。这包括返工票、修正契约、被时钟切断后的续跑所带的 `resume_session_id`，以及发给 `claude lane` 子代理的任何 `SendMessage`。窗口从车道上次活动算起。runner 车道取 receipt 的 `lane_finished_at`。绝不用 receipt 的 `finished_at`：它在核验之后才记录。超出窗口或返工上限时，省略 `resume_session_id`，在同一档位、同一拨盘上新开会话，带上缺陷、原契约、上轮报告和 receipt。

## 报告模式

`mode` 是两条 runner 上的可选键：`implement`（默认，上文所述语义）或 `report`。报告模式把只读角色——`explorer` 或 `advisor`——派到 Grok 或 GPT 家族，且不期望 diff：

- CLI 以只读工具集运行；`files` 是读取范围，可为空；`verification` 可为空。
- CLI 由报告前言交代，而不是 `worker` 前言。
- 工作树无变更是正常结果，且为 `complete`；receipt 额外携带 `mode` 与 `report`（CLI 的最终消息，即车道的答案）。
- 开跑前干净、跑完后脏的工作树是错误类 `unexpected_diff`，绝不是 `complete`：只读角色写了文件是失败，不是彩头。当 `dirty_baseline` 为 `true` 时不判 `unexpected_diff`；`empty_report` 与 `complete` 的判定照常，`changed_files` 仍记录运行后的观察值。此时只读工具集是唯一防线。
- 运行后的 `git status` 失败在报告模式下不是 `git_status_failed`。`dirty_baseline` 保持开跑前那次检查的记录（那次也失败时为 `null`，例如没有 git 仓库的树）。`empty_report` 与 `complete` 照常判定。只读工具集是写保护。
- 收集到的报告文本为空或仅空白，是错误类 `empty_report`，绝不是 `complete`：只读角色什么都没说，就还没有作答。pending spec 保留。git 不可用时这条仍然成立。
- 报告模式下的优先级：先 `unexpected_diff`（车道弄脏的树），再 `empty_report`，然后 `complete`。`git_status_failed` 不在此列。
- 在 Claude Code 中，receipt gate 照常适用：没有 `complete` receipt 的 report-mode pending spec 与其他任何 pending 一样阻塞会话。

未知的 `mode` 值是 `spec_invalid`。pending/receipt 流程、等待协议和 `resume_session_id` 不变。

## Grok 差异（仅 Claude Code）

`scripts/run-grok.mjs` —— 同一 CLI 契约（`--spec`、`--cwd`），同一前言，同一 pending/receipt 流程，同一 receipt gate，同一等待协议，同一 `mode` 取值。

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec 键：五个部分，加上必填的 `role`、`tier`、`model` 与 `effort`，高于 `mainstay` 时必填的 `basis`，以及可选的 `mode`、`title`、`idle_timeout_sec`、`timeout_sec` 和 `resume_session_id`。
- `effort` — 必填，白名单 `low | medium | high | xhigh`；越界值是 `spec_invalid`。runner 无从得知 CLI 自己的默认值，不显式写 `effort` 就无法校验拨盘；省略它的 spec 在 CLI 启动之前被拒绝为 `spec_invalid`。receipt 记录 runner 提交给 CLI 的值，从不是 CLI 实际跑的值。这就是在不换车道的情况下给 grok `worker` 设定拨盘的方式。
- `model` — 必填，理由相同；省略它的 spec 在 CLI 启动之前被拒绝为 `spec_invalid`。当目录可读时，`model` 还要对照 `grok models` 列出的每一个条目校验——不在目录中的模型是 `spec_invalid`。目录不可读不是 `grok_unavailable`：runner 记录一条诊断、跳过目录校验，由真正的运行决定可用性。
- 错误类镜像 `codex lane`（`grok_unavailable | grok_failed | …`，外加 `no_diff`、`unexpected_diff`、`empty_report` 和 `git_status_failed`）。receipt 携带同样的 `role` / `tier` / `basis` / `lane_finished_at` / `model_requested` / `model_used` / `fallback_reason` / `resumed_from` / `end_to_close_ms` / `max_idle_ms` / `idle_timeout_sec` / `timeout_sec` 字段（`fallback_reason` 恒为 null：两条 runner 都不换型号），并额外记录 grok 结束事件中的 `usage` 与 `total_cost_usd`。`grok_session_id` 由 runner 注入（`--session-id`），而非从流中嗅探。

## 派发，而非探测

切勿预先探测 CLI 的认证状态（例如 `grok models` 登录快照之类）：grok CLI 只在真正运行时刷新登录，且用户侧的提供商配置可以完全绕过认证，因此登出快照不是该车道宕机的证据。预检最多可检查安装（`which grok`）。把 spec 路由出去，让 runner 的 receipt 决定——`*_unavailable` 触发 [SKILL.md](SKILL.md) 中的改道规则。
