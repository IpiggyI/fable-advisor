# 0009 — grok 车道去 wrapper 化：run-grok runner + 运行时模型目录

- **Status**: accepted
- **Date**: 2026-07-31
- **影响范围**: `scripts/run-grok.mjs`（新增）、`agents/grok-implementer.md`（删除）、`hooks/`（删 spawn 护栏、receipt gate 文案一般化）、`skills/orchestration/SKILL.md`、`README.md`
- **关联决策**: [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（复盘条件预埋"同法做 run-grok runner"）、[ADR 0003](./0003-codex-lane-param-policy.md)（fail-loud 参数律）

## 背景

ADR 0002 给 codex 去 wrapper 时记录了 grok 车道的同法路线，触发条件写的是"顶替事故"。本次以成本理由触发同一路线：wrapper 子代理每次派工承担 Claude 侧启动基线（ADR 0002 实测 ~25k token 量级），用户判断该固定开支不值得。去 wrapper 后所有外部 CLI 车道均由架构师经确定性 runner 直辖。

事实核验（2026-07-30/31，grok CLI 0.2.114，真实调用）：`--prompt-file`/`--output-format streaming-json`/`--permission-mode acceptEdits`/`--cwd` 可用；事件流 `{"type":"text"}` 承载最终消息、`{"type":"end"}` 带 `sessionId`/`usage`/`total_cost_usd`；`-s/--session-id` 可为新会话注入指定 UUID（比 codex 侧 15 个 extractor 猜字段更强的绑定）；`grok models` 打印登录态、默认模型与目录（当前仅 `grok-4.5`）；无 reasoning-effort / service_tier 类旋钮。

## 选项对比

| 方案 | 优点 | 缺点/风险 |
|------|------|------|
| 保留 wrapper agent | 有临场应变（flag 适配、把 spec 缺口转开放问题） | 每次派工 ~25k 启动基线；wrapper 自实现威胁类仍在，需 spawn 护栏维护 |
| **独立 run-grok.mjs 镜像（选定）** | 零风险不碰在跑的 codex 车道；两份拷贝低于"≥3 抽取"阈值 | receipt 结构改动要改两处（见复盘条件） |
| 抽共享核（run-lane.mjs） | 单一真相源 | 重构在跑的 codex 车道，回归风险换来的收益要到第三条车道才兑现 |
| 改用官方 Codex 插件替代 run-codex.mjs（顺带探测） | 免子代理直呼入口、后台 job 控制、上游维护 | 四缺口：无 spec 校验（model 透传、effort 无 `max`）；不执行 verification（codex 命令退出码被丢弃）；job 按时间戳命名且 SessionEnd 杀删（receipt gate 无从锚定）；task 输出无体积纪律。补齐等于重写 runner 还继承其漂移面（RPC 无版本预检、指导层钉在 GPT-5.3/5.4 世代） |

模型白名单：静态数组（ADR 0003 codex 律）vs **运行时目录（本次选定）**——白名单与默认模型取自 preflight 的 `grok models` 输出，模型换代（grok-4.6/4.7）零代码改动，typo 仍 fail-loud；目录解析失败按 `grok_unavailable` 大声失败，不静默透传。codex 侧无等价廉价目录查询，维持静态白名单不动。

## 决策

1. 新增 `scripts/run-grok.mjs`，镜像 run-codex.mjs 的结构与 receipt 语义：五段 spec + `model`/`timeout_sec`、未知键 fail-loud、同一 `.fable-advisor/{pending,receipts}` 目录与 pending 自清理、同一 error_class 谱系（codex_* → grok_*）。receipt 增记 `usage`/`total_cost_usd`/`stop_reason`（end 事件白给的成本审计）。
2. 删除 `agents/grok-implementer.md` 与 `hooks/block-named-cli-lane.py` 及其 PreToolUse 挂载：wrapper 消失即"wrapper 静默自实现"威胁类整体消失，receipt gate（盯主会话）成为唯一且足够的机制（ADR 0002 后续澄清）。fail-closed shell 兜底随之退役。
3. receipt gate 逻辑零改动（按 spec hash 匹配、不认 producer），仅文案去 codex 化。
4. Codex 插件不替代 run-codex.mjs；其 `/codex:adversarial-review`（schema 化裁决、read-only）收编为验收 Tier 3 的可选跨厂商 reviewer。
5. 版本 3.7.0。

## 实施代价

- runner 镜像带来的双份维护：receipt/验证逻辑改动须同步两个文件。
- 可发现性：grok 车道也从 agent 列表消失，依赖 orchestration skill 被加载（codex 已接受同款代价，ADR 0002）。
- wrapper 的临场应变消失：runner 刚性 fail-loud，spec 必须自足——本就是 spec contract 的要求。

## 复盘条件

- 出现第三条 CLI 车道，或 receipt 结构需要升版 → 抽共享 runner 核。
- `grok models` 输出格式或 streaming-json 事件格式漂移 → runner 大声失败（`grok_unavailable`/解析不出 end 事件），修一处解析器；若漂移频繁 → 评估改挂结构化接口。
- Codex 插件上游补齐 verification 执行 + 持久 receipt → 重估"不替代"结论。
- `codex exec --json` 事件格式漂移导致 run-codex 频繁失败 → 评估改走 `codex app-server` JSON-RPC（插件已验证该路径可行）。

## 备注

- 探测证据：插件 v1.0.5 解剖由只读 scout 完成，承重结论（无 verification 执行、SessionEnd 杀删 job、approval hardcoded `never`）经 file:line 抽查。
- 实施经 codex 车道 dogfood：spec 见 `.fable-advisor/pending/grok-lane-runner.json`。
- 成本口径更正存档：探测调用 usage 里的 ~19k input 是 grok 会话 xAI 侧系统提示基线（迁移前后不变），本决策省的是 Claude 侧 wrapper 启动基线（ADR 0002 记 ~25k）。

## 追记（2026-08-12）— 目录预检降级为提示性校验

前提证伪：`grok models` 打印的登录态快照不可靠——grok CLI 仅在真实运行时刷新登录，且用户侧自定义供应商配置（config.toml 式）可完全绕过 auth。未认证快照曾同时误导架构师侧预探测与本 runner 的 preflight，把可用车道误判为 `grok_unavailable`。

决策修订：目录不可读（进程错误、非零退出或输出不可解析）时不再判 `grok_unavailable`，改为记 diagnostic 并跳过白名单校验——`spec.model` 透传，未指定则不传 `-m` 由 CLI 用自身默认；可用性由实跑裁决。目录可读时行为不变（不在目录内仍为 `spec_invalid`）。代价：目录不可读时模型 typo 推迟到实跑才失败（`grok_failed`），换取不误杀可用车道。SKILL.md 同步新增「派发裁决可用性、禁 auth 快照预探测」条款。

同批第二处前提证伪：`--permission-mode acceptEdits` 仅自动放行文件编辑工具；无头（`--prompt-file`）会话中任何终端命令都触发 permission prompt 且无人应答，整会话按 `permission_cancelled` 取消——lane 因此无法运行验证/构建命令（实测两次派工均死于首个终端命令，见会话事件 `cancellation_category: permission_cancelled`）。修订：executeGrok 改用 `--permission-mode bypassPermissions`。grok CLI 无 codex `workspace-write` 式 OS 沙箱，此为无头可用的最小修法；风险由验收分级（diff 判读 + 回执）兜底，且不超出用户交互侧 `always-approve` 的既定姿态。另：预检降级后二进制缺失曾会落为 `grok_failed`，现于 executeGrok 将 spawn ENOENT 映射回 `grok_unavailable`，保住 SKILL `*_unavailable` 改道触发器。

## 追记（2026-08-13）— 目录解析漏掉非默认行

前提证伪：`grok models` 的目录输出仅当前默认模型行以 `*` 标注，其余模型行以 `-` 开头（grok-4.6 换代后实测：`* grok-4.6 (default)` / `- grok-4.5` / `- grok-s2a`）。parseModelCatalog 的正则只匹配 `*` 行，白名单因此只剩默认模型——spec 指定目录内非默认模型（如自定义供应商渠道需显式传 model 才能选中的 grok-s2a）被误判 `spec_invalid`，违背本 ADR「白名单与默认模型取自现场目录」的决策本意。

修订：解析器同时接受 `*` 与 `-` 行（`/^\s*[-*]\s+(\S+)/gm`），默认模型仍取 `Default model:` 行。行为面：默认模型解析不变，目录内非默认模型恢复合法，目录外 typo 仍 fail-loud（`spec_invalid`）。同批将 SKILL.md 的 grok 车道条款改为「默认省略 model」：CLI 自身默认随目录换代走，spec 零改动跟进换代；仅刻意选非默认目录项（如自定义渠道模型）时才写 model。Cursor 侧不受影响——子代理派发始终显式钉模型。

## 追记（2026-09-06）— 等待协议入技能、`end_to_close_ms` 诊断、空 diff 不得 complete

与 [ADR 0013](./0013-delivery-contract-not-build-instructions.md) 同批落地，两条 runner 同改（镜像维护，本 ADR 既有代价）。

**等待协议（doctrine，`lanes-claude-code.md`）。** 一手证据：2026-09-05 Claude Code 会话 `82ef694a`（cc-usage 仓库）把 `run-grok.mjs` 后台化后以 `sleep 780; sleep 420` 等待，grok 约 15 分钟写完、主会话约 21 分钟才继续。已核实的原因是架构师的固定睡眠，不是 runner。协议：CLI 车道的完成点是 **runner 进程退出**，不是流里的 `end` 事件，也不是睡眠到期；等待方式二选一——前台跑 runner 让 Bash 在退出时返回，或已后台化时对该任务 `TaskOutput(block=true)`；禁止 `sleep N` 再 `ls .fable-advisor/pending/` 充当等待；pending 消失或 receipt 出现是完成证据；`timeout_sec` 只用于杀卡住的进程。并行多车道时逐条 block，或同一条消息里前台并行。此前该规则只存在于机器本地 `.memory/conventions/cli-lane-wait.md`（trial），随本次晋升入技能后删除。

**`end_to_close_ms` 诊断（两条 runner）。** memory 文件里另有一条假设：grok 吐出 `end` 后进程不退出、要等到 `timeout_sec` 才 SIGKILL。未证实，本次不改行为，只加诊断：receipt 新增 `end_to_close_ms` = 终止事件（grok `{"type":"end"}`；codex 取其流中等价的终止事件）到子进程 `close` 的毫秒数，未见终止事件时为 null。数据显示常态滞留时再做行为修复（ADR 0013 复盘条件）。

**空 diff 不得 complete（两条 runner）。** 来源：上游 `ad2bdc3`，经 `docs/upstream-sync/2026-09-05-digest.md` 评估后以 fork 形状吸收。一手核实：`run-codex.mjs:555-561` / `run-grok.mjs:538-545` 在验证全 0 时标 `complete`，不看 `changed_files`；`collectChangedFiles` 在 `git status` 失败时返回 `[]`（`:379-384` / `:340-345`）；`receipt-gate.py:48` 只认 `complete`，runner 随后删 pending——静默空跑会被当成做完。修订：`spec.files.length > 0` 且 `changed_files` 为空 → 新 `error_class: no_diff`（不删 pending）；`git status` 失败 → 新 `error_class: git_status_failed`，不再假 `complete`。`files: []` 仍合法（只读 / 报告型任务）。返工票里车道判定「缺陷不复现、无需改动」同样得到 `no_diff`——这是想要的：架构师读报告后删 pending 并说明。已知边界：`changed_files` 取整个工作目录的 `git status --porcelain`，脏树下永远非空，`no_diff` 在脏树上失效；派 runner 前工作树必须干净（写入 `lanes-claude-code.md`）。

**`resume_session_id`（两条 runner）** 属 ADR 0013 决策 7，此处只交叉引用：codex `codex exec resume <id>`、grok `--resume <id>`，receipt 记 `resumed_from`。

复盘条件追加：`end_to_close_ms` 常态显著大于 0 → runner 在终止事件后短超时收工；`no_diff` 误报（车道确有改动但 `git status` 未捕获，如 `.gitignore` 内路径）→ 改为基于基线 commit 的精确差分。

## 追记（2026-09-07）— 三个时钟、`max_idle_ms` 诊断、中断可回执

**滞留假设证伪，该条复盘条件关闭。** rustpad 仓库 11 份 `complete` 回执的 `end_to_close_ms` 全部落在 776–930 毫秒。终止事件到进程退出没有常态滞留，不做「终止事件后短超时收工」的行为修复。

**提前终止的真实来源是三个互相独立、默认值均不超过 600 秒的时钟。** 一手证据：rustpad receipt `96f6675b` 的 `started_at`/`finished_at` 相隔 600.0 秒、`error_class: timeout`、`verification: []`——车道当时已写完实现，被 runner 自己的墙钟砍掉，回执因此不带任何验证证据，验收退化为架构师手工核对工作区。

1. runner 的 `timeout_sec`（默认 600 秒）：杀 CLI 子进程，跳过验证，回执 `timeout`。
2. harness 的 Bash `timeout` 参数（默认 600000 毫秒，上限 3600000）：砍掉前台派遣调用本身，runner 来不及写任何东西，**没有回执**，pending 留存。其默认值与 runner 默认值重合，只调大 `timeout_sec` 无效。
3. `TaskOutput` 的 `timeout`（默认 30000 毫秒，上限 600000）：不杀进程，但单次 block 会在车道仍在跑时返回。超过十分钟的等待只能靠反复 block；这也是唯一没有绝对上限的等待路径，单次前台调用永远不超过 60 分钟。

**孤儿进程探针（2026-09-07 本机实测）。** CLI 子进程以 `detached` 启动，自成进程组，父进程按进程组 SIGKILL 后子进程原样存活。第 2 个时钟触发时，CLI 会继续改仓库而主会话已认定派遣结束。

**决策：本轮只加测量与中断兜底，不改超时语义。** 两条 runner 同改，`receipt_version` 仍为 1（两处均为增量字段）。

1. receipt 新增 `max_idle_ms` = 事件流上相邻两个事件的最大间隔毫秒数，首个事件之前的间隔自子进程 spawn 起算；无事件为 null。纯诊断，不参与 `error_class`，不派生任何截止。
2. runner 接管 `SIGTERM`/`SIGINT`：杀子进程树 → 写并打印 `error_class: interrupted` 回执（保留已知 session id、跳过验证、保留 pending）→ 非零退出。孤儿与「无回执」两个洞一起补上。
3. 把总墙钟换成静默截止（最后一个事件之后 N 秒才算卡死）推迟到 `max_idle_ms` 有真实分布之后再定 N。现在定值等于拿默认值换另一个拍脑袋的默认值。
4. `lanes-claude-code.md` 记三个时钟的取值口径，以及 `timeout` 回执的恢复路径：回执带 session id 而不带验证证据，正解是带 `resume_session_id` 的返工票让车道自己跑完验证，不是架构师手工验收。

已知边界：信号在 `runVerification` 期间到达时 runner 不中断验证，回执按验证结果落定——此时 CLI 子进程已退出，没有孤儿风险；对 runner 直接 SIGKILL 仍会留下孤儿；Windows 侧进程树清理未实测。

复盘条件追加：`max_idle_ms` 分布可用后 → 以其高分位加余量设静默截止，`timeout_sec` 降级为可选的绝对上限；若观察到 CLI 在长命令期间完全不吐事件（`max_idle_ms` 接近整轮时长）→ 静默截止不成立，改找别的活性信号。
