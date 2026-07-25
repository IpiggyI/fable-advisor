# fable-advisor

本仓库的公共词汇表：钉死最易记混的术语，供编排与决策散文统一取词。只定义"是什么"，不承载实现细节。

## Language

### 护栏与门禁

**spawn 护栏**:
PreToolUse hook，fail closed；针对的是 CLI lane **子代理**——被带 `name` 派生后绕过工具白名单而静默自实现的威胁。
_Avoid_: 笼统称"护栏/guardrail"而不指明针对子代理；勿与 receipt gate 互换（二者针对两类不同威胁）。

**receipt gate**:
Stop hook，fail open；针对的是**主会话自己**——排了 codex spec 却不跑、或把非-complete receipt 当完成的威胁。
_Avoid_: 笼统称"护栏/guardrail"而不指明针对主会话；勿与 spawn 护栏互换（二者针对两类不同威胁）。

### 实现车道

**lane**:
实现工作的三条可选车道（Routine / Cross-vendor / Fallback），按任务性质与可用性择一，而非三种同义叫法。
_Avoid_: 把任意实现路径都叫"lane"而不区分三条；把车道名与具体模型型号混为一谈。

**Routine lane**:
spec 完全决定结果时的默认实现车道，经 grok CLI 执行。
_Avoid_: 把"默认"理解成"唯一"或"可随意改道而不说明依据"。

**Cross-vendor lane**:
正确性或完备性关键、需要第二家独立实现时的车道，经 codex runner 执行。
_Avoid_: 与 Routine 互换使用；把"跨厂"理解成任意备用路径。

**Fallback lane**:
两条 CLI lane 均不可用时的仓内 Claude 兜底实现车道。
_Avoid_: 把兜底当成首选或日常车道；与两条 CLI lane 并列成等价选项而不提可用性前提。

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
