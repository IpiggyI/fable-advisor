# 模型路由校准 + receipt gate 重触发修复

Status: ready-for-agent

## Problem Statement

三个互相独立、但都源于"模型格局变了、机制没跟上"的问题：

1. **架构师身份判定过窄。** 判定式写死"session model 是 Fable"（`~/.claude/rules/fable-advisor.md`）。Opus 5 与 Fable 能力相近，跑在 Opus 5 上的会话本该当架构师，却被判进 advisor-only，拿不到编排能力。更糟的是这个判定式是单名匹配——每出一个模型就要改一次规则，忘了改就静默降级。

2. **兜底 lane 的默认模型选错了。** `implementer` agent 默认 `model: sonnet`。Sonnet 5 在权威榜单上的性价比不如 Opus 4.8，更不如 Opus 5。而本机 grok CLI 未认证，实际只有 codex 一条 CLI lane——codex 一挂就直接掉到 `implementer`，它不是上游设想的"罕走兜底"，而是**第二顺位**，走的频率远高于预期。

3. **收尾门在多会话并行时反复误拦。** `hooks/receipt-gate.py` 是 Stop hook，只看 `<cwd>/.fable-advisor/pending/*.json`，没有任何会话归属概念。两个后果：
   - 同一会话内，它**完全没读 `stop_hook_active`**，于是每次收尾都会重复拦截，直到撞上 harness 的 9 次上限才被强制放行（实录见 `docs/hook频繁拦截问题.txt:207-441`）。
   - 多个会话并行、其中一个正在跑 codex lane 时，其余会话会被那份在飞的 pending spec 拦下——它们跟那份 spec 毫无关系。

## Solution

三条各自最小化的改动：

1. **判定式改成按系列判定，并把第三方模型的授权交给用户显式列名。** Fable 系列 / Opus 系列 → 架构师；Sonnet / Haiku 系列 → advisor-only；两边都不匹配的模型 → 兜底 advisor-only，除非用户在私有规则的名单区块里显式列出。名单默认留空，用户部署时自己填。仓库侧只做去型号化，不承载任何具体型号。

2. **`implementer` 默认模型改为 `opus`，并把它的存在理由从"单价便宜"改写为"不污染架构师上下文"。** 改完后它与架构师同模型同单价，省的不再是 token 单价，而是架构师上下文的永久增长——派出去的实现细节不进架构师上下文、不被每轮重读。这条论证必须写进文档，否则 `SKILL.md` 现有的"spend Fable on judgment, spend Sonnet on volume"会自相矛盾。

3. **receipt gate 只修 `stop_hook_active` 这个 bug，机制一律不动。** 拦截次数从 9 次降到 1 次。不降级为不阻断的警告，不加豁免态，不加并发归属判定。

## User Stories

1. 作为跑在 Opus 5 上的会话，我希望被判定为架构师，以便我能按 orchestration doctrine 编排 lane，而不是退回自己写代码。
2. 作为跑在 Opus 4.8 上的会话，我希望同样被判定为架构师，以便我不必等规则为每个具体版本更新一次。
3. 作为规则的维护者，我希望判定式按模型**系列**而非具体版本书写，以便下一代 Opus/Fable 发布时规则自动适用、无需改动。
4. 作为规则的维护者，我希望遇到既不属 Fable/Opus 也不属 Sonnet/Haiku 的模型时兜底落 advisor-only，以便一个能力未知的模型不会被自动授予"写 spec 派活"的权限。
5. 作为跑在第三方模型（如 glm-5.2、gpt-5.6-sol）上的会话，我希望只有在用户显式把该模型列入名单后才当架构师，以便授权是显式、可审、可撤的。
6. 作为在多个网关 profile 间切换的用户，我希望名单匹配能容忍网关前缀（`hs/`、`go/`）和 `[1m]` 后缀，以便同一个模型在不同 profile 下都能被正确识别。
7. 作为用户，我希望第三方名单留在我的私有规则里而不是写进仓库，以便这个公开 fork 对别人仍然普适。
8. 作为读 README 的插件使用者，我希望它描述的是"旗舰层会话模型"而不是写死 Fable 5，以便我用 Opus 跑时文档与实际相符。
9. 作为没有 Fable 权限的插件使用者，我希望 README 如实说明"session 用 Opus、advisor 也只能用 Opus，此时顾问只剩上下文隔离价值"，以便我不被"层级整体降一级"这句已被证伪的话误导。
10. 作为架构师，我希望在两条 CLI lane 都不可用时，兜底 lane 默认跑 Opus，以便掉到兜底时的实现质量不因默认值而打折。
11. 作为架构师，我希望兜底 lane 的文档明说它的价值是上下文隔离而非单价便宜，以便我理解为什么还要派工而不是自己写。
12. 作为架构师，我希望 orchestration doctrine 里的成本纪律不再写"spend Sonnet on volume"，以便 doctrine 与实际默认值一致、不自相矛盾。
13. 作为架构师，我不希望兜底 lane 提供 `model="sonnet"` 降级出口，以便少一个没人会用、却要每次判断的决策点。
14. 作为架构师，我希望 `grok-implementer` 的驱动壳保持 sonnet，以便不为一个只做转发和取证、且当前未认证闲置的壳付 Opus 单价。
15. 作为架构师，我希望 `fable-advisor` 顾问 agent 保持 `model: fable`，以便在 Opus 5 会话下咨询它仍是跨模型意见而不是自问自答。
16. 作为在同一会话中收尾的架构师，我希望 receipt gate 在 `stop_hook_active` 为真时放行，以便我不会被同一条信息反复拦九次。
17. 作为并行会话中的一员，我希望别的会话正在跑的 codex lane 不会在收尾时把我拦下太多次，以便并行工作不被无关的 pending spec 反复打断。
18. 作为架构师，我希望 receipt gate 在第一次拦截时仍然把完整信息说给我，以便我能如实向用户披露有一份 spec 悬着。
19. 作为用户，我希望 receipt gate 保留阻断能力而不是降级成给人看的警告，以便"主会话声称完成却没跑 codex"仍然被机制拦住。
20. 作为用户，我希望 receipt gate 不提供豁免开关，以便棘轮不被模型自行 waive 掉。
21. 作为维护者，我希望这次修复配一个入库的回归脚本，以便 `stop_hook_active` 这类遗漏不会再次静默回归。
22. 作为维护者，我希望回归脚本零依赖、一条命令跑完，以便它在没有 `package.json` 的仓库里也能用。
23. 作为维护者，我希望回归脚本只测进程边界的外部行为（stdin JSON → exit code + stderr），以便它不会因为内部实现重构而假失败。
24. 作为维护者，我希望 `plugin.json` 版本升到 3.3.0 而不是打 patch，以便默认模型这种行为变更在版本号上可见。
25. 作为维护者，我希望 spawn 护栏与 receipt gate 的区别被写进术语表，以便下次不会再把两条护栏的适用对象记混。
26. 作为维护者，我希望"别名槽位 ≠ 模型身份"被写进术语表，以便下次不会误以为把某模型放进 Opus 槽就等于它是 Opus。
27. 作为维护者，我希望这次的三条决策落进 `docs/adr/`，以便未来有人提议"receipt gate 是不是过时了"时能直接读到已被纠正的前提。
28. 作为同步上游的人，我希望改动集中、去型号化而非双型号并列，以便 rebase 时冲突面可控。

## Implementation Decisions

### 架构师层判定（仓外）

- 判定式只存在于用户私有规则 `~/.claude/rules/fable-advisor.md`，**仓库不承载任何模型准入门控**。事实依据：`skills/orchestration/SKILL.md` 通篇没有以模型名做的门控，唯一提到 Fable 的是成本比喻那一句。
- 两个模式标题改为按系列表述；新增一个默认为空的第三方名单区块，附匹配语义说明：**剥掉 `<gateway>/` 前缀与 `[1m]` 后缀后比对裸模型名**。
- 兜底方向：两边都不匹配 → advisor-only。

**一手验证依据**（2026-07-25，Claude Code v2.1.220）：在 `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME="GLM-5.2"` 的 profile 下，会话环境块逐字输出 `You are powered by the model hs/glm-5.2[1m].` — 显示名不出现，给的是裸模型 ID，且句式与 Anthropic 官方模型（`the model named <名> ... exact model ID is <id>`）不同。故按系列判定不会把第三方模型误判成 Opus。

### 兜底 lane 模型（`agents/implementer.md`）

- frontmatter `model: sonnet` → `model: opus`（用别名，跟随最新 Opus）。取值合法性依据官方 sub-agents 文档的枚举：`sonnet | opus | haiku | fable | <full model id> | inherit`。
- description 与正文重写：删除"Sonnet by default / 高风险用 `model=\"opus\"`"整套叙述；改写为上下文隔离论证。不提供降级出口。
- `agents/grok-implementer.md`、`agents/fable-advisor.md` 均不改。

### 文档去型号化

- `skills/orchestration/SKILL.md`：成本比喻、lanes 表 Fallback 行、commitment-boundary 那句括号。
- `README.md`：架构师叙事各处、implementer 模型叙事各处、无-Fable-权限兜底段（照实重写，不再写"层级降一级"）、v3.3 升级说明一句。
- `.claude-plugin/plugin.json`：description 里的 in-house lane 措辞；版本 3.2.1 → 3.3.0。

### receipt gate（`hooks/receipt-gate.py`）

- 在解析 stdin 之后、扫描 pending 目录之前，读 `stop_hook_active`；为真则立即输出 `{}` 并以 0 退出。
- 依据是 harness 自身的报错文本（`docs/hook频繁拦截问题.txt:438-441` 逐字）：*"For Stop/SubagentStop hooks, check `stop_hook_active` in the input and return success while it's true."* 官方文档页 Stop 段被截断读不到，故此为一手证据而非文档推断。
- 字段缺失时行为不变（仍然拦截）——向后兼容。
- `hooks/hooks.json` 不改。

### 知识资产

- 新建根 `CONTEXT.md`（术语表，只放术语、不放实现细节）：**spawn 护栏 vs receipt gate**、**lane 三类**（Routine / Cross-vendor / Fallback）、**架构师层 / advisor-only**、**别名槽位 ≠ 模型身份**。
- 新增一条 ADR 记录本次三项决策，重点记录被纠正的前提：receipt gate 针对的是主会话自己，不是已被删除的 wrapper 子代理。

## Testing Decisions

**什么是好测试**：只测外部可观察行为，不测内部实现。`receipt-gate.py` 的外部行为就是 Claude Code 实际依赖的那个契约——stdin 收 JSON，产出 exit code 与 stderr 文本。测试不得触碰 `glob`、`hashlib`、路径拼接等内部细节；重构内部实现时测试必须仍然通过。

**seam：一个。** `hooks/receipt-gate.py` 的进程边界。这是最高的可用接缝，也是唯一一个——其余改动（frontmatter、README、SKILL.md、plugin.json、CONTEXT.md、ADR）是声明式配置或散文，没有可测行为。

**不设第二个 seam。** `implementer` 的 `model: opus` 若要行为验证需真派一次子代理观察实际模型，成本高且依赖账号状态；改动是单值替换，取值合法性由官方枚举界定，用静态解析校验即可。

**被测模块**：`hooks/receipt-gate.py`，七个用例：

| # | pending 目录 | receipt | `stop_hook_active` | 期望 |
|---|---|---|---|---|
| 1 | 不存在 | — | — | exit 0 |
| 2 | 有 spec | `complete` | 缺失 | exit 0 |
| 3 | 有 spec | 无 | 缺失 | exit 2 + stderr |
| 4 | 有 spec | 无 | `false` | exit 2 + stderr |
| 5 | 有 spec | 无 | `true` | **exit 0**（本次新增行为） |
| 6 | 有 spec | `error_class: timeout` | `false` | exit 2 + stderr |
| 7 | stdin 非法 JSON | — | — | exit 0（fail open，既有行为） |

用例 3 与 4 覆盖向后兼容：字段缺失或为假时行为不得改变。

**测试载体**：入库一个零依赖回归脚本（Python 或 shell，与 `run-codex.mjs` 的"零依赖"取向一致），自建临时目录、构造 spec 与 receipt、逐例断言 exit code，一条命令跑完并打印通过/失败。

**Prior art**：仓库目前**没有**任何测试文件、`package.json` 或 CI，所以没有可复用的测试框架。既有验证实践是一次性探针——`.memory/tasks/2026-07/07-15-guardrail-mechanization/what.md` 记录的"平台能力实测三件套"（临时项目日志 hook、临时 marketplace + 插件、无头 `claude -p`），以及提交 `8f4d7f9` 的 python smoke test。本次的回归脚本是该实践的第一次入库固化，风格上沿用它：零依赖、自包含、输出即证据。

**无可执行验证器的部分**：README / SKILL.md / plugin.json description / CONTEXT.md / ADR 的措辞改动没有 seam，只做结构检查与一致性 grep（搜残留的 "Sonnet by default"、"spend Sonnet on volume"、"model tiers shift down one"、以 Fable 具名的架构师叙事）。实现时必须如实报告"这部分无可执行验证器"。

## Out of Scope

- **清理 5 个 profile 的 `CLAUDE_CODE_SUBAGENT_MODEL`**（`settings-glm` / `settings-cpa` / `settings-deepseek` / `settings-go` / `settings-hs`）。官方文档明载该变量**覆盖每次调用的 `model` 参数与子代理 frontmatter**，所以在这些 profile 下本 spec 的第 2 条改动不生效，`agents/fable-advisor.md` 的 `model: fable` 也早已失效。用户已表示自行处理；不得代改这些文件（内含凭据）。
- **填写第三方架构师名单的具体型号**。本次只建空的名单区块与匹配语义，具体型号由用户部署时自填。
- **receipt gate 的并发归属判定**（宽限窗口 / in-flight 锁 / transcript 归属）。先修 bug 观察；若 1 次拦截仍嫌吵，届时再上，那时痛点是已验证的而非推测的。
- **receipt gate 降级为不阻断**、**豁免态开关**。已明确否决。
- **`grok-implementer` 与 `fable-advisor` 两个 agent 的任何改动。**
- **grok CLI 的认证问题**。它导致默认 lane 失效、路由实际退化成 codex 单 lane，是独立议题。
- **git 提交与推送。** 需单独授权。
- **DeepSWE 等榜单结论的一手核验。** 属用户前提，对一条兜底 lane 的默认模型不成比例。

## Further Notes

**必须纠正的前提。** 提出议题 3 时的原始判断是"这个 hook 当时是因为派出子代理后子代理自己干了而没派 Codex lane，现在主会话直派，问题不那么紧迫"。仓库记录否定了这一点：

- `.agent-discuss/codex-implementer-architecture/final.md:15` — *"receipt 强制执行点：Stop 类 hook 校验或显式 command 入口，至少绑定其一——receipt 本身是证据不是强制"*
- ADR 0002（原 `.memory/decisions/codex-lane-dewrapper-receipt-gate.md`）— *"receipt gate 实测可机制化拦截'声称完成'，补上'主模型根本不路由给 Codex'这第三类威胁"*

"子代理静默自实现"由 **PreToolUse spawn 护栏**（`hooks/block-named-cli-lane.py`，fail closed）机制化，那条针对的 wrapper 子代理已在 `b114e78` 删除。**receipt gate 针对的是主会话自己**——去 wrapper 之后它是唯一还在盯主会话的机制。所以"现在是主会话直派 Codex lane"不是它过时的理由，恰恰是它的适用场景。

**降级方案的硬约束。** `systemMessage` 是 user-facing only、不喂给模型。所以 exit 0 + systemMessage 的降级等于 gate 对模型彻底失效，功能上约等于删掉这个 hook。这是否决降级的决定性依据。

**残余风险。** 修完 `stop_hook_active` 后，模型理论上可以靠"再停一次"通过 gate。这**不是新增漏洞**——harness 本来就有 9 次上限兜底，绕过成本只是从 9 轮降到 1 轮。棘轮的实际强度是"至少把信息说出来一次"，这一点没变。若日后发现主会话真的开始靠重停绕过，那才是重新上机制的信号。

**分歧面。** 本次连同 setup 一起，给这个 fork 新增了 `AGENTS.md`、`CLAUDE.md`、`docs/agents/`、`docs/adr/`、`.scratch/`，再加本 spec 要求的 `CONTEXT.md`。与上游 `DannyMac180/fable-advisor` 的分歧明显变大，rebase 时需按 ADR 0001 的规则处理。另注意 `docs/` 整个目录当前未跟踪，其中还有 5 个会话转储 `.txt`——一次 `git add docs/` 会把它们一并扫进来。
