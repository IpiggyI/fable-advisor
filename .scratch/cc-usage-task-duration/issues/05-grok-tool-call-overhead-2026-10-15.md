# 2026-10-15 的 Grok 车道每次工具调用多出约 3 秒

Status: needs-triage

## 问题

2026-10-15 cc-usage 的 14 次 Grok 车道运行里，每次工具调用从 `tool_started` 到 `tool_completed` 固定多出约 3.06 秒：开始后约 1.54 秒才出现 `permission_prompt`，执行完又隔约 1.55 秒才报 `tool_completed`。工具本身的执行时间只有 7 到 26 毫秒（`events.jsonl` 里 `tool_completed` 的 `duration_ms`，以及 `~/.grok/logs/unified.jsonl` 里 `shell.tool.exec_done` 的 `elapsed_ms`）。同一批工具调用串行承担这段开销。

14 次运行共 1418 次工具调用，开销合计约 72 分钟，占车道总时长 283 分钟的约 25%。三次超时的运行里分别约 8.5、18.7、10.9 分钟。

其他日期没有这个现象：2026-09-06 至 10-16 的全部 Grok 会话，开始到 `permission_prompt` 的中位间隔是 0.01 到 0.07 秒。当天 08:52（UTC）sub2api 项目的一个 Grok 会话也正常（0.04 秒）。

## 已排除

- runner 版本：10-15 与正常的 10-16 都用插件 6.4.0 的 `run-grok.mjs`。
- Grok 版本：10-15 是 1.0.50，正常的 10-10、10-12 也是 1.0.50；10-16 是 1.0.60。
- Notification 钩子 `~/.grok/hooks/snoretoast.sh`：当天只记录了 24 次跳过，单次运行约 0.07 秒。
- cc-usage 根目录的 `.ignore`：10-16 才创建。

## 待定

- 原因没有查到。下一步：用同一份 runner 对 cc-usage 派一份只读的小契约，看间隔是否复现；复现时对比 `~/.grok/config.toml`、权限规则与当天的 MCP 配置。不能复现就记为当天的偶发现象，并让回执或主会话在单次工具开销超过 1 秒时提示。
- 证据脚本：按 `events.jsonl` 里 `tool_started` 之后紧跟的 `permission_prompt` 计间隔，按天汇总。

## 处理记录

- 2026-10-18：6.6.0 没有处理本单，原因没有查到（ADR 0035「未采纳」）。
