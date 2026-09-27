# 02：写档案前核对 grok 默认型号与 claude 别名

Status: ready-for-agent
Blocked by: 无

**要做什么：** 在写路由档案之前，确认两项档案文字依赖的事实：grok CLI 不传 `model` 时实际跑的型号，以及 claude 车道四个别名实际解析到的型号；证据来自会话记录。Cursor 的 slug 由用户查看。逐拨盘核对不在本票，在工单 05 发布后执行（U14 ⑦）。

**负责的要求：** `../spec.md` 第八节 PRB-1 至 PRB-3；第十二节 S2、S3。

**范围（Files）：** 只写本票 Comments。运行时产生的 `.fable-advisor/` 文件是工作流状态，不入库。

**执行方式：** 主代理执行，或派只读车道执行；每次用最小的只读提示（报告模式）。

## 实施必读

- `../spec.md`：第三节 N7；第八节"发布前的前置核对"、RP-7；第十二节；第十六节"已记录的假设"。
- `plugin/skills/orchestration/lanes-claude-code.md`：grok runner 的调用方式、spec 字段、报告模式。
- 证据位置：grok 会话目录 `~/.grok/sessions/<cwd 编码>/<会话 id>/` 中的 `model_id`（会话 id 取自回执的 `grok_session_id`）；claude 子代理记录（`~/.claude*/projects/<项目>/<会话 id>/subagents/*.jsonl`）中的 `message.model`。

## 验收

- [ ] grok：不传 `model` 跑一次，观测表列出 `grok_session_id` 与会话记录中的 `model_id`；不是 `grok-4.7` 时，传 `model: grok-4.7` 再跑一次并记录；按 `../spec.md` N11 写明结论：默认是 `grok-4.7` 时档案、车道文档与 README 写"跟随 CLI 默认，当前 `grok-4.7`"；不是时写"spec 传 `model: grok-4.7`"。
- [ ] claude：别名 `haiku`、`sonnet`、`opus`、`fable` 各经本插件 agent 文件派发一次；观测表列出 `message.model`；注明强度不可观测。
- [ ] 任一项不符预期时按 S2、S3 停下回报，不改表、不换型号。
- [ ] Cursor（用户执行）：用户回报当回合 `allowlist` 中 `grok-4.7` 的 `xhigh`、`opus-5-5` 各强度、`fable-5-1` 各强度、`sonnet-5`、`haiku-4-5`、`composer-2.5-fast` 的 slug 有无；回报前此项标为"未核实"，不阻塞后续工单。

## Held for batch acceptance

- 无。

## Comments

### 2026-09-27 — PRB-1、PRB-2 观测（主代理）

PRB-1：用工作树的 `plugin/scripts/run-grok.mjs`，报告模式，不传 `model`、不传 `effort`，最小任务（读 `CONTEXT.md` 首行，一次工具调用）。回执 `error_class: complete`，`model_requested`、`model_used` 均为 `null`（省略 `model` 时的现行语义）。

| 项 | 值 | 来源 |
|---|---|---|
| `grok_session_id` | `c2144cf3-51b8-45a7-81a9-a8bc522d73a4` | 回执 |
| 回合型号 | `grok-4.7` | `~/.grok/sessions/%2Fhome%2Fhyy%2Fdevelop%2Fpersonal%2FGitHub%2Ffable-advisor/c2144cf3-…/events.jsonl` 的 `turn_started.model_id` |
| 逐条消息型号 | `grok-4.7-build`（`model_fingerprint` `fp_5719f1aec35dd73c`） | 同目录 `chat_history.jsonl` 的 assistant 记录 |
| 强度 | `high`（未传 `effort` 时的 CLI 默认） | 同目录记录的 `reasoning_effort` |
| CLI 目录 | `Default model: grok-4.7`；另列 `grok-4.7-build-fast`、`grok-4.6`、`grok-4.5`、`grok-s2a` | `grok models`（2026-09-27） |

结论：CLI 默认型号是 `grok-4.7`，不需要第二次传 `model` 的运行。按 N11，档案、车道文档与 README 写"省略 `model`，跟随 CLI 默认，当前 `grok-4.7`"。`chat_history.jsonl` 里的 `grok-4.7-build` 是服务端的构建名，目录里没有同名条目（只有 `grok-4.7-build-fast`），REL-4 以 `events.jsonl` 的 `turn_started.model_id` 为型号证据，并照录消息级构建名。S3 不触发。

PRB-2：`fable-advisor:explorer-h`，不传 `name`，每次一个别名，最小任务含一次 `Read`。证据是本会话 `~/.claude-a/projects/-home-hyy-develop-personal-GitHub-fable-advisor/8763056e-…/subagents/agent-*.jsonl` 中全部 assistant 记录的 `message.model` 集合。

| 别名 | 子代理记录 | `message.model` 集合 | 期望 | 结果 |
|---|---|---|---|---|
| `haiku` | `agent-a419950c…` | `claude-haiku-4-5-20251001` | 同 | 符合 |
| `sonnet` | `agent-ad9e49f7…` | `claude-sonnet-5` | 同 | 符合 |
| `opus` | `agent-a8b3ac2e…` | `claude-opus-5-5` | 同 | 符合 |
| `fable` | `agent-a4fe6d28…` | 只有 `<synthetic>`（错误记录） | `claude-fable-5-1` | 别名解析正确，派发失败 |

`fable` 的失败信息：`Fable 5.1 requires usage credits … (error type rate_limit, HTTP 429 …, model sent to the API: claude-fable-5-1)`。别名解析到的型号就是表中型号，所以 S2 不触发；失败原因是本会话所用的配置目录（`~/.claude-a`）对应账号未开通 usage credits。这是可用性问题：advisor 行的 `fable-5-1` 候选在该配置下派发会失败，按 TR-5 换候选。REL-4 的 `fable` 拨盘需要在开通 credits 的配置下执行，否则按 S1 回报。强度可以观测，与规格 REL-4 的"强度不可观测"不同：`sonnet`、`opus` 两次的 assistant 记录带 `"effort":"high"`，与 `explorer-h` 文件头一致；`haiku` 的记录没有 `effort` 字段（haiku 无强度维度，与车道文档一致）。REL-4 因此可以同时记录 claude 拨盘的强度。

PRB-3：已请椰椰在 Cursor 查看；回报前标为未核实。
