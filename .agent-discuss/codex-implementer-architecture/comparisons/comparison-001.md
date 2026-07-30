# 正式比对归档：codex-implementer 反复失守的架构定性与整改路线

- 输入出版物：claude-001（independent）、codex-001（independent）、claude-003（informed）、codex-002（informed）、claude-004（informed）。claude-002 为误发布占位件，作废，不作比对输入。
- 基线：全部出版物 pin 同一 request ref（sha256:bc8fac42…），非混合基线。
- 独立对齐声明：claude-001 与 codex-001 均为 basis: independent、先于首次 comparison_started，其重合结论具有独立对齐资格（两个模型族在未见对方观点时得出）。

## 一、独立对齐的核心判断（置信度最高）

两侧第一轮独立得出以下一致结论：

1. **业务架构无恙，缺陷在控制面**。"Claude 架构师 + 跨供应商实现 + Claude 验收"的分工保留；错在把"CLI lane 必须真调 Codex、绝不自实现"这一确定性不变量交给条件加载的 prompt 层（tools 白名单 / skill doctrine / Spawn contract）与会自选 spawn 参数的 Sonnet 包装代理。
2. **两次事故是同一控制面缺陷的两次暴露**，不是两个偶然的模型失误：传 name 落 in_process_teammate 通道抹掉白名单与 persona（事故一）；doctrine 依赖 skill 被调用才进上下文（事故二）；Spawn contract 自检在唯一需要生效的场景恰好收不到（永不触发）；SESSION 证据只能事后拒收。
3. **P0 = 插件级 PreToolUse hook**（hooks/hooks.json 随插件交付，跨机器同步），description 加"必须无名派生"仅作提前引导，不能替代 hook。
4. **token 观察定性**：大量 claude-sonnet-5 调用 = Sonnet 包装代理本体运行，符合设计；77.5k 有约 25k/次的 spawn 启动基线支撑（实测探针）；但"15m39s 仍未执行 codex exec"不符合该 lane 快路径设计，属架构效率问题。
5. **确定性 runner 方向**：preflight、spec 校验、timeout、调用、结果捕获、错误分类应移入插件自带脚本——脚本无法抗命。

## 二、交换后达成的修正（互相纠偏的记录）

| 修正 | 提出方 | 接受方 | 内容 |
|---|---|---|---|
| 撤回"物理上不可能自实现" | codex-001 | claude-003 | 白名单去 Write/Edit 后仍有任意 Bash 可写仓库；措辞降级为"结构性提高门槛"，兜底是 SESSION/receipt 证据 |
| SESSION 绑定升级 | codex-001 | claude-003 | 弃用"找同 cwd 最新 rollout"（并发串线竞态），改 codex exec --json 绑定本次进程（flag 行为落地时实测） |
| hook 运行时不可假设 | codex-002 | claude-004 | "任何 Claude Code 机器必有 Node"不成立（原生安装≠npm 安装）；Requirements 声明 + fail loud，或免解释器可执行文件 |
| 薄 wrapper 需能力层约束 | codex-002 | claude-004 | wrapper 持任意 Bash 则"只准调 runner"仍是 prompt 约定；P1 验收 = 能力层无法绕过脚本 |
| P2 不无限后置 | codex-002 | claude-004 | wrapper 验证与架构师验证重复；默认目标形态 architect → runner → Codex → architect，薄 wrapper 仅迁移兼容层，一轮实测确认 runner 报告足够后收敛 |
| 事件 SLO 替代 token 口径 | codex-002 | claude-004 | spec 到达后 Codex 进程未在短预算（约 30s）内启动 → preparation_stalled 失败返回 |
| receipt 机制（第三类威胁） | codex-002 | claude-004 | hook 防不了"主 Claude 根本不路由给 Codex"；runner 产出可核验 receipt（spec_hash/cwd/producer/codex_session_id/时间戳/exit_status/changed_files/验证命令与退出码），无 receipt 不得验收 |
| receipt 需绑定强制执行点 | claude-004 | （对端无异议） | receipt 是证据不是强制；执行点必须是 Stop 类 hook 校验或显式 command 入口之一，否则回到条件加载约定的老问题 |
| hook 启动失败≈护栏静默失效 | claude-004 | codex（会话内确认） | PreToolUse 命令因解释器缺失启动失败时 harness 可能按非阻塞错误放行；fail loud 挂点为 SessionStart 自检 |

## 三、合并整改路线（最终版）

- **P0（立即）**：插件内置 named-spawn PreToolUse hook + hooks/hooks.json；codex/grok-implementer description 加 "Must be spawned WITHOUT a `name`"；修正文档中"物理上不可能"措辞；agent .md 加禁预探索效率条款（spec 为唯一输入，预检后直奔调用）；hook 单测 + 真实插件加载路径触发验证。两台机器用户级 hook 保留至插件 hook 分别冒烟通过后再移除，避免切换窗口裸奔。
- **P1（短期）**：scripts/run-codex.mjs 确定性 runner——五段 spec schema、spec hash、跨平台 timeout（不依赖 timeout/gtimeout 二进制，由 runner 自行终止子进程）、--json session 绑定、结构化 receipt、并发隔离、错误分类（含 preparation_stalled）。
- **P1.5（若暂留 wrapper）**：用 MCP 单工具或 hook allowlist 真正封死任意 Bash；两条路径均不可行则跳过，直接去 wrapper 化。
- **P2（默认目标）**：一轮实测确认 runner 报告足够后，收敛为 architect → runner → Codex → architect。
- **验证清单**：hook 单测（带 name 拒 / 无 name 及普通 agent 放行）；plugin validate；Windows/Linux 双平台 runner 测试；fake Codex 端到端（恰好启动一次、结果绑定本次进程）；同 cwd 并发不串 SESSION；runtime 缺失 fail loud；wrapper 尝试任意 Bash 必须被拒；无有效 receipt 不得验收（绑定执行点）。

## 四、实现层待验证项（不动摇主线，仅决定 P1.5 形态与 receipt 绑定方式）

1. SessionStart 自检对 hook 运行时缺失的检测与告警/禁用形态；
2. PreToolUse hook 输入是否透出调用方 subagent 类型（决定 Bash allowlist 路径可行性）；
3. agent tools frontmatter 对插件 MCP 工具的白名单支持（决定 MCP 单工具路径可行性）；
4. receipt 强制执行点选型（Stop hook vs 显式 command）。

## 五、实现风险（Codex 侧收尾补充，经用户转述，provenance: user-relayed，非出版物）

1. **SessionStart 自检的自举悖论**：自检不能依赖正在被检查的运行时——Node 缺失时，用 Node 编写的自检本身也无法启动。自检须由 harness 保证可用的更低层承载（如 POSIX sh / Windows 兼容的 shell 形态），只探测运行时存在性。
2. **检测失败必须 fail closed**：不应只告警后继续运行，应明确禁用 Codex/Grok lane，直至 hook 运行时可用——否则"告警后照常裸奔"重演事故二的静默失效模式。

Claude 侧确认接受以上两条为归档实现风险。

## 六、结论

两个模型族对"架构问题还是细节问题"的回答独立收敛：**业务架构保留；护栏架构曾有真实的架构级缺陷（不变量托付给条件加载载体）；整改方向是把控制面从约定重构为机制，做到"Codex lane 是不可绕过的确定性能力边界"为止**。方向性分歧为零；全部残留项均为实现层可行性验证，随 P0/P1 落地逐项定案。
