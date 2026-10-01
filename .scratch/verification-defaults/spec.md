# 契约只放本契约范围内的检查，昂贵的宽检查归批次，并票按契约验收

Status: resolved（2026-10-02 随 6.1.0 发布；跨厂商验收第三轮修改后接受，措辞修正已并入。椰椰 2026-10-02 审阅通过修订稿，确认 `SKILL.md` 词数上限 2340）

日期：2026-10-01。决策见 [ADR 0029](../../docs/adr/0029-scoped-contract-checks-and-batch-defaults.md)，证据见 [问题报告](problem-report.md)。上游交接：`/mnt/d/Development/Local/prompts/docs/plans/fable-advisor-verification-handoff-2026-09.md`。

本任务不含发布：版本说明书、两个版本字段、推送、两侧 `claude plugin update`、伴生安装器由椰椰另行安排。

## 派发方式

实现姿态：主会话亲自修改，不派 worker。依据是椰椰 2026-10-01 的声明：「本次修复不允许派worker，必须主会话亲自完成！」下文「契约」一节作为完成标准。

- 本批只有这一份契约，批次检查就是全部改完后的那一次运行。
- 验收：改动出自主会话自己，按分层验收第 3 层请跨厂商 advisor 做 acceptance 形状的评审。

## 契约

### Objective

按 ADR 0029 决策 1 至 6 修改插件。验收标准：

1. 下文「定稿措辞」的 13 组替换逐字落地：每段旧文本在文件中恰好出现一次，被新文本替换。英文 4 份、中文孪生 4 份，共 26 处。
2. 两个 runner 的每个 `verification` 条目新增 `output_log`：
   - 值是 `.fable-advisor/receipts/<spec_hash>.verification-<n>.log`。`n` 从 1 开始，与命令在 `verification` 数组中的位置一一对应。路径相对于 `--cwd`，分隔符用 `/`。
   - 文件内容是该命令的完整合并输出（stdout 与 stderr）。输出边产生边写入文件，不在内存中累积全文。启动失败时，错误信息也写进文件。
   - 回执目录在运行第一条检查之前创建。同一 spec 哈希再次运行时覆盖旧文件。
   - 日志只记录，不改变被记录的命令：runner 不为日志暂停读取命令输出。写入队列超过 16 MiB 时放弃这份日志：`output_log` 为 `null`，stderr 打一行诊断，并尽力删除不完整的文件，删不掉时再打一行诊断。16 MiB 是放弃日志的队列阈值，不是硬性内存上限：超阈值检查在写入之后进行，队列峰值可再多一个输出块。
   - 文件写不出时：`output_log` 为 `null`，stderr 打一行诊断，该命令的 `exit_code`、`output_tail` 与整体 `error_class` 不受影响。
   - `output_tail` 的语义与长度（最后 2000 字符）不变。没有执行核验的路径（`idle_timeout`、`timeout`、`interrupted`、`preparation_stalled` 等）保持 `verification: []`，不写日志。
3. `tests/test_runner_contract.py` 新增一个用例，两个 runner 都要覆盖：
   - 一条检查先输出一个标记，再输出多于 2000 字符的内容，最后以非零码退出。断言：`error_class` 为 `verification_failed`；`exit_code` 正确；标记不在 `output_tail` 里，但在 `output_log` 指向的文件里；`output_log` 的值等于按 spec 哈希算出的路径。
   - 两条检查各自得到序号 1、2 的日志文件。
   - 预先在日志路径上放一个同名目录，让写入失败。断言：`output_log` 为 `null`，`exit_code` 与 `error_class` 照常。
   - 把任一 runner 的 `output_log` 写入去掉，这个用例必须失败。

### Files

- `plugin/skills/orchestration/SKILL.md`、`lane-preamble.md`、`lanes-claude-code.md`、`lanes-cursor.md`
- `plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`
- `tests/test_runner_contract.py`
- `docs/zh/skills/orchestration/SKILL.md`、`lane-preamble.md`、`lanes-claude-code.md`、`lanes-cursor.md`

### Interfaces

- 回执结构只新增 `verification[].output_log`，其余字段、`error_class` 取值和优先级不变。
- `renderPrompt` 注入句不变；前言文件路径不变；receipt gate 只按 `<hash>.json` 读回执，`.log` 文件不影响它。

### Constraints

- 不做任何 git 写操作，不改版本字段，不发布。
- 只改 Files 内的文件。发现 Files 外的文件被本次改动证伪（例如 `README.md`），写进报告，不改。
- 随插件发布的文本遵守 `AGENTS.md` 的 "Wording of shipped text" 与 "Canonical notation"。
- `plugin/skills/orchestration/SKILL.md` 的 `wc -w` 不超过 2340（ADR 0029 决策 8，椰椰 2026-10-02 确认）；定稿措辞落地后实测为 2334。

### Verification

本契约就是整个批次，下列检查在全部改完后各跑一次：

```bash
python3 tests/test_runner_contract.py
python3 tests/test_runner_lifecycle.py
python3 tests/test_receipt_gate.py
python3 tests/test_zh_mirror.py
python3 tests/test_shipped_wording.py
wc -w plugin/skills/orchestration/SKILL.md
git diff --check
```

开发过程中只跑最窄的检查，例如新用例所在的单个测试文件，或 `node --check` 单个 runner。

## 定稿措辞

13 组替换的要点，顺序与下文一致：

| 文件 | 组 | 要点 |
|---|---|---|
| `SKILL.md` | 1 | 第 5 部只放本契约改动及其调用方的检查；先用最便宜的判定检查；不放批次检查 |
| `SKILL.md` | 2 | 任务件只内联本契约自己的检查 |
| `SKILL.md` | 3 | 返工只验覆盖失败用例与修复波及范围的最小检查 |
| `SKILL.md` | 4 | 同一区域的多张票并成一份契约；按契约验收一次；提交只在授权或回滚边界处拆分 |
| `SKILL.md` | 5 | 昂贵的宽检查是批次检查：跑的时机、两种例外、批次大小、登记与收口（含提前停止） |
| `SKILL.md` | 6 | 删除「返工之后，验收重验……」一句，内容已并入第 3 组 |
| `SKILL.md` | 7 | 第 1 层验收复用车道的命令输出，验收的力气花在车道看不到的部分 |
| `lane-preamble.md` | 1 | 车道对自己 diff 的评审是自查；高风险契约可做车道内独立验收；用最窄检查复核；验收归调用方 |
| `lane-preamble.md` | 2 | 开发中只跑最窄检查；更宽的昂贵检查归调用方的批次，子代理也不跑 |
| `lanes-claude-code.md` | 1 | 回执字段新增 `output_log` |
| `lanes-claude-code.md` | 2 | 检查失败时从 `output_log` 读失败用例，只重跑这些用例 |
| `lanes-claude-code.md` | 3 | 返工的 Verification 与 `SKILL.md` 第 3 组一致 |
| `lanes-cursor.md` | 1 | 返工契约带失败的用例 |

同类文本核对（行号按改动前）：Files 之外和 13 组之外，下列行也提到核验命令、检查列表或回执输出。逐行核对后都不改：

- `plugin/skills/orchestration/handoff-lane.md:7` 及孪生：handoff 验收豁免于核验层，也没有 receipt，所以主代理亲自重跑核验命令。第 7 组的「复用命令输出」写在第 1 层里，不适用于 handoff。
- `lanes-claude-code.md:81` 及孪生：这一句规定管道排空期限，不规定跑哪些检查。`output_log` 与 `output_tail` 来自同一次输出捕获。
- `SKILL.md:103` 及孪生：Constraints 约束核验命令能动什么，与检查范围无关。
- `SKILL.md:134` 及孪生：第 1 层的验收证据仍是命令、退出码与输出尾部；`output_log` 用于读失败用例。
- `lanes-cursor.md:11` 及孪生：Task 派发的检查列表由车道在结尾跑一次。新规则只缩小列表的范围，与这句一致。
- `lanes-cursor.md:20` 及孪生：回执字段引用 `lanes-claude-code.md`，所以自动包含 `output_log`。
- `plugin/agents/advisor-*.md:30` 及孪生：要求读回执里的实际核验输出；`output_log` 属于这份输出。
- `README.md`：没有描述回执字段。

### `plugin/skills/orchestration/SKILL.md` 与孪生 `docs/zh/skills/orchestration/SKILL.md`

1. 英文旧文本：

   ```text
   5. **Verification**: for a worker, the checks that decide *this* contract — at least one that fails when the Objective's named behaviour is not met, never held back — with anything held for a later batch named in the contract and its task artifact, and kept out of this list; for an explorer or advisor, the expected evidence or verdict shape, possibly empty
   ```

   英文新文本：

   ```text
   5. **Verification**: for a worker, the checks scoped to *this* contract's change and its callers — at least one that fails when the Objective's named behaviour is not met, never held back, the cheapest that does (an existing test, or a grep for a textual change) before new test code — and no batch check, even one a ticket lists; for an explorer or advisor, the expected evidence or verdict shape, possibly empty
   ```

   中文旧文本：

   ```text
   5. **Verification**：对 `worker`，判定*这一张*契约的检查——至少一条 Objective 点名的行为未达成就会失败、且永不延后的检查——而留给后续批次的检查在契约和它的任务件里点名，不放进这份列表；对 `explorer` 或 `advisor`，期望的证据或裁决形状，可为空
   ```

   中文新文本：

   ```text
   5. **Verification**：对 `worker`，范围限于*这一张*契约的改动及其调用方的检查——至少一条 Objective 点名的行为未达成就会失败、且永不延后的检查，先用能做到这一点的最便宜检查（现有测试，文本类改动用 grep），之后才写新的测试代码——不放批次检查，票据列出的也不放；对 `explorer` 或 `advisor`，期望的证据或裁决形状，可为空
   ```

2. 英文旧文本：

   ```text
   inlines only the acceptance criteria, reserved constraints, and verification commands, naming
   ```

   英文新文本：

   ```text
   inlines only the acceptance criteria, reserved constraints, and the contract's own checks, naming
   ```

   中文旧文本：

   ```text
   并只内联验收标准、保留约束和核验命令，写明
   ```

   中文新文本：

   ```text
   并只内联验收标准、保留约束和本契约自己的检查，写明
   ```

3. 英文旧文本：

   ```text
   Verification = the check that failed. No fix inside.
   ```

   英文新文本：

   ```text
   Verification = the smallest runnable check covering the failing cases and the fix's reach, not the whole suite. No fix inside.
   ```

   中文旧文本：

   ```text
   Verification = 失败的那条检查。里面不写修复方案。
   ```

   中文新文本：

   ```text
   Verification = 能覆盖失败用例和修复波及范围的最小可运行检查，不是整个套件。里面不写修复方案。
   ```

4. 英文旧文本：

   ```text
   sequential chains and single-file surgery stay serial.
   ```

   英文新文本：

   ```text
   sequential chains and single-file surgery stay serial. Tickets sharing files or an area go to one worker as one contract, with a deciding check and a report line per ticket, unless that outgrows one lane's context or a ticket needs another's verified result or separate authorization. The contract is accepted once, not per ticket; commits split only at authorization or rollback boundaries.
   ```

   中文旧文本：

   ```text
   顺序链与单文件手术保持串行。
   ```

   中文新文本：

   ```text
   顺序链与单文件手术保持串行。共用文件或同一区域的多张票交给一个 `worker`，作为一张契约派发，每张票各有一条判定检查和一行报告；以下情况分开派发：超出一条车道的上下文、一张票需要另一张已核验的结果、一张票需要单独授权。这张契约验收一次，不逐票验收；提交只在授权或回滚边界处拆分。
   ```

5. 英文旧文本：

   ```text
   Contracts that share costly setup are verified together once the last has landed; keep a mid-point check where deferring would blur attribution, leave an unverified prerequisite under later work, or block a contract that depends on this one.
   ```

   英文新文本：

   ```text
   A costly check wider than one contract's change (full suite, browser or end-to-end suite, full build or package) is a batch check, run once after the batch's last contract lands, or earlier where later work builds on what only it verifies, and again only after a rework of a failure it found. A batch holds as many contracts as one failing run can attribute; a failure reworks the contract traced as its cause. Record batch checks once in the task artifact as passed, failed or pending, with output; failed or pending, a check left unrun by an early stop included, means the task is not done unless the user waives it.
   ```

   中文旧文本：

   ```text
   共用昂贵准备的契约在最后一张落地之后一起验一次；当延后会让失败难以归因、会把未经核验的前提留在后续工作下面、或会卡住依赖这一张的另一张契约时，保留一次中途检查。
   ```

   中文新文本：

   ```text
   比单张契约改动更宽的昂贵检查（全量测试、浏览器或端到端套件、完整构建或打包）是批次检查：在批次最后一张契约落地之后跑一次；后续工作依赖只有它能验证的结果时提前跑；只在它发现的失败返工之后再跑。一个批次容纳的契约数，以一次失败仍能归因为限；失败时给追溯到的致因契约开返工票。批次检查在任务件里登记一次，记为通过、失败或待跑，并附输出；有失败或待跑的批次检查（包括因提前停止而没跑的），任务就不算完成，除非用户豁免。
   ```

6. 英文旧文本：

   ```text
    After a rework, acceptance re-verifies the failed scenario and whatever the fix touched.
   ```

   英文新文本：（删除）

   中文旧文本：

   ```text
   返工之后，验收重验失败的那个场景，以及修复波及到的范围。
   ```

   中文新文本：（删除）

7. 英文旧文本：

   ```text
   A full unscoped `git diff` never enters the main agent's context.
   ```

   英文新文本：

   ```text
   A full unscoped `git diff` never enters the main agent's context. A lane's own review or acceptance pass is a claim; reuse its command output instead of re-running it, and spend acceptance on what the lane could not see: other contracts, environments it lacked, batch checks.
   ```

   中文旧文本：

   ```text
   完整的未限定范围 `git diff` 从不进入主代理上下文。
   ```

   中文新文本：

   ```text
   完整的未限定范围 `git diff` 从不进入主代理上下文。车道自己做的评审或验收是主张；复用它的命令输出，不重跑，把验收的力气花在车道看不到的部分：其他契约、它不具备的环境、批次检查。
   ```

### `plugin/skills/orchestration/lane-preamble.md` 与孪生 `docs/zh/skills/orchestration/lane-preamble.md`

1. 英文旧文本：

   ```text
   and splitting the work and dispatching your own subagents is your call.
   ```

   英文新文本：

   ```text
   and splitting the work and dispatching your own subagents is your call. A review of your own diff, yours or a subagent's, is self-check; on a contract you judge high-risk it may be an independent acceptance pass. Re-verify its findings with the narrowest check, report them with their evidence, and leave acceptance to the caller.
   ```

   中文旧文本：

   ```text
   拆分工作并派发自己的子代理由你决定。
   ```

   中文新文本：

   ```text
   拆分工作并派发自己的子代理由你决定。对自己 diff 的评审，无论由你还是子代理来做，都是自查；你判定为高风险的契约，可以做一次独立验收。用最窄的检查复核它的发现，连同证据写进报告，验收留给调用方。
   ```

2. 英文旧文本：

   ```text
   A check the contract holds for a later batch is not yours.
   ```

   英文新文本：

   ```text
   While you work, run the narrowest check that answers your question, such as one test file. A costly check wider than your change (the full suite, a browser or end-to-end suite, a full build or package, a slow whole-project type check) belongs to the caller's batch unless your list names it; your subagents do not run it either.
   ```

   中文旧文本：

   ```text
   契约留给后续批次的检查不归你。
   ```

   中文新文本：

   ```text
   工作过程中，只跑能回答当前问题的最窄检查，例如一个测试文件。比你的改动更宽的昂贵检查（全量测试、浏览器或端到端套件、完整构建或打包、耗时长的整项目类型检查）属于调用方的批次，除非你的检查列表写了它；你的子代理也不跑它。
   ```

### `plugin/skills/orchestration/lanes-claude-code.md` 与孪生 `docs/zh/skills/orchestration/lanes-claude-code.md`

1. 英文旧文本：

   ```text
   - `changed_files`, plus the verification commands' actual exit codes and output tails.
   ```

   英文新文本：

   ```text
   - `changed_files`, plus each verification command's actual `exit_code`, its `output_tail` (the last 2,000 characters of its combined output), and its `output_log`: the path, relative to `--cwd`, of `.fable-advisor/receipts/<spec_hash>.verification-<n>.log`, which holds that command's complete output; `null` when the runner could not write the file.
   ```

   中文旧文本：

   ```text
   - `changed_files`，外加核验命令的实际退出码与输出尾部。
   ```

   中文新文本：

   ```text
   - `changed_files`，外加每条核验命令的实际 `exit_code`、`output_tail`（合并输出的最后 2,000 个字符）与 `output_log`：相对于 `--cwd` 的路径 `.fable-advisor/receipts/<spec_hash>.verification-<n>.log`，文件里是该命令的完整输出；runner 写不出该文件时为 `null`。
   ```

2. 英文旧文本：

   ```text
   and the receipt's output is that one run.
   ```

   英文新文本：

   ```text
   and the receipt's output is that one run. Read a failed check's cases from its `output_log` and re-run only those; re-running the list to see what failed repeats the most expensive step.
   ```

   中文旧文本：

   ```text
   receipt 里的输出就是那一次执行。
   ```

   中文新文本：

   ```text
   receipt 里的输出就是那一次执行。检查失败时，从它的 `output_log` 读出失败用例，只重跑这些用例；为了查看失败而重跑整份列表，等于重复最贵的那一步。
   ```

3. 英文旧文本：

   ```text
   Verification = the check that failed — no fix inside
   ```

   英文新文本：

   ```text
   Verification = the smallest runnable check covering the failing cases and the fix's reach — no fix inside
   ```

   中文旧文本：

   ```text
   Verification = 失败的那条检查——里面不写修复方案
   ```

   中文新文本：

   ```text
   Verification = 能覆盖失败用例和修复波及范围的最小可运行检查——里面不写修复方案
   ```

### `plugin/skills/orchestration/lanes-cursor.md` 与孪生 `docs/zh/skills/orchestration/lanes-cursor.md`

1. 英文旧文本：

   ```text
   (defect, original scope, failing check)
   ```

   英文新文本：

   ```text
   (defect, original scope, failing cases)
   ```

   中文旧文本：

   ```text
   （缺陷、原范围、失败的检查）
   ```

   中文新文本：

   ```text
   （缺陷、原范围、失败的用例）
   ```

## 协调件（主会话直接写，不在契约内）

1. `CONTEXT.md`「批次验收」词条整条替换为：

   ```text
   **批次验收**:
   比单张契约改动更宽的昂贵检查（全量测试、浏览器或端到端套件、完整构建或打包）默认归批次：在批次最后一张契约落地之后跑一次；后续工作依赖只有它能验证的结果时提前跑；只在它发现的失败返工之后再跑。一个批次容纳的契约数，以一次失败仍能归因为限。结果在任务件里登记一次，记为通过、失败或待跑，并附输出；有失败或待跑的批次检查（包括因提前停止而没跑的），任务就不算完成，除非用户豁免。执行可以委派，判断归主代理。一张契约的 receipt 或报告只证明它自己，不证明批次已验。
   _Avoid_: 与单张契约的判定检查混称（后者永不延后，也不放批次检查）；把「归批次」理解成「不验」；逐票重复跑批次检查；因为换了角色或换了会话就重跑一遍已验过的批次。
   ```

2. `docs/agents/issue-tracker.md`：约定列表里 `## Held for batch acceptance` 一条，改为：

   ```text
   - Batch checks are recorded once per feature, under a `## Batch checks` heading in its spec or closing ticket
   ```

   同名一节改名为 `## Batch checks`，正文替换为：

   ```text
   A delivery contract carries only the checks scoped to its own change; a costly check wider than one contract's change (full suite, browser or end-to-end suite, full build or package) is a batch check (`CONTEXT.md`, "批次验收"). A batch check has no mechanical keeper — the receipt gate does not see it and no runner records it — so the task artifact is where it lives.

   Name each batch check once under `## Batch checks` in the feature's spec or closing ticket when the batch is planned, and record its result there when it runs: passed, failed or pending, with its output or the path to it. A feature with a failed or pending batch check, one left unrun by an early stop included, is not done unless the user waives it.
   ```

3. `docs/adr/0020-one-executor-per-check-list.md` 状态行追加：「决策 2、3、8 已被 [ADR 0029](./0029-scoped-contract-checks-and-batch-defaults.md) 修订」。
4. `docs/adr/0022-orchestration-load-on-events.md` 状态行追加：「决策 5 的上限已被 [ADR 0029](./0029-scoped-contract-checks-and-batch-defaults.md) 决策 8 上调到 2340」。

## Batch checks

最终工作树（两轮返工之后，2026-10-02）上的结果：

| 检查 | 结果 | 输出 |
|---|---|---|
| `python3 tests/test_runner_contract.py` | 通过 | `21/21 passed, 0 failed`，含新用例 `verification output log` |
| `python3 tests/test_runner_lifecycle.py` | 通过 | 退出码 0；22 行 `PASS`，没有 `FAIL` |
| `python3 tests/test_receipt_gate.py` | 通过 | `11/11 passed, 0 failed` |
| `python3 tests/test_zh_mirror.py` | 通过 | `16/16 passed, 0 failed` |
| `python3 tests/test_shipped_wording.py` | 通过 | `41/41 passed, 0 failed` |
| `wc -w plugin/skills/orchestration/SKILL.md` | 通过 | 2334，上限 2340 |
| `git diff --check` | 通过 | 没有输出 |

两轮返工只改了两个 runner 的日志写入，所以返工后重跑了依赖 runner 的四项：`test_runner_contract.py`、`test_runner_lifecycle.py`、`test_shipped_wording.py`（它也扫描 runner 的注释）与 `git diff --check`，结果如上表。`test_receipt_gate.py`、`test_zh_mirror.py` 与词数依据的文件在返工中没有变化，沿用返工前那一次的结果。

开发中的补充核验，只跑新用例或探针：

- 变异检查：去掉任一 runner 的 `log.write(chunk)` 后，新用例在「完整日志以标记开头」的断言处失败；不改时通过。
- 探针（从 runner 源码取出实际函数，配模拟子进程和慢写入端）：命令退出时写盘还没跟上，尾部与日志都含末尾标记，日志完整。「只暂停」的旧实现在同一场景下触发清理期限，尾部与日志都丢了末尾输出，说明探针能抓到这个问题。写盘落后超过 16 MiB 时，`output_log` 为 `null`，诊断打出，不完整的文件被删除，尾部仍含末尾标记，队列最大为上限加一个 64 KiB 块。
- 真实 runner 跑一条输出 200 MiB 的检查：两条 runner 的日志完整（209,715,207 字节），尾部含末尾标记，没有触发上限。

## Comments
