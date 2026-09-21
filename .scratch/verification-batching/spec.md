# 核验去重与批次验收：一份检查列表一个执行者

Status: ready-for-agent

日期：2026-09-20。目标版本 5.3.0（runner 提示词与 doctrine 语义改变，向后兼容，minor）。上游交接：`/mnt/d/Development/Local/prompts/docs/plans/fable-advisor-verification-handoff-2026-09.md`（2026-09-19，只读核对过源码，未跑插件测试）。词表见 `CONTEXT.md`。

本 spec 不含发布：版本说明书、两个版本字段、push、两侧 `claude plugin update`、伴生安装器由椰椰另行安排。

## Problem Statement

椰椰在使用中反复看到同一批检查被跑很多遍。本仓核对（2026-09-20，工作树含在途改动）确认两个来源：

1. **每次派发把合同检查列表跑两遍。** `renderPrompt` 向车道注入原句 `Run the verification command and include its actual output in your final message.`（`plugin/scripts/run-grok.mjs:186`、`plugin/scripts/run-codex.mjs:209`）；车道退出后 runner 自己又跑一遍同一列表（`run-grok.mjs:748`、`run-codex.mjs:795`）。车道照做，这一列表就至少执行两次，且两次之间工作树没有任何变化。

2. **doctrine 没有给"这张合同的判定检查"与"整个任务的批次验收"分家。** 交付合同第 5 部写 "commands whose output is acceptance evidence, including at least one check that fails when the goal is not met"——它没有**要求**每张工单背整套检查，但"acceptance evidence"这个措辞邀请架构师把整套放进每张合同；真正把整套排了 N 次的是合同分解，不是这一句强制。doctrine 里也没有一句话说明证据在什么条件下继续有效，于是换角色、换会话、勾完一个清单步骤都可能触发重跑。

已核对为**不需要改**的部分：`SKILL.md` 的核验三层没有要求主代理无条件重跑整套测试，Tier 1 明确"依据车道的核验证据验收"；`README.md` 关于验收的两处描述改后仍成立；`advisor-*` 与 `worker-*` agent 文件不含重复执行的指令；`handoff-lane.md` 的"架构师亲自重跑"是另一条理由（无 receipt、产出方不可信），不受本次影响。

## Solution

一句话：**一份检查列表只有一个执行者；共用昂贵准备的合同合并成一次批次验收；证据在其依据未变时继续有效。**

1. **runner 侧去掉终末重复。** 两条 runner 的 `renderPrompt` 改写注入句：告诉车道 runner 会在它退出后自己跑这份列表并把退出码与输出写进 receipt，非零退出仍算车道失败；车道按调试需要跑检查，但不要把这份列表当收尾仪式再跑一遍。`verification` 为空时不注入这句话。runner 自己那次执行不变——它是确定性的、输出进 receipt、车道无法伪造。

2. **合同第 5 部改为"本合同的判定检查"。** 仍要求至少一条检查，且这一条**永远不可延后**；它必须在 Objective 点名的行为未达成时变红，只证明"没崩"不算数。留给后续批次的检查同时在合同正文与上游任务件里点名，**不放进 `verification` 数组**——runner 不认识"延后"，它会执行数组里的每一条；本仓的任务件落点是工单的 `## Held for batch acceptance` 小节。

3. **doctrine 补一段批次规则。** 共用昂贵准备的合同在最后一张落地后一起验一次；三种情况仍保留中途检查——延后会让失败难以归因、会把未经验证的前提留在后续工作下面、或后一张合同依赖这一张的结果；批次的执行可以委派，判断仍归主代理；证据在代码、输入与环境未变时继续有效，换角色或换会话本身不是重跑理由；返工后的验收重验失败场景与修复波及的范围。

4. **两个 harness 说明各写清执行者。** CLI 车道：runner 是合同检查列表的执行者，`complete` receipt 是**它那张合同的证据**，既不是对该合同的验收，也不是对整个任务的验收。Cursor 的 Task 派发没有 runner：列表归车道，它在结尾跑一次，报告里的输出就是全部证据。

5. **`SKILL.md` 词数上限从 1960 上调。** 批次规则必须进主文——它要到达每一个主代理，不能藏在某个 harness 指针后面。落地实测 2101 词，上限定为 2110（见 ADR 0020 决策 6；余量覆盖在途的 `Selector` 删句若不落地的 2106）。

### 已知能力上限

提示词不是机制：车道仍**可以**在收尾前自己跑一遍检查，新增的计数测试只能证明 runner 执行一次，证明不了真实车道不重复。本次移除的是"必须重复、且输出必须进报告"这条要求，不是重复本身。量级削减主要来自第 2、3 条——每张合同只背自己的判定检查，整套昂贵检查一个批次一次。runner 那次确定性执行不动，因为它是唯一不可伪造的证据来源。

## 决策门核对（decision-type gate）

本次改动命中"放宽验收标准"。2026-09-20 以 decision 形状咨询 advisor（codex 车道报告模式，`gpt-6-astra` / `medium`，submitted, not observed；receipt `.fable-advisor/receipts/`）。裁决：方向成立，初稿不宜直接通过，决定性风险是"延后的检查失去明确验收归属，局部绿色被当成完成证明"。五条修订已全部并入上文：

1. 第 5 部必须保住"能否定本合同目标"的那条检查，`held` 不得包含它 → 实现决定 2。
2. "只有下游依赖才保留中途检查"过窄，需补归因与未验证前提两个条件 → 实现决定 3。
3. `complete` receipt 与 `lanes-claude-code.md:103`"还要过分层验收"冲突 → 措辞改为"证据，不是验收" → 实现决定 4。
4. `SKILL.md:138`"没有命令输出的报告即未完成"会误伤不再粘贴输出的 CLI 车道报告 → 改指向证据本身 → 实现决定 3 的措辞。
5. `SKILL.md:112` 返工票的 `Verification` 只写失败项，与"重验波及范围"读起来冲突 → 新句限定为"返工后的**验收**" → 实现决定 3。

advisor 同时确认：`plugin/agents/**`、`lanes-cursor.md` 未发现新增重复要求；第二读者与决策门保留；受 receipt gate 管辖的范围不变。

## User Stories

1. 作为 CLI 车道，我想知道 runner 会在我退出后跑这份检查列表，以便我不把同一列表当收尾仪式再跑一遍。
2. 作为 CLI 车道，我想知道非零退出仍算我的失败，以便我不会因为"有人替我跑"就不管检查是否通过。
3. 作为报告模式的车道，我想在合同没有检查命令时不读到"runner 会跑这些命令"，以便提示词不自相矛盾。
4. 作为架构师，我想合同第 5 部只写这张合同自己的判定检查，以便一个任务的 N 张工单不各背一次整套检查。
5. 作为架构师，我想"能否定本合同目标"的那条检查永远不可延后，以便坏改动不会带着局部绿色进入批次。
6. 作为架构师，我想延后的检查写在合同正文而不进 `verification` 数组，以便 runner 不会把它们照样执行一遍。
7. 作为架构师，我想 doctrine 写明共用昂贵准备的合同可以合并成一次批次验收，以便我不再逐票安排整套检查。
8. 作为架构师，我想 doctrine 写明三种仍需中途检查的情况，以便"合批"不会把关键前提拖到最后才暴露。
9. 作为架构师，我想 doctrine 写明证据的有效条件，以便换角色、换会话本身不触发重跑。
10. 作为架构师，我想 doctrine 写明返工后的验收重验失败场景与波及范围，以便"少跑"不被读成"返工后也不用重验"。
11. 作为架构师，我想 doctrine 允许我把批次检查的执行委派出去而判断仍归我，以便大批输出不占主代理上下文。
12. 作为架构师，我想 `complete` receipt 被写成"那张合同的证据"而不是"验收"，以便它不与分层验收冲突、也不被当成整体完成证明。
13. 作为 Cursor 主代理，我想 `lanes-cursor.md` 写明 Task 派发没有 runner、列表归车道，以便 Cursor 侧不会照搬 CLI 侧的分工。
14. 作为仓库维护者，我想契约测试能在有人把车道侧重复指令加回去时变红，以便这条分工不靠人记。
15. 作为仓库维护者，我想契约测试证明 runner 恰好执行一次检查列表，以便"runner 是执行者"这句话有可执行证据。
16. 作为仓库维护者，我想每个改动的运行时 Markdown 在同一提交里更新中文孪生，以便 `test_zh_mirror` 持续通过。

## Implementation Decisions

### 1. runner 提示词（两条 runner 同改）

`renderPrompt` 中 `# Verification` 一节：

- `spec.verification` 非空：渲染 bash 代码块，随后注入
  `The runner runs these commands itself after you exit and records their exit codes and output in the receipt; a non-zero exit is your failure. Run what you need while you work; do not repeat this list as a closing step.`
- `spec.verification` 为空：渲染与今天完全一致（空 bash 代码块），不注入上句。
- 退役原句 `Run the verification command and include its actual output in your final message.`，全仓零命中。
- runner 自身的 `runVerification` 调用、排除分支（`preparation_stalled` / `timeout` / `idle_timeout` / `interrupted` 跳过核验）、receipt 字段一律不动。

### 2. `lane-preamble.md`

新增一条 `**Verification.**`，放在 `**Gaps.**` 与 `**Report.**` 之间：

> **Verification.** A contract's check list has one executor. When the Verification section says the runner runs it after you exit, do not run that list again to close; run what you need to reach a state you believe passes. When nothing says so, the list is yours: run it once at the end. A check the contract holds for a later batch is not yours.

`**Report.**` 末句 `actual verification output` 改为 `the actual output of the checks you ran`。

`lane-preamble-report.md` 不动（只读角色没有检查列表分工问题）。

### 3. `SKILL.md`

- 交付合同第 5 部改为（2026-09-20 拷问后的终稿）：
  > 5. **Verification**: for a worker, the checks that decide *this* contract — at least one that fails when the Objective's named behaviour is not met, never held back — with anything held for a later batch named in the contract and its task artifact, and kept out of this list; for an explorer or advisor, the expected evidence or verdict shape, possibly empty
- 核验节首句补尾：`…the object of review is the contract, and accepting one closes that contract, not the task.`
- 三层之后、`"Should work"…` 之前新增一段：
  > **Run each check once.** A contract's check list has one executor — the lane's file names which — and is not run again to close. Contracts that share costly setup are verified together once the last has landed; keep a mid-point check where deferring would blur attribution, leave an unverified prerequisite under later work, or block a contract that depends on this one. The main agent may hand a batch's execution to a lane; the verdict stays its own. Evidence holds as long as the code, inputs and environment behind it hold: a changed role or session is not a reason to re-run. After a rework, acceptance re-verifies the failed scenario and whatever the fix touched.
- 末句 `"Should work", "tests should pass", or a report with no command output means not done.` 改为 `"Should work", "tests should pass", or an acceptance with no command output behind it means not done.`
- 其余段落不动。词数验收线 ≤ 2110（原 1960），落地实测 2101。

### 4. `lanes-claude-code.md`

第 4 节 `CLI-lane acceptance = …` 一句之前新增：

> The runner is the executor of the contract's check list: it runs `verification` itself after the CLI exits, so the lane is told not to repeat it, and the receipt's output is that one run. A `complete` receipt is evidence for its own contract — never acceptance of it, and never of the task.

### 5. `lanes-cursor.md`

`**Acceptance.**` 条目末尾新增：

> A Task dispatch has no runner, so the contract's check list is the lane's to run, once, at the end; its output in the report is the only evidence there is.

### 6. 契约测试

`tests/test_runner_contract.py` 新增一个用例，两条 runner 都覆盖：

- 合同 `verification` 非空时，prompt 含新注入句，且不含退役原句。
- 合同 `verification` 为空（报告模式）时，prompt 不含新注入句，`# Verification` 一节渲染与今天一致。
- 用一条会留痕的检查命令（每次执行追加一行到计数文件）证明 runner 恰好执行一次：计数文件正好一行。

### 7. 不改动的文件

`README.md`、`plugin/agents/**`、`docs/zh/agents/**`、`lane-preamble-report.md`、`handoff-lane.md`、`plugin/hooks/**`、`scripts/**`、`cursor-hooks/**`、两条 runner 的核验执行与 receipt 结构。

## 验收

- `python3 tests/test_runner_contract.py` 绿（新用例覆盖第 6 条每一款）。
- `python3 tests/test_zh_mirror.py` 绿。
- `python3 tests/test_runner_lifecycle.py` 无 FAIL 行。
- `wc -w plugin/skills/orchestration/SKILL.md` ≤ 2110。
- 退役原句 `Run the verification command` 在 `plugin/`、`docs/zh/`、`README.md` 零命中；`tests/test_runner_contract.py` 里的一处是新用例的反向断言，属预期。
- 四个改动的 `plugin/**/*.md` 各有中文孪生在同一批更新。
- `git diff --stat` 只含本 spec 列出的文件。

## 落地记录（2026-09-20）

两张工单并行派发，一次批次验收——本 spec 的规则在它自己的交付上先用了一次。

- 工单 01：grok 车道 implement 模式，receipt `complete`。工单 02：claude 车道同模派发（`worker-h` + `model: opus`），doctrine 散文归此类。
- 批次验收（两张工单落地之后一次跑完）：`test_runner_contract` 19/19、`test_zh_mirror` 15/15、`test_runner_lifecycle` 22 条 PASS 零 FAIL、`git diff --check` 干净、`SKILL.md` 2101 词。
- **没有重跑**的：`test_receipt_gate`、`test_lane_family_gate`、`test_install_user_level`、`test_user_level_archive`。它们的被测对象（`plugin/hooks/`、`cursor-hooks/`、`scripts/install-user-level.py`、三件正典）本次零改动，基线证据按新规则继续有效。
- Tier 3 验收：工单 02 是同族 diff，取跨厂填充（codex 车道报告模式，`gpt-6-astra` / `low`，submitted, not observed）。裁决 ACCEPT-WITH-REWORK，唯一阻塞项是本 spec 与工单 02 里残留的 `≤ 2100` 与验收节、ADR 0020 的 `≤ 2110` 互相矛盾——协调件上的契约缺口，已由架构师改齐。其余各条 ACCEPT。
- ADR 0020 记录本批决定与已知能力上限。

基线（2026-09-20，改动前）：`test_runner_contract` 18/18、`test_zh_mirror` 15/15、`test_receipt_gate` 8/8、`test_lane_family_gate` 18/18、`test_install_user_level` 8/8、`test_runner_lifecycle` 无 FAIL；`test_user_level_archive` 5/6——Windows 侧活体路由档案漂移，与本次无关，需椰椰跑一次伴生安装器。
