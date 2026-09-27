# 01：codex runner 换用 gpt-6 白名单，取消自动换模型

Status: ready-for-agent
Blocked by: 无

**要做什么：** 主代理按新表派 `gpt-6-luna`、`gpt-6-sol` 时 codex runner 接受；派 `gpt-5.6-*` 时判 `spec_invalid`；astra 在会话建立前失败时 runner 只报告失败，不换成任何其他型号，回执结构不变；README 里 codex 车道的描述与之一致。

**负责的要求：** `../spec.md` 第八节 RN-1 至 RN-6，DOC-5 中 codex 车道行与安装说明的部分；第九节第 1、2 项。

**范围（Files）：** `plugin/scripts/run-codex.mjs`、`tests/test_runner_contract.py`、`tests/test_runner_lifecycle.py`、`tests/test_runner_lifecycle_windows.cjs`、`plugin/skills/orchestration/lanes-claude-code.md` 的 codex 段与回执字段说明、`docs/zh/skills/orchestration/lanes-claude-code.md` 的对应段、`README.md` 中 codex 车道表格行与 codex 安装说明（型号、默认强度、回退三处）。`plugin/scripts/run-grok.mjs` 只读（它已恒写 `fallback_reason: null`），不改。

**执行方式：** 交付物，编排姿态下经 worker。

## 实施必读

- `../spec.md`：第一节"权威与冲突"、第三节 U11、N2、D13、第八节"codex runner"、第九节第 1、2 项、第十四节前四条。
- `plugin/scripts/run-codex.mjs`（基线）：`DEFAULT_EFFORTS`、`VALID_MODELS`、`shouldFallback` 分支。
- `tests/test_runner_contract.py`（基线）：现有回退用例 `case_codex_single_hop_fallback`、`case_codex_fallback_boundaries`，报告模式场景里的回退断言，正常调用中的旧型号输入（`gpt-5.6-luna`、`gpt-5.6-sol`），拒绝用例（Terra）。
- `tests/test_runner_lifecycle.py`、`tests/test_runner_lifecycle_windows.cjs`（基线）：旧型号输入。
- `plugin/skills/orchestration/lanes-claude-code.md`（基线）：codex 段的 `model`、`effort` 条目，"Fallback."段，回执字段列表中的 `fallback_reason`。
- `README.md`（基线）：codex 车道表格行（"currently GPT-6 Astra default, GPT-5.6 Luna, and GPT-5.6 Sol"）与 codex 安装说明（型号清单、默认强度、"Only astra falls back (to luna)."）。

溯源（不约束）：`.agent-discuss/tiers-and-consult-iteration/gpt/003.md`（旧型号依赖清单，静态检索）。

## 验收

- [ ] `gpt-6-luna`、`gpt-6-sol` 被接受；省略强度时提交 luna → `max`、sol → `high`；astra 默认不变。
- [ ] `gpt-5.6-luna`、`gpt-5.6-sol` 判 `spec_invalid` 且不启动子进程（新增或改写用例覆盖）。
- [ ] astra 会话建立前失败（`preparation_stalled`；`codex_failed` 且无会话 id）各一例：假 CLI 只被调用一次；回执错误类为该失败；`model_requested`、`model_used` 都是 `gpt-6-astra`；`fallback_reason` 为 `null`。原回退用例与报告模式回退断言改写为此行为，不是删除。
- [ ] 回执仍含 `fallback_reason` 键（两条 runner）。
- [ ] 生命周期测试的型号输入已迁移，且用例走到进程阶段（断言或输出能证明不是在参数校验处退出）。
- [ ] `python3 tests/test_runner_contract.py`、`python3 tests/test_runner_lifecycle.py` 退出 0；`node tests/test_runner_lifecycle_windows.cjs` 在本机可运行时退出 0，不可运行时写明原因。
- [ ] 能证明测试会因意图错误而失败：把 runner 临时恢复为自动换型号时，改写后的用例失败（记录一次红的输出，然后恢复）。
- [ ] `lanes-claude-code.md` codex 段符合 RN-6，中文孪生同步；`python3 tests/test_zh_mirror.py` 退出 0。
- [ ] README：codex 车道行与安装说明列出 `gpt-6-astra`（默认）、`gpt-6-luna`、`gpt-6-sol` 与 RN-2 的默认强度；"Only astra falls back (to luna)"不存在；README 的档位段落与升级段不在本票范围，留给工单 03。
- [ ] 本票文件内 `gpt-5.6-` 只出现在拒绝用例与 README 的历史升级描述中；`retries once on luna`、`falls back (to luna)` 零命中。

## Held for batch acceptance

- 全仓文字扫描（`../spec.md` 第九节第 5 项）——工单 05 执行。2026-09-27 已执行：命中只剩允许的例外（见工单 05 Comments）。通过。

## Comments

### 2026-09-27 — 实施与验收（主代理）

分两份契约：
- runner、测试、README 的 codex 部分：codex 车道 `gpt-5.6-sol[high]`（旧档案 worker standard 格，后端偏 codex 车道；经已安装 5.2.0 缓存里的 runner），会话 `01a0e0e0-a9a4-71d2-9d1c-ea0312f69e9e`，回执 `complete`。
- `lanes-claude-code.md` codex 段与中文孪生：技能散文，同模派发（`worker-h`，`model: opus`），与工单 03 的散文同一份契约完成。

验收证据（runner 执行一次，回执内输出）：
- `python3 tests/test_runner_contract.py`：`19/19 passed, 0 failed`，退出 0。
- `python3 tests/test_runner_lifecycle.py`：退出 0，22 行 `PASS`；迁移后的 codex 用例新增断言 `model_used == gpt-6-luna`（`kill_failed` 为 `gpt-6-astra`），证明走到了进程阶段而不是在参数校验处退出。
- `node tests/test_runner_lifecycle_windows.cjs`：退出 0，输出 `SKIP native Windows process tests: requires Windows Node`——本机不是原生 Windows，原生 Windows 行为未验证；型号已迁移，并加了同样的 `model_used` 断言。
- 红灯证明（车道报告）：临时恢复 astra → luna 自动换型号后，`16/19 passed, 3 failed`，失败为 `report and implement modes`、`codex single-hop fallback`、`codex fallback boundaries`；恢复后 runner SHA-256 与实验前一致（`bfde32b9…`）。
- 退役型号：`gpt-5.6-luna`、`gpt-5.6-sol` 判 `spec_invalid` 且调用日志不存在（未启动子进程）；Terra 拒绝用例保留。
- 两个会话前失败类各一例（`codex_failed` 无会话 id；`preparation_stalled`）：只调用一次，`model_requested`、`model_used` 都是 `gpt-6-astra`，`fallback_reason` 为 `null`。
- 扫描：`retries once on luna`、`falls back (to luna)` 零命中；`gpt-5.6-` 只在拒绝用例与 README 历史升级描述中。
- Tier 2 抽查 `run-codex.mjs` diff：`DEFAULT_EFFORTS` 三项为 `gpt-6-*`；`shouldFallback` 分支整段删除，主流程只调用一次 `executeCodex`；`state.model`、`modelUsed`、`effort` 在第 718–721 行由 spec 赋值；`fallback_reason` 由初始状态恒写 `null`。

实现选择：两个原回退用例改写后沿用旧函数名，后在工单 03 的 README 契约里改名为 `case_codex_no_model_switch`、`case_codex_no_model_switch_boundaries`（显示名 `codex no model switch`、`codex no model switch boundaries`），改名后 `19/19` 通过。

结论：本票验收项全部满足（Windows 原生运行除外，已注明）。
