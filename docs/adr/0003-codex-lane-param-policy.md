# 0003 — codex 车道参数化（effort/model/service_tier）+ fail-loud 校验

- **Status**: accepted（「决策落点」一行已被 [ADR 0004](./0004-adr-store-in-repo.md) 取代）
- **Date**: 2026-07-15
- **影响范围**: `scripts/run-codex.mjs`、`skills/orchestration/SKILL.md`、`README.md`
- **关联决策**: [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md)（去 wrapper 化后，runner 成为 codex 车道唯一入口，本决策扩展其入参）
- **Migrated**: 2026-07-25，从 `.memory/decisions/codex-lane-param-policy.md` 迁入

## 背景

去 wrapper 后 runner 是 codex 车道唯一入口,但入参被写死:`effort` 只认 `xhigh`、其余静默降到 `high`(`run-codex.mjs:125`);`model` 任意串透传、无校验;无 `service_tier` 概念。用户要求把三者交给架构师按任务自选:effort 放开到 `low/medium/high/xhigh/max`;model 增加 `gpt-5.6-terra`、`gpt-5.6-luna`(≈sonnet/haiku,对照旗舰 `gpt-5.6-sol`≈opus);`service_tier=fast` 仅在追求速度时加。核心取向:质量优先,`xhigh/max` 谨慎(明显变慢)。

事实核验(2026-07-15,codex-cli 0.144.4):`-c model_reasoning_effort=<v>` 与 `-c service_tier=fast` 为正确注入机制;`effort=max` 经真实调用验证被 gpt-5.6-sol 接受(reasoning effort: max,exit 0);`service_tier` 是模型 catalog 属性(binary 含 `service_tiers`/`default_service_tier`),真实会话实测发送过 `default`/`priority`/`fast`;codex 在 config 解析期**不**校验 effort/model/tier 取值(连 `bogus` 都不报错,错误延后到 API)——故校验只能落在 runner。

## 选项对比

| 维度 | 选项 | 选定 | 理由 |
|------|------|------|------|
| 越界入参 | ①fail loud→spec_invalid ②静默纠正 ③透传给 codex | **①** | ②沿用的静默降级会把架构师笔误藏起来照跑;③把错误延后到一次付费 API 往返且 error_class 笼统落到 codex_failed。①与"质量优先"、fail-loud 一致 |
| effort 白名单 | ①恰好 5 个 ②含 minimal | **①{low,medium,high,xhigh,max}** | minimal 与质量优先相悖,真要用再加一行 |
| model 白名单 | ①严格 sol/terra/luna ②自由透传 ③白名单+逃生舱 | **①** | 白名单本身即"三档菜单",与 fail-loud 一致;出 gpt-5.7 时改一行数组即可(本就要重映射梯子);③YAGNI |
| service_tier 默认档 | ①runner 硬编码非-fast 档 ②照字面:仅 fast 时加,否则交 codex 原生默认 | **②** | runner 不写读 config 的逻辑、不硬编码默认档;只在被要求提速时加 `-c service_tier=fast`,平时交 codex 原生默认。消费机 config 是机主的事,非 runner 责任 |
| service_tier 字段形状 | ①`service_tier` 字段白名单仅 fast ②布尔 `fast` ③放宽到 {fast,priority,default} | **①** | 字段名与 codex 机制/receipt 对齐、最小;③超出"只要 fast"范围 |
| receipt | ①记录 service_tier ②不记 | **①** | 与已记录的 model/effort 一致、可审计;省略记 null(如实反映 runner 传了什么,不假装知道 codex 解析后的有效档) |
| doctrine 定位 | ①分层 ②codex 升为全谱系车道 | **①** | 车道选择仍成本优先(grok 默认);上了 codex 后才质量优先(默认 sol+high,谨慎升 xhigh/max)。terra/luna/降 effort 仅用于 codex 家族内确实简单的任务,不取代 grok 默认 |
| ~~决策落点~~ | ~~①.memory/decisions ②docs/adr ③两边~~ | ~~**①**~~ | ~~沿用仓库现有决策存储,避免与 docs/adr 双份真相源~~ — **已于 2026-07-25 取代，见 [ADR 0004](./0004-adr-store-in-repo.md)** |
| 市场描述 | ①不改/轻改 ②更新 | **①** | 仍以 sol+默认 high 作旗舰描述,依然准确;避免市场文案随参数频繁改 |

## 决策

runner 三个入参(`effort`/`model`/`service_tier`)全部 fail-loud 校验:越界即 `error_class: spec_invalid`、不 spawn codex。`effort∈{low,medium,high,xhigh,max}` 默认 `high`;`model∈{gpt-5.6-sol,gpt-5.6-terra,gpt-5.6-luna}` 默认 `gpt-5.6-sol`;`service_tier∈{fast}` 可选,省略则不注入(交 codex 原生默认),`fast` 则追加 `-c service_tier=fast`。receipt 新增 `service_tier` 字段(传值或 null)。

**核心理由**:

1. **fail-loud 统管三字段**:静默降级/透传都会把架构师的选参错误藏到一次付费调用之后;质量优先的取向下,宁可让 runner 立即回 spec_invalid。
2. **doctrine 分层不自相矛盾**:插件的成本控制主要来自"把活从架构师(贵)派给 grok/Codex(便宜)"这一步;既然那步已压住成本,车道内部适当提质量(默认 sol+high)是负担得起的。故"成本优先选车道 + codex 内质量优先"两条并存。
3. **service_tier 交 codex 原生默认**:runner 立身之本是确定性(已显式传 model/effort/sandbox),但用户明确 runner 不读、不代管机器 config——只留一个 `fast` 提速杠杆,平时不碰 tier。

## 实施代价

- `run-codex.mjs`:新增 3 个白名单集合;`normalizeSpec` effort/model 改为校验-或-抛错、`SPEC_KEYS` 加 `service_tier`;`executeCodex` 条件追加 `-c service_tier=fast`;receipt/state 贯穿 `service_tier`。
- `SKILL.md`:spec 例子补 model/service_tier;删"effort floor is high"(第 72 行)与车道表"GPT-5.6 Sol (high reasoning)";写入分层选择 doctrine(默认 sol+high、xhigh/max 谨慎且明显变慢、terra/luna 降档、fast 仅提速)。
- `README.md`:三处"GPT-5.6 Sol at high reasoning"改为可选模型档+推理档范围+可选 fast。
- 兼容性:老 spec(effort high/xhigh、省略 model)照常;medium/low 从"被降级"变"被采纳";过去靠静默降级跑通的**非法** effort/model 现在 spec_invalid——预期内。

## 复盘条件

- OpenAI 改模型目录(sol/terra/luna 更名或出 gpt-5.7)→ 更新 model 白名单数组并重映射三档梯子。
- 若需要 `priority`/`flex` 等非-fast 档作架构师可选杠杆 → 放宽 `service_tier` 白名单(当前仅 fast)。
- `max` 若在后续模型上被拒或语义变化 → 复核 effort 白名单(本次 `max` 已真实验证)。

## 备注

- 事实核验环境:codex-cli 0.144.4;`effort=max` 真实调用 session `019f6538-…`。
- 遗留(非本次范围):`hooks/block-named-cli-lane.py` 的 `GUARDED` 仍含 `"codex-implementer"`(v3.2 已删该 agent)——死引用;当前会话 agent 列表仍显示 `fable-advisor:codex-implementer`,说明已安装插件版本落后仓库 HEAD。（该死引用已于提交 `a89231f` 清理。）
- 实施经由 codex 车道自身完成(dogfood):spec 见 `.fable-advisor/pending/codex-param-policy.json`。
