# 0026 — codex 白名单换成 gpt-6.1-sol，advisor 行加入 sol，能力排名改为按家族定位

- **Status**: accepted（2026-10-01 椰椰声明）
- **Date**: 2026-10-01
- **影响范围**: `plugin/scripts/run-codex.mjs`、`tests/test_runner_contract.py`、`plugin/skills/orchestration/routing-profile.md`、`plugin/skills/orchestration/lanes-claude-code.md` 与两者的中文孪生、`README.md`、`CONTEXT.md`。并入未发布的 6.1.0。
- **关联**: 修订 [ADR 0021](./0021-tiers-mainstay-crux-rescue.md) 决策 6（排名的读法）、决策 8（advisor 行映射）、决策 9（白名单名单）；沿用 [ADR 0018](./0018-post-5-1-tuning.md)"型号换代只改白名单型号名与默认强度"。

## 背景

椰椰 2026-10-01 声明三件事。

1. `gpt-6-sol` 升级为 `gpt-6.1-sol`。能力不高于 `opus-5-5`，价格低于 `sonnet-5-5`。原来所有 `gpt-6-sol` 的位置都换成 `gpt-6.1-sol`。
2. advisor 行加入 `gpt-6.1-sol`，并给出整行取值。
3. 跨家族比较能力没有权威依据：很多型号能力接近，没人能声明谁更强，所以旧排名里多处用 ≤ 和 ≈。椰椰要的是按家族排序，再把型号放进四个定位；价格仍可以跨家族排，因为价格清楚。

## 决策

1. **codex 白名单。** 恰为 `gpt-6-astra`（默认）、`gpt-6-luna`、`gpt-6.1-sol`。`gpt-6-sol` 与 `gpt-5.6-*` 一样判 `spec_invalid`。sol 省略强度时仍提交 `high`。
2. **advisor 行**（Claude Code 与 Cursor 相同）：`mainstay` 为 `gpt-6.1-sol[medium*, high]` › `opus-5-5[medium*, high]` › `gpt-6-astra[low*, medium]` › `fable-5-1[low*, medium]`；`crux` 为 `gpt-6.1-sol[xhigh]` › `opus-5-5[xhigh]` › `gpt-6-astra[high]` › `fable-5-1[high]`；`rescue` 不变。新顺序按价格从低到高排，所以档案删去"advisor `mainstay` 把 astra 放在更便宜的 opus 前面"一条有意顺序。`fable-5-1[low]` 经 `advisor-l` 派发。
3. **advisor 映射。** 验收形状用 `mainstay` 的默认强度；决策形状用 `mainstay` 默认之后的那一档强度。旧写法"决策用 `medium`"在新首候选上与验收落在同一拨盘（`gpt-6.1-sol[medium]`），决策失去比验收高一级的区分。
4. **能力按定位排名。** 四个定位从低到高为 `starter`（入门）、`midrange`（中端）、`premium`（高端）、`flagship`（旗舰）。每个家族只给自己的型号定位：Claude 为 `haiku-4-5`、`sonnet-5-5`、`opus-5-5`、`fable-5-1`；GPT 为 `gpt-6-luna`、无、`gpt-6.1-sol`、`gpt-6-astra`；Grok 为 `composer-2.5-fast`、`grok-4.7`、无、无。不同家族的型号只按定位比较，同一定位内不分高下。≈ / ≤ 读法退役；`haiku-4-5` 与 `composer-2.5-fast` 不再是"不排级"的特例。价格链保持跨家族。
5. **家族擅长点写进排名表。** Claude 前端；GPT 后端、复杂任务；Grok 价智比高。格内选择的擅长点示例改为引用这张表。
6. **命名。** 选"定位 / segment"与上述四个名字，原因是其他候选都撞上现有词：低 / 中 / 高直译成 `low` / `medium` / `high`，与强度名相撞；level 在 `SKILL.md` 里解释档位；entry 已表示"进入某一档"；档、级与档位、升档、升级梯相撞。
7. **`SKILL.md` 不改。** R2 只写"不低于失败型号在档案排名中的位置"，档案重新定义排名即可；`CONTEXT.md` 的升级梯改为按定位比较，并新增"定位"词条。

## 后果

- 换代只需重放一个型号：`gpt-6-sol` 原在 `midrange`，升级到 `gpt-6.1-sol` 后进入 `premium`；grok 从 4.6 到 4.7 仍在 `midrange`。
- 升档路径只有一条由合法变为禁止：worker 在 `crux` 用 `gpt-6-astra`（`flagship`）失败后，不能再升到 `rescue` 的 `opus-5-5[xhigh]`（`premium`），只剩 `gpt-6-astra[high*, xhigh]`。旧读法里 opus ≈ astra，这条路径合法。
- advisor 置信度低时转 `crux` 属于 advisor 映射，不是 R2 升档，不受定位下限约束。

## 未采纳

- **保留跨家族能力链，用 ≈ / ≤ 表达模糊。** 被椰椰否决：跨家族的先后没有权威依据，换代时整条链都要重估。
- **段位命名（青铜 / 白银 / 黄金 / 铂金）与数字段位（1 段到 4 段）。** 都没有撞词，椰椰选了入门到旗舰。

## 复盘条件

- 某个家族在同一定位出现两个型号 → 需要补一条定位内的排序规则。
- 新增模型家族 → 给它的型号定位，并写擅长点。
- 某个型号换代 → 只重新定位这个型号；跨定位移动时核对填充表里涉及它的升档路径。
