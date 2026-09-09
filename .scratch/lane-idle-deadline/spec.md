# 车道静默截止：用 `max_idle_ms` 分布取代总墙钟

Status: ready-for-agent

## Problem Statement

一次车道派发压着三个互相独立、默认值都不超过 600 秒的时钟：runner 自己的 `timeout_sec`、宿主 Bash 工具的 `timeout`、`TaskOutput` 的 `timeout`。其中只有第一个会杀掉真正在干活的车道——它是总墙钟，不看车道是否还在产出，到点就砍，而且超时路径跳过验证，回执因此不带任何验证证据。

runner 里还有第二个瞎墙钟：`PREPARATION_TIMEOUT_MS` 固定 30 秒，续跑一个大会话时同样会砍掉正在装载的车道。

4.1.0 只落了测量与中断兜底（`max_idle_ms` 诊断、`SIGTERM`/`SIGINT` 写 `interrupted` 回执），没有改超时语义。默认 600 秒仍在原地。

## Solution

把总墙钟换成静默截止：以「最后一个事件之后 N 秒没有新事件」判定卡死，而不是「总共跑了多久」。一直在吐事件的车道跑多久等多久；真卡住的车道在最后一个事件之后 N 秒被砍。`timeout_sec` 降级为可选的绝对上限，默认不设。续跑的首个事件同样由静默截止管，不再由 30 秒准备窗口管。

改动面与 4.1.0 相同：两条 runner（`plugin/scripts/run-grok.mjs`、`run-codex.mjs`）加 `tests/test_runner_contract.py`，外加 `plugin/skills/orchestration/lanes-claude-code.md` 及其中文孪生。事件流的逐行观测点已经存在，静默截止复用它。

## 取值依据（2026-09-09 取得）

全库回执里带 `max_idle_ms` 且非空的样本 19 份，全部来自 cc-usage 2026-09-08 那批 grok 串行派发：

- 相邻事件最大间隔：min 33 s，p50 66 s，p90 121 s，max 134 s。
- 这些跑的总时长 641–1725 s，且按前言各自跑过 typecheck 与全量测试。原先「验证阶段 CLI 是否完全不吐事件」这个空白由此填上：不会，最长的静默段仍是 134 s。
- 两次 `timeout` 回执被砍时的 `max_idle_ms` 是 76.6 s 与 43.4 s——车道在吐事件，墙钟砍的是活的。
- 18 次 `complete` 里 15 次总时长超过 1080 s，最长 1725 s。墙钟与活性不相关。

样本只覆盖 grok 车道；codex 车道零样本，N 对它是按同一量级外推，不是实测。

**定值：N = 600 秒**（观测上界 134 s 的约 4.5 倍余量）。砍错一条活车道要赔掉 20 分钟以上的实现；多等 8 分钟才确认一条真死车道，代价小得多。数字与旧默认值相同，但语义从「总时长」变成「静默时长」。

## Comments

### 2026-09-08 — 4.1.0 之后同型事故（cc-usage）

一手回执：`/home/hyy/develop/personal/GitHub/cc-usage/.fable-advisor/receipts/209641528c3a8864f5e7ebf7a85daa896aeccf0b42c17724561db0cd358d21ab.json`

- pending 设 `timeout_sec: 1080`；前台 Bash 超时 20 分钟（大于 runner）。
- `started_at`/`finished_at` 相隔 1083.9 秒，`error_class: timeout`，`verification: []`。
- `max_idle_ms: 76627`（约 77 秒）≪ 墙钟。车道在吐事件，不是卡死。
- `grok_final_message` 末句：「接着跑契约要求的 typecheck 和全量测试。」实现已落地，切在车道自己开跑契约验证之前。
- 同会话续跑回执 `1739f328…`：`resumed_from` 同一 `grok_session_id`，32.7 秒、`max_idle_ms: null`、`error_class: preparation_stalled`。

同类历史：rustpad `96f6675b`（默认 600 秒，同样切在「接着跑契约里的校验」）；cc-usage 另有约 15 条 `timeout`，墙钟多落在 1080–1140 秒附近。调大 `timeout_sec` 是权宜，不是语义修复。

连带、且不依赖 N 的一个洞（与静默截止正交，可另立票）：前言要求车道自己跑契约命令，runner 在 CLI 退出后再跑一遍。墙钟预算被车道侧验证吃掉；被砍时 runner 又因 `timeout` 跳过自己的验证。

### 2026-09-09 — 更正上一条对续跑失败的归因

上一条把 `preparation_stalled` 归给「SIGKILL 之后会话不可恢复」。查证后不成立：

- 被杀会话在磁盘上完好：`~/.grok/sessions/%2F…%2Fcc-usage/68e7fa5c-0daa-4748-a51f-5dc92b453209/` 共 3.0 MB，`chat_history.jsonl`、`events.jsonl`、`updates.jsonl` 都写到被杀前一秒。
- 全库 11 份带 `resumed_from` 的回执里，父跑是 `timeout`（即被 SIGKILL）的有 5 份，其中 3 份续跑 `complete`。被杀会话可续跑。
- 两份失败的续跑都停在 32.7 秒左右，正是 30 秒 `PREPARATION_TIMEOUT_MS` 加开销。续跑要重放 3 MB 会话历史，30 秒的固定准备窗口本身就是第二个瞎墙钟。

因此续跑失败与静默截止是同一类缺陷，并入本票，不另立票。

## 决策来源

[ADR 0009 追记（2026-09-07）](../../docs/adr/0009-grok-lane-dewrapper-runner.md)。三个时钟、孤儿进程探针、「本轮只测量不改超时语义」的理由都在那里，此处只排队，不复述。
