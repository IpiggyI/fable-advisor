# 0028 — 车道运行中纠偏：claude 车道发消息，CLI 车道停 runner 后带会话重发

- **Status**: accepted（2026-10-01 椰椰选择"先实测，再补规则"）
- **Date**: 2026-10-01
- **影响范围**: `plugin/skills/orchestration/lanes-claude-code.md` 与其孪生 `docs/zh/skills/orchestration/lanes-claude-code.md`
- **关联**: 依赖 [ADR 0027](./0027-runner-running-marker-and-background-wait.md) 的运行中标记（提供 runner 的 pid）与后台等待；沿用 [ADR 0009](./0009-grok-lane-dewrapper-runner.md)「追记（2026-09-07）」的 `interrupted` 回执和 [ADR 0013](./0013-delivery-contract-not-build-instructions.md) 决策 7 的 `resume_session_id`。

## 背景

椰椰问：车道派出去后，主会话只能等它完成再看报告，中途做不了任何事，这样是否不好；Claude Code 自己的子代理是否也这样，主会话能否中途和它们沟通。

ADR 0027 之后，主会话在车道运行期间已经可以结束本轮、和椰椰对话或做独立工作。剩下的缺口是纠偏：车道运行期间发现合同有错，规则里没有写怎么改。

已核实的事实（2026-10-01，本会话）：

- **后台子代理能在运行中收到消息。** 派出一个无 `name` 的后台子代理（`haiku`），让它分 8 次调用 `sleep 8`；约 15 秒后按 `agentId` 发 `SendMessage`，内容是它事先不知道的口令。它在第 2 次调用返回后收到消息，写出口令文件（文件内容与时间戳已核对）并停止。平台回执写明消息"在下一次工具轮次送达"。
- **CLI 车道没有运行中的消息通道。** codex runner 把提示词写进 CLI 的标准输入后立即关闭（`run-codex.mjs` 的 `child.stdin.end(promptContents)`）；grok runner 不给 CLI 接标准输入，提示词只经文件交付一次。
- **`TaskStop` 先发 SIGTERM，约 1 到 2 秒后强制结束。** 一个收到 SIGTERM 后要 5 秒收尾的进程，只记录到第 1 秒的收尾。对真实 runner（假 grok CLI）调用 `TaskStop`：`interrupted` 回执带 session id 写出，CLI 进程已结束，运行中标记已删除，pending spec 保留。runner 收到 SIGTERM 后第一步就结束 CLI 进程树，所以 CLI 不会成为孤儿；`git status` 慢时，回执写入可能被截断。

## 决策

1. **claude 车道：发消息纠偏。** 按派发结果返回的 `agentId` 调用 `SendMessage`，不传 `name`（传 `name` 会让 frontmatter `effort:` 失效）。消息在子代理下一次调用工具时送达，正在执行的长工具调用要先返回。纠偏改变合同：只在 Objective、Constraint 或 Verification 某一项有错时发送，验收依据合同加这条消息。
2. **CLI 车道：停 runner，再带会话重发。** 用 `kill <pid>`（pid 取自运行中标记）只发 SIGTERM，让中断路径走完；`TaskStop` 可用，但可能截断回执写入。删除旧的 pending spec，排入修正后的合同，`resume_session_id` 指向那份 `interrupted` 回执的 session id。这与 SKILL.md "合同缺口得到修正后的合同、同一车道会话"一致。
3. **不新增运行中消息通道。** 不改 runner 的提示词交付方式。

## 后果

- 发现合同有错时，不必等车道跑完再返工。
- CLI 车道的纠偏代价是一次中断：被中断的一轮没有验证结果，恢复后由 runner 重新验证。
- 子代理正在前台运行 runner 时，消息要等 runner 退出才送达；这时纠偏走第 2 条，停 runner。
- `TaskStop` 的宽限时长只测了一次，没有平台文档依据。

## 未采纳

- **给 runner 加运行中消息通道**（例如保持 CLI 标准输入打开、或轮询一个消息文件后注入）。codex 与 grok 的无头模式都只在启动时接收提示词；中途注入需要两个 CLI 都支持，目前没有依据。
- **给子代理传 `name` 以便按名字发消息。** 会让 frontmatter `effort:` 失效；`agentId` 已足够。

## 复盘条件

- codex 或 grok 的无头模式提供运行中输入 → 重新评估第 3 条。
- `TaskStop` 停 runner 时出现无回执 → 规则改为只用 `kill <pid>`。
