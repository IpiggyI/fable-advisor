# 车道全部串行，等车道是最大的一类时间

Status: resolved

## 问题

S1 的 14 次 Grok 运行互不重叠，合计约 283 分钟。S2 的 14 次 Codex 运行也互不重叠，合计约 139 分钟。两次任务里，等车道都是最大的一类时间。

cc-usage 的项目记忆 `cc-usage-app-ts-is-the-parallelism-chokepoint.md` 规定：契约有共同文件时不并发，没有共同文件时各用独立工作目录并发。这次是否每一对相邻契约都有共同文件，没有核实。

## 证据

- 回执的 `started_at` 与 `lane_finished_at`，由 [tools/lanes.py](../tools/lanes.py) 列出。

## 待定

- 先跑问题报告第 6 节第 2 条探针：比较相邻契约的 Files 列表。
- 如果存在可并发而没并发的契约，插件侧可以在派发前提示「这份契约与正在运行的车道没有共同文件」。

## 处理记录

- 6.6.0 处理（ADR 0035 决策 4）：实施契约的 Files 写具体路径；串行要在计划里写理由。探针结果见问题报告第 7 节第 1 条。cc-usage 的记忆 `cc-usage-app-ts-is-the-parallelism-chokepoint.md` 已同步改写。并发 Grok 车道约 20 分钟硬切的说法仍未复核。
