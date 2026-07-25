# 01 — 建立术语表 CONTEXT.md

**What to build:** 仓库有一份根目录术语表，把四组最容易记混的概念钉死，后续几张票的散文重写都从这里取词。最要紧的一组是两条护栏：spawn 护栏与 receipt gate 针对的是**两类不同威胁**，其中一条的适用对象在 codex 车道去 wrapper 之后变了——这个混淆在本次讨论中已经真实发生过一次。

术语表只放术语，不放实现细节、不放实现决策、不当草稿纸。它是词汇表，仅此而已。

**Blocked by:** 无 — 可立即开始。这是 prefactor：03/04/05 要重写多处散文，没有统一口径就会各写各的。

**Status:** ready-for-agent

**Spec:** `.scratch/model-routing-and-receipt-gate/spec.md`

- [x] 根目录存在 `CONTEXT.md`，遵循 domain-modeling 的 CONTEXT 格式（术语 + 一到两句定义 + `_Avoid_` 标出应回避的近义说法）
- [x] 定义 **spawn 护栏**：PreToolUse、fail closed、针对 CLI lane 子代理被命名派生后绕过工具白名单而静默自实现
- [x] 定义 **receipt gate**：Stop hook、fail open、针对**主会话自己**排了 codex spec 却不跑、或把非-complete receipt 当完成
- [x] 两条护栏的定义各自点明「针对谁」，使二者不可互换；`_Avoid_` 中标出把它们混称为「护栏」的说法
- [x] 定义 **lane** 三类（Routine / Cross-vendor / Fallback）及其判别依据
- [x] 定义 **架构师层** 与 **advisor-only**：由会话模型身份决定的两种工作模式
- [x] 定义 **别名槽位**：`opus`/`sonnet`/`haiku`/`fable` 是可被环境变量重定向的指针，不是模型身份；`_Avoid_` 中标出「跑在 Opus 槽 = 跑 Opus」的说法
- [x] 全文不含任何具体第三方型号（名单属于用户私有规则，不入库）
- [x] 全文不含文件路径、行号、代码片段或实现决策

## Comments

2026-07-25 — 已实现并通过双轴评审；验收清单逐项核对通过（回归证据见 tests/test_receipt_gate.py 7/7，决策记录见 docs/adr/0005）。
