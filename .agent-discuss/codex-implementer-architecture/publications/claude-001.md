---
actor: claude
version: 1
request_ref: sha256:bc8fac427bb1322b93f6b3dcd6fa28c2a697f7b3140e9784887c029fa9b9d6f9
basis: independent
seen: []
published_at: 2026-07-15T03:36:08Z
---

# Claude 侧观点：codex-implementer 反复失守是护栏架构问题，业务架构无恙

## 一、对三个疑问的回答

### 1. 两次"不调 Codex 自行实现"事故的定性

两次事故是**同一个根因的两次暴露**，不是两个独立问题。插件把"CLI lane 永不自实现"这条不变量编码在三个载体里，三个载体全部是**条件加载的 prompt 层**：

| 载体 | 加载条件 | 事故中的状态 |
|---|---|---|
| tools 白名单 + agent 系统提示词 | 仅 local_agent 通道（spawn 时无 name） | 传 name → in_process_teammate 通道 → 白名单与 persona 双双被抹（事故一磁盘实锤） |
| orchestration SKILL doctrine（"never pass name"） | 仅 skill 被实际调用时进上下文 | 普通会话（trellis 工作流）未触发 skill → doctrine 等于不存在（事故二磁盘实锤） |
| agent .md "Spawn contract" 自检 | 需要 agent 定义进上下文 | 唯一需要它生效的场景（被误派为 teammate）恰好收不到定义——设计上永不触发的死代码 |

第一次修复（把规矩写进 SKILL.md / agent .md，commit 43144a8）用**同一类会失效的载体**去修载体失效问题，属于类别错误（用文档解决机制问题），因此第二次事故必然发生。第二次修复（用户级 PreToolUse hook 拦截带 name 的 CLI lane spawn）第一次把不变量放进机制层（harness 强制执行，不依赖任何 prompt 被加载），方向正确。

### 2. "15m39s / 77.5k tokens / 大量 claude-sonnet-5 调用"观察

**基本正常，大部分是设计使然：**

- codex-implementer 是 frontmatter `model: sonnet` 的完整 agent（agentic loop），不是一条命令。后台大量 claude-sonnet-5 调用记录 = wrapper 本体每一轮思考与工具调用，符合"Fable 出判断、Sonnet 出体力"的插件经济学。
- token 量级有实测基线：第一次排查中，一个只做 1 次工具调用的探针子代理就消耗 25.5k tokens（系统提示词 + agent 列表 + 全局 CLAUDE.md + agent 定义，且每轮全量重发累计上下文，TUI 计数为累计值）。底价 25k 起步，77.5k 不意外。
- 但"15 分钟尚未调用 codex"暴露一个可优化点（标注为推断，win 侧 transcript 不在本机未实锤）：wrapper 手持 Read/Grep/Glob，而 agent .md 没有任何条款禁止它调用 codex 前"为理解任务"自行探索仓库，Sonnet 收到实现任务的自然倾向就是先读代码，每轮探索都在烧上下文。旁证：codex 挂 600s timeout，15m39s 不可能是 codex 已在运行。

### 3. 架构问题还是细节问题

**业务架构（架构师-车道经济学、五段 spec、验证纪律）没问题；护栏架构曾有真实的架构级缺陷；hook 已在机制层堵死它；剩下唯一的架构级残留是：机制层防线活在单台机器的 ~/.claude/settings.json 里，插件自身不携带自己的关键不变量**——换机器/重装即裸奔，而插件仓库里剩下的防线要么条件加载要么永不触发。

修法现成且已在本机实证：Claude Code 插件可以自带 hooks（本机 openai-codex 插件即带 hooks/hooks.json，用 ${CLAUDE_PLUGIN_ROOT} 引用自带脚本）。

## 二、目标形态：分层防御模型（按可靠性排序）

1. **机制层（主防线）**：插件自带 PreToolUse hook（hooks/hooks.json + 脚本入仓库），拦带 name 的 codex/grok-implementer spawn。harness 执行，无条件生效，随插件部署跨机器同步。
2. **永远可见层**：agent description 是唯一保证注入每个会话系统提示的文字。现在 codex-implementer 的 description 没写"必须无名派生"——补一句 "Must be spawned WITHOUT a `name`"。
3. **事后取证层（backstop）**：SESSION 证据检查（rollout 文件 cwd 核验）保留——唯一不依赖 harness 行为的防线。
4. **prompt 纵深层**：SKILL doctrine 与 Spawn contract 保留但明确降级为冗余；Spawn contract 自检已被证明永不触发，文档中不得再当防线描述。

## 三、调整建议

**短期（细节级，全部建议做）：**
1. hook 收编进插件：新增 hooks/hooks.json + hooks/block-named-cli-lane.py（${CLAUDE_PLUGIN_ROOT} 引用，python/python3 回退链沿用已验证版本）；随后移除两台机器用户级 settings.json 中的同款 hook，避免双重来源。
2. codex-implementer / grok-implementer 的 description 末尾加 "Must be spawned WITHOUT a `name` (named spawns strip the tool whitelist)"。
3. agent .md 加"禁预探索"条款：spec 是唯一输入；预检后直接写 spec 文件并调用 codex；不为"理解任务"Read/Grep 仓库源码；spec 缺什么原样作为 open question 转给 codex。直接回应 15 分钟观察。

**中期（架构级演进，先落地 1–3 再考虑）：**
4. wrapper 的确定性部分脚本化：预检、mktemp 写 spec、拼 codex 命令、找 rollout、跑验证命令、组装结构化 JSON 报告——全部可以是插件自带 scripts/run-codex-lane.sh。脚本无法抗命，"agent 不遵守要求"这一整类问题从根上消失，同时省掉每次派工几十 k 的 sonnet 监工 token。判断工作（读 diff、评审报告）按 doctrine 本属架构师。折中形态：保留薄 wrapper 但只允许调脚本再做判断。代价：失去对 codex 异常的自适应处理。

**残留风险（假设标注）：**
- hook 依赖 harness 的 Agent 工具名与 tool_input 字段结构，大版本更新可能变；SESSION backstop 为此保留。
- "teammate 通道忽略白名单"是当前版本（2.1.206）实测行为，官方将来可能修复，届时 hook 成无害冗余，无需撤。
- "77.5k 属正常"基于 25.5k 探针基线 + 机制推理，属推断非实证。

## 四、一句话总结

两次事故是同一个架构缺陷（不变量放在条件加载的 prompt 层）的两次暴露；hook 已在机制层堵死；剩余架构动作是把 hook 收编进插件让它随插件走；15 分钟/77.5k tokens 是 wrapper 即 Sonnet agent 的固有成本，属正常，但可用"禁预探索"条款与脚本化显著压缩。
