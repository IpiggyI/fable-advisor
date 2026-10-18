# 主会话自设的总时长上限杀掉仍在干活的车道

Status: resolved

## 问题

`timeout_sec` 在 runner 里没有默认值，`lanes-claude-code.md` 也写明「不写就不限时」，静默截止（`idle_timeout_sec`，默认 600 秒）负责判卡死。这是 [lane-idle-deadline](../../lane-idle-deadline/spec.md) 的结论。

但 cc-usage 的主会话在 2026-10-15 仍给每份 Grok 契约写了 `timeout_sec`，取值 1200 到 3000 秒。C1、C3、C6 三次撞上 2700 或 3000 秒被 `SIGKILL`，被切时 `max_idle_ms` 为 112 到 151 秒，这段最长的静默就是一次自动压缩，其余时间车道一直在吐事件。

来源是 cc-usage 的项目记忆 `grok-lane-20-minute-session-wall.md`：「串行派活：`timeout_sec` 给 2400–2700」。插件文档没有阻止主会话照项目记忆设上限。

## 证据

- 回执：`cc-usage/.fable-advisor/receipts/` 中 `started_at` 为 2026-10-15 的 Grok 回执，`error_class: timeout` 的三张，字段 `timeout_sec`、`max_idle_ms`。
- 主会话记录 `f94fcdb6` 里写入的 `timeout_sec` 取值分布：1200 两次，1500 一次，1800 两次，2400 两次，2700 四次，3000 两次。
- 每次被杀的损失见 [问题报告 3.3 节](../problem-report.md)：被杀那一轮没有收尾检查，正在进行的调用作废，多一份续作契约。cc-usage 还会丢失那一回合的调用记录。

## 待定

- 插件侧怎么处理：编排文档里明确「串行车道不写 `timeout_sec`」；runner 在 `timeout_sec` 小于某个值时提示；或者回执把「被切时仍活跃」单独标出来。
- cc-usage 那条记忆是否要改。它属于 cc-usage，改动由椰椰安排。

## 处理记录

- 6.6.0 处理（ADR 0035 决策 3、6、7）：`runners.md` 规定 `timeout_sec` 只在当前请求给出时限时才写；长车道按运行中标记的 `session_id` 找会话记录判断是否失控；停车道先发 SIGINT。cc-usage 的记忆 `grok-lane-20-minute-session-wall.md` 已同步改写。
