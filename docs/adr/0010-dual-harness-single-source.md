# 0010 — 双 harness 单源准则：Cursor 原生子代理车道

- **Status**: accepted
- **Date**: 2026-08-12
- **影响范围**: `skills/orchestration/SKILL.md`、`agents/fable-advisor.md`、`README.md`、`.claude-plugin/plugin.json`
- **关联决策**: [ADR 0009](./0009-grok-lane-dewrapper-runner.md)（runner 直辖与 dispatch-not-probes，本次原样保留于 Claude Code 节）、[ADR 0008](./0008-context-discipline.md)（三层验收，Cursor 侧成为唯一验收机制）

## 背景

Cursor 原生支持多厂商模型的子代理委派：Task 派发可按次钉定模型（Grok 4.5、GPT-5.6 Sol、Opus、Fable 等），两条 CLI 车道的存在前提（本 harness 调不到其他厂商）在 Cursor 侧不成立。

事实核验（2026-08-12，本仓库 Cursor 会话，第一方）：

- Cursor 经 Claude-plugin 兼容路径加载了已安装插件——orchestration skill 来自 `~/.claude/plugins/cache/fable-advisor/3.8.0/`，`fable-advisor` 子代理类型同时可用。
- Task 钉 `grok-4.5` 与 `gpt-5.6-sol` 各完成一个五部 spec 只读任务，无需预配代理文件；报告行号引用抽查全对，格式契约与行数预算守住。
- `model: fable` 别名在 Cursor 解析成功（子代理系统提示声明 "powered by Fable 5"，自报告证据）。
- `tools: Read, Grep, Glob` 字段被 Cursor 忽略：3.8.0 的 advisor 在 Cursor 侧工具全开（含 Write/StrReplace/Delete/Shell），只读性仅剩行为约定。
- 官方文档确认（经 Cursor 文档代理，2026-08-12）：subagent frontmatter 支持 `model`（含 `gpt-5.6-sol[effort=high]` 式方括号参数）与 `readonly`，无 `tools` 字段；skill 与 agents 的兼容加载路径含 `.claude/` 系；同名 skill 的遮蔽行为未见文档确认。

由此平行 Cursor 版 skill 不可行：最好情况同名遮蔽（未确认），最坏情况两份准则同时生效；且项目级遮蔽只护住单个仓库，其他项目里 Cursor 读到的仍是满是 runner 指令的插件缓存版。

## 选项对比

| 方案 | 优点 | 缺点/风险 |
|------|------|------|
| 平行 Cursor 版 skill（`.cursor/skills/`） | 各 harness 文本纯净 | 双份生效或依赖未确认的遮蔽行为；平行真相源，改一漏一；只护住单仓库 |
| `.cursor/agents/` 车道代理文件 + Cursor 版 skill | effort 方括号参数可用 | 同上，另加一组要维护的代理文件；实测证明临时钉模型已够用 |
| **单源双 harness（选定）** | 一份准则一处改；共享准则（成本纪律、两阶段路由、spec contract、三层验收）本就 harness 无关 | SKILL.md 承载两套调用小节，读者须按 harness 取用；文件继续变长 |

## 决策

1. `skills/orchestration/SKILL.md` 改为双 harness 单源：车道表 Invoke 列按 harness 双写；"The CLI lanes" 节标注 (Claude Code)、正文零改动；新增 "The lanes in Cursor" 节（harness 判别、五部 spec 直接作子代理 prompt、无 pending/receipt/receipt gate、改道规则、effort 档位差异、额度经济学不变）；Parallelism 补 Cursor 竞跑表达。dispatch-not-probes 规则原样留在 Claude Code 节——它是"以派发定可用性"的禁令（ADR 0009 追记），非探测残留；Cursor 节无 CLI 可探故不出现。
2. `agents/fable-advisor.md` frontmatter 加 `readonly: true`：Cursor 侧取回机制强制的只读（`tools:` 字段失效已实测证实）；Claude Code 忽略未知字段，`tools:` 行保留不动。
3. runner、receipt、receipt gate、Handoff 车道零改动。receipt gate 在 Cursor 侧被加载亦无害：Cursor 流程不产生 `.fable-advisor/pending/`，门禁天然放行（fail open）。
4. 经济学叙述不改写（用户裁定，2026-08-12）：Cursor 各厂商模型走独立额度池，车道间价差与成本纪律原样成立。
5. 版本 3.9.0。

## 实施代价

- SKILL.md 单文件承载两套调用机制，篇幅增长约一节；读者需先做 harness 判别。
- Cursor 侧临时钉模型的 effort 档位焊死在槽位里；取回 `effort=high/xhigh` 需按需补 `.cursor/agents/` 代理文件（本次显式不做，见复盘条件）。
- `readonly: true` 的机制生效无法在做出改动的同一会话内验证（子代理类型枚举于会话启动时固定，实测新代理文件派发被拒），行为测试推迟到插件更新后的新会话。

## 复盘条件

- Cursor 的 Claude-plugin 兼容加载策略变更，或同名 skill 遮蔽行为被官方文档化 → 重估单源 vs 平行版本。
- 出现真实需要 `effort=xhigh/max` 的 Cursor 任务 → 按需补 `gpt-5.6-sol[effort=…]` 代理文件，届时与本 ADR 的"不做"决定对账。
- 模型别名（`fable`/`opus`）在 Cursor 的解析行为变化（如回落 inherit 或解析失败报错）→ 更新 SKILL.md Cursor 节与 README。
- Cursor 子代理获得结构化回执/用量报告等价物 → 重估 Cursor 侧验收是否补机械锚点。

## 备注

- 别名解析证据为子代理自报告（系统提示声明），属弱证据但方向一致；`model: opus` 未单独实测，按同机制推定，标注为推断。
- 干跑证据存于 2026-08-12 会话：Grok 4.5 分析 `hooks/receipt-gate.py`、GPT-5.6 Sol 分析 `scripts/run-grok.mjs`，行号抽查（L17/L59、L468/L531/L543-544）全对。
- spec 与票据见 `.scratch/dual-harness-doctrine/`。

## 追记（2026-08-12）— readonly 机制强制被证伪

前提证伪：插件更新到 3.9.0 后用户在 Cursor 新会话实测（第一方），`readonly: true` 对经 Claude-plugin 兼容路径加载的 `fable-advisor` **既未从工具清单剥离可变工具，也未在调用时拦截**——与官方文档对 subagent `readonly` 字段的语义描述冲突（文档针对的可能仅是 `.cursor/agents/` 原生定义；该入口未测，记为 untested）。

修订：

1. 决策 2 的效力声明降级——`readonly: true` 保留在 frontmatter（无害、语义有文档背书、Cursor 侧解析行为改善即自动生效），但**不得声称机制强制**。Cursor 侧 advisor 的只读性现状：仅行为约定（agent 章程"never implement"）；Claude Code 侧仍由 `tools:` 白名单机制强制。
2. README Upgrading 段的 "mechanically enforced" 措辞同步更正。
3. 若需要 Cursor 侧机制强制，已知候选是 Cursor hooks 的 `preToolUse` 拦截（按 agent 过滤写类工具），本次不做——advisor 是低风险只读咨询角色，行为约定 + 验收纪律够用；出现 advisor 越权写文件的真实事故即触发重估。

复盘条件追加：Cursor 对插件兼容路径 agent 的 `readonly` 解析生效（版本说明或实测确认）→ 撤销本追记的降级措辞；`.cursor/agents/` 原生定义的 `readonly` 行为若被实测（生效或同样失效）→ 补录结论，更新上面的 untested 标注。

## 追记（2026-08-12，第二批）— frontmatter `model:` 不被采纳，裸派发 inherit 父模型

前提证伪（用户第一方实测）：在 Cursor 里裸派发 `subagent_type: fable-advisor`（不带 dispatch 级 `model` 参数）得到的是**父会话模型**，frontmatter 的 `model: fable` 未被采纳；要落到 Fable 必须在派发时显式钉 `model: claude-fable-5-thinking-high`。无法从该测试判别是 `fable` 别名不解析还是插件兼容路径 agent 的 `model` 字段整体被忽略（判别探针：`.cursor/agents/` 原生定义带具体模型 id 的 agent，未测）。

连带更正本 ADR 背景节第三条：早先"`model: fable` 在 Cursor 解析成功"的探针存在混杂变量——探针从 Fable 5 父会话发出，"自报 Fable 5"与 inherit 父模型不可区分，该结论作废，以本追记为准。

危害与修订：

1. 危害不对称——旗舰父会话下 inherit 无损（advisor 价值退化为上下文隔离，与 README 无 Fable 时的既有定位一致）；**advisor-only 模式（非旗舰会话）下裸派发 advisor 静默降级**，是 README quiet-fallback 警告的 Cursor 变体，且无任何报错。
2. SKILL.md Cursor 节 Invocation 条改为"每次派发显式钉模型"，并写明 frontmatter `model:` 不被采纳、裸派发 inherit 的事实；README Cursor 节同步加一句。
3. 版本 3.9.1（操作性准则更正，patch 级，沿 3.2.1 patch 先例）。

复盘条件追加：Cursor 开始采纳插件兼容路径 agent 的 frontmatter `model:`（版本说明或判别实测确认）→ 收回"必须 dispatch 级钉模型"的强制措辞，降回建议。
