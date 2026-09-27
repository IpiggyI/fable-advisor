# 05：发布 6.0.0

Status: ready-for-agent
Blocked by: 04

**要做什么：** 两侧装上 6.0.0，活体档案等于编辑源；全部测试与全仓文字扫描通过；新表每个拨盘经已安装的插件实际运行一次，并有会话记录为证。每个发布步骤都在用户当次授权后执行。

**负责的要求：** `../spec.md` 第八节 REL-1 至 REL-4；第九节第 5 项全仓扫描；第十四节全部（最终排除）；O1 的询问。

**范围（Files）：** 两处版本字段；发布提交按文件名暂存。

**执行方式：** 版本字段是协调件，主代理直接改；提交、推送、两侧更新、运行安装器需用户授权（REL-2、S7）。

## 实施必读

- `docs/agents/plugin-release.md` 第 1–6 步。
- `../spec.md`：第八节"发布"；第九节；第十二节 S7；第十四节；第十五节（不暂存的文件）。
- 工单 01–04 的 Comments 与各自的"Held for batch acceptance"。

## 验收

- [ ] 两处版本字段为 `6.0.0`。
- [ ] 测试全部退出 0：`test_runner_contract.py`、`test_runner_lifecycle.py`、`test_zh_mirror.py`、`test_receipt_gate.py`、`test_lane_family_gate.py`、`test_install_user_level.py`；`test_user_level_archive.py` 在安装器运行之后执行；`git diff --check` 干净；`SKILL.md` ≤ 2160 词。
- [ ] 全仓文字扫描零命中（`../spec.md` 第九节第 5 项的范围与例外）；结果回填到 01、03 的"Held for batch acceptance"。
- [ ] 第十四节逐条排除，结果写入 Comments。
- [ ] 询问用户 O1（是否提交本任务记录与溯源材料），按答复执行。
- [ ] （需授权）按文件名暂存、`git diff --cached --stat` 复核、提交、推送；未跟踪的无关文件不暂存。
- [ ] （需授权）两侧 `claude plugin marketplace update` 与 `claude plugin update`；缓存出现 `6.0.0` 且抽查命中本版新增短语。
- [ ] （需授权）两侧运行伴生安装器；两个家目录 `--check` 退出 0；`test_user_level_archive.py` 退出 0；结果回填到 03 的"Held for batch acceptance"。
- [ ] REL-4：用已安装的插件逐拨盘派发一次（codex 10 个、grok 3 个、claude 13 个，清单见 `../spec.md` REL-4），观测表列出每次的会话 id 与会话记录中的型号（codex、grok 另列强度）；任一拨盘不符按 S1 停下回报。
- [ ] 在 `../spec.md` 的 Comments 追加实施记录：各票结论、未核实项（如 PRB-3 未回报、claude 车道强度不可观测）、遗留。

## Held for batch acceptance

- 无（本票即批次执行处）。

## Comments

### 2026-09-27 — 发布前检查（主代理）

版本字段：`plugin/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` 的 `plugins[0].version` 均为 `6.0.0`（JSON 解析核对）。

测试（工作树，发布前）：`test_runner_contract.py` 19/19、`test_runner_lifecycle.py` 退出 0、`test_zh_mirror.py` 15/15、`test_receipt_gate.py` 8/8、`test_lane_family_gate.py` 18/18、`test_install_user_level.py` 8/8；`git diff --check` 退出 0；`wc -w SKILL.md` = 2160。`test_user_level_archive.py` 按规定在真实家目录运行安装器之后执行——待授权。

全仓文字扫描（范围：`plugin/`、`docs/zh/`、`README.md`、`CONTEXT.md`、`AGENTS.md`、`docs/agents/`、两个清单）：命中只剩 `CONTEXT.md` 第 41、49 行（`_Avoid_`）与 README 第 126 行（v6.0.0 升级说明中的旧列名及 v5.2.0 历史描述），均属例外；中文译法扫描零命中。已回填 01、03 的"Held for batch acceptance"（全仓扫描一项）。

第十四节逐条排除：
- runner 换名继续换型号：`run-codex.mjs` 只调用一次 `executeCodex`，无任何重试分支；红灯证明见工单 01。排除。
- 白名单接受 `gpt-5.6-*` 或拒绝 `gpt-6-*`：契约测试覆盖两向。排除。
- 回退测试被删除：两个用例改写并改名为 `codex no model switch*`，报告模式断言改写。排除。
- 生命周期测试在参数校验处退出：新增 `model_used` 断言。排除。
- `SKILL.md` 换名保留首轮池或 senior 门、把车道顺序写成格内顺序、写进型号取值：advisor 与主代理核对，型号名集合与基线相同。排除。
- 档案重排格子：逐格比对零差异。排除。
- ≤ 写成同级、haiku 与 composer 进排名：档案"Model ranking"一节保留 ≤ 方向并注明二者不排级。排除。
- Cursor explorer 保留 Claude 优先或丢 composer：RP-8 比对零差异。排除。
- advisor 映射写错格：档案"Advisor mapping"为验收 `mainstay` 默认、决策 `mainstay` 的 `medium`、低置信 `crux`、`rescue` 凭声明。排除。
- `worker-md`、`advisor-h` 自述与内置 Explore：已改；README 第 107 行"`advisor-h` is the default dial"由 code-review 发现，返工后删除。排除。
- 实机核对只看回执：工单 02 以会话记录为证；REL-4 待发布后执行。部分待定。
- 只改活体未改编辑源：本批只改编辑源，活体未动。排除（活体待授权安装）。
- 说明书视觉未经查看、漏 ADR 0019/0020、改了基准：见工单 04。排除。
- README 升级段漏不兼容点或安装器：第 126 行齐全。排除。
- "cheapest adequate"残留：零命中。排除。
- "currently grok-4.6"残留：零命中；档案写跟随 CLI 默认，当前 `grok-4.7`，与工单 02 观测一致。排除。
- 换候选顺序偏离 D6、D7：`SKILL.md` Re-routing 与档案均写按车道顺序、不按书写顺序，Claude Code explorer 例外在档案。排除。
- 加观察日志或统计：无。排除。
- 引入 advisor 专题内容：说明书与正文扫描 `SessionStart|过程咨询|完成前强制` 零命中。排除。

code-review（`/code-review`，两轴 advisor，`opus`）：Spec 轴 1 项缺失（README 第 107 行，已返工修正）；Standards 轴 2 项硬性（`CONTEXT.md` "接管包"改为"接管契约"；档案首段"不复述"的承诺改为"承载取值及其依赖的格内选择规则"）与 5 项判断（测试准备重复、`processStopped` 已无读者、`CONTEXT.md` "高档位"、中文 effort/强度混用、ADR 影响范围漏列——最后一项已补）。未修的判断项作为遗留上报。
