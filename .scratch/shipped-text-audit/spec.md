# 发布文本规范排查（2026-10-17）

Status: resolved

## 目标

按项目规范排查 `plugin/**`、`docs/zh/**` 与 `README.md`，列出违规处。只读排查；修改另起。

## 规范

- N1 发布文本措辞：`AGENTS.md`「Wording of shipped text」。
- N2 规范记法：`AGENTS.md`「Canonical notation for the user's declarations」。
- N3 中文镜像内容一致：`AGENTS.md`「Chinese mirror of runtime docs」（测试只查存在）。
- N4 单一语言：英文文件不夹中文正文，中文文件不夹未翻译的英文正文；代码格式标识符、专有名词、标准缩写、`CONTEXT.md` 定义的术语除外。
- N5 术语表用词：`CONTEXT.md` 的术语与 `_Avoid_`。

## 计划

四张只读契约，互不依赖，同时派发；车道 claude，`explorer` @ `mainstay`，拨盘 `haiku-5-5[high]`。

| 契约 | 读取范围 | 规范 |
|---|---|---|
| E1 | `plugin/skills/**/*.md`、`plugin/agents/*.md`、`plugin/.claude-plugin/plugin.json`、`plugin/hooks/hooks.json`；`README.md` 只查 N2 | N1、N2、N4、N5 |
| E2 | `plugin/scripts/*.mjs`、`plugin/hooks/*.py` 的注释与面向用户的消息 | N1、N2、N4 |
| E3 | `docs/zh/skills/orchestration/SKILL.md`、`docs/zh/skills/orchestration/lanes-claude-code.md` 对照英文原件 | N3、N4、N1、N5 |
| E4 | `docs/zh/**` 其余文件对照英文原件 | N3、N4、N1、N5 |

主代理逐条核对报告引文与原文，再判定是否违规。

## Batch checks

无宽检查；排查只读。

## 结果

四份报告已回收；主代理逐条对照原文核对。以下为确认项，现有测试都不拦截。

### 英文发布文本

1. `plugin/hooks/receipt-gate.py:3`：「the architect」。N5：`CONTEXT.md`「主代理」条 `_Avoid_` 禁止与「架构师」等同；改「the main agent」。
2. `plugin/hooks/receipt-gate.py:11`：「not the primary guardrail」。N5：`CONTEXT.md`「receipt gate」条 `_Avoid_` 禁止笼统称 guardrail。
3. `plugin/skills/orchestration/lanes-cursor.md:9` 与中文孪生：「even when an example names another generation」。N1：评论文本自身的示例，与测试禁用的「example may name」同类。
4. `plugin/skills/orchestration/routing-profile.md:10` 与中文孪生：「these are examples, not a complete list」。N1：评论列表省略了什么。该句是椰椰的第一人称声明，改不改由椰椰决定；不改表格单元格，属 patch。

### 中文镜像

5. `docs/zh/skills/orchestration/routing-profile.md:1`：标题后缀「（中文译本，不随插件发布）」。N1 与 N3：英文标题无此后缀。
6. 决策形状与验收形状写成 `decision`、`acceptance`。N5：`CONTEXT.md:14` 与中文档案第 37–38 行用「决策形状」「验收形状」。位置：`docs/zh/agents/advisor-{l,md,h,xh}.md:16,25`、`docs/zh/agents/worker-{md,h,xh}.md:24`、`docs/zh/skills/orchestration/SKILL.md:50,155,163`、`docs/zh/skills/orchestration/lanes-claude-code.md:154`。
7. `docs/zh/skills/orchestration/SKILL.md:71`：引用「重路由」，该文件的节名是第 92 行「改道」。N3：中文交叉引用指向不存在的标签。
8. `docs/zh/skills/orchestration/lanes-claude-code.md`：第 21、135 行「合同」（全文其余处为「契约」）；第 123、125 行「收据」（其余处为 receipt）；第 123 行「执行器」（英文为 runner）。N5。
9. `subagent` 与「子代理」并用：`docs/zh/skills/orchestration/lanes-cursor.md:1,3,26,28`、`docs/zh/skills/orchestration/lanes-claude-code.md:3`；其余 21 处为「子代理」。N5。
10. `skill` 与「技能」并用：`docs/zh/agents/advisor-h.md:27`、`docs/zh/skills/orchestration/lanes-cursor.md:3`、`docs/zh/skills/orchestration/lanes-claude-code.md:29,102`；`SKILL.md:100` 为「技能」。N5。
11. `profile` 与「档案」并用：`docs/zh/skills/orchestration/SKILL.md:96`（节名）、`:106`；`docs/zh/skills/orchestration/handoff-lane.md:3` 引用该节名，同改。N5。
12. `docs/zh/skills/orchestration/SKILL.md:161` 用「片段」，`:163` 用 `hunk`。N5。

### 可选项（项目无对应规则）

- 中文镜像里的裸英文词：`frontmatter`、`allowlist`、`slug`、`session id`、`pending`、`teammate`、`worktree` 等。镜像普遍保留英文术语，项目没有禁止规则。
- 「强度」与 `effort`、「票」与「票据」、`verdict` 与「裁决」在中文镜像里混用；`CONTEXT.md` 自身两种都用。

### 已否决

- `plugin/skills/orchestration/SKILL.md:44`「capability level」：`CONTEXT.md:61` 的 `_Avoid_` 以 `SKILL.md` 用 level 解释档位为前提。
- 「Fable」作家族名（`lanes-claude-code.md:19`、`README.md:58,63`）：家族名不是型号声明。
- `routing-profile.md:55-57` 的 `[medium]` → `explorer-md`：强度到 agent 文件的映射，不是拨盘。
- `README.md:127` 的 `gpt-6-sol`：6.0.0 升级说明记录当时的型号名。
- `handoff-lane.md:9`「This is deliberate」与 `routing-profile.md:9`「One order is deliberate」：后接 because 子句，属规则理由。
- `SKILL.md:94`「the profile's ranking」：指档案的「Model ranking」一节，该节按定位分段。
- `lanes-claude-code.md:23`「the codex walkthrough is canonical」：读法指引，不评论文本来历。

### 机械检查（2026-10-17）

- 两处版本号一致：`6.4.0`。
- 5.2.0 起每个发布都有说明书：5.2.0、6.0.0 至 6.4.0。
- `tests/test_routing_profile_parity.py` 29/29 通过；`tests/test_user_level_archive.py` 5/5 通过。
- ADR 0025 至 0032 修订的前序 ADR 都已在状态行加反向指针；ADR 0032 第 39 行是复盘条件，不是修订。
- 第 5 项的标题后缀不被 `tests/`、`docs/agents/` 引用。

### 未覆盖

`docs/adr/**`、`CONTEXT.md`、`docs/agents/**` 等协调件的措辞；`tests/**` 与 `scripts/**` 的注释；`README.md` 除记法之外的内容。

## 修复计划（2026-10-17，椰椰选定：全部修复；档案第 10 行改为「Specialties include:」；与标题规则合成一个 patch 版本，发布与推送前再问）

- 一张契约 F1，覆盖确认项 1–12；文件互有重叠，不拆分。
- 车道：claude 车道同模型派发，`worker-md` + `opus`，拨盘 `opus-5-5[medium]`。理由：`plugin/skills/**` 的 doctrine 文本须同模型派发；grok runner 的 implement 模式要求干净工作树，而工作树有本次之前的改动与未提交的标题规则改动，提交须另行授权。
- 判定检查：契约内的 grep 与 Python 检查，加 `tests/test_zh_mirror.py`、`tests/test_shipped_wording.py`、`tests/test_routing_profile_parity.py`。
- 验收后：写 `docs/manuals/6.4.1.html`、改两处版本号，推送前问椰椰。

## 验收（2026-10-17）

F1 已验收。依据：worker 报告的检查输出（三个测试全过；英文旧措辞 grep 无输出；中文术语扫描只剩 `SKILL.md:100` 链接目标 `routing-profile.md` 的误报与 `advisor-*.md:31` 的 `hunk`），主代理逐文件读了 `git diff --word-diff`，并抽查了 `lanes-claude-code.md:123-125`、`lanes-cursor.md:9` 的中文原文。16 个改动文件都在 Files 内。

遗留：
- 中文 `advisor-{l,md,h,xh}.md:31` 仍写 `hunk`，中文 `SKILL.md` 已统一为「片段」；不在第 12 项范围内，记为可选项。
- `receipt-gate.py:11` 现为「this gate only backstops the main session itself; it is not the primary check.」，已不用 guardrail；后半句仍是与未点名对象的比较，记为可选项。

## 发布（2026-10-17）

6.4.1 补丁版本：说明书 `docs/manuals/6.4.1.html` 已验收，两处版本号已改。椰椰选择只本地提交、不推送；推送、两侧更新与伴生安装器留给椰椰。
