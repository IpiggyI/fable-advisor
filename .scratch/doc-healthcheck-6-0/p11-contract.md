# P11 实施契约（6.1.0）

Status: ready-for-agent
Blocked by: 工单 05 推送 6.0.0（需椰椰授权）

本文件是 6.1.0 的交付契约草稿，6.0.0 推送后原样派发。依据：`review.md` 的 P11、R13、R15、RI2、PS3；[ADR 0024](../../docs/adr/0024-orchestration-files-by-lane-and-word-budgets.md)（`proposed`，派发前改为 `accepted`）。

## 派发方式

- 契约一（准则散文）：`plugin/skills/orchestration/**`（`routing-profile.md` 除外）与中文孪生，走同模派发（`AGENTS.md` "Delegation boundary by artifact class"）。
- 契约二（测试）：`tests/test_word_budget.py`，普通 `worker`。它依赖契约一落地后的实测词数，所以排在契约一验收之后。
- 验收：同族 diff 按 Tier 3，用跨厂商 advisor 的验收形状。
- 派发前核对：工作树干净时，契约二可走 CLI 车道；否则走 claude 车道并披露。

## 契约一：拆分与指针

**Objective**：按 ADR 0024 决策 2 把 `lanes-claude-code.md` 拆成 `lanes-claude-code.md`（Claude Code 的 claude 车道机制）与 `runners.md`（两个宿主共用的 runner 流程），并改写指针。验收标准：

1. 逐句比对脚本通过。基线固定为最终推送的 6.0.0 提交（含 2026-09-29 审查清单的修复，不是 `50e1151`）里的 `lanes-claude-code.md`。脚本检查三件事：遗漏（旧句不在任何新文件）、重复（旧句出现在两个新文件）、新增（新文件里有旧文件没有的句子）。例外只有三类：列明的删除、宿主条件标注、指针改写。每个例外逐条列出；删除还要说明它不改变规则含义，只列出不算豁免。
2. 按规则归属拆分（ADR 0024 决策 2）：claude 车道派发的前言规则留在 `lanes-claude-code.md`，runner 前置前言的规则进 `runners.md`。报告逐条车道列出它需要的规则及所在文件，证明第一次执行之前可达。
3. `runners.md` 里只在 Claude Code 成立的机制（两种等待方式、Bash 工具的 `timeout`、receipt gate）位于按宿主条件标注的小节里。
4. `SKILL.md` 的宿主指针改为事件句："第一次派 claude 车道之前读 …"、"第一次运行 runner 之前读 …"；`lanes-cursor.md` 原指向 `lanes-claude-code.md` 的 runner 内容改指 `runners.md`。
5. `SKILL.md` 词数不超过 6.0.0 发布时的实测值。
6. 中文孪生同步：新建 `docs/zh/skills/orchestration/runners.md`；`python3 tests/test_zh_mirror.py` 退出 0。镜像测试只查存在，所以主代理另行人工核对中文与英文逐段语义一致。
7. `grep -rn "lanes-claude-code.md" plugin/ docs/zh/ README.md` 的每个命中都指向 claude 车道内容，不指向 runner 流程。

**Files**：`plugin/skills/orchestration/SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md`、新建 `runners.md`；`docs/zh/skills/orchestration/` 下对应孪生；`README.md` 中引用被拆内容的链接。

**Interfaces**：`lane-preamble.md` 与 `lane-preamble-report.md` 不移动、不改名；agent 文件对前言路径的引用不变。

**Constraints**：只移动已定稿的文字，不改规则含义；决策类型门五项、契约五部分、"报告是声明、不是证据"留在 `SKILL.md`；不拆 `SKILL.md` 的路由、契约、验收三节；失败路径不单独成文件（(b2) 暂缓）；插件文本不带本仓内容；不做 git 写操作。

**Verification**：逐句比对脚本（车道自写，写在 `/tmp`，验收时读脚本本身）；`wc -w plugin/skills/orchestration/*.md`；`python3 tests/test_zh_mirror.py`；`git diff --check`。

## 契约二：词数预算测试（RI2）

**Objective**：新增 `tests/test_word_budget.py`，逐文件检查 `plugin/skills/orchestration/*.md` 的 `wc -w` 口径词数不超过预算。预算取契约一落地后的实测值加少量余量（每个文件余量写明），写在测试里；`SKILL.md` 的预算不超过 2210。测试要求目录里的 `.md` 文件集合与预算条目完全一致。验收标准：现状通过；把任一文件临时追加超出余量的词后失败，并在失败信息里点名文件、实测值与预算；目录里多出一个没有预算的 `.md` 文件时失败。

**Files**：`tests/test_word_budget.py`。

**Interfaces**：与现有测试同风格（`check(desc, fn)`、`PASS`/`FAIL` 行、失败时退出非 0）。

**Constraints**：不改被测文件；临时追加只在 `/tmp` 的副本上做。

**Verification**：`python3 tests/test_word_budget.py` 退出 0；对副本注入超额词数后退出非 0。

## 发布与验证

- 按 `docs/agents/plugin-release.md` 发 6.1.0：说明书、两处版本字段、推送、两侧更新，均按当次授权执行。
- ADR 0024 决策 6：实施时检索两侧全局提示词是否按名引用 "User routing profile"，结果写进 ADR 0024。
- 对照任务（在已安装的 6.1.0 上执行，依赖模型行为）：`review.md` P11 验证一节的四项。PS3 的缓解措施随之验证。
  - 执行者：Claude Code 的两项由主代理在新会话派发并读子代理与主会话的转写；Cursor 的一项由椰椰在 Cursor 执行并回报转写要点。
  - 证据落点：本文件 Comments，每项写会话 id、读取了哪些文件、通过与否。
  - 关闭条件：四项全部通过，P11 才算完成，本文件与 ADR 0024 的状态才能改为终态。任一项未执行或失败，加载行为保持未验收；运行文档与测试通过不能替代它。
