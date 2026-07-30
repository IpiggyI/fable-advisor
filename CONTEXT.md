# fable-advisor

本仓库的公共词汇表：钉死最易记混的术语，供编排与决策散文统一取词。只定义"是什么"，不承载实现细节。

## Language

### 护栏与门禁

**receipt gate**:
Stop hook，fail open；针对的是**主会话自己**——排了 spec 却不跑、或把非-complete receipt 当完成的威胁。
_Avoid_: 笼统称"护栏/guardrail"而不指明针对主会话；勿与历史上的 spawn 护栏混同（后者针对 wrapper 子代理，已随 wrapper 一并退役，见 ADR 0009）。

### 实现车道

**lane**:
实现工作的四条可选车道（Routine / Cross-vendor / In-house / Handoff），按任务性质与可用性择一，而非四种同义叫法；其中 Handoff 是条件成员，仅在用户声明后进入候选。
_Avoid_: 把任意实现路径都叫"lane"而不区分四条；把车道名与具体模型型号混为一谈。

**Routine lane**:
spec 完全决定结果时的默认实现车道，经 grok runner 执行。
_Avoid_: 把"默认"理解成"唯一"或"可随意改道而不说明依据"。

**Cross-vendor lane**:
正确性或完备性关键、需要第二家独立实现时的车道，经 codex runner 执行。
_Avoid_: 与 Routine 互换使用；把"跨厂"理解成任意备用路径。

**In-house lane（仓内车道）**:
与架构师同族、仓内自含、无外部 CLI 依赖的实现车道；可按专长命中、上下文隔离、额度/时限声明主动路由，也承担两条 CLI lane 均不可用时的兜底。
_Avoid_: 把它当成无代价的默认选项而不披露三条固定代价（同族无跨厂评审、共享主会话额度、单价最贵）；用型号名（Opus/Sonnet）指称该车道。

**Handoff lane（交接车道）**:
用户中介的实现车道：架构师把五部 spec 与操作指南写入 `.fable-advisor/handoff/<slug>.md`，由用户手动带到自己选定的 harness 执行，回来后架构师读 diff、亲自重跑 verification 验收；无机械门禁（不在 receipt gate 视野内）、fail open，默认不在候选集内，仅在用户显式声明后成为 stage 2 的条件成员。
_Avoid_: 未经用户声明将其纳入路由候选；因"免费"把小任务也交接出去（往返开销压倒收益）；把回传报告当验收证据（证据是 diff）。

### 会话工作模式

**架构师层**:
由会话模型身份决定的工作模式：会话模型属旗舰层系列时，按编排准则写 spec 派活，只出判断、不写实现。
_Avoid_: 用具体型号名指称该模式；把"架构师"当成任意会写代码的会话。

**advisor-only**:
由会话模型身份决定的工作模式：会话模型不属于旗舰层系列时，自己实现，仅在承诺边界咨询顾问。
_Avoid_: 与架构师层混称；把"顾问"理解成另一种实现车道。

### 模型别名

**别名槽位**:
`opus` / `sonnet` / `haiku` / `fable` 这类模型别名是可被环境变量重定向的**指针**，不是模型身份。
_Avoid_: "跑在 Opus 槽位 = 跑的是 Opus"这类说法；把别名名当成已解析的具体型号。
