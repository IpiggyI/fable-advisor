# 08: 发布 5.2.0

**What to build:** 两侧装上 5.2.0，活体等于正典，旧规则活体消失；在有未提交改动的工作树上以报告模式派一次 grok explorer 得到 `complete`；codex / grok 会话列表首行显示标题。

**Blocked by:** 07（说明书是发布前置条件；07 又依赖 01–06）

**Status:** ready-for-agent

来源：`docs/agents/plugin-release.md`。提交、推送、两侧更新、两侧运行安装器均需椰椰在当次明确授权。

- [x] 两处版本字段改为 5.2.0
- [x] 全部测试绿：`test_runner_contract`、`test_zh_mirror`、`test_lane_family_gate`、`test_user_level_archive`、`test_receipt_gate`、安装器测试；`git diff --check` 干净；`SKILL.md` 词数 ≤ 1960
- [x] 按文件名暂存、`git diff --cached --stat` 复核、提交、推送（需授权）
- [x] 两侧 `claude plugin marketplace update` 与 `claude plugin update`，缓存出现 5.2.0 且内容抽查命中本版新增短语
- [x] 两侧运行伴生安装器；`--check` 通过；两份旧规则活体不存在
- [x] 行为验证：脏工作树 + 报告模式 grok explorer → receipt `complete`、`dirty_baseline: true`；会话列表首行是标题
- [x] 在 `../spec.md` 的 Comments 追加实施记录

## Comments

### 2026-09-16 — 发布记录

- 提交 `89b0b52`，推送 `origin/main`；两侧 `claude plugin update` 5.1.0 → 5.2.0；缓存含 `lane-preamble-report.md`、`dirty_baseline` 文本。
- 伴生安装器双家目录运行：路由档案两侧 installed，pin 规则与门禁脚本 unchanged，四份旧规则 removed；`--check` 退出 0；`test_user_level_archive` 6/6。两侧 `hooks.json` 均检测到门禁条目，无警告。
- 行为验证：脏工作树上 grok runner 报告模式 → `complete`、`dirty_baseline: true`（grok-4.6 默认，effort medium，$0.033）；两次 codex runner 报告模式（code review 两轴，astra low）同样 `complete`、`dirty_baseline: true`。会话列表首行显示标题：未由架构师目视确认，留椰椰查看 `codex resume` / grok 会话列表。
- 全量测试：runner 契约 18/18、zh 镜像 15/15、门禁 18/18、receipt gate 8/8、安装器 8/8、用户级存档 6/6；`SKILL.md` 1958 词；`git diff --check` 干净。
