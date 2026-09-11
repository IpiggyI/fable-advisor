# 02: runner —— 报告模式 `mode: "report"`（两条 runner）

**What to build:** 架构师能经 grok lane 或 codex lane 派一个**只读**角色（explorer 检索、advisor 判断）并拿回报告正文。pending spec 加 `mode`：`implement`（默认，现行语义零变化）或 `report`。报告模式下 CLI 以只读工具集启动；运行结束工作树无改动是正常态（`complete`），出现改动是新失败类 `unexpected_diff`；`files`（只读范围）与 `verification` 允许为空；receipt 新增 `mode` 与 `report`（CLI 最终消息正文）。五部字段复用，不另起 schema。receipt gate 对报告模式的 pending spec 照常管辖。

**Blocked by:** 01（非语义依赖：同一 runner 文件与同一契约测试文件，串行落地）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "runner 契约" 节。只读工具集的具体 flag（grok 的 `--tools` / `--disallowed-tools` 取值，codex 的 `--sandbox read-only`）由本票以一手探针确定，并把确定的 argv 形状固化进契约测试。

- [x] 两条 runner 接受可选顶层键 `mode ∈ {implement, report}`；非法值 → `spec_invalid`；省略等价于 `implement`
- [x] `mode: "report"` 时，子进程 argv 含只读工具限制参数（形状由探针确定并在测试中断言）
- [x] `mode: "report"` 且工作树无改动 → `error_class: complete`，receipt 含 `mode: "report"` 与非空 `report`；pending 文件被删除
- [x] `mode: "report"` 且工作树有改动 → `error_class: unexpected_diff`，不 `complete`，pending 文件保留
- [x] `mode: "report"` 接受空 `files` 与空 `verification`
- [x] `mode: "implement"` 与省略 `mode` 的全部既有用例零回归；`no_diff` 语义在 implement 模式下不变
- [x] `tests/test_runner_contract.py` 覆盖以上各态，两条 runner 都跑；`python3 tests/test_runner_contract.py` 全绿
- [x] `tests/test_receipt_gate.py` 保持绿（可加一例：报告模式 pending 无 complete receipt 仍拦）

## Comments

2026-09-11 — 首轮已实现（codex lane 复用 01 会话，gpt-6-astra[high]，receipt `complete`，契约测试 14/14、receipt gate 8/8，diff +228）。只读工具集：grok `--tools read_file,grep,list_dir --disallowed-tools search_tool,use_tool,Agent`（架构师真机单轮探针：模型报告可用工具恰为 `read_file, list_dir, grep`）；codex `--sandbox read-only`（`codex exec --sandbox read-only resume --help` 解析通过，flag 属 exec 级、置于 `resume` 之前正确）。

advisor 验收形状（Fable，读 worktree 代码）：ACCEPT。两处非阻塞标记：codex 报告模式 resume 路径的 `--sandbox` 位置（已由上条探针补验）；报告模式脏树会覆盖已置位的 `*_failed` 分类（`child_exit_code` 仍可审计，记作已知）。一处契约空白：`complete` 不要求 `report` 非空——已开修正契约 02b（新错误类 `empty_report`，同会话续跑）。

2026-09-11 — 02b 完成（同会话，astra[medium]，receipt `complete`）：两条 runner 各加两行，优先序 `unexpected_diff` > `empty_report` > `complete`；契约测试 15/15、receipt gate 8/8。`lane/runner-contract` 已合入 `main`（`b8b2b9d`），main 上契约测试复跑 15/15。02 全部验收项完成。
