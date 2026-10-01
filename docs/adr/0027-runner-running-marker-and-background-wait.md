# 0027 — runner 运行中标记与心跳，receipt gate 放行在跑的车道，等待改为后台运行加宿主唤醒

- **Status**: accepted（2026-10-01 椰椰选择全套四项：运行中标记加心跳、gate 放行在跑的车道、拒绝重复启动、等待规则只留一条后台路径）
- **Date**: 2026-10-01
- **影响范围**: `plugin/scripts/run-grok.mjs`、`plugin/scripts/run-codex.mjs`、`plugin/hooks/receipt-gate.py`、`plugin/hooks/hooks.json`（描述）、`plugin/skills/orchestration/lanes-claude-code.md` 与其孪生 `docs/zh/skills/orchestration/lanes-claude-code.md`、`tests/test_receipt_gate.py`、`tests/test_runner_contract.py`、`tests/test_runner_lifecycle.py`、`CONTEXT.md`（receipt gate 条目）
- **关联**: 修订 [ADR 0009](./0009-grok-lane-dewrapper-runner.md)「追记（2026-09-06）」的等待协议与「追记（2026-09-07）」第 3 个时钟；沿用 [ADR 0002](./0002-codex-lane-dewrapper-receipt-gate.md) 的 receipt gate（Stop hook，fail open）；与 [ADR 0024](./0024-orchestration-files-by-lane-and-word-budgets.md)（proposed）的拆分相关，见后果。决策类型门（推翻既定等待协议）经会话内顾问工具咨询，意见已并入决策 1、3、4、5。

## 背景

椰椰报告编排期间多次出现空等待：车道早已结束，主会话仍在等。主会话事后给出的两次解释：

1. 主会话留下的轮询循环用 `pgrep` 按命令行匹配运行器，循环自己的命令行包含匹配串，于是匹配到自己，永远不退出。
2. 01 号车道跑了 16 分钟，03 号跑了 11 分钟，期间输出文件一直为空；receipt gate 阻止结束回复后，主会话在前台每 15 秒检查一次运行器进程，直到它退出；第二次等待时主会话还在前台串行跑了 11 个浏览器测试脚本。

已核实的原因（2026-10-01）：

- `receipt-gate.py` 只看 pending spec 有没有 `complete` receipt，分不清"runner 在跑"和"没人在跑"。gate 自身只拦一次（`stop_hook_active` 为真时放行），但拦截消息要求"Run the matching runner"。runner 已在跑时，这句话诱导主会话轮询，或对同一 spec 再起一个 runner：两个写入者同时改仓库，并写同一个 receipt 路径。
- `lanes-claude-code.md` 第 3 节的后台分支要求"反复 `Read` 输出文件直到完成证据出现"。两次读取之间没有等待手段，模型只能自己加 `sleep` 或 `pgrep`。ADR 0009 记录的 `sleep 780; sleep 420` 与这次的 `pgrep` 循环同源。
- runner 只在结束时向 stdout 打印 receipt，执行期间没有任何输出。
- 本机实测：`bash -c 'pgrep -f <pattern>'` 在没有任何目标进程时仍返回匹配，匹配到的是运行它的 shell。
- 本会话实测：一条 20 秒的后台 Bash 命令退出后，Claude Code 发出 task-notification 唤醒了已结束回复的会话；后台调用的输出文件同时收录 stdout 与 stderr。

## 决策

1. **运行中标记。** runner 读完合法 spec 后，以独占创建（`wx`）写 `.fable-advisor/running/<spec_hash>.json`，内容为 runner、pid、spec 路径、开始时间、心跳时间、阶段（`preparing | cli | verifying`）、事件数。runner 进程自己的计时器每 60 秒重写一次，主会话不参与。顶层 `finally` 删除标记，覆盖 runner 观察到的每条退出路径（含 `interrupted`、`timeout`、`idle_timeout`、异常）。180 秒未刷新的标记视为死亡。存活判断用文件修改时间，不用 PID：Windows 上 Python 的 `os.kill(pid, 0)` 会终止目标进程，PID 还会被复用。删除前先等最后一次刷新写完，避免刷新在删除之后重建标记。
2. **心跳进度行。** 每次刷新同时向 stderr 写一行 `[run-<cli>] running <时长>; phase <阶段>; <n> events; last event <时长> ago`。stdout 仍只放 receipt，解析 stdout 的调用方不受影响。
3. **receipt gate 放行在跑的车道。** pending spec 有新鲜标记时不计入未匹配；全部未匹配项都有新鲜标记时放行结束。没有新鲜标记的照旧拦截，拦截消息改为指引"以后台 Bash 调用运行 runner，然后结束本轮"。标记过期阈值 180 秒在 gate 与两个 runner 中各写一处，注释互指。
4. **拒绝重复启动。** 同一 spec 已有新鲜标记时，第二个 runner 以状态 1 退出，不写 receipt、不启动 CLI、不动对方的标记；标记过期则接管。
5. **等待规则（Claude Code）。** 只留两条路径：前台运行 runner；或把 runner 本身作为后台 Bash 调用运行，然后结束本轮或做互不依赖的工作，由宿主在进程退出时唤醒会话。后一条只属于主会话：子代理结束本轮就是把报告交还给上级，插件只注册了 `Stop` 而没有 `SubagentStop`，没有任何门拦住它，所以子代理在前台运行 runner。禁止自写等待循环（`sleep`、`while`、`until`、`pgrep`），也禁止把循环包进后台调用；删除"反复读输出文件"一条。第 3 个时钟改述为"后台调用只受 runner 自己的截止约束"。
6. **Cursor 不变。** Cursor 没有 receipt gate，`lanes-cursor.md` 的等待方式（在 shell id 上等待）不变。codex runner 在 Cursor 中同样写标记、同样拒绝重复启动。

## 后果

- 车道运行期间主会话可以结束回复，椰椰能看到状态并插话；进度在输出文件和标记文件里可见。
- 被 SIGKILL 的 runner 留下的标记，在最多 180 秒内让 gate 放行、让同一 spec 的重跑被拒绝。拒绝消息指明标记路径。
- gate 无法区分"结束回复等待唤醒"与"在 runner 跑完前声称完成"；后者由第 5 条规则与验收约束，gate 在 runner 退出后的下一次结束时照常检查。
- 两条 runner 同改（镜像维护，ADR 0009 既有代价）。
- `lanes-claude-code.md` 增加约 170 词。ADR 0024 拆分时，标记、心跳与拒绝重复启动属于 runner 流程，进 `runners.md`；后台调用加宿主唤醒属于 Claude Code，留在 `lanes-claude-code.md`。
- 主会话自己在前台串行跑长命令（背景第 2 条的第二次等待）不属于车道等待，本决策不覆盖。
- 端到端（已安装插件的新 gate 放行在跑车道、runner 退出后宿主唤醒）要在发布并更新本机插件后验证；本次只有单元与进程边界测试覆盖。

## 未采纳

- **固定间隔轮询。** 两次已记录的事故都源于轮询；宿主已在进程退出时唤醒会话，轮询不增加信息。
- **PID 存活检查。** 见决策 1。
- **PreToolUse 钩子按正则拦截轮询命令。** 匹配脆弱、容易绕过；先移除诱因（gate 消息与第 3 节规则）。
- **`ScheduleWakeup`。** 只在 `/loop` 模式可用。

## 复盘条件

- 再次出现"runner 已退出而会话未被唤醒" → 先查宿主是否发出 task-notification，再考虑 gate 侧兜底。
- 主会话仍手写等待循环 → 考虑 PreToolUse 拦截。
- 出现标记在 runner 存活时过期（gate 误拦、或重复启动未被拒绝） → 查事件循环是否被长时间阻塞，再调整刷新间隔或过期阈值。
