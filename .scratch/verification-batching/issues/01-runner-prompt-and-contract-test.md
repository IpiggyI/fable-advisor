# 01: runner 提示词——合同检查列表只由 runner 执行

**What to build:** 派给 CLI 车道的提示词不再要求车道在收尾时把合同检查列表再跑一遍；它改为告诉车道 runner 会在它退出后自己跑这份列表、退出码与输出进 receipt、非零退出仍算车道失败。合同没有检查命令时不注入这句话。契约测试证明这条分工：prompt 里退役原句零命中、新句按条件出现、runner 对同一列表恰好执行一次。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 1、6 条。范围：两条 runner 脚本的 `renderPrompt`、`tests/test_runner_contract.py`。

- [x] `run-grok.mjs` 与 `run-codex.mjs` 的 `renderPrompt`：`spec.verification` 非空时，`# Verification` 的 bash 代码块之后注入 `The runner runs these commands itself after you exit and records their exit codes and output in the receipt; a non-zero exit is your failure. Run what you need while you work; do not repeat this list as a closing step.`
- [x] `spec.verification` 为空时，`# Verification` 一节的渲染与改动前逐字符一致（空 bash 代码块），不注入上句
- [x] 退役原句 `Run the verification command and include its actual output in your final message.` 在两条 runner 中删除
- [x] `runVerification` 的调用点、排除分支（`preparation_stalled` / `timeout` / `idle_timeout` / `interrupted` 跳过核验）、receipt 字段、错误分类一律不动
- [x] 契约测试新增一个用例，两条 runner 都覆盖：非空 `verification` 时 prompt 含新句且不含退役原句；空 `verification`（报告模式）时 prompt 不含新句；用一条每次执行都追加一行的检查命令证明 runner 恰好执行一次（计数文件正好一行）
- [x] 新用例登记进 `CASES`
- [x] `python3 tests/test_runner_contract.py` 全绿

## Held for batch acceptance

- `python3 tests/test_zh_mirror.py` —— 2026-09-20 批次执行，15/15。
- `python3 tests/test_runner_lifecycle.py` —— 2026-09-20 批次执行，22 条 PASS 零 FAIL。
- 退役原句在 `plugin/`、`docs/zh/`、`README.md` 的全仓 grep —— 2026-09-20 批次执行，零命中。

## Comments

### 2026-09-20 — 实施记录（grok 车道，implement 模式，`effort: medium`，submitted, not observed）

- receipt `error_class: complete`；车道自验 `python3 tests/test_runner_contract.py` 退出码 0，19/19（基线 18/18，新增一个用例）。
- 落地：两条 runner 的 `renderPrompt` 改成 `sections` 数组加条件 `push`，两份实现逐字符相同（`diff` 比对为空）；新用例 `case_runner_owns_verification_list` 已登记进 `CASES`。
- 架构师验收：读了两条 `renderPrompt` 与新用例。计数断言 `counter.read_text().splitlines() == ["ran"]` 成立即证明 runner 执行一次——假 CLI 不执行核验命令，唯一执行者是 runner；文件不存在会直接抛错，所以漏跑也红。空列表分支用 `empty_fence` 断言渲染与改动前一致。
- 本工单之外、同一工作树里的在途改动（runner 生命周期、报告模式 `git_status_failed`）未被触碰。
