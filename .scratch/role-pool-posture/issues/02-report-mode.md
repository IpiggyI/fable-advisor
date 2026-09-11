# 02: runner —— 报告模式 `mode: "report"`（两条 runner）

**What to build:** 架构师能经 grok lane 或 codex lane 派一个**只读**角色（explorer 检索、advisor 判断）并拿回报告正文。pending spec 加 `mode`：`implement`（默认，现行语义零变化）或 `report`。报告模式下 CLI 以只读工具集启动；运行结束工作树无改动是正常态（`complete`），出现改动是新失败类 `unexpected_diff`；`files`（只读范围）与 `verification` 允许为空；receipt 新增 `mode` 与 `report`（CLI 最终消息正文）。五部字段复用，不另起 schema。receipt gate 对报告模式的 pending spec 照常管辖。

**Blocked by:** 01（非语义依赖：同一 runner 文件与同一契约测试文件，串行落地）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "runner 契约" 节。只读工具集的具体 flag（grok 的 `--tools` / `--disallowed-tools` 取值，codex 的 `--sandbox read-only`）由本票以一手探针确定，并把确定的 argv 形状固化进契约测试。

- [ ] 两条 runner 接受可选顶层键 `mode ∈ {implement, report}`；非法值 → `spec_invalid`；省略等价于 `implement`
- [ ] `mode: "report"` 时，子进程 argv 含只读工具限制参数（形状由探针确定并在测试中断言）
- [ ] `mode: "report"` 且工作树无改动 → `error_class: complete`，receipt 含 `mode: "report"` 与非空 `report`；pending 文件被删除
- [ ] `mode: "report"` 且工作树有改动 → `error_class: unexpected_diff`，不 `complete`，pending 文件保留
- [ ] `mode: "report"` 接受空 `files` 与空 `verification`
- [ ] `mode: "implement"` 与省略 `mode` 的全部既有用例零回归；`no_diff` 语义在 implement 模式下不变
- [ ] `tests/test_runner_contract.py` 覆盖以上各态，两条 runner 都跑；`python3 tests/test_runner_contract.py` 全绿
- [ ] `tests/test_receipt_gate.py` 保持绿（可加一例：报告模式 pending 无 complete receipt 仍拦）
