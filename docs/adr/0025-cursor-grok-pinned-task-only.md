# 0025 — Cursor 下 Grok 只经钉型号的 Task 到达，不跑 grok runner

- **Status**: accepted（2026-09-29 椰椰声明："cursor 里不会跑 grok runner，grok 是 cursor 的本家模型"）
- **Date**: 2026-09-29
- **影响范围**: `plugin/skills/orchestration/lanes-cursor.md`（删去 grok runner 经 Shell 一段，grok lane 回到原生列表）；`plugin/skills/orchestration/routing-profile.md` 的 "Cursor candidates" 调用入口句与声明日期；两者的中文孪生；`docs/manuals/6.0.0.html`。并入未发布的 6.0.0。
- **关联**: 取代 [ADR 0018](./0018-post-5-1-tuning.md) 决策 9 中"grok runner 经 Shell 在 Cursor 可用"的部分；该决策的 cursor lane 部分不变。任务件 `.scratch/doc-healthcheck-6-0/review.md` 的 P02、R02（方向被本决定推翻）。

## 背景

5.2.0 起，`lanes-cursor.md` 写"grok runner 同样经 Shell 运行，尚未在 Cursor 实跑"；6.0.0 的路由档案据此把 Cursor 下 `grok-4.7` 的 `medium`、`high` 路由到经 Shell 的 grok runner，只有 `xhigh` 经钉型号的 `Task`。`SKILL.md` 车道表与 `lanes-cursor.md` 首段却把 Cursor 的 Grok 写成原生钉型号派发。6.0.0 发布前的审查清单把这记为同一事实的两种说法（P02），并建议以档案为准。

椰椰 2026-09-29 更正：Grok 是 Cursor 的本家模型，Cursor 里不跑 grok runner。

## 决策

1. Cursor 下 Grok 只经钉型号的 `Task` 到达，与 Claude 候选、Cursor 自家模型相同。当回合 allowlist 缺少某个强度变体时，按既有规则跳过该候选并披露。
2. `lanes-cursor.md` 删去 grok runner 经 Shell 一段；Cursor 下经 Shell 运行的只有 codex runner。
3. 路由档案 "Cursor candidates" 的调用入口句按决策 1 改写，表格取值不变，声明日期改为 2026-09-29。
4. Claude Code 下 Grok 仍经 grok runner 到达，不变。

## 未采纳

- 审查清单 P02 的原建议（把 `SKILL.md` 与 `lanes-cursor.md` 改成档案的说法，并在 Cursor 实跑一次 grok runner）：前提被椰椰的更正推翻。

## 复盘条件

- Cursor 的 allowlist 长期缺少档案所需的 Grok 强度变体，Grok 候选在 Cursor 频繁被跳过 → 重估档案 Cursor 部分的 Grok 格。
- Cursor 不再原生提供 Grok → 重议 Cursor 下 Grok 的到达方式。
