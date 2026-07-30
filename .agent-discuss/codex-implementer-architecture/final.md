# 最终结论：codex-implementer 反复失守问题

## 定性

**业务架构无恙；护栏架构存在真实的架构级缺陷**——"CLI lane 必须真调 Codex、绝不自实现"这一确定性不变量被托付给条件加载的 prompt 载体（tools 白名单 / skill doctrine / Spawn contract），而 harness 存在绕过全部三者的 spawn 路径（named teammate）。两次事故是该缺陷的两次暴露，非偶然模型失误。用户第二次修复（PreToolUse hook）首次将不变量放入机制层，方向正确；剩余架构动作是让插件携带自己的关键不变量。

"15m39s / 77.5k tokens / 大量 claude-sonnet-5 调用"观察：属 Sonnet 包装代理本体运行的固有成本（约 25k/次 spawn 启动基线，实测），定性正常；但调用前 15 分钟未启动 codex 属架构效率问题，由禁预探索条款（短期）与确定性 runner + preparation_stalled 事件 SLO（中期）消除。

## 整改路线（两模型族收敛一致）

- **P0（立即）**：named-spawn PreToolUse hook 收编进插件（hooks/hooks.json）；CLI lane description 加"必须无名派生"；修正"物理上不可能"措辞（任意 Bash 仍可写仓库）；agent .md 加禁预探索条款；双机冒烟通过后再移除用户级 hook。
- **P1（短期）**：scripts/run-codex.mjs 确定性 runner——五段 spec schema、spec hash、跨平台 timeout（runner 自行终止子进程）、codex exec --json 进程级 session 绑定（替代易并发串线的 rollout 搜索）、结构化 receipt（spec_hash/codex_session_id/exit_status/changed_files/验证输出）、错误分类。
- **P1.5**：若暂留 wrapper，须在能力层封死任意 Bash（MCP 单工具或 hook allowlist）；否则"薄"只是文字。
- **P2（默认目标）**：一轮实测确认 runner 报告足够后，收敛为 architect → runner → Codex → architect，删除重复验证层。
- **receipt 强制执行点**：Stop 类 hook 校验或显式 command 入口，至少绑定其一——receipt 本身是证据不是强制。

## 归档实现风险（Codex 侧收尾补充，user-relayed）

1. SessionStart 自检不得依赖被检查的运行时（Node 缺失时 Node 写的自检也无法启动），须由 harness 保证可用的 shell 层承载。
2. 检测失败必须 fail closed：禁用 Codex/Grok lane 直至 hook 运行时可用，不得告警后继续裸奔。

## 待验证项（决定 P1.5 形态与 receipt 绑定，不动摇主线）

1. SessionStart 自检的检测与禁用形态；2. PreToolUse 输入是否透出调用方 subagent 类型；3. agent tools frontmatter 对插件 MCP 工具的白名单支持；4. receipt 执行点选型。

## 过程记录

有效出版物 claude-001/003/004 与 codex-001/002（claude-002 为误发布占位件，作废）；claude-001 与 codex-001 构成独立对齐。完整比对见 comparisons/comparison-001.md。
