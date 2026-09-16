# 02: lanes 文件与前言承接宿主事实

**What to build:** `plugin/skills/orchestration/lanes-claude-code.md`、`lanes-cursor.md`、`lane-preamble.md` 按 [spec.md](../spec.md) 的 A3a、A4、A5、A6、B7、B10、D4、N05、Q09 修订。只改这三个文件；`docs/zh/` 孪生由工单 06 处理。

**Status:** ready-for-agent

**Blocked by:** 无

## 验收标准（全部为必须）

行号以 `ec36345` 的文件为准。

### `lanes-claude-code.md`

1. **A3a** 第 3 行 "the built-in explorer for the explorer" 改为：内置 Explore 带显式按次 `model`；省略时它继承会话模型（Claude API 上限 Opus）与会话 effort。
2. **A5** 第 3 行段末补：claude 车道子代理（`worker`、`fable-advisor`、Explore）的报告在 Task 结果内返回；后台派发的报告读该任务的输出文件。
3. **A6** 第 25 行 "The receipt records the values actually used." 与第 109 行 "the receipt records the value actually used" 改为 runner 提交给 CLI 的值。第 70 行段末补三层表述：`model_requested` 是 spec 请求值；`model_used` 与 `effort` 是 runner 提交给 CLI 的值（含回退后）；runner 不读 CLI 的运行事件，实际执行配置保持未知，报告时写 "submitted, not observed"。
4. **N05** 第 29 行 `service_tier` 说明改为：`"fast"` 是 Codex 的提速模式，速度约 1.5 倍、ChatGPT 额度消耗约 2.5 倍，不降低智能；API key 计费时不适用。
5. **B7 / D3** 第 35 行整段（"Dial the codex lane quality-first … Escalate to `high` for unusually hard tasks."）删除。第 28 行白名单与按模型默认值保留。
6. **B10** 第 47–61 行等待协议更新：`TaskOutput` 已被官方标为弃用，后台任务改用 `Read` 读该任务的输出文件直到出现完成证据；保留一句"弃用不等于当前不可用"。第 52 行与第 60 行涉及 `TaskOutput(task_id, block=true)` 及其 timeout 的描述相应改写；"三个时钟"里第三个时钟改为后台读取的等待语义，不再写 `TaskOutput` 的 30000 ms / 600000 ms 数字。前两个时钟（runner 静默截止、Bash 工具 timeout）原文保留。
7. **D4** 在第 3 行段或新小节补 claude 车道 effort 事实：Task 按次参数没有 `effort`；effort 来自 agent 文件 frontmatter 或 `--agents` 定义，省略则继承会话；`worker.md` 的 `effort: medium` 与 `fable-advisor.md` 的 `effort: high` 是该角色在此车道的默认；`/tasks` 自 v2.1.242 起显示子代理实际模型与 effort，是用户侧观测入口。
8. **Q09** 第 81 行 "a pick-the-stronger-diff race is both runners as background Bash on the same spec content in two distinct pending files" 改为：竞赛须各自隔离的工作目录（`git worktree`）与各自的 pending / receipt；两个执行者在同一工作树会互相覆盖，不同 pending 文件名不构成隔离。
9. 文件中不再出现：`actually used`、`Dial the codex lane quality-first`、`Escalate to \`high\``、`TaskOutput(task_id, block=true)`、`trading quality for speed`。

### `lanes-cursor.md`

10. **A6** 第 8 行 Roles 段末或第 9 行 Pin 段末补：pin 是请求值，Cursor 不向主代理暴露执行元数据，报告时标 "requested, not confirmed"。
11. **D4** 第 14 行 "Effort is pinned to the slug" 段补：路由档案的 `model[…]` 括号映射到 slug 变体；本轮 allowlist 只有一个变体时它就是拨盘，披露时点名。
12. **Q09** 第 15 行 Races 改为：竞赛用隔离 worktree 的派发方式；两个执行者在同一工作树会互相覆盖。
13. **A5** 第 25–30 行生命周期段补两条：后台派发的完成通知不是报告，报告在工具结果或输出文件里读；报告缺失时先读输出文件与工作区确认状态，再按缺口恢复，确需重新执行才重派，不用 `resume` 去催。

### `lane-preamble.md`

14. **A4** 第 1 行 "The target repo's conventions do apply." 前补：`Constraints' reserved operations still bind you and any subagent you spawn; when a step needs one, report it under GAPS with your evidence instead of performing it or claiming the check passed.` 前言仍是三段。

## 保留项

- `lanes-claude-code.md` 第 54 行（不 `sleep` 再 `ls`）、第 116–118 行（不预探登录态）、第 76–78 行（验收定义与 receipt gate）原文不动。
- `lanes-cursor.md` 第 9 行显式指定要求、第 20–23 行 codex 经 Shell 段不动。
- 不改 runner、不改其他文件。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
rg -n "actually used|Dial the codex lane quality-first|Escalate to .high|TaskOutput\(task_id|trading quality for speed" plugin/skills/orchestration/lanes-claude-code.md ; echo "exit=$?"   # 期望无输出、exit=1
rg -n "submitted|deprecated|worktree|/tasks|--agents" plugin/skills/orchestration/lanes-claude-code.md
rg -n "requested, not confirmed|slug variant|worktree|output file" plugin/skills/orchestration/lanes-cursor.md
rg -n "reserved operations" plugin/skills/orchestration/lane-preamble.md
awk 'END{print NR" lines"}' plugin/skills/orchestration/lane-preamble.md   # 仍为三段
git diff --stat -- plugin/skills/orchestration/lanes-claude-code.md plugin/skills/orchestration/lanes-cursor.md plugin/skills/orchestration/lane-preamble.md
```
