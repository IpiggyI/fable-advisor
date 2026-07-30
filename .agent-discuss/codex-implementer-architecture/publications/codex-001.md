---
actor: codex
version: 1
request_ref: sha256:bc8fac427bb1322b93f6b3dcd6fa28c2a697f7b3140e9784887c029fa9b9d6f9
basis: independent
seen: []
published_at: 2026-07-15T03:34:56Z
---

# Codex 观点：保留跨模型分工，重构 CLI lane 控制面

## 结论

`fable-advisor` 的目标架构没有错：Claude 负责架构、规格与验收，Codex/Grok 负责跨供应商实现，可以获得成本隔离和不同模型族的失败分布。

真正有问题的是控制面：当前把“必须实际调用 Codex、绝不能由 Claude 包装代理自行实现”这一确定性不变量，交给了可能未加载的 prompt/skill 和会自行选择 spawn 参数的 Sonnet 子代理。因此不应推倒跨模型分工，而应把 Codex 调用重构成确定性工具或 runner，并用插件级 hook 强制关键约束。

## 两次事故揭示的根因

当前防线分别是：

1. `codex-implementer` 的工具白名单不含 Write/Edit；
2. orchestration skill 规定 CLI lane 不传 `name`；
3. agent 正文包含 Spawn contract；
4. 报告必须带 Codex `SESSION` rollout 证据。

这些防线没有形成可靠的机制闭环：

- 传 `name` 会进入 `in_process_teammate` 通道，工具白名单和 agent persona 不再可靠；
- orchestration skill 没被调用时，“不传 name”规则不会进入主代理上下文；
- agent 的 Spawn contract 恰好在误派为 teammate 时也不会被加载；
- `SESSION` 证据只能事后拒收，不能阻止事故发生。

而且“没有 Write/Edit 就物理上无法自行实现”并不严谨：agent 仍有任意 Bash，理论上仍可通过 shell 修改仓库。真正的隔离必须限制可执行操作，而不能只移除两个编辑工具。

Windows 侧后来创建的 PreToolUse hook 才是已知事故入口上的机制级防线，但它目前只是每机独立的用户配置，没有随插件交付。

## 关于 15 分钟和 77.5k tokens

大量 `claude-sonnet-5` 请求本身符合当前实现：`codex-implementer` 明确是一个 Sonnet 包装代理，Codex 只在它执行 `codex exec` 后才参与。

`↓77.5k tokens` 反映的是 Sonnet 子代理自己的上下文或输入消耗，不是 Codex token。普通子代理会加载自己的 system prompt、任务消息、适用的 CLAUDE.md/规则/记忆、Git 状态等，然后继续累积文件和工具输出。同一套 harness 中，一个只有一次工具调用的探针也显示过 25.5k tokens，说明启动基线可能已经很大。

但“运行 15 分钟、消耗 77.5k，仍未执行 `codex exec`”不符合该 lane 的目标快路径。现行定义要求第一动作先检查 Codex，随后应尽快调用。对一个已获得完整五段式规格的实现 lane，十五分钟的额外研究意味着规格不完整、包装代理重复承担了 architect 工作，或存在多轮读取/重试；这属于架构效率问题，不能仅用 token 统计口径解释掉。要精确还原那一次运行仍需对应 JSONL。

## 建议的调整顺序

### P0：将 named-spawn hook 纳入插件

新增插件级 `hooks/hooks.json` 和跨平台 Node hook：当 `Agent` 的 `subagent_type` 是 Codex/Grok CLI lane 且带 `name` 时，PreToolUse 直接 `deny`，要求无名重派。插件 hook 在 harness 中执行、不依赖 skill 是否加载，也没有模型上下文成本。

同时把“必须无名派生”写进 agent description 作为提前引导；description 只负责帮助模型选对参数，不能代替 hook。

### P1：实现确定性 Codex runner

把 preflight、五段式 spec 校验、跨平台 timeout、`codex exec` 调用、结果捕获和错误分类移入 `scripts/run-codex.mjs`。

使用 `codex exec --json` 的本次进程事件直接取得 session/thread id。当前“寻找 cwd 相同的最新 rollout”在同一仓库并行运行多个 Codex 时可能关联到错误会话，不应继续作为唯一身份绑定方式。

### P2：最终将 Codex lane 从 agent 改为工具

理想链路：

```text
Claude architect
  -> 生成完整 spec
  -> 调用确定性 codex-runner 或 MCP tool
  -> Codex 修改工作区
  -> Claude architect 验证 diff 和测试
```

这样可以去掉 Sonnet 包装层的重复上下文和角色混淆。若为了自动 lane 选择仍保留 `codex-implementer`，它应退化为只拥有一个结构化 runner 工具的薄适配器，不能拥有任意 Bash、Write 或 Edit。

## 必须补的验证

- hook 单测：带 `name` 的 Codex/Grok 被拒，无 `name` 和普通 agent 放行；
- `plugin validate`；
- Windows 与 Linux runner 测试；
- fake Codex 端到端测试：恰好启动一次 Codex，并将结果绑定到本次进程；
- 同一 cwd 并发执行不串 SESSION；
- 无 `timeout`/`gtimeout` 时仍能由 Node 终止子进程；
- 真机冒烟验证 Codex 在派工后短时间内启动。

## 最终判断

保留“Claude 架构师 + 跨供应商实现 + Claude 验收”的产品方向；立即把 hook 纳入插件，然后将 CLI lane 重构为确定性 runner。继续堆叠 prompt 禁令或增加事后报告字段，只会延后同类事故，不会消除它。
