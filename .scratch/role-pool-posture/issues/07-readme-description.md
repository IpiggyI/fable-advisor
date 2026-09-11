# 07: README 重定位 + 插件 description

**What to build:** 新用户读 README 与 marketplace 描述时，看到的定位是"角色池 + 姿态 + 升级 + 独立评审，任一模型可当主代理"，不再是"旗舰 Claude 架构师带廉价车道"。车道表改机制名；角色与档位有一段说明；runner 新字段（grok `effort`、两条 runner 的 `mode`）出现在 runner 说明里；Cursor 段说明 GPT 家族经 codex runner；"Upgrading" 追加 v5.0.0 条目（破坏性：模式退役、车道改名、`implementer` 移除、runner 契约扩展），历史条目不改写。`plugin.json` 与 `marketplace.json` 的 description 同步改写（版本号不在本票）。

**Blocked by:** 02、03、04、06

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "文档与版本" 节；术语以 `CONTEXT.md` 为准。范围：`README.md`、`plugin/.claude-plugin/plugin.json`（仅 description）、`.claude-plugin/marketplace.json`（仅两处 description）。

- [x] README 旧名清零：`Routine`、`Cross-vendor`、`In-house`、`implementer`、`architect tier`、`advisor-only`（`grep -c` 为 0）
- [x] README 含姿态、三角色、三档位、四条机制名车道、决策类型门的说明；含 v5.0.0 Upgrading 条目
- [x] README 不含任何 Cursor allowlist 型号枚举；具体型号只以带日期的 "currently …" 示例出现
- [x] `plugin.json` 与 `marketplace.json` 的 description 不再含 "flagship-tier Claude model" 式的主代理身份限定；`version` 字段未动
- [x] `node -e 'JSON.parse(require("fs").readFileSync("plugin/.claude-plugin/plugin.json"))'` 与 marketplace.json 同样解析通过

## Comments

2026-09-11 — 已实现（grok lane，cursor-grok-4.6-xhigh）。首轮为满足旧名 grep 改写了 Upgrading 历史段落，与“历史叙述不改写”冲突（契约两条约束相撞，架构师责任）；返工票（同会话 resume）已把历史段落还原为与 HEAD 逐字节一致，v5.0.0 条目追加在其后并直呼 `implementer`。旧名 grep（历史段落之外）为零；两处 JSON 解析通过、version 仍 4.2.0。架构师读了 README 前 34 行的定位与两张表。
