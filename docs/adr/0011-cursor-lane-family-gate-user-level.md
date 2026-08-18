# 0011 — Cursor 车道家族门：user-level 存活、仓库留档

- **Status**: accepted
- **Date**: 2026-08-18
- **影响范围**: `cursor-hooks/`、`tests/test_lane_family_gate.py`、`docs/agents/cursor-lane-gate.md`、根目录 `AGENTS.md` / `CONTEXT.md`
- **关联**: [ADR 0010](./0010-dual-harness-single-source.md)（Cursor 经插件兼容路径加载 skill/agent；receipt gate 在 Cursor 侧无 pending 故无害）

## 背景

Cursor 对 `fable-advisor` / `implementer` 的家族钉钉，由用户级 `preToolUse` 脚本强制，不由插件 `hooks.json` 强制。2026-08-18 修过 BOM 与 `cursor-grok-4.6-*` 信封后，权威副本仍只在两台机器的 `~/.cursor/hooks/`，仓库里没有。下次热修会只改活体。

## 选项对比

| 方案 | 优点 | 缺点 |
|---|---|---|
| **仓库根 `cursor-hooks/` 留档（选定）** | 跟仓走；不假装随 `claude plugin update` 生效 | 活体仍须手动拷；档案与活体会漂 |
| `plugin/cursor-hooks/` 或放进 `plugin/hooks/` | 下次插件更新把文件拷进缓存 | Cursor 不从插件读 user-level hook；制造「随插件生效」的假象；未注册文件躺在 `plugin/hooks/` 会被当成已挂钩 |
| 本仓 `.cursor/hooks/` | 对本仓会话自动生效 | 漏拦发生在别的工作区；范围错 |

## 决策

1. 权威脚本与 `preToolUse` 片段留在 `cursor-hooks/`，**不**进入 `plugin/`，**不**写入 `plugin/hooks/hooks.json`。
2. 活体仍是 user-level：WSL `/home/hyy/.cursor/hooks/` 与 Windows `C:\Users\Shy\.cursor\hooks\`。两侧 `hooks.json` 已经分叉，未经点名不改。
3. `tests/test_lane_family_gate.py` 跑仓库副本 `--self-test`，并在活体存在时断言与档案逐字节一致。无漂移检测的留档比没有更危险。
4. 不 bump 插件版本：`plugin/` 无变更。

**核心理由**：`plugin/` 是 Claude Code 插件分发面。Cursor 的 user-level hook 与 Claude Code 的 receipt-gate 不是同一份 `hooks.json`。留档的职责是可审的权威副本，不是第二条安装通道。

## 复盘条件

- Cursor 开始从已安装 Claude 插件加载 user-level `preToolUse` → 重估是否把脚本迁入 `plugin/` 并真正挂钩。
- 活体与档案反复漂、手动拷不可维持 → 重估安装方式（仍不要把未挂钩文件塞进 `plugin/hooks/`）。
