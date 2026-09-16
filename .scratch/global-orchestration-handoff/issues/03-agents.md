# 03: agent 文件描述压短、删重复规则

**What to build:** `plugin/agents/fable-advisor.md`、`plugin/agents/worker.md` 按 [spec.md](../spec.md) 的 B2、B3、B4、B5、Q01a 修订。只改这两个文件；`docs/zh/` 孪生由工单 06 处理。

**Status:** ready-for-agent

**Blocked by:** 无

## 验收标准（全部为必须）

### `fable-advisor.md`

1. **B2** 第 3 行 `description` 压短，不再复述门清单，例如：`Read-only second reader. Consult at the decision-type gates in fable-advisor:orchestration (decision shape), or for acceptance of a delivery (contract, diff, receipt) when the orchestration skill's Tier 3 applies. Advises only.`
2. **Q01a** 正文任何"多步交付完成前"的触发表述改为：验收形状在 orchestration skill 的 Tier 3 条件下到达（正确性关键、同族 diff、或用户要求评审），不按步数触发。第 24 行 "## Acceptance shape" 段的输入与输出定义不动。
3. frontmatter 其余字段（`model: fable`、`effort: high`、`tools`、`readonly`）不动。

### `worker.md`

4. **B2** 第 3 行 `description` 压短为：`The claude lane's writing role: takes a five-part delivery contract, owns the implementation inside its Files, and returns a diff plus verification evidence.`
5. **B4 / B5** 第 12–16 行 "The three standing disclosures" 整段（含 "Highest unit price"）改为一行普通自查：`Re-read your diff before you report.` 不使用 "second reader" 措辞。
6. **B3** 第 26 行 "Never claim completion without running the verification. "Should work" is forbidden." 删除。第 27 行改为：`No swallowed errors or placeholders in your own diff.` 第 28–29 行两条不动。
7. frontmatter（`model: opus`、`effort: medium`）不动。
8. 两个文件中不再出现：`highest unit price`、`second reader before`、`Should work`、`multi-step deliverable is declared done`、`three standing disclosures`。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
rg -n -i "highest unit price|second reader before|Should work|multi-step deliverable is declared done|three standing disclosures" plugin/agents/ ; echo "exit=$?"   # 期望无输出、exit=1
rg -n "Tier 3|Re-read your diff|own diff" plugin/agents/fable-advisor.md plugin/agents/worker.md
head -8 plugin/agents/fable-advisor.md plugin/agents/worker.md
git diff --stat -- plugin/agents/
```
