# 0009 — grok 车道去 wrapper 化：run-grok runner + 运行时模型目录

- **Status**: accepted
- **Date**: 2026-07-31
- **影响范围**: `scripts/run-grok.mjs`（新增）、`agents/grok-implementer.md`（删除）、`hooks/`（删 spawn 护栏、receipt gate 文案一般化）、`skills/orchestration/SKILL.md`、`README.md`
- **关联决策**: [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（复盘条件预埋"同法做 run-grok runner"）、[ADR 0003](./0003-codex-lane-param-policy.md)（fail-loud 参数律）

## 背景

ADR 0002 给 codex 去 wrapper 时记录了 grok 车道的同法路线，触发条件写的是"顶替事故"。本次以成本理由触发同一路线：wrapper 子代理每次派工承担 Claude 侧启动基线（ADR 0002 实测 ~25k token 量级），用户判断该固定开支不值得。去 wrapper 后所有外部 CLI 车道均由架构师经确定性 runner 直辖。

事实核验（2026-07-30/31，grok CLI 0.2.114，真实调用）：`--prompt-file`/`--output-format streaming-json`/`--permission-mode acceptEdits`/`--cwd` 可用；事件流 `{"type":"text"}` 承载最终消息、`{"type":"end"}` 带 `sessionId`/`usage`/`total_cost_usd`；`-s/--session-id` 可为新会话注入指定 UUID（比 codex 侧 15 个 extractor 猜字段更强的绑定）；`grok models` 打印登录态、默认模型与目录（当前仅 `grok-4.5`）；无 reasoning-effort / service_tier 类旋钮。

## 选项对比

| 方案 | 优点 | 缺点/风险 |
|------|------|------|
| 保留 wrapper agent | 有临场应变（flag 适配、把 spec 缺口转开放问题） | 每次派工 ~25k 启动基线；wrapper 自实现威胁类仍在，需 spawn 护栏维护 |
| **独立 run-grok.mjs 镜像（选定）** | 零风险不碰在跑的 codex 车道；两份拷贝低于"≥3 抽取"阈值 | receipt 结构改动要改两处（见复盘条件） |
| 抽共享核（run-lane.mjs） | 单一真相源 | 重构在跑的 codex 车道，回归风险换来的收益要到第三条车道才兑现 |
| 改用官方 Codex 插件替代 run-codex.mjs（顺带探测） | 免子代理直呼入口、后台 job 控制、上游维护 | 四缺口：无 spec 校验（model 透传、effort 无 `max`）；不执行 verification（codex 命令退出码被丢弃）；job 按时间戳命名且 SessionEnd 杀删（receipt gate 无从锚定）；task 输出无体积纪律。补齐等于重写 runner 还继承其漂移面（RPC 无版本预检、指导层钉在 GPT-5.3/5.4 世代） |

模型白名单：静态数组（ADR 0003 codex 律）vs **运行时目录（本次选定）**——白名单与默认模型取自 preflight 的 `grok models` 输出，模型换代（grok-4.6/4.7）零代码改动，typo 仍 fail-loud；目录解析失败按 `grok_unavailable` 大声失败，不静默透传。codex 侧无等价廉价目录查询，维持静态白名单不动。

## 决策

1. 新增 `scripts/run-grok.mjs`，镜像 run-codex.mjs 的结构与 receipt 语义：五段 spec + `model`/`timeout_sec`、未知键 fail-loud、同一 `.fable-advisor/{pending,receipts}` 目录与 pending 自清理、同一 error_class 谱系（codex_* → grok_*）。receipt 增记 `usage`/`total_cost_usd`/`stop_reason`（end 事件白给的成本审计）。
2. 删除 `agents/grok-implementer.md` 与 `hooks/block-named-cli-lane.py` 及其 PreToolUse 挂载：wrapper 消失即"wrapper 静默自实现"威胁类整体消失，receipt gate（盯主会话）成为唯一且足够的机制（ADR 0002 后续澄清）。fail-closed shell 兜底随之退役。
3. receipt gate 逻辑零改动（按 spec hash 匹配、不认 producer），仅文案去 codex 化。
4. Codex 插件不替代 run-codex.mjs；其 `/codex:adversarial-review`（schema 化裁决、read-only）收编为验收 Tier 3 的可选跨厂商 reviewer。
5. 版本 3.7.0。

## 实施代价

- runner 镜像带来的双份维护：receipt/验证逻辑改动须同步两个文件。
- 可发现性：grok 车道也从 agent 列表消失，依赖 orchestration skill 被加载（codex 已接受同款代价，ADR 0002）。
- wrapper 的临场应变消失：runner 刚性 fail-loud，spec 必须自足——本就是 spec contract 的要求。

## 复盘条件

- 出现第三条 CLI 车道，或 receipt 结构需要升版 → 抽共享 runner 核。
- `grok models` 输出格式或 streaming-json 事件格式漂移 → runner 大声失败（`grok_unavailable`/解析不出 end 事件），修一处解析器；若漂移频繁 → 评估改挂结构化接口。
- Codex 插件上游补齐 verification 执行 + 持久 receipt → 重估"不替代"结论。
- `codex exec --json` 事件格式漂移导致 run-codex 频繁失败 → 评估改走 `codex app-server` JSON-RPC（插件已验证该路径可行）。

## 备注

- 探测证据：插件 v1.0.5 解剖由只读 scout 完成，承重结论（无 verification 执行、SessionEnd 杀删 job、approval hardcoded `never`）经 file:line 抽查。
- 实施经 codex 车道 dogfood：spec 见 `.fable-advisor/pending/grok-lane-runner.json`。
- 成本口径更正存档：探测调用 usage 里的 ~19k input 是 grok 会话 xAI 侧系统提示基线（迁移前后不变），本决策省的是 Claude 侧 wrapper 启动基线（ADR 0002 记 ~25k）。
