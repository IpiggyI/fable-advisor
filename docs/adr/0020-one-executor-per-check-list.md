# 0020 — 一份检查列表一个执行者，昂贵检查合并成批次验收

- **Status**: accepted
- **Date**: 2026-09-20
- **影响范围**: `plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`tests/test_runner_contract.py`、`plugin/skills/orchestration/`（`SKILL.md`、`lane-preamble.md`、`lanes-claude-code.md`、`lanes-cursor.md`）、`plugin/agents/explorer-h.md`、`plugin/agents/explorer-xh.md` 与 `docs/zh/` 六份孪生、`CONTEXT.md`（新词条「批次验收」）、`docs/agents/issue-tracker.md`。版本定为 5.3.0，但本批不单独发布——椰椰 2026-09-20 决定与后续改动攒齐一起发
- **关联**: [ADR 0012](./0012-orchestration-skill-progressive-disclosure.md)（`SKILL.md` 词数预算——本次把上限从 1960 上调）、[ADR 0013](./0013-delivery-contract-not-build-instructions.md)（五部契约与前言单源——本次改第 5 部语义、前言增一条）、[ADR 0015](./0015-global-orchestration-entry.md)（上限 1960 的来源）、[ADR 0009](./0009-grok-lane-dewrapper-runner.md)（runner 直驱，注入句的出处）。上游交接 `/mnt/d/Development/Local/prompts/docs/plans/fable-advisor-verification-handoff-2026-09.md`；任务件 `.scratch/verification-batching/`

## 背景

椰椰报告：使用中同一批检查被反复执行。2026-09-20 在本仓只读核对，确认两个来源。

第一个在代码里。`renderPrompt` 向每条 CLI 车道注入 `Run the verification command and include its actual output in your final message.`，车道退出后 runner 又调用 `runVerification(spec.verification, …)` 跑同一份列表。车道照做，这份列表每次派发至少执行两次；两次之间工作树没有任何变化，所以第二次与第一次逐位相同。

第二个在 doctrine 里。交付合同第 5 部写 "commands whose output is acceptance evidence"。它没有**要求**每张工单背整套检查——把整套排了 N 次的是合同分解——但"acceptance evidence"这个措辞邀请架构师这么做，而 doctrine 里没有任何一句说明证据在什么条件下继续有效。结果是换角色、换会话、勾完一个清单步骤都可能触发重跑。

核对同时确认三处**不需要改**：核验三层没有要求主代理无条件重跑整套测试（Tier 1 明确依据车道证据验收）；`plugin/agents/**` 不含重复执行指令；`handoff-lane.md` 的"架构师亲自重跑"另有理由（无 receipt、产出方不可信），与本次的重跑规则不冲突。

## 决策

1. **runner 是 CLI 车道合同检查列表的唯一执行者。** `renderPrompt` 的注入句改为告知车道：runner 在它退出后自己跑这份列表、退出码与输出进 receipt、非零退出仍算车道失败；车道按调试需要跑检查，但不把这份列表当收尾仪式再跑一遍。`spec.verification` 为空时不注入这句话。runner 自身那次执行、排除分支与 receipt 结构一概不动——它是车道无法伪造的唯一证据来源。

2. **交付合同第 5 部只承载"判定这张合同"的检查。** 仍要求至少一条检查，且这一条**永远不可延后**；它必须在 Objective 点名的那个行为未达成时变红——只证明"没崩"的冒烟检查不算数，否则坏改动带着字面满足的绿色进入批次。留给后续批次的检查同时在合同正文与上游任务件里点名，不放进 `verification` 数组——runner 不认识"延后"，它执行数组里的每一条；合同验收之后任务件是这条检查唯一的落脚点，本仓的落点是工单文件的 `## Held for batch acceptance` 小节（见 `docs/agents/issue-tracker.md`）。

3. **昂贵检查合并成批次验收。** 共用昂贵准备的合同在最后一张落地后一起验一次。三种情况仍保留中途检查：延后会让失败难以归因、会把未经验证的前提留在后续工作下面、后一张合同依赖这一张的结果。批次的执行可以交给车道，判断仍归主代理。

4. **证据有有效期，且有效期由依据决定。** 代码、输入与环境未变时证据继续有效；换角色或换会话本身不是重跑理由。返工后的**验收**重验失败场景与修复波及的范围。

5. **`complete` receipt 是那张合同的证据，不是验收。** 验收仍要过 `SKILL.md` 的分层；一张合同关掉不等于整个任务关掉。Cursor 的 Task 派发没有 runner，列表归车道，报告里的输出就是全部证据。

6. **`SKILL.md` 词数上限从 1960 上调到 2110，落地实测 2101 词。** 批次规则要到达每一个主代理，不能按 ADR 0012 的分层原则沉进某个 harness 分支文件；harness 专属的"谁是执行者"仍分别落在两份 lanes 文件。上调 7.7% 是本次为此付的价，不删无关句子抵扣。上限留 9 词余量，因为本次落地时工作树里有一处未提交的在途改动删掉了 `Selector` 段末的 `Model identity never selects posture.`（5 词）；那处改动若不落地，词数为 2106，仍在上限内。

7. **顺手修正 explorer 的前言指针。** `plugin/agents/explorer-h.md` 与 `explorer-xh.md` 原先把只读 explorer 指向 worker 前言 `lane-preamble.md`，改指 `lane-preamble-report.md`。这本是既有缺陷；决策 1 往 worker 前言加了 `**Verification.**`（"列表归你，结尾跑一次"）之后，它从无害错位变成有害错位，因此归本批清理，不另开工单。`advisor-*` 自带完整正文、`worker-*` 指向 worker 前言，两者都正确，不动。

8. **合批与证据失效不设可观察门槛。** 三个中途检查条件与"代码、输入、环境未变"都留作主代理的判断依据，不改成门禁。考虑过两条机械化：按"改动文件集合不相交"才许合批——会否掉最值得合批的同模块连续工单；按"证据采集后所读文件被改过即失效"——要逐检查追踪读了哪些文件，成本高于它省下的那次重跑。真正的兜底是决策 2 那条不可延后的判定检查。

## 未采纳

- **车道报告说跑过就让 runner 跳过。** 用车道的主张替换不可伪造的证据；与"报告是主张，不是证据"直接冲突。
- **取消 runner 那次执行，改用车道粘贴的输出。** 同一缺陷。
- **只改 doctrine、不动注入句。** 终末那次重复是已核实的第二次执行，工作树在两次之间没有变化。
- **保住 1960 上限、删同文重复句抵扣新段。** ADR 0015 用过这条路（删六句）；本次的新段与任何现有段落都不重复，抵扣只能砍到无关内容，属于静默的附带修改。

## 已知能力上限

提示词不是机制。车道仍**可以**在收尾前自己跑一遍；契约测试只能证明 runner 执行一次，证明不了真实车道不重复。本次移除的是"必须重复、且输出必须进报告"这条要求，不是重复本身。量级削减主要来自决策 2、3。

## 决策门核对

本次命中决策类型门的"放宽验收标准"。2026-09-20 以 decision 形状咨询 advisor（codex 车道报告模式，`gpt-6-astra` / `medium`，submitted, not observed）。裁决：方向成立，初稿不宜直接通过；决定性风险是"延后的检查失去明确验收归属，局部绿色被当成完成证明"。五条修订全部并入：第 5 部必须保住能否定本合同目标的那条检查（决策 2）；中途检查条件从"只有下游依赖"扩到三条（决策 3）；`complete` receipt 的措辞从"关闭合同"改为"证据，不是验收"（决策 5）；`SKILL.md` 末句从"没有命令输出的报告"改为指向证据本身，以免误伤不再粘贴输出的 CLI 车道报告；返工重验一句限定为"返工后的验收"，以免与返工票 `Verification` 只写失败项的规定冲突。

## 复盘条件

- CLI 车道在收尾前仍自己跑整套检查（对比 receipt 的 `verification` 输出与车道报告里自述跑过的命令）→ 注入句措辞或位置需要再改，或承认提示词到此为止。
- 批次验收接连放过应当在中途暴露的失败 → 决策 3 的三条件不够，补条件或缩小合批粒度。
- 延后的检查在任务件里被漏掉（工单全勾，而 `## Held for batch acceptance` 还留着没跑的项，或压根没开这个小节）→ 决策 2 的散文约定不够，把 `held` 做成 spec 与 receipt 的字段再议。
- 车道把红色结果交出来的频率上升（`verification_failed` receipt 占比）→ 决策 1 的"非零退出仍算你的失败"没有兜住所有权，需要在前言加强。
- `SKILL.md` 再次逼近 2110 → 重新按 ADR 0012 判断哪一段该沉入分支文件，而不是继续上调。
