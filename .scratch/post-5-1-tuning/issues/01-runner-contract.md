# 01: runner 契约——脏基线、标题、sol 白名单

**What to build:** 架构师在有未提交改动的工作树上以报告模式派 grok / codex 的 explorer，runner 跑完给出 `complete`，receipt 里 `dirty_baseline: true` 说明脏检测被跳过；每条车道会话在 codex / grok 会话列表里的首行是架构师写的一句标题；按路由档案派 `gpt-5.6-sol` 不再 `spec_invalid`。两条 runner 同改，行为在进程边界可验证。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 1、2、4、15 条。范围：两条 runner 脚本、runner 契约测试、`lanes-claude-code.md` 对应句与其中文孪生。

- [x] runner 在 spawn CLI 前跑一次 `git status --porcelain`；receipt 新增布尔字段 `dirty_baseline`，两条 runner、两种模式都记；开跑前 `git status` 失败记 `null` 并继续
- [x] 报告模式且 `dirty_baseline: true`：不判 `unexpected_diff`；`empty_report`、`complete` 判定不变；`changed_files` 照记观察值
- [x] 报告模式且 `dirty_baseline: false`、CLI 写了文件 → 仍是 `unexpected_diff`
- [x] implement 模式在脏工作树上的行为与 5.1.0 一致（`no_diff`、`git_status_failed` 语义不变）
- [x] spec 新增可选顶层键 `title`（非空字符串）；空串或非字符串 → `spec_invalid`、不 spawn
- [x] prompt 第一行是 `title` 原文（纯文本，无 Markdown 标记），空一行，再前言，再五部；省略 `title` 时第一行是 slug；`[fable-advisor] <slug>` 行退役，prompt 里零命中
- [x] codex 白名单加 `gpt-5.6-sol`，默认 effort `high`；sol 在建立会话前失败不回退（`model_used` 仍是 sol，`fallback_reason` 为 null）；astra → luna 回退不变
- [x] 契约测试覆盖以上每条；假 git 能区分开跑前与运行后两次调用
- [x] `lanes-claude-code.md`：spec 字段列表加 `title`；receipt 字段列表加 `dirty_baseline`；报告模式段写明脏基线语义；"Start from a clean working tree" 限定为 implement 模式；白名单与回退范围更新；中文孪生同提交
- [x] `python3 tests/test_runner_contract.py`、`python3 tests/test_zh_mirror.py` 绿

## Comments

### 2026-09-16 — 实施记录（grok 车道，`cursor-grok-4.6-xhigh`，requested, not confirmed）

- TDD：改 runner 前 10/17 红（7 个新用例失败），落地后 17/17 绿；`test_zh_mirror` 14/14。
- 验收：架构师复跑 17/17；读了两条 runner 的 diff（`dirty_baseline` 在 spawn 前采集、`spec_invalid` 路径下为 null；报告模式 `unexpected_diff` 加 `dirtyBaseline !== true` 条件；prompt 首行 `title ?? slug`；sol 进 `DEFAULT_EFFORTS`，回退条件仍限 `DEFAULT_MODEL`）；`git diff --stat` 只含五个契约文件。
- 报告模式 overlay 未动，归工单 02。
