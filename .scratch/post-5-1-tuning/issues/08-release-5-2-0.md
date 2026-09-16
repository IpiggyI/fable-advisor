# 08: 发布 5.2.0

**What to build:** 两侧装上 5.2.0，活体等于正典，旧规则活体消失；在有未提交改动的工作树上以报告模式派一次 grok explorer 得到 `complete`；codex / grok 会话列表首行显示标题。

**Blocked by:** 07（说明书是发布前置条件；07 又依赖 01–06）

**Status:** ready-for-agent

来源：`docs/agents/plugin-release.md`。提交、推送、两侧更新、两侧运行安装器均需椰椰在当次明确授权。

- [ ] 两处版本字段改为 5.2.0
- [ ] 全部测试绿：`test_runner_contract`、`test_zh_mirror`、`test_lane_family_gate`、`test_user_level_archive`、`test_receipt_gate`、安装器测试；`git diff --check` 干净；`SKILL.md` 词数 ≤ 1960
- [ ] 按文件名暂存、`git diff --cached --stat` 复核、提交、推送（需授权）
- [ ] 两侧 `claude plugin marketplace update` 与 `claude plugin update`，缓存出现 5.2.0 且内容抽查命中本版新增短语
- [ ] 两侧运行伴生安装器；`--check` 通过；两份旧规则活体不存在
- [ ] 行为验证：脏工作树 + 报告模式 grok explorer → receipt `complete`、`dirty_baseline: true`；会话列表首行是标题
- [ ] 在 `../spec.md` 的 Comments 追加实施记录
