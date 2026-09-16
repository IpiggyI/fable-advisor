# 03: 伴生安装器与漂移测试

**What to build:** 椰椰在插件更新后从仓库检出跑一条命令，三件正典（路由档案、Cursor pin 规则、Cursor 门禁脚本）被覆盖到指定家目录的活体，两份已退役的旧规则活体被删除，`~/.cursor/hooks.json` 缺门禁条目时得到警告；`--check` 只比对不写，供测试与自检；`--also` 顺带写一份备份快照。漂移测试改为调用 `--check`，prompts 副本退出测试。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 5–9 条；ADR 0011（本票修订其"活体须手动拷"）。形态参照 codex-advisor 的 `install-agents.sh`，覆盖策略与之相反（无条件覆盖）。范围：新安装器脚本、新安装器测试、`tests/test_user_level_archive.py`、`docs/agents/plugin-release.md`、`docs/agents/cursor-lane-gate.md`。正典位置不变。

- [x] Python 脚本，仓库检出内运行，不进 `plugin/`，不作为插件 hook
- [x] 清单：路由档案 → `~/.claude/docs/`；pin 规则 → `~/.cursor/rules/`；门禁脚本 → `~/.cursor/hooks/`；`retire`：`~/.claude/rules/fable-advisor.md`、`~/.cursor/rules/fable-advisor.mdc`
- [x] 默认家目录为当前用户；`--home <目录>` 可重复，逐个处理
- [x] 无条件覆盖，不比较新旧，不留 `.bak`；每个目标输出动作（installed / unchanged / removed / warning）
- [x] `--check`：只比对；任一活体缺失或字节不同 → 退出非零并列出
- [x] `--also <目录>`：把同一批英文正典写到备份目录
- [x] `~/.cursor/hooks.json`：只检测 `preToolUse` 是否有指向门禁脚本的条目；缺失或文件不存在 → 打印警告，退出码不变，不修改文件
- [x] 新测试在命令行边界（临时目录当家目录）：空目录安装、改动后 `--check` 非零再安装覆盖、`retire` 删除、`--also`、`hooks.json` 警告、两个 `--home`
- [x] `tests/test_user_level_archive.py`：活体比对改为对每个存在的家目录调用 `--check`；prompts 路径删除；中文孪生存在性检查保留
- [x] `plugin-release.md` 两侧更新步骤后加"跑安装器"一步，给出本机双家目录命令；`cursor-lane-gate.md` 的"手动拷贝"改为"跑安装器"
- [ ] 新测试与 `python3 tests/test_user_level_archive.py` 绿；在本机对两侧实际运行一次并 `--check` 通过（此步需椰椰授权，未授权则只在临时目录验证）

## Comments

### 2026-09-16 — 实施记录（grok 车道，`cursor-grok-4.6-xhigh`，requested, not confirmed）

- 落地：`scripts/install-user-level.py`、`tests/test_install_user_level.py`（8/8）、`tests/test_user_level_archive.py` 改为调 `--check`、`plugin-release.md` 第 5 步、`cursor-lane-gate.md` 两处更新。TDD：脚本缺失时 0/8 红，落地后 8/8 绿。
- 验收：架构师复跑 8/8；读了脚本全文；`git diff --stat` 只含契约内文件。
- 未完成项：真实家目录安装留给工单 08。当前 `test_user_level_archive.py` 4/6：两侧路由档案活体落后于正典（工单 05 已重写），`--check` 报 differs 并非零退出；退役文件只警告。发布票跑安装器后转绿。
- 备注：`--check` 对漂移目标打印的是 `warning differs …` 前缀并以非零退出；前缀词表沿用四个，语义靠退出码区分。
