# 02: doctrine——判定检查、批次验收、证据有效期

**What to build:** 编排技能写清三件事：交付合同第 5 部只承载"判定这张合同"的检查、延后的检查点名但不进 `verification` 数组；共用昂贵准备的合同合并成一次批次验收，并列出仍需中途检查的三种情况；证据在其依据未变时继续有效，换角色或换会话本身不是重跑理由。两个 harness 说明各写清检查列表的执行者是谁。四份运行时 Markdown 的中文孪生同批更新。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 2、3、4、5 条（逐字给出目标句）。范围：`plugin/skills/orchestration/` 的四份文件与 `docs/zh/skills/orchestration/` 的四份孪生。

- [x] `SKILL.md` 交付合同第 5 部换成 spec 实现决定 3 给出的句子
- [x] `SKILL.md` 核验节首句补尾 `…, and accepting one closes that contract, not the task.`
- [x] `SKILL.md` 三层之后、`"Should work"…` 之前插入 spec 给出的 `**Run each check once.**` 整段
- [x] `SKILL.md` 末句改为 `"Should work", "tests should pass", or an acceptance with no command output behind it means not done.`
- [x] `lane-preamble.md` 在 `**Gaps.**` 与 `**Report.**` 之间插入 spec 给出的 `**Verification.**` 一条；`**Report.**` 末句 `actual verification output` 改为 `the actual output of the checks you ran`
- [x] `lanes-claude-code.md` 第 4 节 `CLI-lane acceptance = …` 之前插入 spec 给出的两句
- [x] `lanes-cursor.md` 的 `**Acceptance.**` 条目末尾追加 spec 给出的一句
- [x] 四份中文孪生同批更新：译出对应句段，术语取 `CONTEXT.md` 的既有词（合同、检查列表、执行者、批次、证据、验收、返工）；孪生只翻译，不增删条目
- [x] `SKILL.md` 词数 ≤ 2110（见 ADR 0020 决策 6；落地实测 2101）
- [x] 其余段落、其余文件不动；`lane-preamble-report.md`、`handoff-lane.md`、`plugin/agents/**`、`README.md` 零改动

## Held for batch acceptance

- `python3 tests/test_runner_contract.py` —— 2026-09-20 批次执行，19/19。
- `python3 tests/test_runner_lifecycle.py` —— 2026-09-20 批次执行，22 条 PASS 零 FAIL。
- `python3 tests/test_receipt_gate.py`、`test_lane_family_gate.py`、`test_install_user_level.py` —— **未执行**：被测对象本次零改动，基线证据按 ADR 0020 决策 4 继续有效。

## Comments

### 2026-09-20 — 实施记录（claude 车道同模派发，`worker-h` + `model: opus`）

- 五句指定英文原文逐字符落地，位置正确；`python3 tests/test_zh_mirror.py` 15/15。
- 车道报了两处缺口，均由架构师裁决：
  1. **词数 2101，超出当时写死的 2100 一词。** 裁决为上调上限到 2110 并记入 ADR 0020 决策 6，不删无关句子抵扣。车道同时查明：HEAD 为 1958，改动前工作树为 1953——差额来自一处在途未提交改动删掉了 `Selector` 段末 `Model identity never selects posture.`（5 词）；那处若不落地则为 2106，仍在上限内。
  2. **术语 `合同` 对 `契约`。** 本工单词表写了 `合同`，但 `CONTEXT.md` 与四份孪生通篇用 `契约`。车道选了 `契约`。裁决：正确，工单词表有误，以 `CONTEXT.md` 为准。
- 架构师验收：读了英文四份与中文四份的完整 diff。中文按位翻译，术语与 `CONTEXT.md` 一致，未增删条目。
