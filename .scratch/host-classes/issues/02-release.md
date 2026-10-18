# 02 — 发布 6.5.0

Status: resolved
Blocked by: 01

椰椰 2026-10-18 授权"发6.5.0"：说明书、两处版本字段、提交、推送、两侧更新、伴生安装器。流程按 `docs/agents/plugin-release.md`。

## 契约：版本说明书（worker）

**Objective**：新建 `docs/manuals/6.5.0.html`，自包含的中文 HTML，结构与样式沿用 `docs/manuals/6.4.1.html`（以它为模板复制改写）。两部分：

1. 「本版完整行为」：按 6.5.0 的 `plugin/**` 全量描述本版行为。在 6.4.1 的基础上改写受影响的章节——宿主识别与分文件（Claude Code 读 `lanes-claude-code.md`，第一次运行 runner 之前读 `runners.md`，Cursor 读 `lanes-cursor.md`，其他宿主读 `lanes-other-hosts.md`）、路由行归 `SKILL.md`、其他宿主的规则（ADR 0033 决策 5）、`runners.md` 中标注"仅 Claude Code"的小节；其余章节保持与 6.4.1 一致，只改其中指向被拆文件的路径。
2. 「相对上一版的变化」：列出 6.4.1 到 6.5.0 的每项变化——改了什么、为什么、对应 ADR（0033，及它执行或修订的 0024、0023、0031）与工单（`.scratch/host-classes/issues/01-split-and-other-hosts.md`）。

验收标准：标题与版本号写 6.5.0；变化一节覆盖 `git diff HEAD --stat -- plugin docs/zh README.md` 与两个新文件的全部变化；内容与 ADR 0033 和实际文件一致，不写未发生的变化；HTML 能被 Python `html.parser` 无错解析；页内锚点链接都有对应 id。

**Files**：`docs/manuals/6.5.0.html`。

**Interfaces**：无。

**Constraints**：只写这一个文件；不改 `plugin/**`、`docs/zh/**`、版本字段、ADR、`.scratch/**`；不做 git 写操作。

**Verification**：`python3 -c` 用 `html.parser` 解析并检查每个 `href="#x"` 都有 `id="x"`；`grep -c '6.5.0' docs/manuals/6.5.0.html` 非 0；`grep -c 'lanes-other-hosts' docs/manuals/6.5.0.html` 非 0。

## 主代理步骤（说明书验收之后）

1. 两处版本字段改为 6.5.0。
2. 按文件名暂存（`plugin/`、`docs/zh/`、`.claude-plugin/marketplace.json`、`README.md`、`CONTEXT.md`、`docs/adr/0023`、`0024`、`0031`、`0033`、`docs/manuals/6.5.0.html`、`.scratch/host-classes/`、`.scratch/doc-healthcheck-6-0/p11-contract.md`），不带 `.scratch/tiers-and-routing-6-0/` 的既有改动与其他未跟踪文件；看暂存 diff；提交并推送。
3. WSL 与 Windows 两侧更新；运行伴生安装器；抽查新版本缓存目录里的 `lanes-other-hosts.md`。

## Comments

- 2026-10-18 说明书：claude 车道 `worker-h` + `sonnet`（`Route: role=worker tier=mainstay dial=sonnet-5-5[high]`）。改派的原因：工作树里有既有的未跟踪文件，grok runner 需要干净的树，所以从 `grok-4.7[high]` 改派到格内第二候选，同族，没有跨厂商审查。主代理 Tier 1：`html.parser` 解析无错，锚点没有缺失；变化一节与 ADR 0033、工单 01 一致。验收通过。
- 2026-10-18 版本字段改为 6.5.0；`test_zh_mirror.py` 19/19，`test_shipped_wording.py` 49/49。
- 2026-10-18 提交 `476c683` 并推送到 `origin/main`。WSL 与 Windows 两侧插件都更新为 6.5.0（`updated from 6.4.0 to 6.5.0`）；伴生安装器四个文件均为 unchanged。抽查 `~/.claude`、`~/.claude-a`、`/mnt/c/Users/Shy/.claude` 三处的 6.5.0 缓存：都有 `runners.md` 与 `lanes-other-hosts.md`，`SKILL.md` 里都含 "In any other host, before the first dispatch"。各会话需要重启才会加载新版本。
