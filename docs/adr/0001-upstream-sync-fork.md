# 0001 — 上游同步须保留 fork 加固提交

- **Status**: accepted
- **Date**: 2026-07-08（最后更新 2026-07-12）
- **Migrated**: 2026-07-25，从 `.memory/decisions/upstream-sync-fork.md` 迁入（见 [ADR 0004](./0004-adr-store-in-repo.md)）

## 决策

本仓库是 `DannyMac180/fable-advisor` 的 fork（origin → `git@github.com:IpiggyI/fable-advisor.git`），领先上游**四个**自有提交（SHA 随每次 rebase 变化，2026-07-11 同步后为）：**`40c0fc7`**（原 `c4f4f7a`/`4a9de29`；codex 通道加固：`agents/codex-implementer.md` 的 SESSION 证据 + 禁自我兜底；`skills/orchestration/SKILL.md` 的通道核验 + Subagent lifecycle 小节）、**`2063b55`**（原 `32b0e0c`；codex 推理档位 floor=high / 复杂升 xhigh，详见下方「fork 对上游的额外偏离」）与 **`e8e1c9d`**（2026-07-11 新增；恢复 `agents/implementer.md` 为 in-house 兜底 lane，详见下方）与 **`43144a8`**（2026-07-12 新增；CLI lane 无名派生护栏，详见下方「额外偏离」与 [07-12 任务](../../.memory/tasks/2026-07/07-12-cli-lane-spawn-guardrail/what.md)）。

**同步上游时（rebase/merge upstream）必须保留该提交的改动，不得被上游版本覆盖。** 若上游后续自行实现了等价机制，再删除本地版本并记录于此。

## 部署链（三份拷贝，容易漏）

1. 本地 clone（本仓库）— 编辑处
2. fork 远端 `IpiggyI/fable-advisor` — 持久化处
3. **生效处**：`~/.claude/plugins/cache/fable-advisor/fable-advisor/3.1.0/`（换源重装后目录名已跟版本走；旧 `2.1.0` 目录为残留）— 每次手工改动后需覆盖此目录，或经换源后 `/plugin` 重装

## 部署源（2026-07-12：已切 fork，风险消除）

marketplace 源已切到 `IpiggyI/fable-advisor`（`known_marketplaces.json` 的 `fable-advisor.source.repo` = `IpiggyI/fable-advisor`）。`/plugin` 更新此后从 fork 拉取，不再被上游覆盖——原「遗留风险」已消除。当时的换源命令（留档）：

```
/plugin marketplace remove fable-advisor
/plugin marketplace add IpiggyI/fable-advisor
/plugin install fable-advisor@fable-advisor
```

## 原因

无上游推送权限；先自用验证加固效果，成熟后向上游提 PR（届时若合并，本 fork 可回归纯镜像）。

详细背景见 [任务归档](../../.memory/tasks/2026-07/07-08-harden-codex-lane/what.md)。

## 同步记录

- **2026-07-12**：确认 marketplace 源已切至 `IpiggyI/fable-advisor`（`known_marketplaces.json` 的 `fable-advisor.source.repo`），上方原「遗留风险」消除——`/plugin` 更新此后从 fork 拉取。同日新增 fork 提交 `43144a8`（CLI lane 无名派生护栏，见「额外偏离」与 [07-12 任务](../../.memory/tasks/2026-07/07-12-cli-lane-spawn-guardrail/what.md)），已推 `origin/main` 并覆盖 cache 3.1.0。
- **2026-07-11**：同步上游 `main` → `c5a1bf5`（上游唯一增量：`c5a1bf5 Update README.md`，仅改 Attention Heads 订阅文案一句，零冲突）。两个 fork 加固提交 rebase 重放：`4a9de29→40c0fc7`、`32b0e0c→2063b55`。**同一会话内又新增第三个 fork 提交 `e8e1c9d`**：恢复 `agents/implementer.md` 为 in-house 兜底 lane（Sonnet 默认 / Opus 升级，与 architect 同族、无跨厂复审），并把 `skills/orchestration/SKILL.md` lanes 表 + 「both CLI unavailable」规则、README lane 表/Requirements/v2-升级 FAQ、`plugin.json`/`marketplace.json` 描述指向它——目的是让插件在未装 Grok/Codex CLI 时仍自洽可用。已 force-with-lease 推 `origin/main`（`32b0e0c...e8e1c9d`）。backup 分支 `backup/main-20260711-223840`。marketplace 源仍指 `DannyMac180`（`known_marketplaces.json`）+ marketplaces 克隆 remote 也是上游——遗留风险未消（**2026-07-12 已切源解决，见上方「部署源」**）。
- **2026-07-10**：同步上游 `main` → `b3b50a9`（上游 v3.0.0 用 Grok 4.5 换掉 Sonnet implementer lane + codex 升 GPT-5.6 Sol + README）。fork 加固 `c4f4f7a` rebase 重放为 `4a9de29`（纯新增 15 行）。唯一冲突 `skills/orchestration/SKILL.md`：上游**未**自带等价加固（无 channel authenticity / SESSION 核验 / Subagent lifecycle），故按本决策**保留 fork 加固**，仅取上游把 "An implementer" 泛化为 "A lane" 的措辞。`agents/codex-implementer.md` 自动合并（上游 GPT-5.6 与 fork SESSION 加固并存）。已 force-with-lease 推 `origin/main`，cache 已刷新到 3.1.0。本次 sync 状态见本机 `.git/sync-upstream-state.json`。marketplace 源仍指 `DannyMac180`（`known_marketplaces.json`）——下次 `/plugin` 更新仍会覆盖 cache，遗留风险未消（**2026-07-12 已切源解决，见上方「部署源」**）。

## fork 对上游的额外偏离（同步须保留）

- **CLI lane 无名派生护栏**（2026-07-12，提交 `43144a8`，已推 `origin/main` + cache 3.1.0）：`skills/orchestration/SKILL.md` 新增「Spawning the CLI lanes」节——codex/grok-implementer 禁传 `name`（否则落 `in_process_teammate` 通道、`tools` 白名单失效、Write/Edit 复现导致静默自实现），implementer 豁免；channel-authenticity 降级为兜底；lifecycle teammate 措辞绑定 `name`。`agents/codex-implementer.md`+`grok-implementer.md` 各补 spawn 契约（含 Write/Edit 即误派，自检上报）。上游无等价机制，rebase 冲突按 fork 保留。详见 [07-12 任务](../../.memory/tasks/2026-07/07-12-cli-lane-spawn-guardrail/what.md)。
- **`agents/implementer.md` in-house 兜底 lane**（2026-07-11，提交 `e8e1c9d`，已推 `origin/main`）：上游 v3.0.0 删除了 Sonnet/Opus 的 `implementer` agent（Grok 成默认 lane），导致未装 Grok/Codex CLI 时插件无可用实现 lane（orchestration 只含糊说「用 Claude subagent」）。fork 恢复该文件并**重构定位为兜底**：五段 spec + 报告契约不变，Sonnet 默认 / `model="opus"` 高风险，明确写出权衡（与 architect 同族→无跨厂复审，仅在两条 CLI lane 都不可用时走）。orchestration SKILL lanes 表新增「Fallback」行、「both CLI unavailable」规则改为路由到 `implementer`。下次 rebase 上游若重新引入等价 in-house lane，则删本地版本并记录；否则保留。
- **`agents/codex-implementer.md` 推理档位策略**（2026-07-10，提交 `32b0e0c`/`2063b55`，已推 `origin/main`；cache 也已同步）：上游写死 `-c model_reasoning_effort=high`；fork 改为「high 为 floor（不得更低，低于 high 的请求一律按 high），复杂任务 caller 可在 spec 指定升到 `xhigh`（codex 顶格）」。改了三处：description 括号、flag 表 `model_reasoning_effort` 行、model-override note 下新增一段。**codex 合法档位经 API 实测为 `none/minimal/low/medium/high/xhigh`，无 `max`**（`codex exec -c model_reasoning_effort=__bogus__` 的报错枚举为证）。下次 rebase 上游若改动此文件此处，须保留 fork 的 floor+xhigh 措辞。

> 注：`agents/codex-implementer.md` 已于 v3.2.0（提交 `b114e78`）删除——上面两条涉及它的偏离记录为历史状态，见 [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)。`effort` 白名单其后放开到含 `max`，见 [ADR 0003](./0003-codex-lane-param-policy.md)。
