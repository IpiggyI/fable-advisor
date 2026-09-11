# 05: 中文镜像 —— 03 与 04 改动的全部运行时 md 孪生

**What to build:** 中文读者在 `docs/zh/` 下读到的每个运行时 md，与 `plugin/` 下的英文原文同版：五个 orchestration 文件与两个 agent 文件的孪生内容更新；`docs/zh/agents/worker.md` 新增；`docs/zh/agents/implementer.md` 删除。译文遵循 `CONTEXT.md` 词表（角色 / 档位 / 车道 / 姿态等术语按词表取词；`explorer` / `worker` / `advisor` / `light` / `standard` / `senior` 作为标识符保留英文）。

**Blocked by:** 03、04

**Status:** ready-for-agent

上游：`AGENTS.md` "Chinese mirror of runtime docs"；`docs/agents/plugin-release.md` §1b。范围：`docs/zh/**`。

- [x] `docs/zh/skills/orchestration/` 下五个文件与英文原文逐节对应，无遗漏段落
- [x] `docs/zh/agents/worker.md` 存在、`docs/zh/agents/implementer.md` 不存在、`docs/zh/agents/fable-advisor.md` 更新
- [x] `python3 tests/test_zh_mirror.py` 绿
- [x] 译文中旧术语（Routine / Cross-vendor / In-house 车道名、架构师层、advisor-only、审查员）为零
- [x] 不改动 `plugin/**`

## Comments

2026-09-12 — 已实现（grok lane，cursor-grok-4.6-xhigh）。七个孪生按今日英文全文重译，`worker.md` 孪生新增、`implementer.md` 孪生删除；`python3 tests/test_zh_mirror.py` 7/7；标题数逐文件对齐；旧术语 grep 为零。架构师抽读 zh 前言全文与 `SKILL.md` 姿态节，术语与 `CONTEXT.md` 一致。
