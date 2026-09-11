# 05: 中文镜像 —— 03 与 04 改动的全部运行时 md 孪生

**What to build:** 中文读者在 `docs/zh/` 下读到的每个运行时 md，与 `plugin/` 下的英文原文同版：五个 orchestration 文件与两个 agent 文件的孪生内容更新；`docs/zh/agents/worker.md` 新增；`docs/zh/agents/implementer.md` 删除。译文遵循 `CONTEXT.md` 词表（角色 / 档位 / 车道 / 姿态等术语按词表取词；`explorer` / `worker` / `advisor` / `light` / `standard` / `senior` 作为标识符保留英文）。

**Blocked by:** 03、04

**Status:** ready-for-agent

上游：`AGENTS.md` "Chinese mirror of runtime docs"；`docs/agents/plugin-release.md` §1b。范围：`docs/zh/**`。

- [ ] `docs/zh/skills/orchestration/` 下五个文件与英文原文逐节对应，无遗漏段落
- [ ] `docs/zh/agents/worker.md` 存在、`docs/zh/agents/implementer.md` 不存在、`docs/zh/agents/fable-advisor.md` 更新
- [ ] `python3 tests/test_zh_mirror.py` 绿
- [ ] 译文中旧术语（Routine / Cross-vendor / In-house 车道名、架构师层、advisor-only、审查员）为零
- [ ] 不改动 `plugin/**`
