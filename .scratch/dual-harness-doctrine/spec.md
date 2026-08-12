# 双 harness 单源准则：Cursor 原生子代理车道

Status: ready-for-agent

## Problem Statement

用户同时在 Claude Code 与 Cursor 里工作，希望在 Cursor 里也运行架构师模式。Cursor 原生支持多厂商模型的子代理委派（Task 调用可直接钉 Grok 4.5、GPT-5.6 Sol、Opus、Fable 等），两条 CLI 车道的存在理由（本 harness 调不到其他厂商）在 Cursor 侧不成立。但 Cursor 会通过兼容路径加载已安装 Claude 插件的 skill 与 agents（实测：Cursor 会话中的 orchestration skill 来自 `~/.claude/plugins/cache/fable-advisor/3.8.0/`，`fable-advisor` 子代理类型同时可用）——若另写一份平行的 Cursor 版 skill，最好情况是同名遮蔽（skill 的遮蔽行为文档未确认），最坏情况两份同时生效；且项目级遮蔽只护住单个仓库，其他项目里 Cursor 读到的仍是满是 runner 指令的版本。

## Solution

单一来源、双 harness：同一份 orchestration skill 同时承载两套车道调用方式，会话按所处 harness 取用对应小节；agents 文件做双兼容加固而非复制。harness 无关的准则（成本纪律、两阶段路由、五部 spec contract、三层验收、commitment boundaries）一字不动；Claude Code 的 runner + pending/receipt + receipt gate 流程一字不动。经济学叙述不变——Cursor 各模型额度池独立、单价差依然存在，"贵模型出判断、便宜模型出体量"原样成立。

已实测验证（2026-08-12，本仓库 Cursor 会话）：Task 钉 `grok-4.5` 与 `gpt-5.6-sol` 各完成一个五部 spec 只读任务，报告行号引用抽查全对，格式契约与行数预算均守住；无需预配代理文件。

## User Stories

1. 作为 Cursor 用户，我希望装了本插件后 orchestration skill 直接指导会话用 Task 钉模型委派实现，从而不需要安装任何外部 CLI。
2. 作为 Claude Code 用户，我希望 runner/receipt/receipt-gate 流程在这次改动后语义完全不变，从而已有工作流零迁移成本。
3. 作为同时使用两个 harness 的用户，我希望只有一份 skill 与一套 agents 文件生效，从而不会出现两份准则打架或过期副本误导路由。
4. 作为 Cursor 架构师会话，我希望 Routine lane 落在 Grok 4.5 子代理上，从而机械性任务走最便宜的独立额度池。
5. 作为 Cursor 架构师会话，我希望 Cross-vendor lane 落在 GPT-5.6 Sol 子代理上，从而正确性关键任务获得第二家独立实现。
6. 作为 Cursor 架构师会话，我希望 In-house lane 与 Judgment（fable-advisor）继续以子代理形式可用，从而四条车道语义在两个 harness 一致。
7. 作为 Cursor 架构师会话，我希望竞跑模式（同 spec 双车道）表达为单消息并行 Task 派发，从而保留三厂商置信的选项。
8. 作为 Cursor 用户，我希望 `fable-advisor` 的只读约束在 Cursor 侧真实生效（`readonly: true`），从而顾问不可能顺手改文件。
9. 作为 Cursor 用户，我希望即使 Cursor 加载了插件的 Stop hook，receipt gate 也天然放行（无 `.fable-advisor/pending/` 即通过），从而不产生误拦截。
10. 作为新用户，我希望 README 有 Cursor 使用说明，从而不必读源码就能在 Cursor 里跑起该模式。
11. 作为插件用户，我希望版本号随语义变更递增，从而 `claude plugin update` 后两个 harness 同时吃到新版。
12. 作为在 Cursor 里遇到特别难任务的架构师，我希望文档明说 effort 档位差异（临时钉模型时档位焊死在槽位里，方括号参数需代理文件），从而知道何时值得补一个 `.cursor/agents/` 文件。

## Implementation Decisions

- `skills/orchestration/SKILL.md`：车道表 Invoke 列改为按 harness 双写；"The CLI lanes — runners, not agents" 一节之前新增短小节说明 harness 判别（会话有 Task 工具且无 runner 可执行路径即 Cursor 侧）与 Cursor 调用方式（五部 spec 直接作子代理 prompt、报告带内返回、无 receipt 机制、验收全靠三层协议）；Parallelism 一节补一句 Cursor 的单消息并行 Task 表达；dispatch-not-probes 规则原样留在 Claude Code 节（3.8.0 已去掉登录态探测，该规则是禁令本身，非探测残留）；Handoff 车道 harness 无关，不动。
- `agents/fable-advisor.md`：frontmatter 加 `readonly: true`（Cursor 不识别 `tools:` 字段，只读约束当前在 Cursor 侧失效；Claude Code 忽略未知字段，无副作用）。`model: fable` 别名在 Cursor 的解析待实测——不解析则回落 inherit，旗舰会话下等价，结果记入 ADR。
- `agents/implementer.md`：同样实测 `model: opus` 在 Cursor 的解析，仅记录结论，不改契约文本。
- `docs/adr/0010-dual-harness-single-source.md`：新建，中文，沿 ADR 0009 结构；记录"单源双 harness 而非平行版本"的决策、Cursor 兼容路径加载的实测证据、别名解析结论、复盘条件（Cursor 兼容路径策略变更或 skill 遮蔽行为文档化时重估）。
- `README.md`：新增 Cursor 使用小节（无 CLI 要求、车道映射、effort 档位差异一句话）；Upgrading 段追加 v3.9 一句并链接 ADR 0010。
- `.claude-plugin/plugin.json`：3.8.0 → 3.9.0（车道调用语义扩展，沿 minor 先例）。
- 经济学叙述不改写（用户裁定：Cursor 各模型独立额度池，价差与省钱原则原样成立）。

## Testing Decisions

- 无新增自动化测试：改动为纯文档/frontmatter，可执行验证器仅有既有 `tests/test_receipt_gate.py`（不触碰，保持绿）。
- 最高接缝为活体委派干跑：Cursor 会话中 Task 钉 Grok 4.5 与 GPT-5.6 Sol 各跑一个五部 spec 任务，报告过三层验收 Tier 1（行号引用抽查），复现 2026-08-12 的验证。
- `readonly: true` 的验证是行为测试：Cursor 侧派发 fable-advisor，确认其无法编辑文件。
- Claude Code 节语义不变的验证是路径限定 diff 审读：runner/receipt/receipt-gate 相关文本零改动。

## Out of Scope

- Cursor 专版 skill、`.cursor/agents/` 代理文件、`.cursor-plugin/` 打包与 Marketplace 分发（effort 旋钮需求真实出现时再立项）。
- runner、receipt、receipt gate 的任何代码改动。
- Handoff 车道的任何改动。
- README 经济学叙述的改写。
- 上游同步（见 ADR 0001）。

## Further Notes

- 澄清一处早期讨论的误会：dispatch-not-probes 规则不删。3.8.0（ADR 0009）已移除登录态探测；该规则是"以派发定可用性"的禁令本身，留在 Claude Code 节，Cursor 节无 CLI 可探故不出现。
- effort 档位差异要有预期：Cursor 临时钉模型时档位焊死在模型槽位里（如 Sol 为 medium 档），原 codex 车道的 `effort: xhigh/max` 只有代理文件的方括号参数（`gpt-5.6-sol[effort=high]`）才能取回。
- 生效路径：改仓库 → bump 版本 → `claude plugin update fable-advisor@fable-advisor`，两个 harness 同时更新。
