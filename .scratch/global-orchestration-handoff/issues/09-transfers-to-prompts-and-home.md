# 09: 转出项——prompts 仓库文本与用户目录清理

**What to build:** 本仓不动，只提供文本与清单，由椰椰在 prompts 仓库与用户目录执行。

**Status:** ready-for-human

**Blocked by:** 无

## prompts 仓库 `current-prompts/docs/fable-advisor-routing.md`

**D2 取值**（已按推荐确认，含中文镜像同步）。在第 5 行角色默认句后加记法说明：

> Dial notation: `model[first-round options | escalation-only]`; `*` marks the default. Options after `|` are reached by a worker only through escalation after a failed rework ticket, and by any role only on my declaration.

表格单元格改为：

- explorer @ light / worker @ light：`grok-4.6[medium* / high | xhigh]` › `gpt-5.6-luna[high* / xhigh / max]`
- worker @ standard：`grok-4.6[high / xhigh*]` › `claude-opus-5[medium / high*]`
- worker @ senior：`gpt-6-astra[medium* / high | xhigh]`（删 "use gpt-6-astra[high] for unusually hard work" 散文，括号已表达）
- advisor：`gpt-6-astra[medium / high* | xhigh]` › `claude-fable-5-1[medium / high* | xhigh]`（Cursor 表顺序相反，保留）

**C14** 第 20 行 Cursor 说明改为：

> Cursor model-family values come from the live allowlist; do not persist a possibly stale slug. In Cursor the effort is the slug suffix: pick the slug variant whose effort fits the cell; when this turn's allowlist has one variant, it is the dial, named in the disclosure.

## prompts 仓库 `current-prompts/rules/fable-lane-pin.cursor.mdc`

**A7 副本注记**：在 prompts 仓库根指南 `AGENTS.md:30` 的 `rules/` 描述里注明该文件是插件仓库 `cursor-hooks/fable-lane-pin.mdc` 的部署快照，编辑源在插件仓库。文件本身不加注释（活体须与存档逐字节一致）。

## prompts 仓库全局提示词（N03、N04、Q04，GPT 审查提出）

- N03：`CLAUDE.en.md` 第 3、33、81 行的披露、检查点、逐步验证计划三处合并；简单改动只说验证方法，依赖复杂或高风险再列逐步计划。
- N04：第 60、64 行的数字阈值改为观察线索，取消机械对应动作。
- Q04：第 70 行日志要求改为在合适边界记录可诊断失败，不要求每层捕获与每次成功调用都记录；保留显式失败与禁记敏感数据。

三条属全局提示词层，本仓不评估其影响。

## 用户目录（A8，椰椰自行执行）

部署顺序：先把 `fable-advisor-routing.md` 放到两侧 `~/.claude/docs/` 并确认可读 → 换 `~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md` 为新工作副本 → Cursor 真实会话确认入口生效 → 撤旧规则活体（`~/.claude/rules/fable-advisor.md`、`~/.cursor/rules/fable-advisor.mdc`，Windows 同）。

可选清理：`~/.claude/docs/fable-advisor-rule.zh.md`（v4 中文对照，自注不参与加载）；`~/.claude/rules/*.bak-*`、`~/.cursor/rules/*.bak-*` 至少各留一份可恢复版本。
