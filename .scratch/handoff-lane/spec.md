# Handoff lane（交接车道）：用户中介的第四条实现车道

Status: ready-for-agent

## Problem Statement

用户拥有其他 harness（Cursor、OpenCode 等）的固定订阅额度，边际成本≈0，但现有三条车道都无法利用它：每条车道都要求本会话能直接调用执行器。用户愿意充当"人肉执行器"（把 spec 复制到另一个窗口、跑完拿回结果），换取任意 harness 的灵活性与近零成本——但 doctrine 里没有这条路，架构师也不知道何时该建议它。

## Solution

新增 **Handoff lane（交接车道）**：架构师把五部 spec + 操作指南写成 `.fable-advisor/handoff/<slug>.md`，用户手动带到任意 harness 执行，完成后架构师直接审 diff + 重跑 verification 验收（不要求报告回传）。核心边界：**该车道默认不进 stage 2 候选集，仅在用户显式声明后进入**（声明属易变层）；架构师在甜点区任务上可建议、不可自动路由。receipt gate 不看 handoff 目录（放 `pending/` 会在用户离开会话期间误拦收尾），以会话末清点的软规则兜底。

## User Stories

1. 作为用户，我想声明"这个任务走 handoff"，让架构师产出一份可直接粘贴到任意 harness 的自含 spec，以便用我的免费订阅额度干活。
2. 作为用户，我想在未声明时这条车道完全不出现在路由结果里，因为它依赖我的手动操作，架构师擅自路由等于任务搁浅。
3. 作为架构师，我想在任务命中甜点区（大颗粒、spec 完全确定、不赶时间、用户声明过外部额度充裕）时建议走 handoff，但建议不阻塞、由用户拍板。
4. 作为架构师，我想在 handoff 完成后直接读 diff 并亲自重跑 verification 命令验收，而不依赖对方 harness 的报告——diff 是证据，报告只是复述。
5. 作为接收方 harness 的执行者（零上下文、不能回问），我想拿到五部 spec 之外的操作指南（建议用什么模型/模式跑），以便一次做对。
6. 作为主会话，我不想 receipt gate 因为 handoff 文件在飞就拦我收尾——handoff 目录必须在 gate 的视野之外。
7. 作为用户，我想要会话结束前架构师清点 `.fable-advisor/handoff/` 并报告未决项（完成/放弃/留待下次，说清楚），以免交接件静默积压。
8. 作为未来读者，我想在词汇表与 ADR 里看到这条车道"无机械门禁、fail-open"的定位及其理由。

## Implementation Decisions

- **改动落点（纯文档，零代码；尤其 `hooks/receipt-gate.py` 零改动——handoff 目录天然在其视野外，因为它只读 `pending/`）**：
  - 编排 skill（SKILL.md）：车道表加 Handoff 行（Producer: 用户选定的任意 harness/模型；Invoke: `.fable-advisor/handoff/<slug>.md` + 用户手动执行；Route when: 用户显式声明后）；"User routing profile" 一节加 opt-in 不变量句（英文，语义为 "The handoff lane never enters stage 2 uninvited — it is selectable only after an explicit user declaration; the architect may suggest it for large, fully-specified, non-urgent tasks, but a suggestion never routes"）；新增 handoff 流程小节：spec 文件=五部 spec + operating guide；验收=架构师读 diff + 亲自重跑 verification（无 receipt）；会话末清点软规则（对齐既有 "never leave a spec under pending/ unresolved" 措辞，注明 fail-open）；披露：产出模型族未知，架构师验收按不可信来源对待。
  - CONTEXT.md：新增 **Handoff lane（交接车道）** 词条（用户中介、无机械门禁、fail-open、默认不进候选集）；**lane** 词条枚举改为四条（Routine / Cross-vendor / In-house / Handoff）。
  - README.md：车道表加 Handoff 行（简洁风格）；如"Upgrading"段落有必要则追加一句 v3.5 条目、不改写历史。
  - `.claude-plugin/plugin.json`：version 3.4.0 → 3.5.0（新增车道=路由语义变更，沿 minor 先例）；description 是否提 handoff 由实现者判断（可不提，它是可选人工车道）。
  - ADR 0007：记录决策（用户中介车道、opt-in 边界、gate 视野外的取舍——机械门禁换灵活性，软规则兜底）。
  - `~/.claude/rules/fable-advisor.md`（仓外）：Routing profile 区块加一条——Handoff lane 声明机制（按任务/会话声明；订阅额度状态可作为持久判断记录，如"Cursor 订阅有效期内 handoff 边际成本≈0"，带日期与失效条件）。
- **帕累托坐标披露**（写进 SKILL.md Handoff 行或流程小节）：价格≈0（订阅套利）、速度最慢（人肉往返）、能力=用户当场选定、可用性=仅用户在场且声明时。
- **甜点区判据**（架构师建议的触发参考）：大颗粒 + spec 完全确定 + 不赶时间；小任务往返开销压倒收益，明确不建议。
- **与逃生门的关系**：handoff 的进入靠声明，不靠逃生门；逃生门规则零改动。

## Testing Decisions

- 无可执行校验器（纯散文变更），一次性结构化检查验收：
  1. `grep -n "Handoff" SKILL.md CONTEXT.md README.md` → 三文件均命中；
  2. SKILL.md 含 opt-in 不变量句（"never enters stage 2 uninvited" 或等义措辞）；
  3. CONTEXT.md lane 词条枚举为四条车道；
  4. SKILL.md 明确 handoff 目录在 receipt gate 视野外 + 会话末清点软规则；
  5. `git diff` 零触碰 `hooks/`、`scripts/`、`tests/`；plugin.json 仅 version（及可选 description）变更且 JSON 可解析为 3.5.0；
  6. ADR 0007 存在且风格对齐 0006。
- 好测试标准：漏改任一落点（如 lane 词条仍是三条）必被上述检查抓住。

## Out of Scope

- 任何代码/hook 改动；给 handoff 造机械门禁（那会重新引入对特定 harness 的耦合，违背这条车道的存在理由）。
- 回传报告的格式约定——验收以 diff 为准，报告可有可无。
- 对目标 harness 的任何适配、文档或集成。
- 逃生门规则、既有三车道语义。

## Further Notes

- 决策链：上游 v4.0.0 审计后的第四条路讨论；使用边界（用户声明制）由用户拍板，架构师补"可建议不可自动路由"。
- 本 spec 实施后与 ADR 0006 的两段式框架完全兼容：handoff 只是 stage 2 候选集的条件成员。
