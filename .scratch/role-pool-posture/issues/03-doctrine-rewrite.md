# 03: 准则重写 —— orchestration skill 全部英文运行时文本

**What to build:** 任何主代理读到 orchestration skill 时，看到的是"角色 × 档位 × 车道 × 姿态"的 doctrine，而不是"按模型身份分模式"：第一原则与主代理档位无关；委派边界随姿态；三角色（explorer / worker / advisor）× 三档位（light / standard / senior）；车道用机制名（grok / codex / claude / handoff）；两段式路由先定（角色, 档位）再在填充里做帕累托；升级路径是"一张返工票失败 + 归因"；承诺边界并入对任何主代理都适用的决策类型门；Tier 3 变成 advisor 的 `验收` 形状。前言压到三行（姿态行 / GAPS 行 / 报告形状行，报告头 `WORKER REPORT`）。Claude Code 分支文件更正 "grok has no such knobs"、补 `effort` 与 `mode` 两节、改名、`implementer` → `worker`。Cursor 分支文件写清 GPT 家族经 Shell 跑 codex runner、无 receipt gate（fail open、主代理判 receipt）、不枚举 allowlist。handoff 文件只改车道名。

**Blocked by:** None（可立即开始；接口以 spec 为准，不等 01 / 02 落地）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` 的 Solution 与 "概念层（doctrine）" 节为约束性内容；术语以根目录 `CONTEXT.md` 为准。范围：`plugin/skills/orchestration/` 下五个英文 md（中文孪生归 05 票）。产物类别：准则散文。

- [x] `SKILL.md`：第一原则改为 spec 的三句；"delegation boundary" 节改为随姿态（编排姿态下按产物类别、实现姿态下主代理可直接改）；新增姿态选择器与默认规则；车道表改机制名并去掉"Route here when"式的路由时机（时机归角色与档位）；两段式改写；升级路径改写；"Commitment boundaries" 改为决策类型门清单（含"宣告完成前 → advisor 验收形状"）；Verification 的 Tier 3 改措辞
- [x] `SKILL.md` 词数 ≤ 约 1.9k（`wc -w`）；harness 判别句与两个分支文件指针保留
- [x] `lane-preamble.md` 为三行：姿态行（持有 Files 范围内交付物；机器级"架构师不碰交付物"规则不适用；拆分派发是车道自己的事）、GAPS 定义行、报告形状行（`WORKER REPORT`，OBJECTIVE / CHANGES / VERIFIED / GAPS）
- [x] `lanes-claude-code.md`：车道改名；`implementer` → `worker`；grok deltas 节更正并写 `effort`；新增 `mode` 节（按 spec 接口描述，不写具体只读 flag）；`IMPLEMENTER REPORT` → `WORKER REPORT`
- [x] `lanes-cursor.md`：车道改名；GPT 家族经 Shell 跑 codex runner（pending / receipt 照走、无 gate、fail open）；不出现任何 allowlist 型号枚举；`implementer` 消失
- [x] `handoff-lane.md`：车道名同步
- [x] 结构化 grep：`Routine lane`、`Cross-vendor lane`、`In-house lane`、`architect tier`、`advisor-only`、`IMPLEMENTER REPORT`、`no such knobs`、`implementer` 在五个文件中为零；`posture`、`explorer`、`worker`、`advisor`、`light`、`standard`、`senior`、`mode` 出现
- [x] 不改动 `plugin/agents/**`、`plugin/scripts/**`、`docs/zh/**`

## Comments

2026-09-11 — 已实现（同模派发，inherit）。退役短语 grep exit 1；`SKILL.md` 1955 词（预算约 1.9k，超 5 词，接受）；zh 镜像测试 7/7（文件集未变）。架构师通读 `SKILL.md`、前言全文与两个 harness 文件的新增节，语义与 ADR 0014 十五条决策一致。`handoff-lane.md` 无旧车道名，未改。待办：02b 的 `empty_report` 错误类需补进 `lanes-claude-code.md`（并入 04 票）。
