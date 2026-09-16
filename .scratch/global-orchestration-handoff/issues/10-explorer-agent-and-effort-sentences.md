# 10: explorer agent 文件与被证伪的 effort 表述

**What to build:** 新增 `plugin/agents/explorer.md`（`tools: Read, Grep, Glob`，不写 `effort:`）与中文孪生 `docs/zh/agents/explorer.md`；改 `SKILL.md:62`、`lanes-claude-code.md:3`、`lanes-claude-code.md:5` 三处被实测证伪的 effort 与 `/tasks` 表述。

**Status:** ready-for-agent

**Blocked by:** 无。与 07 的发布互不阻塞；若在 5.1.0 推送前完成，并入 5.1.0，不再单独升版。

**依据:** ADR 0015 追记（2026-09-16）与工单 08 的 `## Comments`。advisor 决策形状裁定为 C。

## 内容

1. **新建 `plugin/agents/explorer.md`。** frontmatter：`name: explorer`；`description` 压短，一句说明只读取证角色与返回形状，不复述决策类型门与路由理由；`tools: Read, Grep, Glob`；`model:` 不设默认值，按次由派发方给（取值留用户路由档案）；**不写 `effort:`**——理由见 ADR 0015 追记"新的未决项"。正文只写只读取证契约：输入是读取范围，输出是 `FINDINGS` 与 `GAPS` 两段，证据带 `file:line`、逐字引用、仓相对路径，不自加小标题。操作契约沿用 `<plugin-root>/skills/orchestration/lane-preamble.md`，按 `worker.md` 的写法指过去，不复述。
2. **中文孪生同一提交内跟改**（AGENTS.md 的镜像规则，`tests/test_zh_mirror.py` 只检存在性，内容靠人工对齐）：新建 `docs/zh/agents/explorer.md`；改 `docs/zh/skills/orchestration/SKILL.md:62` 与 `docs/zh/skills/orchestration/lanes-claude-code.md:3`、`:5`，这三处是下面第 3、4、5 条的中文对应句。
3. **`SKILL.md:62`** claude 车道单元格：explorer 由"内置 Explore"改为本插件的 `explorer` agent，保留"按次 `model` 必须显式"的要求；effort 半句改为"取实跑模型的配置档位"，删"inherits the session model ... and effort"。
4. **`lanes-claude-code.md:3`**：同步改这一句；删"omitted, Explore inherits the session's model ... and the session's effort, so an unpinned explorer runs at session price"，改为：不带 `model` 时实跑会话模型，档位随该模型的配置走，因此按次 `model` 要显式给。
5. **`lanes-claude-code.md:5`**：删"an agent that sets none inherits the session's effort"，删把 `worker.md` 的 `effort: medium` 与 `fable-advisor.md` 的 `effort: high` 称作"role defaults on this lane"的句子（待证）。`/tasks` 一句按实测改写：不再称它是"用户侧观测点"——团队模式（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）下 `/tasks` 只列成员名与状态，不显示模型与档位；官方文档的限定是档位只在子代理定义或其 fork 的技能设了 `effort` 时才显示。改指子代理转写 `~/.claude/projects/<项目>/<会话>/subagents/agent-*.jsonl`（每条 assistant 记录带实跑 `model` 与 `effort`）与同名 `.meta.json`（记请求模型），并注明两者可能不一致。
6. **词数预算**：`SKILL.md` ≤ 1960 词（ADR 0015 实施段），改动不得突破。

## 不做

- 不写任何 effort 声明或档位承诺，`explorer.md` 与 doctrine 都不写。
- 不改 `worker.md`、`fable-advisor.md` 现有的 `effort:` 与 `model:` frontmatter；等经典 Task 路径复测后另议。
- 不碰 Cursor 侧：`explore` 加显式 slug 已满足要求（工单 08 核对项 4）。
- 不与 `.scratch/role-pool-posture/issues/10-report-mode-preamble.md` 的报告前言合并实施，只保持单源引用。
- 不提交、不推送、不发布、不改用户目录。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
test -f plugin/agents/explorer.md && test -f docs/zh/agents/explorer.md && echo "both present"
rg -n "effort" plugin/agents/explorer.md ; echo "expect no output"
rg -n "the session's effort|role defaults on this lane|inherits the session model" plugin/skills/orchestration/SKILL.md plugin/skills/orchestration/lanes-claude-code.md ; echo "expect no output"
rg -n "继承会话的 effort|继承会话模型" docs/zh/skills/orchestration/SKILL.md docs/zh/skills/orchestration/lanes-claude-code.md ; echo "expect no output"
rg -n "user-side observation point" plugin/skills/orchestration/lanes-claude-code.md ; echo "expect no output"
rg -n "explorer" plugin/skills/orchestration/SKILL.md plugin/skills/orchestration/lanes-claude-code.md
wc -w plugin/skills/orchestration/SKILL.md   # 期望 ≤ 1960
python3 tests/test_zh_mirror.py
python3 tests/test_user_level_archive.py
python3 tests/test_runner_contract.py
git diff --check
```

失败判据：`rg` 两条期望无输出的命令任一有命中，或 `SKILL.md` 超过 1960 词，或任一测试脚本非零退出。
