# 0030 — 6.2.0：派发前做全局规划、按结果验收；派发写明路由，由 runner 与钩子校验；车道会话设续用窗口

- **Status**: accepted（2026-10-03 至 10-04 椰椰的决定见「决策门核对」；`gpt-6-astra[xhigh]` 两轮评审的意见已并入；实施进度与批次检查记在任务件的 `## Batch checks`）
- **Date**: 2026-10-04
- **影响范围**:
  - `plugin/skills/orchestration/SKILL.md`：同模派发、角色与档位、路由第一阶段、升级梯 R1、"Rework tickets"、新增的 "Session reuse"、"Parallelism"、第 1 与第 2 层验收、"Run each check once"。
  - `plugin/skills/orchestration/lanes-claude-code.md`：第 0 节的路由行与路由闸门、第 1 节的路由字段、第 4 节的回执字段与并发隔离、"Rework tickets" 的时间来源、"Grok deltas"。
  - `plugin/skills/orchestration/lanes-cursor.md`：Invocation、Rework、并发隔离、Shell 跑 codex runner 时的路由字段。
  - `plugin/skills/orchestration/lane-preamble.md`：Verification。
  - `plugin/skills/orchestration/routing-profile.md`：worker 两格、声明日期、档位句、新增「Session reuse windows」一节、grok 的到达方式、worker 的 agent 文件映射。
  - `plugin/scripts/run-codex.mjs`、`plugin/scripts/run-grok.mjs`，新增 `plugin/scripts/routing-profile.mjs`。
  - 新增 `plugin/hooks/route-gate.py`；`plugin/hooks/hooks.json`。
  - 测试：`tests/test_runner_contract.py`、`tests/test_runner_lifecycle.py`、`tests/test_runner_lifecycle_windows.cjs`，新增 `tests/test_route_gate.py`、`tests/test_routing_profile_parity.py`。
  - `docs/zh/` 下五份孪生、`README.md`、`docs/manuals/6.2.0.html`、两个版本字段。
  - 协调件：`CONTEXT.md`、`docs/agents/issue-tracker.md`、`docs/agents/plugin-release.md`，以及 ADR 0009、0021、0022、0024、0029 的状态行。
  - 插件之外：cc-usage 的四条项目记忆（椰椰授权）。
  - 任务件 `.scratch/trial-6-1-0-feedback/spec.md`，问题报告 `.scratch/trial-6-1-0-feedback/problem-report.md`。
- **关联**:
  - 修订 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 1（档位划分）与决策 10（grok 跟随 CLI 默认型号），连同 [ADR 0009](./0009-grok-lane-dewrapper-runner.md) 的同一做法；推翻 ADR 0021「未采纳」中的「为观察档位使用增加标记、日志或统计」。
  - 取代 ADR 0021 决策 11、[ADR 0022](./0022-orchestration-load-on-events.md) 决策 5、[ADR 0029](./0029-scoped-contract-checks-and-batch-defaults.md) 决策 8 的 `SKILL.md` 词数上限，以及 [ADR 0024](./0024-orchestration-files-by-lane-and-word-budgets.md) 决策 4 的词数预算。
  - 修订 ADR 0029 决策 2：恢复它退役的「共用昂贵准备」，并把主会话自己的检查归入宽检查。
  - 沿用 ADR 0029 决策 1（契约只放本契约的判定检查）与决策 3（并票、按契约验收），[ADR 0013](./0013-delivery-contract-not-build-instructions.md) 的五部契约，ADR 0024 决策 1 的分层。

## 背景

椰椰 2026-10-03 报告了 6.1.0 试用中的三个问题。证据来自 cc-usage 会话 `be93294f-4abe-4bbe-a2df-73aa8fe76cda`（2026-10-02 至 10-03，加载 6.1.0），详见问题报告。下面只列决定方向的事实，都已核实。

**逐票验证。**

- 前端 5 张票逐张派发、逐张验收、逐张提交，下一张等上一张提交后才派。
- 01 与 02 改同一张表，03 与 04 改同一张图表，都没有并成一份契约。合票与按契约验收的规则当时就写在 `SKILL.md` 里。
- 会话至少跑了 141 次检查，其中定向检查至少 104 次。票 01 单独做了一轮约 8 分钟的渲染验收。
- 主会话把「每票验收后提交」作为推荐项提给椰椰，没有给出按契约提交的选项。
- ADR 0029 决策 2 退役了「共用昂贵准备」。按条文，只覆盖一张票的渲染检查仍归那张票。

椰椰 10-04 的说明把重点放在主会话的全局意识上：子代理交回后，主会话要看改动是否符合要求，不能只靠测试；没有依赖关系的票尽量并发，用修改范围和隔离来限制；测试在一个环节结束时跑。

**档位形同虚设。**

- 首轮直接进 `rescue` 的有 4 张票，都没有椰椰的声明。椰椰只声明了前端由 Claude、后端由 `gpt-6-astra`，主会话把家族声明读成可以任选强度。
- 条文有准入规则，但派发说明从不写档位，也没有任何机制核对。
- 新票经 `SendMessage` 和 codex 会话续跑进入已有会话。只在首次派发时把关，挡不住这条路。
- 条文说档位按型号划分，表格里同一型号却跨档。

**冷会话续用。**

- codex 车道在上回合结束 143.7 分钟后续用会话，第一次请求的 146,061 个输入词元只命中 3,968 个。那一次间隔、强度、工作目录同时变了，原因分不开。
- R1、「Rework tickets」和车道文件都没有时间条件，也没有规定新票能否续用。
- 回执的 `finished_at` 在验证之后记录，不等于车道最后活动的时刻。

## 决策

1. **派发前做全局规划，只等真实的依赖。**
   - 任务有两张以上的票时，主会话在第一次派发前把计划写进任务件。计划有四项：
     - 依赖；
     - 契约：共用文件或同一区域的票并成一份；
     - 隔离：每份契约的 Files；同时进行的契约若共用一个工作目录，就各用一个独立的工作目录，只换分支不算隔离；Cursor 的普通 `Task` 共用工作区，并发契约改用隔离工作树的派发类型，或依次执行；
     - 宽检查：每项覆盖哪些契约、由谁跑、何时跑。
   - 没有全局的阶段屏障。一份契约在它需要的契约验收通过、判定检查就绪后就派发。只有它需要的结果只能由某项宽检查证明时，才等这项宽检查。
   - 提交仍按授权和回滚边界拆，与验收分开。问提交粒度时，给出按契约提交的选项。
2. **按结果验收。**
   - 第 1 层验收对照契约逐条核对三样东西：报告对每条标准的说法、车道的检查证据、承载 Objective 所述行为的文件的限定路径差异。
   - 测试只证明它覆盖的断言。差异实现的是别的行为时，即使检查全部通过也拒收。
   - 差异太大时交 advisor 阅读。主会话核对标准、证据、结论是否一一对应，再读 advisor 标出的片段。
   - 第 3 层的触发条件不变。
3. **宽检查一批只跑一次。**
   - 宽检查包括：全量测试、渲染或浏览器检查、端到端套件、构建或打包、共用昂贵准备（服务、浏览器、设备、构建）的检查，以及主会话自己的渲染和人工检查。
   - 宽检查在它覆盖的契约都落地并验收之后跑一次，只挡需要它结果的工作。
   - 一次失败要能归因到一份契约；做不到时，把批次分小。
   - 契约仍只放本契约的判定检查（ADR 0029 决策 1 不变）。
   - 恢复「共用昂贵准备」的理由：渲染截图这类检查只覆盖一张票，却共用服务和浏览器。
4. **档位准入。**
   - 档位按任务难点或升级梯定。椰椰声明的家族或型号只筛选候选。
   - 取满足三个条件的最低一档：不低于按难点或升级梯定下的档位；格里有符合声明的候选；有该档接受的依据（`mainstay` 不需要）。
   - 家族或型号声明可以作为 `crux` 的 `user-declaration` 依据，`ref` 写椰椰的原话。它不算 `rescue` 的准入。
   - 三个条件同时满足不了时，向椰椰报告冲突，不自动降档。
5. **每次派发写明路由。** 路由是角色、档位、拨盘；高于 `mainstay` 时加依据。经 `SendMessage` 或 `resume` 发给已有会话的消息也写路由。
   - 依据种类按角色和档位定：

     | 角色 | `crux` | `rescue` |
     |---|---|---|
     | worker、explorer | `key-difficulty`、`failure`、`user-declaration` | `failure`、`user-declaration` |
     | advisor | `low-confidence`、`user-declaration` | `user-declaration` |

     `ref` 不能为空。
   - runner：spec 新增必填的 `role` 与 `tier`；高于 `mainstay` 时 `basis {kind, ref}` 也必填。回执原样记录这三个字段。
   - claude 车道：提示词和 `SendMessage` 消息的第一行是路由行 `Route: role=… tier=… dial=… basis=… ref=…`，第二行是读前言的指令。
   - 同模派发只限 worker：`tier=same-model`，依据种类 `same-model`，`ref` 写产物类别。
6. **机械校验。** 程序只查依据存在、格式合规，不查真假。
   - runner 在启动 CLI 之前校验：
     - 角色与模式匹配：implement 只收 worker，report 收 explorer 与 advisor；
     - 拨盘在档案该角色、该档位的格里，取 Claude Code 表与 Cursor 表同一格的并集，因为 runner 在两个宿主上都运行；
     - 依据种类合规。
     codex 按补齐省略默认值之后的有效拨盘校验。grok 必须显式写 `model` 和 `effort`，因为 runner 无从得知 CLI 的默认值。两个 runner 都拒绝 `same-model`。校验失败判 `spec_invalid`。
   - Claude Code 新增 `PreToolUse` 钩子 `route-gate.py`，匹配 `Agent` 与 `SendMessage`。拒绝用 `permissionDecision: deny`，不用 `ask`。规则见任务件 D2 规则 1 至 8：
     - 角色取自 agent 文件；
     - 拨盘由派发的 `model` 与 agent 文件的强度推出，别名按宿主的解析顺序处理；
     - 档位按 Claude Code 表；
     - 同模派发比较会话型号，推出的型号还要在档案的 Claude Code 表里；
     - 带 `name` 的派发拒绝；
     - `SendMessage` 的拨盘取目标子代理的实际配置，找不到记录的 agentId 拒绝；
     - 档案读不出时拒绝。
   - 档案是唯一来源，不另建路由配置。解析、校验、取值三件事分开。JS 与 Python 两个解析器由一致性测试对照一张独立手写的预期表。
   - 型号推导依据阶段零在 Claude Code 2.1.287 上核实的宿主事实（任务件 D2「宿主事实」，样本在任务件的 `evidence/phase0/`）：
     - 单次派发的 `model` 优先于 `CLAUDE_CODE_SUBAGENT_MODEL`；
     - `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 为真时，宿主去掉 `model` 参数，钩子改按强制的型号推出；
     - 别名所属家族与会话型号相同时，子代理跑会话型号；
     - 拒绝在无界面会话的 `auto` 与 `bypassPermissions` 模式下都生效。
7. **会话续用窗口。**
   - 以下续用只在车道的窗口之内进行：返工票、修正契约、被时钟切断后的续跑、发给子代理的后续消息、新票。
   - 取值是椰椰声明的续用政策，不是实测的缓存寿命，写在路由档案的「Session reuse windows」：
     - claude 车道（Claude Code 的 `SendMessage`）：1 小时；
     - codex 车道：30 分钟；
     - grok 车道：1 小时；
     - Cursor 的 `Task` `resume`：1 小时。
   - 窗口从车道上次活动算起，时间来源如下：
     - runner 回执新增的 `lane_finished_at`：CLI 退出的时刻，在验证之前记录；
     - claude 车道：子代理记录最后一条助手记录的时刻；
     - Cursor：主会话在 `Task` 结果返回时用 Shell 记下的时刻。
     时间不明时，按超出窗口处理。
   - 超出窗口时，在同一档位、同一拨盘上新开会话，带上缺陷、原契约、上轮报告和回执。这不算升档，失败计数不变。续用时不改强度。
   - 超出窗口仍要续用时，派发说明要做到四点：点名原会话独有的可观察状态，列出已检查的磁盘材料与日志，说明为何不能交接，写出重建的步骤和代价。此外还要披露接受冷缓存的成本。
   - 新票只在四个条件同时成立时续用：同一区域、确实需要共享上下文、同一拨盘、在窗口之内。
8. **路由档案。** 按椰椰 2026-10-03 的声明修改：
   - 两张表的 worker 行相同：`mainstay` 为 `grok-4.7[high*, xhigh] › sonnet-5-5[high*, xhigh] › gpt-6.1-sol[medium*, high]`，`crux` 为 `opus-5-5[medium*, high] › gpt-6-astra[low*, medium] › gpt-6.1-sol[xhigh*, max]`。
   - 声明日期改为 2026-10-03。
   - worker 的 `sonnet-5-5` 拨盘经 `worker-h`、`worker-xh` 加 `sonnet` 到达。
   - 档位句改为：档位是每个角色的一组拨盘；同一型号可以按强度分在不同档位。档案、`SKILL.md`、`CONTEXT.md` 三处一起改。这修订 ADR 0021 决策 1。
   - grok 的到达方式改为显式写 `model` 和 `effort`。这修订 ADR 0021 决策 10，以及 ADR 0009 的「跟随 CLI 默认型号」。
9. **`SKILL.md` 不设词数上限，计划中的词数预算全部取消。**
   - 这取代四处规定：ADR 0021 决策 11、ADR 0022 决策 5、ADR 0029 决策 8 的上限，以及 ADR 0024 决策 4 的预算测试。ADR 0024 的其余决策不受影响。
   - ADR 0024 决策 1 的分层规则不变：`SKILL.md` 只收跨车道、跨宿主的规则。它决定内容放在哪里，与字数无关。
   - 依据：椰椰 2026-10-04 指出，上限每次改条文都要问、都会改，数字没有依据。
10. **版本。** 本次发布 6.2.0。版本规则改为：
    - 主版本只用于颠覆性改动，并由椰椰确认；
    - 不兼容的 runner 字段和条文改动用次版本；
    - 只改文字用修订版本。
    规则写进 `docs/agents/plugin-release.md`。
11. **插件之外。**
    - cc-usage 的四条项目记忆按任务件 D7 修改，椰椰已授权。
    - 发布后核对 codex-advisor 是否有同样的三个问题；有就写交接文档进该仓。该仓的提交另行请椰椰授权。
12. **协调件同步。**
    - `CONTEXT.md`：改「档位」「批次验收」「升级梯」，新增「续用窗口」「路由行」。
    - `docs/agents/issue-tracker.md`：批次的定义。
    - `docs/agents/plugin-release.md`：版本规则。
    - ADR 0009、0021、0022、0024、0029 的状态行：只注明被修订或取代的条款，不把整篇标为失效。

## 未采纳

- **只靠减少测试次数（问题报告 1A 至 1C 的原稿）。** 椰椰 10-04 指出，砍测试次数不能从根本上解决问题。1A 至 1C 的内容并入决策 1 与 3。
- **只改文本（2A）。** 准入规则早就写着，仍被越过；椰椰选了 2C。
- **宽约束（2B）。** 它的覆盖边界没有定义。
- **钩子用 `ask`。** 被拒的派发由主会话自己改正，不把校验转给椰椰；确实缺少椰椰的授权时，主会话自己提问。
- **runner 机械拦截冷续用（3B）。** runner 跨工作目录查不到会话的上次活动，按文件修改时间判断的可靠性也没有证据。将来要做，先定下：哪些事件算活动、边界时刻、运行中的纠正消息怎么算、例外写在哪个字段。
- **新票一律新开（3C 取法一）。** 同一区域、确实需要共享上下文时，续用更便宜。
- **7.0.0。** 椰椰 10-04 决定，没有颠覆性改动不升主版本。
- **让 Cursor 的用户级钉型号钩子也校验路由。** 用户级钩子文件不在本次范围；Cursor 的 `Task` 路由只有文本规则。

## 已知能力上限

- 钩子只覆盖 Claude Code 里本角色池的 `Agent` 与 `SendMessage`：
  - Cursor 的 `Task`（含 `resume`）只有文本规则；
  - 内置代理不在本角色池；
  - 没有 Python 时，钩子放行，并在 stderr 写一行。
- 程序只查依据存在与格式，不查真假；产物类别也由主会话判断。
- 钩子校验的是提交的配置。子代理实际跑的型号，以它记录里的 `message.model` 为准。
- 会话型号取自会话记录里最后一条带真实型号的助手记录（宿主在 API 报错等情况下写入的 `<synthetic>` 记录被跳过），而钩子运行时本条回复还没写进记录。所以：
  - 会话第一条回复里的同模派发会被拒绝；
  - 用 `/model` 换型号后的第一条回复里，钩子看到的仍是旧型号；
  - 会话型号读不到时，别名解析跳过家族这一步。
- runner 按两张表的并集校验，比单个宿主的表宽：在 Claude Code 里，runner 也接受只出现在 Cursor 表里的拨盘。
- `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 为真、`CLAUDE_CODE_SUBAGENT_MODEL` 未设时，子代理继承会话型号。这一条取自 2.1.287 的代码，没有样本。
- 续用窗口没有机械校验。
- 钩子的输入、`SendMessage` 的字段和子代理记录的格式会随 Claude Code 版本变化。钩子遇到不认识的输入时拒绝。

## 决策门核对

本次命中两种决策类型：推翻已定方案（ADR 0021 决策 1、10 与一项未采纳，ADR 0029 决策 2 退役的触发词），以及修改公共接口（runner spec 的必填字段、回执的新字段、新钩子）。

1. **第一轮评审**，2026-10-03：`gpt-6-astra[xhigh]` 评审问题报告（会话 `01a1023f-7cd3-7610-87d0-73265b03eb3f`，回执 `.fable-advisor/receipts/862ec27b….json`）。意见见问题报告第 8 节。
2. **椰椰的决定**，2026-10-03：
   - 问题二取 2C；
   - 授权修改 cc-usage 的记忆；
   - grok 车道与 Cursor `resume` 的窗口取 1 小时；
   - 不复审问题报告，改为评审实施方案。
   同日声明：Claude Code 的窗口 1 小时、Codex 30 分钟，以及档案 worker 行两格的新值。
3. **第二轮评审**，2026-10-03：`gpt-6-astra[xhigh]` 评审实施方案（会话 `01a1028b-c6f3-7700-9e3d-54c962c562e3`，回执 `.fable-advisor/receipts/07988970….json`）。裁决：修改后采纳。意见已全部并入任务件，清单见任务件的「评审记录」。
4. **椰椰的决定**，2026-10-04：
   - 问题一的重点是主会话的全局意识，原话见任务件；
   - 取消 `SKILL.md` 的上限和全部词数预算；
   - 发布 6.2.0；
   - codex-advisor 有同样的问题时，写一份交接文档；
   - 授权阶段零的探针、端到端检查和临时工作目录。
5. **阶段零探针**，2026-10-04：结果见决策 6 的宿主事实。
6. **主会话补定的三处**，2026-10-04，起因是契约 02 报告的缺口：
   - 家族或型号声明可以作为 `crux` 的 `user-declaration` 依据；
   - Cursor 的时间来源；
   - Cursor 的并发隔离。
   这三处已写进决策 1、4、7 与任务件。
7. **实施后的验收**，2026-10-04：advisor 验收形状，`gpt-6.1-sol[medium]`，codex 车道报告模式，会话 `01a102d5-f0d1-7390-b5b0-5ab1a0561b18`，覆盖契约 02 至 05 与 D1 的四个行为场景。
   - 第一轮裁决「完成以下修改后接受」。中文孪生与四个行为场景都通过。三处修改：
     - 同模派发也要求推出的型号在档案里：规则 5 只免去格子校验，不免去规则 2 的锚点要求，所以改机制；
     - `README.md` 的默认验收说明要改成按结果验收；
     - 带 `name` 字段而值为空时，也要拒绝。
   - 三处按返工票完成后，同一会话复核，裁决「接受」。
   - 同批的其他检查都通过：全部 Python 测试、Windows 原生 Node 测试、`claude -p` 加 `--plugin-dir` 的钩子端到端检查。结果与证据见任务件的 `## Batch checks`。

## 复盘条件

- 6.2.0 试用后统计三项：首轮越档的派发数、缺路由行被拒的次数、被拒后主会话改对所用的往返次数。钩子误拒合法派发，出现一次就复查规则。
- 同一区域的票仍被逐票验收、逐票提交，或没有依赖的契约仍串行派发，说明决策 1 没有被执行。那时考虑机械检查规划是否存在。
- 宽检查或渲染仍逐票跑，说明决策 3 的措辞不够。
- 超出窗口的续用仍然出现，且派发说明里没有例外理由，那时考虑 3B 的机械拦截。
- Claude Code 升级后钩子拒绝合法输入，先重跑阶段零的探针。
- 档案的表格语法改动时，一致性测试应先失败；改语法要同时改两个解析器。
