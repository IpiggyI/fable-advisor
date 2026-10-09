# 0031 — `haiku-5-5` 替换 `haiku-4-5` 并新增 `explorer-md`；车道返工设上限；其他宿主的兜底条款

- **Status**: accepted（2026-10-09 椰椰的声明与决定；同日随 6.3.0 发布，说明书 `docs/manuals/6.3.0.html`）
- **Date**: 2026-10-09
- **影响范围**:
  - `plugin/skills/orchestration/routing-profile.md`：声明日期、锚点、排名表 Claude 的 `starter`、explorer 的 agent 文件映射、Claude Code 表的 explorer `mainstay` 格，Cursor 表的 explorer `mainstay` 与 `crux` 格。
  - 新增 `plugin/agents/explorer-md.md`。
  - `plugin/hooks/route-gate.py`：别名 `haiku` 的锚点。
  - `plugin/skills/orchestration/SKILL.md`："Harness mechanics"、执行侧契约一句、升级梯 R1、"Rework tickets"、新增 "Rework limit"。
  - `plugin/skills/orchestration/lanes-claude-code.md`：角色池文件列表、无 `effort:` 时的强度说明、路由行的拨盘说明与示例、路由门规则 2、"Rework tickets"。
  - `plugin/skills/orchestration/lanes-cursor.md`：Rework。
  - 测试：`tests/test_route_gate.py`、`tests/test_routing_profile_parity.py`。
  - `docs/zh/` 下对应孪生与新增的 `docs/zh/agents/explorer-md.md`、`README.md`、`CONTEXT.md`。
  - 版本 6.3.0：`docs/manuals/6.3.0.html` 与两个版本字段；ADR 0016、0030 的状态行。
- **关联**: 修订 [ADR 0016](./0016-effort-per-agent-file-role-pool.md) 决策 1 的文件集合（9 个文件增为 10 个），沿用其"每个（角色，强度）一份 agent 文件"；修订 [ADR 0030](./0030-global-plan-route-gate-reuse-window.md) 决策 7 的会话续用，给它加次数上限；沿用 [ADR 0010](./0010-dual-harness-single-source.md) 的单一来源，给第三类宿主补规则。

## 背景

椰椰 2026-10-09 提出三项改动：

1. `haiku-4-5` 升级为 `haiku-5-5`，在路由表里的位置不变，强度为 `haiku-5-5[medium*, high]`。
2. 车道返工设次数上限：首次派发加两次返工后问题依旧，继续复用这份上下文收益很低，甚至为负，此时重新派发。
3. 插件在 Claude Code 与 Cursor 之外的宿主（如 grok build）也要能用。椰椰草拟的三条：没有车道文件的宿主不沿用另一个宿主的 runner、回执门或型号钉选；角色只从该宿主实际提供的入口派发；入口启动不了的填充视为不可用，改路由并说明。

同日椰椰追加两项：Cursor 的路由去掉 `gpt-6-luna` 与 `haiku` 型号；删去 `lanes-claude-code.md` 开头"没有 subagent 启动成本"一句，理由是它不提供读者要据以行动的信息。

改动前的事实：`haiku-4-5` 没有强度维度，档案里裸写；explorer 只有 `explorer-h` 与 `explorer-xh` 两个文件，所以 `sonnet-5-5[medium]` 只能经 `explorer-h` 以 `high` 运行；升级梯 R1 与两份 lanes 文件允许契约缺口在同一会话里无限次修正后续用；`SKILL.md` 只为 Claude Code 与 Cursor 指了 lanes 文件。

## 决策

1. **`haiku-5-5[medium*, high]` 替换 `haiku-4-5`。** Claude Code 表的 explorer `mainstay` 格里位置不变；排名表 Claude 的 `starter` 改为 `haiku-5-5`；声明日期改为 2026-10-09；路由门的别名 `haiku` 解析为 `haiku-5-5`。
2. **新增 `explorer-md`（effort `medium`）。** 不加它，`haiku-5-5[medium]` 只能经 `explorer-h` 以 `high` 运行，声明的默认强度达不到，而路由门照样放行（`haiku-5-5[high]` 也在格里）。椰椰 2026-10-09 选了新增文件，`sonnet-5-5[medium]` 因此也按 `medium` 运行。agent 文件只在会话启动时加载，新文件在重启会话之后才能派发。
3. **返工上限。** 一张契约在同一个车道会话里最多三次尝试：首次派发加两次返工。返工票与修正契约各算一次；车道运行中的纠正（`SendMessage` 纠正）不算。第二次返工后问题依旧时，下一次尝试新开会话，即使仍在续用窗口之内；超过窗口续用的例外不解除上限。档位仍由升级梯决定：能力失败按升档处理；其他情况在同一档位、同一拨盘上新开会话。新开会话不算升档，失败计数不变。上限是文本规则，没有机械校验。
4. **其他宿主的兜底条款。** 写在 `SKILL.md`「Harness mechanics」，作为第三个条目，采用椰椰草拟的三条，另补两点（椰椰 2026-10-09 选定）：填充取自路由档案的 Claude Code 表，该宿主上没有入口的候选跳过并在披露中说明；路由按 `lanes-claude-code.md`「The route line」的格式写成文本，没有机械校验。派发同样指向角色所需的执行侧契约。`README.md` 的常见问题补一句。
5. **文本清理。** 档案锚点不再有无强度维度的 Claude 型号，所以删去 `lanes-claude-code.md` 中 `claude-haiku-4-5` 没有强度维度的说明、"`haiku-4-5` 不带方括号"一句，以及路由门规则 2 的"`haiku-4-5` 没有强度可比"；路由行示例改为 `haiku-5-5[medium]`。`CONTEXT.md` 拨盘词条的裸写示例改为 `composer-2.5-fast`。路由门保留裸写型号的处理逻辑，测试夹具仍保留一个裸写的 `haiku-4-5`，经 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 到达，以覆盖这一分支。`lanes-claude-code.md` 开头删去"没有 subagent 启动成本"。
6. **Cursor 表去掉 `gpt-6-luna` 与 `haiku-5-5`。** 只有 Cursor 表的 explorer 行含这两个型号：`mainstay` 格改为 `composer-2.5-fast › grok-4.7[medium*, high]`，`crux` 格改为 `grok-4.7[xhigh] › sonnet-5-5[medium*, high]`。worker 与 advisor 两行本来就不含它们。Claude Code 表不变。

## 未采纳

- **沿用 `sonnet-5-5[medium]` 的先例、不加文件。** 默认强度会静默变成 `high`。
- **给返工上限加机械校验。** runner 与路由门都不知道哪几次派发属于同一张契约；需要新的标识字段，收益不足以抵消改动面。
- **其他宿主沿用 codex runner。** 椰椰的草拟明确不沿用另一个宿主的 runner。

## 已知能力上限

- 返工上限靠主代理自觉计数；计数错了没有程序拦截。
- 其他宿主的路由只是文本，任何门都不校验；该宿主有没有可钉选型号的入口，由首次派发的结果决定。

## 复盘条件

- 出现第二个有固定入口的宿主（例如有了它自己的钉选机制），就给它写 lanes 文件，不再走兜底条款。
- 试用中出现第三次返工仍在同一会话的记录，说明文本规则没被遵守，再考虑机械校验。
