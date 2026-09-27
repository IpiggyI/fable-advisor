# Cursor 中的各车道 —— 钉死的 subagent，外加经 Shell 的 codex runner

在 Cursor 中派发车道之前阅读本文。Cursor 通过其 Claude 插件兼容路径加载本 skill。`grok lane`、`claude lane` 与 `cursor lane`（Cursor 自家模型）是原生的：一次 subagent 派发钉死自己的模型。`codex lane` 不在 Task 枚举里；通过 Shell 工具运行 [lanes-claude-code.md](lanes-claude-code.md) 中的 codex runner 到达。

## Task 派发 —— grok lane 与 claude lane

- **调用。** 派发提示以一行开场，把 subagent 指向其角色所需的前言——`worker` 指向 `<plugin-root>/skills/orchestration/lane-preamble.md`，`explorer` 或 `advisor` 指向 `<plugin-root>/skills/orchestration/lane-preamble-report.md`——这里没有东西替你前置它，而执行侧契约必须到达每一条车道。五部契约原文紧随其后。
- **角色。** `worker` 是带显式 `model` 的 `generalPurpose` 派发；`explorer` 是带显式 `model` 的 `explore`（或 `generalPurpose`）派发；`advisor` 是具名的 `advisor-*` agent 之一，显式钉死。钉死的家族由填充表选择：Grok 家族钉死即 `grok lane`，Claude 家族钉死即 `claude lane`，Cursor 家族钉死（Cursor 自家模型）即 `cursor lane`，它只在本宿主存在。钉死点名的是拨盘，即该格所在档位内的型号与 effort。钉死是请求值：Cursor 不向主代理回传执行元数据（model、effort），因此路由披露或报告引用一次派发的 model 时，标为 "requested, not confirmed"。
- **每次都显式钉死。** Agent 的 frontmatter `model:` 对 Cursor 中插件加载的 agent 不生效，且省略 `model` 时 Task 继承会话模型——一次未钉死的派发会静默变成会话正在跑的那个。用户级 lane family gate 只管一种情况：`model` 缺失、为空或为 `inherit` 的 `advisor-*` 派发。钉的是哪个家族、以及未钉死的 `generalPurpose` `worker`，要你自己抓住。使用本轮 allowlist 里存活的 slug；skill 示例可能点名 allowlist 没有的世代。
- **同模派发。** 唯一不携带 `model` 的派发：编排姿态下准则散文的 `claude lane` 拨盘是省略 `model` 的 `generalPurpose` 派发——继承会话模型是目的，不是疏漏，且它不是具名 agent 派发，所以门禁不会触发。在路由披露中写明「inherit」，以免被误当成未钉死的车道。
- **验收。** 报告作为派发结果在带内返回，失败或不可用的派发也在带内大声失败。验收完全按 [SKILL.md](SKILL.md) 中的核验层运行；Task 派发没有 receipt。Task 派发没有 runner，所以契约的检查列表归车道来跑，在结尾跑一次；报告里的那份输出就是全部证据。
- **返工。** 返工票是一次带先前派发 agent id 的 Task `resume`，把返工契约（缺陷、原范围、失败的检查）作为新提示带上——车道保留它已经建好的上下文。返工票也失败时，归因（SKILL.md「升级」）：契约缺口在修正契约下再次 resume；能力失败则按 SKILL.md 的升级梯升到下一档（R2–R3），以新派发携带接管契约。
- **改道。** 因用户套餐上模型不可用而失败的派发，改道到同一格的另一种填充，并显式披露——与 CLI 车道同一规则。
- **effort 钉死在 slug 上。** 临时模型钉死携带固定的 effort 档——`codex lane` 的 `effort` 旋钮在裸派发上不存在。方括号参数（`<slug>[effort=high]`）仅在自定义 agent 定义文件中可用；仅当任务真正需要升高 effort 时才有意添加一份定义文件，而非默认。路由档案的 `model[…]` 方括号在此映射为 slug 变体——effort 是 slug 的后缀——因此挑选 effort 符合该格的 slug 变体。本轮 allowlist 只约束钉型号的 Task 派发：所需变体不在其中的候选被跳过，披露说明这一点。
- **竞速。** 「挑选更强 diff」的竞速让每位选手跑在隔离 worktree 的派发类型上（当前 `Task` 枚举中的 `best-of-n-runner`：每次尝试自有分支与工作目录），各自带显式 `model`，在同一条消息中发出。同一工作树上的两个执行者会互相覆盖对方的改动；两次普通钉死派发共享该树，不是竞速。
- **经济。** 各厂模型在 Cursor 中占用各自的额度池，因此各车道价格——以及整套成本纪律——按原文适用。

## 经 Shell 的 codex lane

经 Shell 工具运行 `node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"` 到达 GPT 家族。spec、pending/receipt 流程、等待协议（阻塞 Shell 进程，绝不用固定睡眠）、receipt 字段、`resume_session_id`，以及只读角色的 `mode: "report"`，与 [lanes-claude-code.md](lanes-claude-code.md) 完全相同。两点不同：

- **无 receipt gate。** Cursor 是否加载插件 Stop hook 未经核实，因此本车道按「不加载」来设计：pending spec 缺少 `complete` receipt 时没有东西阻塞会话。它 fail-open，安全等级与 `handoff lane` 相同。主代理亲自裁决 receipt——`error_class: complete`、session id、对照工作树抽查的核验输出——并在结束会话前扫一遍 `.fable-advisor/pending/`：落地、放弃（删除文件并说明），或说明它带到下一会话。
- **等 Shell 工具自己的时钟。** runner 的静默截止和 `timeout_sec` 按文档生效；Shell 工具自己的前台上限是外层天花板，因此长票据在后台运行，并按 shell id 等待。

**grok runner 以同一方式运行。** 经 Shell 工具运行 `node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"`，spec、pending/receipt 流程与等待协议相同，上述两点不同同样适用。尚未在 Cursor 中实跑。

## Subagent 生命周期

带 `name`（「teammate」）拉起的 subagent 在完成后仍会保留，以便再次发消息——每一批你未清理的具名批次都会作为后台工作徘徊，直到会话退出。两条规则：

- 串行批次（同一文件、严格顺序）从后台化得不到任何好处：用 `run_in_background: false` 运行，并当场消费报告。
- 当一批确实在后台运行时，仅在验收之后才停止其 teammate——核验通过不是结束，因为返工票会恢复同一 agent。一旦 diff 已验收且预期没有后续，就停止它；不要让已验收的车道闲置到会话结束。
- 后台派发的完成通知是生命周期信号，不是报告：报告在前台派发的工具结果里，或在后台派发的输出文件里——到那里去读。
- 报告缺失时，先读输出文件与工作区，确认车道到达了什么状态，再按你发现的缺口恢复；仅当工作确实必须再执行一遍时才重新派发，且从不对已结束的 agent 做 `resume` 来催要报告——那会重启该 agent，再得到一次完成通知。
