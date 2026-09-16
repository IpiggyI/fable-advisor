# 04: README 去重、改安装源、更新过时机制句

**What to build:** `README.md` 按 [spec.md](../spec.md) 的 A1、A2、A6、B5、B10、C1–C6、N05、Q01a 修订。只改这一个文件。

**Status:** ready-for-agent

**Blocked by:** 无

## 验收标准（全部为必须）

行号以 `ec36345` 的文件为准。

1. **A2** 第 22 行 "a user-side **fill table** in your rules; the plugin ships no default table" 改为：填充表在你的用户路由档案里，由调用方指令指定给技能；插件不带默认表。
2. **A1** 第 31 行删 "A code block longer than an interface signature is a contract not yet delegated."，其余句保留。
3. **C6** 第 38–39 行安装命令改为本分叉的部署目标 `IpiggyI/fable-advisor`；在附近保留一句上游署名与链接（`DannyMac180/fable-advisor`）。第 43–46 行更新命令不动。
4. **C1** 第 49–52 行 "Start a session on any model:" 及 `/model fable` 代码块删除。
5. **C2 / A6 / N05 / B5** 第 61–64 行四条 Requirements 各压到两句以内，加指向 `plugin/skills/orchestration/lanes-claude-code.md` 的链接：
   - 第 61 行 grok 车道：保留 CLI 安装要求、`effort` 白名单、失败即 `grok_unavailable`；"The receipt records the value actually used" 改为 runner 提交的值。
   - 第 62 行 codex 车道：保留 CLI 安装要求、模型白名单、effort 白名单与默认、receipt 与 Stop hook 一句；`service_tier=fast` 语义改为提速约 1.5 倍、额度消耗约 2.5 倍、不降低智能。
   - 第 63 行报告模式：两句说明只读角色经 `mode: "report"` 到达、无改动为 `complete`、有改动为 `unexpected_diff`，其余细节链接。
   - 第 64 行 claude 车道：删 "highest unit price"，保留同族与共享额度；同模派发一句保留。
6. **B10** 第 67 行模型解析顺序改为：按次 `model` 参数 → agent frontmatter → `CLAUDE_CODE_SUBAGENT_MODEL` → 会话模型（Claude Code v2.1.251 起）。
7. **C4** 第 82–89 行与第 119–124 行两段"加到项目 `CLAUDE.md`"合并为一段，放在第一段位置；第二段及其引言句 "A typical consult costs cents. To make the gate automatic…" 删除。
8. **C3** 第 95 行 Cursor 段压到五行以内，保留：经兼容路径加载；grok / claude 车道为带显式 `model` 的 Task 派发；GPT 家族经 Shell 跑 codex runner、无 receipt gate；用户级门只拦 `fable-advisor` 缺 pin；其余链接到 `plugin/skills/orchestration/lanes-cursor.md` 与 ADR 0010、0011、0014。
9. **Q01a** 第 100–106 行决策类型门清单删第六项 "before declaring a multi-step deliverable done (this one takes the advisor's **acceptance** shape)"；第 108 行 "The others take the **decision** shape" 改为全部取决策形状，验收形状按 orchestration skill 的 Tier 3 到达。
10. **C5** 第 134 行 "Upgrading from v2?" 段只保留 v5.0.0 一段（从 "v5.0.0 is breaking" 起），前面 v3–v4 叙述删除，加 ADR 0014 链接；段首问句改为 "Upgrading from an earlier version?"。
11. 第 59 行 "Claude Code ≥ 2.1.170" 不动。第 136 行 "Why Grok and GPT-family lanes" 段、"Go deeper"、"License" 不动。
12. 文件中不再出现：`in your rules`、`longer than an interface signature`、`/model fable`、`actually used`、`highest unit price`、`trading quality`、`declaring a multi-step deliverable done`、`grok-implementer`、`v3.1 upgrades`。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
rg -n "in your rules|longer than an interface signature|/model fable|actually used|highest unit price|trading quality|declaring a multi-step deliverable done|grok-implementer|v3.1 upgrades" README.md ; echo "exit=$?"   # 期望无输出、exit=1
rg -n "IpiggyI/fable-advisor|DannyMac180|routing profile|Tier 3|lanes-cursor.md|lanes-claude-code.md|CLAUDE_CODE_SUBAGENT_MODEL" README.md
wc -w README.md   # 期望明显低于 2100
git diff --stat -- README.md
```
