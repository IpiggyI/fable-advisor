# 02 — receipt gate 不再重复拦截

**What to build:** 一次收尾里 receipt gate 只拦一次，而不是反复拦到撞上 harness 的连续阻断上限才被强制放行。harness 在触发上限时会明确要求：Stop 类 hook 应当检查输入中的 `stop_hook_active`，为真时返回成功。当前实现根本没读这个字段。

**只修这个 bug，机制一律不动。** 不降级为不阻断的警告（`systemMessage` 是 user-facing、不喂给模型，降级等于让 gate 对模型彻底失效），不加豁免开关（模型自己就能 waive，棘轮价值归零），不加并发归属判定（先修 bug 观察；若一次拦截仍嫌吵，那时的痛点才是已验证的）。

同时把这七条外部行为固化成一个入库的回归脚本。仓库目前没有任何测试框架或 `package.json`，既有实践是一次性探针；这个脚本是该实践的第一次入库固化，风格沿用它：零依赖、自包含、输出即证据。

测试只测进程边界的外部行为——stdin 收 JSON，产出 exit code 与 stderr。不得触碰内部实现细节，重构内部结构时测试必须仍然通过。

**Blocked by:** 无 — 可立即开始。只碰 receipt gate 脚本与一个新的测试脚本，与其余票零文件重叠，可与 01 并行。

**Status:** ready-for-agent

**Spec:** `.scratch/model-routing-and-receipt-gate/spec.md`

- [x] `stop_hook_active` 为真时放行（exit 0），即使存在无 receipt 的 pending spec
- [x] `stop_hook_active` 字段缺失时行为完全不变：有孤儿 spec 则 exit 2 并在 stderr 给出原有提示
- [x] `stop_hook_active` 为 false 时行为完全不变：有孤儿 spec 则 exit 2
- [x] pending 目录不存在时 exit 0
- [x] pending spec 有 `complete` receipt 时 exit 0
- [x] pending spec 的 receipt 非 complete 时 exit 2，stderr 指明实际的 error_class
- [x] stdin 为非法 JSON 时 exit 0（既有的 fail-open 行为不得改变）
- [x] 回归脚本入库：零依赖、自建临时目录、逐例断言 exit code、一条命令跑完七例并打印通过/失败汇总
- [x] hook 注册配置未改动
- [x] gate 仍以 exit 2 阻断，未降级为不阻断的警告
- [x] 未新增任何豁免/waive 开关
- [x] 未新增并发归属判定（宽限窗口、in-flight 锁、transcript 归属均不在本票范围）

## Comments

2026-07-25 — 已实现并通过双轴评审；验收清单逐项核对通过（回归证据见 tests/test_receipt_gate.py 7/7，决策记录见 docs/adr/0005）。
