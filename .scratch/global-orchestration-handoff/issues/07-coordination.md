# 07: 协调件——词表、ADR 0015、仓内文档、版本

**What to build:** 主代理亲写的协调件：`CONTEXT.md` 词条（拨盘、填充表、决策类型门）；ADR 0015 记录本次决策；`AGENTS.md` 用户级填充表节改写；`docs/agents/cursor-lane-gate.md`（C10、C11、中文备份新路径）、`docs/agents/plugin-release.md`（C7、C8、C9、Q08）、`docs/agents/domain.md`（B9）、`docs/agents/triage-labels.md`（C13）；版本 5.1.0 两处。

**Status:** ready-for-agent

**Blocked by:** 05（`AGENTS.md` 与 `cursor-lane-gate.md` 的路径句要对应迁移后的位置；可与 05 并行起草，05 完成后核对）

## 内容

- **`CONTEXT.md`**：拨盘词条加记法 `model[first-round | escalation-only]` 与 `*`；填充表词条把"放用户级规则"改为"放调用方指定的用户路由档案"；决策类型门词条删"宣告多步交付物完成前"，加"验收形状经 Tier 3 到达"。
- **ADR 0015**：决策——填充表迁到调用方指定档案并定义读取契约；决策类型门第六项退役、验收形状归 Tier 3；拨盘记法入仓、取值留档案；用户规则存档退役、pin 规则权威留本仓；explorer 显式 `model` 为文档要求、agent 文件待核（A3b）；调用方保留操作经 Constraints 与前言传递；执行记录三层表述；版本 5.1.0。复盘条件——A3b 核对结果；Q01a 后同族多步改动漏判 ≥2 次 → 重议；N02 若 SKILL.md 再增长 → 拆派发文件。
- **`AGENTS.md:27-29`** 改一句：模型候选与资源偏好在 prompts 仓库的用户路由档案，本仓不留副本；pin 规则权威与中文备份在 `cursor-hooks/`。
- **`docs/agents/cursor-lane-gate.md`**：Behaviour 四条与 Update 第 1 步的规则复述合一；Task pin rule 段删第 44 行全文复述；中文备份路径改 `cursor-hooks/zh/fable-lane-pin.mdc`。
- **`docs/agents/plugin-release.md`**：第 10 行版本规则三类；第 12 行删目录枚举、留三句机制依据；第 21 行改显式暂存加 `git diff --cached --stat`，注明 `outputs/` 未忽略；第 45–53 行删 `test ! -d` 三行。
- **`docs/agents/domain.md`**：删第 12 行模板句与第 14–29 行目录树。
- **`docs/agents/triage-labels.md`**：删映射列，留"状态 / 含义"。
- **版本**：`plugin/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` → `5.1.0`。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
rg -n "5.1.0" plugin/.claude-plugin/plugin.json .claude-plugin/marketplace.json
rg -n "user-rules" AGENTS.md docs/agents/ ; echo "exit=$?"   # 期望无输出
rg -n "git add -A" docs/agents/plugin-release.md ; echo "exit=$?"   # 期望无输出
test -f docs/adr/0015-*.md && echo "adr present"
git diff --check
```
