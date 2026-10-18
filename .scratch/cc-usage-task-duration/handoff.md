# 交接：cc-usage 任务耗时（2026-10-18）

先读 [problem-report.md](problem-report.md)。本文件只记状态、怎么复查、注意事项。

## 状态

- 调查完成。问题单 01、03、04 由 6.6.0 处理（ADR 0035），02、05 未处理。
- 本仓库的问题单 5 张，01、03、04 为 `resolved`，02、05 为 `needs-triage`：
  1. [01](issues/01-self-set-wall-clock-kills-live-lanes.md) 主会话自设的总时长上限杀掉仍在干活的车道。
  2. [02](issues/02-long-lane-runs.md) 超时的车道一轮要走 60 到 120 多步模型调用。
  3. [03](issues/03-main-session-full-suite-reruns.md) 主会话重复跑全量测试。
  4. [04](issues/04-serial-lanes.md) 车道全部串行。
  5. [05](issues/05-grok-tool-call-overhead-2026-10-15.md) 2026-10-15 的 Grok 车道每次工具调用多出约 3 秒。
- 属于 cc-usage 仓库的问题列在问题报告第 5 节，不在这里开单。
- 还没核实的线索列在问题报告第 6 节，每条带探针。查实一条，就补进问题报告，需要修的另开问题单。

## 复查

脚本在 [tools/](tools/)，都只读。会话记录在 `~/.claude/projects/-home-hyy-develop-personal-GitHub-cc-usage/`，参数是会话编号。

| 脚本 | 用途 | 命令 |
|---|---|---|
| `timeline.py` | 主会话逐秒分类，并把标注写到 `/tmp/lab-<编号前 8 位>.json` | `python3 -I tools/timeline.py <会话编号>` |
| `cover.ts` | 用 cc-usage 库的调用区间算覆盖率，按上一步的标注交叉统计 | `bun tools/cover.ts ~/.cc-usage/usage.sqlite /tmp/lab-<前 8 位>.json <主会话编号> <车道会话编号…>` |
| `full.py` | 列出主会话与子代理里每次全量测试的时刻、耗时、结果和前一句说明 | `python3 -I tools/full.py <会话编号>` |
| `lanes.py` | 列出时间窗内的回执，拆车道的模型时间与工具时间 | `python3 -I tools/lanes.py`（时间窗与回执目录写在文件开头） |
| `dbq.ts` | 单个会话在 cc-usage 库里的调用数、并集时长和跨度 | `bun tools/dbq.ts ~/.cc-usage/usage.sqlite <会话编号…>` |
| `analyze.py` | 上面几个脚本共用的解析函数 | 不单独运行 |

2026-10-18 那次全量测试的逐用例计时在 [evidence/full-suite-2026-10-18.junit.xml](evidence/full-suite-2026-10-18.junit.xml)，问题报告第 5 节的慢文件数字取自它。

## 注意

- `cover.ts` 要把车道会话编号一起传进去，覆盖率才和问题报告一致。只传主会话时，S2 只有 22%。Grok 会话编号取回执的 `grok_session_id`，Codex 取 `codex_session_id`。
- `full.py` 只认无参数的 `bun run test`。S2 21:43 那次 `bun run test test/` 是人工从记录里找到的，所以脚本列出 10 次，问题报告记为 11 次。
- `analyze.py` 的命令分类是启发式的：写规格的 heredoc 里出现 `bun run test` 也会被归成测试。计次以 `full.py` 的输出和测试输出里的「Ran N tests across M files」为准。
- cc-usage 库正在被应用写入，只能只读打开。全量测试不要和 cc-usage 的采集同步同时跑。
