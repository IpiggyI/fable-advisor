# Fable Advisor — 姿态、角色、填充表

本文件是仓外活体的中文备份，不是活体。Claude Code 与 grok build 加载的是英文正典 `user-rules/claude-fable-advisor.md`（活体路径 `~/.claude/rules/fable-advisor.md`）。

任意模型都可以当主代理。怎么干活由姿态决定，不由型号身份决定。编排准则在 `fable-advisor:orchestration` 里；本文件只放用户侧输入。日期 2026-09-11；锚定 Grok 4.6 / GPT-6 Astra / GPT-5.6 Luna / Opus 5 / Fable 5.1。其中任一模型换代时，重估对应条目。

## 姿态

两种姿态只差一条规则：主代理能不能亲手改交付物。两种姿态都可以派 explorer / worker / advisor。

- **编排**：写交付契约、派 worker、凭证据验收；不亲手改交付物（产物类别见该仓库的 `AGENTS.md`）。协调件可以直接写。
- **实现**：可以亲手改交付物；仍可按需要派 explorer、worker、advisor。
- 选择器，按优先级：我在本会话的声明（「直接改」→ 实现；「派活 / 编排」→ 编排）→ 提示词里的上层指示 → 默认：有上游任务件（`.scratch/<feature>/issues/`、spec、Trellis task）则编排；没有则实现。
- 姿态相对一次派发：车道对自己的契约是实现，对自己再派出的子代理是编排。委派深度不限。

## 决策类型门（任何主代理、任一档位）

到这些点咨询 advisor（`fable-advisor`，决策形状）：架构、数据迁移、API 形状、重构策略；推翻既定方案；改公共接口或跨模块依赖；放宽验收标准；同一问题两次失败。宣告多步交付物完成前，用 advisor 的验收形状（契约 + diff + receipt）。没有其他必问点；不逐 diff 过审。

## 填充表 — (角色, 档位) → 候选，优者在前

候选是经某条车道到达的拨盘（型号[effort]）。准则第一段选定格子；本表只给格子里的顺序。

| 格子 | 填充 |
|---|---|
| explorer @ light | grok-4.6[medium]，经 grok 车道 `report` 模式 › gpt-5.6-luna[high]，经 codex 车道 `report` 模式 › 宿主内建 Explore |
| explorer @ standard / senior | 与同档位 worker 填充相同，走 `report` 模式 |
| worker @ light | grok-4.6[medium] › gpt-5.6-luna[high]（Luna 当 worker 只在我声明时，或任务简单且就要 GPT 家族） |
| worker @ standard | grok-4.6[xhigh] › claude-opus-5[high]，经 claude 车道（`worker` 代理） |
| worker @ senior | gpt-6-astra[medium]；特别难的活升到 [high]。接管契约 = 原契约 + 前次报告 + receipt，新会话 |
| advisor（默认 senior） | gpt-6-astra[high]，经 codex 车道 `report` 模式（Claude Code 也可用 `/codex:adversarial-review`）› claude-fable-5-1[high]，经 `fable-advisor` 代理。任一档位都可派；advisor 的权威来自它读到的代码 |

说明：角色默认 effort 为 worker medium、explorer medium、advisor high；角色没写时用该车道默认值。

## 帕累托输入（声明于 2026-09-06）

- 速度（快到慢）：grok-4.6 > fable5.1 ≈ astra ≈ opus5 > Luna-max。
- 价格（便宜到贵）：Luna-max < grok-4.6 << opus5 ≤ astra ≤ fable5.1。
- 能力：Luna-max < grok-4.6 ≤ opus5 < astra ≈ fable5.1。
- 专长：前端偏 claude 车道；后端偏 codex 车道。反例积累后重估。
- 易变状态（额度余量、工期）只在开工时由我口头声明，仅当次会话有效，不落盘。没有声明 → 走该格最便宜且胜任的默认拨盘。
- handoff 车道只有我按任务或按会话声明后才进候选。
- 低置信逃生口：见 `fable-advisor:orchestration` 的 `User routing profile` 节。
