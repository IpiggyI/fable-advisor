# 6.2.0：全局规划与按结果验收、档位校验、会话续用窗口

Status: ready-for-agent（`gpt-6-astra[xhigh]` 评审裁决为「修改后采纳」，本稿已按意见修订；椰椰 2026-10-04 授权了文末第 1、2 项）。进度与未完成的事见 [handoff-2026-10-04.md](handoff-2026-10-04.md)。

日期：2026-10-04。证据与诊断见 [问题报告](problem-report.md)。决策将记入 ADR 0030。

## 椰椰的决定

- 2026-10-03，问题报告第 9 节的结构化提问：
  - 问题二采用 2C：文本加机械校验。
  - 授权修改 cc-usage 的记忆（选项 1D）。
  - grok 车道和 Cursor 的 `resume` 续派，续用窗口为 1 小时。
  - 不复审问题报告，改为请 `gpt-6-astra[xhigh]` 评审实施方案。
- 2026-10-03，声明续用窗口：Claude Code 1 小时，Codex 30 分钟。同日声明路由档案 worker 行两格的新值（问题报告第 6 节）。
- 2026-10-04，补充说明（原话）：
  > 不是说把01、02，03、04两两合并测试就万事大吉了，砍几次测试次数并不能从根本上解决问题，关键在于主会话要有这个全局意识在！子代理完成后返回的结果主会话要看呐，看看改的是不是符合要求的，不能纯依赖测试来判断！就拿这八张票来说，不能是前一张票完美无瑕，全部测试都通过才能开始下一张票，这样的话效率非常地低！除非是有依赖关系的，否则能并发执行的尽量并发执行，可以通过规定修改范围、切分支等方式来限制；测试是某个环节要结束了验收完好进行下一个环节
  > 其他要求：
  > - 直接干掉SKILL.md上限xx词数，每次都要问每次都会改，一点意义没有，数字完全是一拍脑子决定的
  > - 不升到7.0.0版本，升太快了，后续无颠覆性改动一律不升大版本
  > - grok缓存时间官方没说，不过无所谓按一小时来，太久了再捡起之前的会话我觉得也意义不大
  > - 同源的codex-advisor插件如果也有这个问题需要在完成后写一份交接文档到对方仓库
- 2026-10-04，结构化提问的回答：
  - 授权阶段零的探针和阶段一的端到端检查（`claude -p` 加 `--plugin-dir`）；
  - 授权 runner 车道使用分离 HEAD 的临时工作目录；
  - ADR 0024 计划的词数预算全部取消，P11 的其余部分不变。

## 评审记录

- 第一轮评审问题报告：会话 `01a1023f-7cd3-7610-87d0-73265b03eb3f`，见问题报告第 8 节。
- 第二轮评审本方案：2026-10-03 16:14 至 16:26（UTC），会话 `01a1028b-c6f3-7700-9e3d-54c962c562e3`，回执 `.fable-advisor/receipts/07988970b34a2ee6fa94ec43c5ec55037fe7aa9fb3fd05216066b24fe6ce8cd7.json`。裁决：「修改后采纳，当前稿不宜直接实施。置信度高，限于条文与源码核验。」它指出的问题已按严重程度并入下文：
  - D2 的最低兼容档可能降档；
  - 型号推导漏了 `CLAUDE_CODE_SUBAGENT_MODEL` 和别名重定向；
  - 解析不出 `SendMessage` 的目标时放行，会留下缺口；
  - 按文件修改时间校验窗口，可靠性没有证据；
  - `finished_at` 晚于验证；
  - D1 的阶段可能成为全局屏障；
  - 一致性测试排得太晚；
  - 工作树里的证据要先保存；
  - 版本号必须在说明书之后改；
  - worker 前言、`CONTEXT.md`、`issue-tracker.md`、ADR 0021 和测试夹具需要连带修改。

## 决策

### D1 问题一：主会话的全局规划

本节取代问题报告第 3.3 节的 1A 至 1C。椰椰 10-04 的说明把重点从「少跑几次测试」移到主会话的全局意识上。条文改为四条规则：

1. **派发前做全局规划。** 任务有两张以上的票时，主会话在第一次派发前，把下列内容写进任务件：
   - 依赖：哪张票需要另一张票的结果，例如接口，或在同一文件上先后修改。
   - 契约：共用文件或同一区域的票并成一份契约。这是现行规则，不变。
   - 隔离：每份契约的修改范围（Files）。同时进行的契约若会共用一个工作目录，就各用一个独立的工作目录（`git worktree`）。只换分支名而共用一个工作目录，不算隔离。Cursor 里普通的 `Task` 共用工作区，并发契约改用隔离工作树的派发类型（`best-of-n-runner`，一次尝试），否则依次执行（2026-10-04 契约 02 报告缺口后补定）。
   - 宽检查：每项宽检查覆盖哪些契约，由谁跑，在哪个时点跑。
2. **只等真实的依赖。** 没有依赖的契约在一条消息里同时派发。一份契约在它需要的契约验收通过、判定检查就绪后就派发，不等无关的契约。只有它需要的结果只能由某项宽检查证明时，才等这项宽检查。一份独立契约的验收、返工和测试，不挡另一份契约的派发。
3. **按结果验收，不只看测试。** 改写现行验收第 1 层：车道交回后，主会话对照契约逐条核对三样东西：
   - 报告对每条验收标准的说法；
   - 车道的检查证据；
   - 承载 Objective 所述行为的文件，按路径限定的差异。
   测试证明它覆盖的断言成立，不能单独证明契约整体达成。差异太大时，交 advisor 阅读差异；主会话核对「标准、证据、结论」是否一一对应，再读 advisor 标出的片段。第 3 层原有的触发条件不变：正确性关键、同家族改动、椰椰要求评审。不限定路径的全量差异仍不进主会话的上下文。
4. **宽检查一批只跑一次。** 宽检查在它覆盖的契约都落地并验收之后跑一次。宽检查包括：全量测试、渲染或浏览器检查、构建、打包、主会话自己做的渲染和人工检查，以及共用昂贵准备的检查。需要宽检查结果的后续工作，等它通过再开始；其余工作不等。契约里保留本契约的判定检查（ADR 0029 不变）。一次失败要能归因到一份契约；做不到时，把这一批分小。

提交边界仍按授权和回滚拆，与验收分开。向椰椰问提交粒度时，要给出按契约提交的选项。

**行为场景**，用于阶段一的 advisor 验收。新条文要让主会话在每个场景里做出预期的安排：

| 场景 | 预期 |
|---|---|
| A、B 没有共同文件，C 需要 A 的接口 | A、B 在一条消息里同时派发，各用独立工作目录；A 验收通过后立即派 C，不等 B；宽检查在 A、B、C 落地后跑一次，除非 C 需要只有宽检查能证明的结果 |
| 两张票改同一张表格的同一区域 | 并成一份契约，验收一次；提交按授权拆 |
| 车道的测试全部通过，但差异实现的是另一种行为 | 主会话读限定路径差异时发现，拒收并开返工票 |
| 两份界面契约 | 两份都落地并验收后，渲染截图合成一轮 |

### D2 问题二：档位准入与机械校验（2C）

**文本**，放在 `SKILL.md`「Routing」的第一阶段：

- 先按任务难点定档位。新工作从 `mainstay` 开始；已识别关键难点或相互制约的条件时，首轮可以进 `crux`；首轮 `rescue` 只凭椰椰声明。升档按升级梯。
- 椰椰声明的家族或型号只筛选候选。取满足三个条件的最低一档：不低于按难点或升级梯定下的档位；有兼容候选；准入允许。家族或型号声明可以作为 `crux` 的 `user-declaration` 依据，`ref` 写椰椰的原话；它不算 `rescue` 的准入。三个条件同时满足不了时，向椰椰报告约束冲突，不自动降档。（`crux` 一句是 2026-10-04 契约 02 报告缺口后主会话补定的。）
- 每次派发都写出路由：角色、档位、拨盘；高于 `mainstay` 时写出依据。经 `SendMessage` 或 `resume` 发给已有会话的消息，也要写出路由。

**机械校验的入口：**

| 入口 | 路由写在哪里 | 谁校验 |
|---|---|---|
| codex 与 grok runner | spec 新增字段 `role`、`tier`、`basis` | runner，在启动 CLI 之前 |
| Claude Code 的 `Agent`，类型为 `fable-advisor:*` | 提示词第一行 `Route:` | 新的 `PreToolUse` 钩子 |
| Claude Code 的 `SendMessage`，目标是本会话本角色池的子代理 | 消息第一行 `Route:` | 同一个钩子 |

**格式：**

- spec：`"role": "worker"`，`"tier": "crux"`，`"basis": {"kind": "key-difficulty", "ref": "…"}`。`tier` 为 `mainstay` 时可以不写 `basis`。回执原样记录这三个字段。
- `Route:` 行：`Route: role=<role> tier=<tier> dial=<dial> basis=<kind> ref=<到行尾的文字>`。拨盘写法同档案，例如 `opus-5-5[medium]`；`haiku-4-5` 不带方括号。`tier` 为 `mainstay` 时省略 `basis` 和 `ref`。claude 车道的提示词以 `Route:` 行开头，下一行是读前言的指令（`lanes-claude-code.md` 现在要求提示词以读前言的指令开头，随之改）。

**校验规则**（runner 与钩子相同，除非另行注明）：

1. **角色。** runner 的 implement 模式只接受 `worker`，report 模式只接受 `explorer` 或 `advisor`。钩子按 agent 文件名取角色；`Route:` 写的角色必须与它一致。
2. **拨盘。** 只校验提交的配置；子代理实际跑的型号，仍以子代理记录的 `message.model` 为准，二者不混同。
   - codex runner 取有效提交值：省略时照算 runner 自己的省略默认值。
   - grok runner 必须显式写 `model` 和 `effort`，否则拒绝，因为 CLI 的默认值 runner 无从得知。这取代 ADR 0021 决策 10 的「grok 跟随 CLI 默认型号」。
   - 钩子要求本角色池的 `Agent` 派发显式带 `model`；不带就拒绝，因为不带时的解析顺序还受 agent 文件的 `model:` 与 `CLAUDE_CODE_SUBAGENT_MODEL` 影响。例外：`CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 为真值时，宿主从 `Agent` 的参数里去掉了 `model`，钩子不要求它，按强制的型号推出拨盘：`CLAUDE_CODE_SUBAGENT_MODEL` 有值且不是 `inherit` 时取它，否则取会话型号。
   - 别名按宿主的解析顺序推出型号（阶段零核实）：别名所属家族与会话型号相同时，取会话型号；否则取别名重定向变量；都没有时按档案的锚点对应：`haiku`、`sonnet`、`opus`、`fable` 依次为 `haiku-4-5`、`sonnet-5-5`、`opus-5-5`、`fable-5-1`。会话型号读不到时跳过家族这一步。推出的型号规范化后不是锚点型号时，拒绝。强度取 agent 文件 frontmatter 的 `effort:`；`haiku-4-5` 不比强度。`explorer-h` 配 `sonnet` 按 `high` 校验，所以路由要写 `sonnet-5-5[high]`。
   - `SendMessage` 的拨盘取目标子代理的实际配置：它的记录里最后一条助手记录的 `message.model`（规范化）与 `effort`。目标还没有助手记录时，取它的 `meta.json`（`agentType` 与 `model`），再按上一条推出。
   - `Route:` 写的拨盘必须与推出的拨盘相同。
3. **档位。** （角色，拨盘）必须出现在档案里该角色、该档位的格里。runner 取两张表同一格的并集，因为它在两个宿主上都会运行；钩子取 Claude Code 表。档案是唯一来源，不另建路由配置。实现上把三件事分开：解析档案、校验规则、取宿主的值。
4. **依据。**

   | 角色 | `crux` 接受的依据种类 | `rescue` 接受的依据种类 |
   |---|---|---|
   | worker、explorer | `key-difficulty`、`failure`、`user-declaration` | `failure`、`user-declaration` |
   | advisor | `low-confidence`、`user-declaration` | `user-declaration` |

   `ref` 不能为空：失败写失败那次派发的标识（回执哈希、会话 id 或 agentId），声明写椰椰的原话。程序只查依据存在、种类合规，不查真假，条文要写明这一点。
5. **同模派发。** 只在钩子、只对 `worker-*` 成立：`tier=same-model`，依据种类 `same-model`，`ref` 写仓库规定的产物类别。钩子把推出的型号与会话型号规范化后比较；会话型号取会话记录最后一条助手记录的 `message.model`，读不到就拒绝。两个 runner 拒绝 `tier=same-model`。产物类别和依据的真假仍由主会话判断，不属于机械保证。
6. **`name`。** 带 `name` 的本角色池派发一律拒绝，因为 `name` 会让 agent 文件的强度失效。
7. **`SendMessage` 的目标。**
   - 只带 `notify_when_idle`、不带消息的订阅，不是派发，放行。
   - 目标是本会话 `subagents/` 下有 `meta.json` 的子代理：`agentType` 以 `fable-advisor:` 开头时校验，否则放行。
   - 目标是名字、`main` 或别的会话：放行。本角色池的子代理派发时不带 `name`（规则 6），所以按名字寻址的目标一定不在本角色池里。
   - 目标形如 agentId，却在本会话找不到：拒绝，理由写明找不到它的记录。
   - 停止一个子代理用 `TaskStop`，钩子不管。暂停、纠正等消息照样带 `Route:` 行；拒绝理由里给出目标的拨盘，主会话照抄即可。
8. **拒绝。** 字段缺失、格式错误或互相矛盾时拒绝。理由写明缺了什么，以及该角色、该档位的合法拨盘有哪些。钩子用 `permissionDecision: deny`，不用 `ask`。档案读不出或解析失败也拒绝。

**覆盖不到的地方**，条文要写明：

- Cursor 钉型号的 `Task`（含 `resume`）只有文本规则。Cursor 经 Shell 跑的 codex runner 受 runner 校验。
- 没有 Python 时钩子放行，stderr 写一行说明。receipt gate 也是这样。
- 内置代理（`general-purpose`、`Explore` 等）不属于本角色池，钩子不管。

**宿主事实。**

- 已核实，取自 cc-usage 会话的已有样本（主会话记录第 1754 至 2885 行）：
  - `SendMessage` 的 `to` 是子代理的 agentId，与 `subagents/agent-<id>.meta.json` 的文件名一致；
  - `meta.json` 含 `agentType` 与 `model`（别名）；
  - 子代理记录的每条助手记录带 `message.model` 与 `effort`；
  - 暂停、恢复、纠正路径这类消息也经 `SendMessage` 发出。
- 文档所述，未经本机验证（2026-10-04 由 Claude Code 文档代理查证）：
  - 别名重定向变量：`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`ANTHROPIC_DEFAULT_FABLE_MODEL`。
- 阶段零核实（2026-10-04，Claude Code 2.1.287）。探针插件与样本在 `evidence/phase0/`：`hook-runA.jsonl` 至 `hook-runC.jsonl` 是钩子收到的原始输入，`subagents/` 是子代理的 `meta.json` 与助手记录摘要，`main-*-assistant-records.json` 是主会话的助手记录摘要。三次会话：A 在 `auto` 模式，设 `CLAUDE_CODE_SUBAGENT_MODEL=sonnet`；B 在 `bypassPermissions` 模式，另设 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`；C 的会话型号是 `claude-sonnet-4-5-20250929`。
  - `--plugin-dir` 加载的同名插件取代已安装的 6.1.0：init 记录的插件表里只有 `fable-advisor@inline`，agent 只有探针自带的 `fable-advisor:explorer-h`。
  - 匹配器 `Agent|SendMessage` 两者都命中。钩子输入和 tool_use 里的工具名是 `Agent`；init 记录的工具表写作 `Task`。
  - `permissionDecision: "deny"` 在 `auto` 与 `bypassPermissions` 两种模式的无界面会话里都生效，被拒的子代理没有启动。`Agent` 的工具结果是 `PreToolUse:Agent hook error: <理由>`，`SendMessage` 的是 `<理由>`，两者都标为错误。
  - 钩子输入：主会话发出的调用含 `session_id`、`prompt_id`、`transcript_path`、`cwd`、`permission_mode`、`hook_event_name`、`tool_name`、`tool_input`、`tool_use_id`、`effort`（对象，如 `{"level": "medium"}`）。子代理发出的调用另含 `agent_id`、`agent_type`，没有 `effort`；`transcript_path` 仍是主会话的记录。
  - `Agent` 的 `tool_input`：`description`、`prompt`、`subagent_type`，按需出现 `model`、`run_in_background`、`isolation`。本版本的 `Agent` 没有 `name` 参数；规则 6 留作防御。
  - `SendMessage` 的 `tool_input`：`to`、`summary`、`message`；宿主另加 `type`（`"message"`）、`recipient`（同 `to`）和 `content`。`content` 是 `message` 的截断预览，钩子读 `message`。只订阅时 `message` 是空字符串，`notify_when_idle` 为真；目标是子代理时宿主自己回 `success: false`。
  - 子代理记录在 `<transcript_path 去掉 .jsonl>/subagents/agent-<agentId>.jsonl`，`meta.json` 在同一目录，含 `agentType`、`description`、`toolUseId`、`spawnDepth`、`requestShape`、`requestNonInteractive`；派发带 `model` 时另有 `model`，是原样的别名。agentId 形如 `a` 加 16 位十六进制数。
  - 钩子运行时，本次调用所在的助手消息还没有写进会话记录，最后一条助手记录属于上一条消息。会话的第一条消息里还没有助手记录。
  - 型号的解析顺序：
    - 单次派发的 `model` 优先于 `CLAUDE_CODE_SUBAGENT_MODEL`（A：派发写 `haiku`，子代理跑 `claude-haiku-4-5-20251001`）。
    - `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 是布尔变量，`1`、`true`、`yes`、`on` 为真。为真时 `Agent` 的参数里没有 `model`，子代理跑 `CLAUDE_CODE_SUBAGENT_MODEL`（B：跑 `claude-sonnet-5-5`，`meta.json` 里没有 `model`）。该变量未设或为 `inherit` 时继承会话型号；这一条取自 2.1.287 的代码，没有样本。
    - 别名所属家族与会话型号相同时，子代理跑会话型号（C：派发写 `sonnet`，子代理跑 `claude-sonnet-4-5-20250929`）。
  - 助手记录的 `effort`：haiku 子代理没有这个字段；sonnet 子代理是 agent 文件的强度（B：`high`）。
  - 钩子进程能读到 `CLAUDE_PLUGIN_ROOT`、`CLAUDE_PROJECT_DIR`，以及启动 Claude Code 时设的 `CLAUDE_CODE_SUBAGENT_MODEL`。

按 D6，不兼容的 spec 字段只升次版本。

### D3 问题三：会话续用窗口（3A 加 3C 的取法二）

- **窗口。** 都是椰椰声明的续用政策，不是实测的缓存寿命：
  - claude 车道：Claude Code 里经 `SendMessage` 续派，1 小时；
  - codex 车道：30 分钟；
  - grok 车道：1 小时；
  - Cursor 的 `Task` `resume`：1 小时。
  取值写进路由档案新的一节；条文只引用档案。
- **规则。** 以下几种续用都只在窗口之内进行：返工票、修正契约、被时钟切断后的续跑、发给子代理的后续消息、新票。间隔从车道上次活动算起，时间要有可追溯的来源：
  - runner 回执新增字段 `lane_finished_at`：CLI 进程退出的时刻，在 runner 跑验证之前记录。不能用 `finished_at`，因为它在验证之后才记录。
  - claude 车道：子代理记录最后一条助手记录的时刻。
  - Cursor 的 `Task`：结果返回的时刻。主会话在结果到达时用 Shell 记下（`date -u +%Y-%m-%dT%H:%M:%SZ`），写进任务件。（2026-10-04 契约 02 报告缺口后补定。）
  时间不明时，按超出窗口处理。
- **超出窗口。** 在同一档位、同一拨盘上新开会话。契约带上缺陷、原契约、上轮报告和回执。新开会话不算升档，也不重置失败计数。续用时不改强度。
- **例外。** 采用 `gpt-6-astra` 第一轮建议的措辞（问题报告第 5.3 节）：超过窗口仍要续用时，派发说明要点名原会话独有的可观察状态，说明为何不能交接，写出重建的步骤和代价，并披露接受冷缓存的成本。
- **新票。** 同一区域、确实需要共享上下文、同一拨盘、在窗口之内，才能续用已有会话；否则新开。
- **机械校验。** 本轮不做。runner 跨工作目录查不到会话的上次活动；按文件修改时间判断的可靠性没有证据。将来要做，先定下：哪些事件算活动、边界时刻、运行中的纠正消息怎么算、例外写在哪个字段。

### D4 路由档案（椰椰 10-03 的声明）

按问题报告第 6 节修改，并加两项：

- 新增「会话续用窗口」一节，写入 D3 的四个取值。
- grok 的「Reach」改为显式写 `model` 和 `effort`（D2 规则 2）。

「档位按型号划分，强度只做档内细分」一句改为：档位按角色、型号、强度划分；同一型号可以按强度分在不同档位。这句话在档案、`SKILL.md` 和 `CONTEXT.md`「档位」各有一处，三处一起改。它原是 ADR 0021 决策 1 定的，ADR 0030 记下这次改写。

### D5 去掉 `SKILL.md` 的词数上限

- 没有测试强制这个上限（已核实：`tests/` 里没有词数检查）。它只写在 ADR 0021 决策 11、ADR 0022 决策 5、ADR 0029 决策 8，以及 ADR 0024 决策 4 计划中的预算测试里。ADR 0030 宣布 `SKILL.md` 不设词数上限；这四条决策的状态注明被取代，四篇 ADR 的其余决策不受影响。
- ADR 0024 决策 4 计划给同目录的每个文件设预算。椰椰 2026-10-04 决定全部取消；P11 的其余部分（按车道拆文件）不变。
- ADR 0024 决策 1 的分层规则不变：`SKILL.md` 只收跨车道、跨宿主的规则。它决定内容放在哪里，与字数无关。

### D6 版本

- 本次发布 6.2.0。
- `docs/agents/plugin-release.md` 的版本规则改为：
  - 主版本只用于颠覆性改动，并由椰椰确认；
  - 不兼容的 runner 字段和条文改动用次版本；
  - 只改文字用修订版本。

### D7 cc-usage 的记忆（1D，椰椰已授权）

在 D1 至 D3 的条文定稿后，由主会话直接修改：

- `render-verification-via-headless-chrome.md`：渲染改为在覆盖的界面契约都落地并验收后跑一轮。亮暗两模式、对照 prior-art 第七节的要求保留。
- `ui-tickets-need-render-verification.md`：保留「验收包含渲染」，执行时点同上。
- `cc-usage-app-ts-is-the-parallelism-chokepoint.md`：
  - 保留事实：`src/app.ts` 是唯一装配点；并发前先对文件清单。
  - 「并发车道在这个仓库基本不可用」改为：改 `src/app.ts` 的契约之间有共同文件，不并发；没有共同文件的契约，各用一个独立工作目录并发。
  - 「前一份验收并提交后再派下一份」改为：在同一工作目录里先后执行的契约，在已获提交授权时，前一份的改动先提交再派下一份，让回执的 `changed_files` 只含本契约的改动。提交不等于验收。
- `test-run-budget.md`：第 23 行「每张前端票都重启隔离服务、单独截图验收」改为事实：只有票 01 单独做了渲染验收。
- 涉及的索引行同步改。

### D8 codex-advisor 交接

发布之后，主会话核对 `/home/hyy/develop/personal/GitHub/codex-advisor` 是否有同样的三个问题。有就按该仓库的惯例写一份交接文档放进去；该仓库的提交另行请椰椰授权。

## 契约与阶段

本节按 D1 自己的规则排。契约之间的接口在上文 D2 至 D4 定死：spec 字段名与取值、`Route:` 行的语法、依据种类、窗口取值与位置、档案表格的语法（不变）。

### 阶段零：核对宿主事实

1. 文档核对：已完成，结果见 D2「宿主事实」。
2. 宿主样本：在 `/tmp` 建一个只含 `PreToolUse` 记录钩子的探针插件，用 `claude -p --plugin-dir` 起一个无界面会话。会话派一个本角色池的 `explorer-h` 加 `haiku`，再向它发一条 `SendMessage`。钩子把收到的输入原样写进文件。另配一次 `deny`，确认无界面会话会遵守；`bypassPermissions` 模式下再试一次。再派一次带 `model` 的子代理，同时设 `CLAUDE_CODE_SUBAGENT_MODEL` 为另一个别名，从子代理记录的 `message.model` 看谁优先。这一步需要椰椰授权，会用掉少量额度。

产出：宿主事实一节，附样本路径。契约 04 的接口以它为准。

### 阶段一

| 契约 | Files | 路由 | 隔离 | 前提 |
|---|---|---|---|---|
| 01 路由档案 | `plugin/skills/orchestration/routing-profile.md` 与中文孪生 | worker `mainstay` `grok-4.7[high]`，第一候选 | 临时工作目录 | 无 |
| 02 条文 | `SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md`、`lane-preamble.md` 与中文孪生 | 同模派发：`worker-xh` 加 `opus`。主会话型号是 `claude-opus-5-5`（已核实，会话环境信息） | 主工作目录 | 无 |
| 03 runner | `plugin/scripts/run-codex.mjs`、`run-grok.mjs`、新增的共享解析模块，`tests/test_runner_contract.py` 与其他受影响的 runner 测试、`tests/test_runner_lifecycle_windows.cjs` | worker `mainstay` `gpt-6.1-sol[medium]`，擅长后端 | 临时工作目录 | 无 |
| 04 钩子 | `plugin/hooks/route-gate.py`（新）、`plugin/hooks/hooks.json`、`tests/test_route_gate.py`（新） | worker `mainstay` `grok-4.7[high]`，第一候选 | 临时工作目录 | 阶段零 |
| 05 解析一致性 | `tests/test_routing_profile_parity.py`（新） | worker `mainstay` `grok-4.7[high]` | 主工作目录 | 01、03、04 合入 |

01、02、03 同时派发；04 在阶段零完成后派发，不等其他契约；05 在 01、03、04 合入主工作目录后派发。

各契约的要点：

- **01** 按 D4 修改；同时改「Claude Code candidates」：worker 的 `sonnet-5-5` 拨盘对应 `worker-h`、`worker-xh` 加 `sonnet`。
- **02** 按 D1 至 D3 改条文：
  - `SKILL.md` 改「Parallelism」、验收各层与「Run each check once」、第一阶段路由、升级梯 R1、「Rework tickets」、「档位按型号划分」一句。
  - 车道文件写 `Route:` 行、spec 新字段、钩子的行为与覆盖缺口、续用窗口的时间来源、并发契约的独立工作目录，以及提示词以 `Route:` 行开头、下一行读前言。
  - `lane-preamble.md` 里「比本契约更宽才归批次」的说法，按 D1 第 4 条补上共用准备和主会话的检查。
  中文孪生同步，语义逐段核对；镜像测试只查文件存在。
- **03** spec 新字段与校验；回执记录 `role`、`tier`、`basis` 和 `lane_finished_at`；拒绝 `tier=same-model`；grok 要求显式 `model` 与 `effort`。测试夹具同步：
  - 复制共享模块和档案（或夹具档案）；
  - 基础 spec 带合法路由；
  - 改掉「grok 省略字段仍成功」的断言（`tests/test_runner_contract.py:553`）；
  - Windows 夹具同样处理。
  Windows 测试用 Windows 原生 Node 运行。
- **04** 按 D2 规则 1 至 8 实现。测试覆盖：
  - `Agent`：合法路由、缺路由、带 `name`、不带 `model`、别名重定向、同模派发的合法与非法；
  - `SendMessage`：带路由、缺路由、找不到的 agentId、名字目标、只订阅；
  - 档案读不出时拒绝。
  测试夹具按阶段零的宿主样本写。
- **05** 用一张独立写成的预期表（按椰椰声明的新档案逐格手写），分别核对 Python 与 JS 两个解析器对真实档案的输出。两个解析器一起漏读时，测试也要失败。

主会话同时写协调件：

- ADR 0030；
- `CONTEXT.md`：「档位」「批次验收」「升级梯」，新增「续用窗口」「路由行」；
- `docs/agents/issue-tracker.md` 的批次定义；
- `docs/agents/plugin-release.md` 的版本规则；
- ADR 0021、0022、0024、0029 被取代的条款：只在状态行注明，不把整篇标为失效；
- 问题报告第 9 节。

临时工作目录用分离 HEAD 创建（`git worktree add --detach`），不建分支，不提交。理由：主工作目录有椰椰的未跟踪文件，runner 的实施模式要求从干净工作树起步。

**阶段一的合入与验收：**

1. 每份契约交回时，按 D1 第 3 条验收。
2. 验收通过后，先把该契约的报告、回执和验证日志复制到 `.scratch/trial-6-1-0-feedback/evidence/<契约号>/`，再把差异（含新文件）应用到主工作目录。全部合入并通过下面的检查后，才删除临时工作目录。
3. 批次检查，主会话跑一次：
   - `for t in tests/test_*.py; do python3 "$t" || exit 1; done`；
   - Windows 原生 Node 跑 `tests/test_runner_lifecycle_windows.cjs`。
4. 端到端检查新钩子：用 `claude -p` 加 `--plugin-dir plugin` 起无界面会话，覆盖契约 04 测试的各个入口。先确认加载的是新钩子：拒绝理由里有新钩子独有的字样。按文档，`--plugin-dir` 加载的插件会静默取代同名的已安装插件，不需要另行停用 6.1.0；这一点同样要在这次检查里确认。这一步需要椰椰授权，会用掉少量额度。
5. advisor 验收形状的评审，一次覆盖 02 至 05：
   - 条文与机制是否一致；
   - 校验逻辑是否正确；
   - D1 的四个行为场景。
   拨盘按档案的 advisor 映射，取 `mainstay` 默认的 `gpt-6.1-sol[medium]`；椰椰另行声明时按声明。

### 阶段二（依赖阶段一）

1. 契约 06 版本说明书：`docs/manuals/6.2.0.html`。worker `mainstay` `sonnet-5-5[high]`：Claude 擅长前端，说明书是 HTML。
2. 说明书验收通过后，主会话把两个版本字段改为 6.2.0。发布流程要求先写说明书、后改版本字段。
3. 与第 1 步同时：主会话按 D7 改 cc-usage 的记忆。

### 阶段三（需要椰椰授权）

提交、推送、两侧 `claude plugin update`、伴生安装器，按 `docs/agents/plugin-release.md` 执行。

### 阶段四

D8。

## 需要椰椰授权的操作

1. 阶段零的探针，和阶段一的端到端检查：都是 `claude -p` 加 `--plugin-dir` 的无界面会话，会用掉少量额度。已授权，2026-10-04。
2. 阶段一的临时工作目录：`git worktree add --detach`，用完删除。不建分支，不提交。已授权，2026-10-04。
3. 阶段三的提交、推送和两侧更新。
4. D8 在 codex-advisor 仓库里提交（如果需要）。

## Batch checks

| 检查 | 时点 | 结果 |
|---|---|---|
| 全部 Python 测试 | 阶段一合入后；advisor 返工后重跑 | 通过。终版：2026-10-03T18:24Z（本地 10-04 02:24），在返工与版本字段修改之后的工作树上跑，`for t in tests/test_*.py` 循环退出码 0，10 个文件都通过：route_gate 43/43、routing_profile_parity 29/29、runner_contract 23/23、shipped_wording 43/43、zh_mirror 16/16、receipt_gate 11/11、lane_family_gate 18/18、install_user_level 8/8、user_level_archive 5/5；runner_lifecycle 只打印 PASS 行，没有 FAIL。日志 `evidence/batch/batch-python-final.log`。第一次运行（17:33Z 前后，route_gate 40/40）在 advisor 返工之前，日志 `evidence/batch/batch-python.log` |
| Windows 原生 Node 测试 | 阶段一合入后 | 通过，2026-10-04。`cmd.exe` 跑 Windows 原生 Node，退出码 0，codex 与 grok 的 inherited、timeout、hang 共 6 项 PASS。日志 `evidence/batch/batch-windows.log` |
| 钩子端到端检查 | 阶段一合入后 | 通过，2026-10-04，Claude Code 2.1.287，主会话 `sonnet`，`bypassPermissions`，cwd 为 `/tmp/fa-e2e/cwd`。init 记录的插件表里 fable-advisor 只有 `fable-advisor@inline`，已安装的 6.1.0 被取代。第一次运行：合法路由放行（子代理跑 `claude-haiku-4-5-20251001`）；缺路由行、缺 `model`（理由带合法拨盘）、拨盘不在格里、同模派发的型号不是会话型号，都被拒；`SendMessage` 带路由放行，缺路由被拒（理由给出目标拨盘 `haiku-4-5`），找不到的 agentId 被拒，名字目标和只订阅不被钩子拒绝（宿主自己回 `success: false`）；同模派发 `sonnet-5-5[high]` 放行（子代理跑 `claude-sonnet-5-5`，强度 `high`）；内置 `Explore` 放行。第二次运行设 `ANTHROPIC_DEFAULT_OPUS_MODEL=claude-sonnet-5-5`：`opus` 推出 `sonnet-5-5[high]`，路由写 `opus-5-5[high]` 被拒。第三次运行设 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` 与 `CLAUDE_CODE_SUBAGENT_MODEL=haiku`：路由写 `sonnet-5-5[high]` 被拒（推出 `haiku-4-5`），写 `haiku-4-5` 放行。所有拒绝理由都以 `fable-advisor route gate:` 开头。`name` 无法覆盖：本版本的 `Agent` 没有 `name` 参数。记录与摘要在 `evidence/batch/e2e/`。范围：这次运行用的是 advisor 返工之前的钩子逻辑；返工改的同模型号核对与 `name` 空值由 `test_route_gate.py` 43/43 覆盖，`hooks.json` 与钩子接线没有再改 |
| advisor 验收（02 至 05，含行为场景） | 阶段一合入后 | 第一轮：2026-10-04 17:35Z 至 17:41Z，`gpt-6.1-sol[medium]`（已提交，未观测），codex 报告模式，会话 `01a102d5-f0d1-7390-b5b0-5ab1a0561b18`，回执 `evidence/batch/advisor-acceptance-1.json`。裁决「完成以下修改后接受」，提出三处修改，主会话全部采纳：同模派发也要求推出的型号是档案里的型号（改机制，D2 规则 2）；`README.md:76` 仍写证据加差异统计是默认验收（D1 第 3 条）；`name` 为空值时被放行（D2 规则 6）。中文孪生和四个行为场景都通过。三处修改按返工票完成，主会话读差异验收（`evidence/04/acceptance.md`「批次 advisor 验收后的返工」）。复核：同一会话续用，17:48Z 至 17:50Z，回执 `evidence/batch/advisor-acceptance-2.json`，裁决「接受」，三处都已解决，没有引入新的条文与机制差异。**通过** |
| 说明书渲染检查（`docs/manuals/6.2.0.html`） | 契约 06 验收后 | 通过，2026-10-04。`chrome-headless-shell` 1243，经 DevTools 协议把第 14、15、16、20 节滚到视口顶部后截图，宽度 1440×1000 与 390×844（移动模式）。四节在两种宽度下标题都停在顶部 36 像素处（与 `scroll-padding-top` 一致），排版、代码块、表格正常。两种宽度下页面 `scrollWidth` 都等于 `clientWidth`，没有横向溢出；窄屏超出视口的只有表格，装在带「左右滑动查看完整表格」提示的滑动容器里。观察项，不阻塞：侧栏目录是可滚动容器，停在第 20 节时高亮条目在视口下方，侧栏不自动跟随；这是 6.1.0 沿用的脚本行为，契约要求 CSS 与 JS 与 6.1.0 逐字节相同。说明书没有暗色模式。截图在 `evidence/manual-render/` |
