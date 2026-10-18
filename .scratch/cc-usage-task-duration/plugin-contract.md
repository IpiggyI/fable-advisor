# 契约：车道退出前自检与等待时间削减（6.6.0）

依据：[ADR 0035](../../docs/adr/0035-lane-pre-exit-checks-and-wait-cuts.md) 的「决策」一节，五条全部约束本契约。问题单 01、03、04 由本契约处理，02、05 不改。

## 计划

- 只有一份契约，所有改动都在 `plugin/skills/orchestration/` 与两条 runner 的同一区域，交给一个 worker。
- 路由：`Route: role=worker tier=same-model dial=opus-5-5[high] basis=same-model ref=doctrine prose under plugin/skills/** (with the runner prompt sentence and test that mirror it)`。
- 宽检查：无。本仓 `tests/` 下的脚本各自几秒，都是本契约的判定检查，由车道运行，主代理复核输出。

## 五部

1. **Objective**：按 ADR 0035 决策 1 到 5 改动 shipped 文字与 runner 注入句。验收：
   - 两条 runner 的注入句不再叫车道「不要把列表当收尾再跑」，改为：runner 收尾时自己跑，这一遍是回执里的证据；车道退出前，对列表里自上次相关修改后还没见过通过的命令各跑一次；范围内的失败自己修，被保留操作或环境挡住的写进 GAPS。两条 runner 的句子逐字相同。
   - `lane-preamble.md` 的 `**Verification.**` 段与注入句一致；「比改动更宽、且不在列表里的检查归调用方批次」这条保留。
   - `runners.md`：`timeout_sec` 条目写明只在当前请求给出时限时才写，项目记忆或笔记里的取值不算；写明静默截止只看事件是否停止，长车道要看事件日志，失控时按中途停止流程停它。「runner 是检查列表的执行者 … so the lane is told not to repeat it」一句改成与决策 1 一致。
   - `SKILL.md`：交付合同第 2 部（实施契约 Files 写具体路径，只在新建文件处写目录，原因是 Files 决定哪些契约能同时跑；报告契约仍是读取范围）；第 5 部（改动可能破坏廉价的类型检查或 lint 时，它进检查列表）；`## Parallelism` 的计划条目（两份契约串行要写理由：共用文件、需要对方结果、容量限制、有证据的环境限制）；`**Run each check once.**`（完整输出写文件、从文件读失败；写入其范围的车道全部退出后才开跑；返工后先跑失败文件，这一批最后一次返工落地后再跑一次宽检查；代码、依赖、输入或环境变了，证据失效仍要重跑）。SKILL.md 里与「车道不再跑列表」矛盾的句子一并改。
   - 每个改动的 `.md` 在 `docs/zh/` 下的孪生同步改，术语按 `CONTEXT.md`。
2. **Files**：`plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`plugin/skills/orchestration/SKILL.md`、`plugin/skills/orchestration/runners.md`、`plugin/skills/orchestration/lane-preamble.md`、`docs/zh/skills/orchestration/SKILL.md`、`docs/zh/skills/orchestration/runners.md`、`docs/zh/skills/orchestration/lane-preamble.md`、`tests/test_runner_contract.py`。
3. **Interfaces**：runner 的 spec 键、回执字段、`error_class` 不变。
4. **Constraints**：
   - 不改 runner 的行为，只改注入句的文字。
   - shipped 文字按 `AGENTS.md`「Wording of shipped text」：只写规则与事实，不写来历、不写 ADR 编号、不写「本次改了什么」。
   - 不改版本号、不写说明书、不提交、不推送。
   - 不动 Files 之外的文件；`plugin/skills/orchestration/routing-profile.md` 与其他 lanes 文件不在范围内。若发现范围外的文件必须改才一致，写进 GAPS。
5. **Verification**（车道运行，报告里贴输出）：
   - `python3 tests/test_runner_contract.py`
   - `python3 tests/test_zh_mirror.py`
   - `python3 tests/test_shipped_wording.py`
   - `grep -rn "do not repeat this list" plugin docs/zh tests` 无输出。
   - `grep -n "timeout_sec" plugin/skills/orchestration/runners.md` 的输出里能看到「当前请求」这一条件的英文表述。

## 结果

2026-10-18，worker（`opus-5-5[high]`，same-model）交回，改了 Files 里全部 9 个文件。主代理按 Tier 1 读了两条 runner、`lane-preamble.md`、`SKILL.md`、`runners.md` 和测试的限定路径差异，与 ADR 0035 决策 1 到 5 逐条对得上。主代理复跑：`test_runner_contract.py` 24/24、`test_zh_mirror.py` 19/19、`test_shipped_wording.py` 49/49，全部通过。

- 决策 3 落地为「读最新一行进度和工作树改动」，因为 runner 不写事件日志文件；ADR 已同步。
- 车道报的既有问题：报告模式的 spec 带非空检查列表时，注入句也会叫只读车道「修范围内的失败」。旧句子就有这个问题，本契约不改 runner 行为，未处理。
- Tier 3（同族差异的 advisor 验收）未做，等椰椰确认。

## 更正契约：运行中标记带会话编号（新会话）

原会话已用满三次（首派加两次返工）。第二次 acceptance 复审（codex 会话 `01a14f7a-4d8c-7a11-8ce5-297a521392da`）判 `runners.md:71` 不满足：按「最近修改、开始时间不早于标记」定位会话记录，续跑时排除了正确记录，并发时可能找到另一条车道。椰椰选了 ADR 0035 决策 6。路由同上：`Route: role=worker tier=same-model dial=opus-5-5[high] basis=same-model ref=doctrine prose under plugin/skills/** (with the runner code and tests that it documents)`。

1. **Objective**：两条 runner 的运行中标记新增 `session_id`。Grok：从标记第一次写入起就是本次会话编号（注入的或 `resume_session_id`）。Codex：读到编号前为 `null`，读到后最迟在下一次刷新写入；续跑时从一开始就是 `resume_session_id`。`runners.md` 第 61 行的标记字段清单加上它；第 71 行改为按标记里的 `session_id` 找会话记录，删掉「最近修改」那条定位规则；`session_id` 为 `null` 时，主代理不按猜测的记录停车道。中文孪生同步。
2. **Files**：`plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`plugin/skills/orchestration/runners.md`、`docs/zh/skills/orchestration/runners.md`、`tests/test_runner_contract.py` 或 `tests/test_runner_lifecycle.py`（选一个放新用例）。
3. **Interfaces**：标记的现有字段与语义不变；`hooks/receipt-gate.py` 读标记的方式不变，新字段只增不改。回执字段不变。
4. **Constraints**：除新增字段外不改 runner 行为。shipped 文字规则同前。不改版本号、不提交、不推送。
5. **Verification**：一条新用例：分别对两条 runner，在运行中读标记，断言 `session_id` 等于 runner 注入的编号（Grok）或假 CLI 吐出的编号（Codex），续跑时等于 `resume_session_id`；改坏写入时它会失败。再跑 `python3 tests/test_runner_contract.py`、`python3 tests/test_runner_lifecycle.py`、`python3 tests/test_receipt_gate.py`、`python3 tests/test_zh_mirror.py`、`python3 tests/test_shipped_wording.py`；`sed -n 61p` 与 `sed -n 71p` 两份 `runners.md`。

## 新票：停车道时先发 SIGINT（同一会话，排在会话编号票之后）

依据 ADR 0035 决策 7。与上一票同改两条 runner，所以串行，交给同一个会话。

1. **Objective**：两条 runner 的 `killProcessTree` 在 POSIX 上先向 CLI 进程组发 SIGINT，等 5 秒宽限期；进程组仍在时再发 SIGKILL。中断、`idle_timeout`、`timeout` 三条路径都走它。Windows 分支不变。现有的两秒清理时限、`kill_failed` 诊断与「退出未观察到」的语义保持成立；如需调整清理时限以容纳宽限期，在报告里写明新值。`runners.md` 描述停止流程的句子（第 65、69 行一带）与中文孪生同步。
2. **Files**：`plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`plugin/skills/orchestration/runners.md`、`docs/zh/skills/orchestration/runners.md`、`tests/test_runner_lifecycle.py`（必要时 `tests/test_runner_contract.py`）。
3. **Interfaces**：回执字段与 `error_class` 不变。
4. **Constraints**：同上一票。
5. **Verification**：新用例：假 CLI 捕获 SIGINT 后自行退出时，runner 不发 SIGKILL，回执的 `error_class` 正确；假 CLI 忽略 SIGINT 时，宽限期后被 SIGKILL。改回直接 SIGKILL 时第一条会失败。再跑 `python3 tests/test_runner_lifecycle.py`、`python3 tests/test_runner_contract.py`、`python3 tests/test_receipt_gate.py`、`python3 tests/test_zh_mirror.py`、`python3 tests/test_shipped_wording.py`。
