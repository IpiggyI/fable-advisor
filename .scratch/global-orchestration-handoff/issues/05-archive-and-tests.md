# 05: 退役用户规则存档，迁移 pin 规则中文备份，调整漂移测试

**What to build:** 按 [spec.md](../spec.md) 的 A7、Q06：删除 `user-rules/` 下两份规则存档及其中文孪生；`user-rules/zh/fable-lane-pin.mdc` 迁到 `cursor-hooks/zh/fable-lane-pin.mdc`；`tests/test_user_level_archive.py` 只保留 pin 规则的存在性、中文孪生与漂移检查。`AGENTS.md` 与 `docs/agents/**` 的对应句由主代理另改（协调件）。

**Status:** ready-for-agent

**Blocked by:** 无

## 验收标准（全部为必须）

1. 删除 `user-rules/claude-fable-advisor.md`、`user-rules/cursor-fable-advisor.mdc`、`user-rules/zh/claude-fable-advisor.md`、`user-rules/zh/cursor-fable-advisor.mdc`。
2. `git mv user-rules/zh/fable-lane-pin.mdc cursor-hooks/zh/fable-lane-pin.mdc`；删除空目录 `user-rules/`。文件内容若引用自身旧路径或 `user-rules/`，改为新路径；"不是活体" 声明句保留。
3. `tests/test_user_level_archive.py`：
   - `ENGLISH` 只保留 `cursor-hooks/fable-lane-pin.mdc` 一组，其活体列表为 `~/.cursor/rules/fable-lane-pin.mdc`、`/mnt/c/Users/Shy/.cursor/rules/fable-lane-pin.mdc`、`PROMPTS_RULES/fable-lane-pin.cursor.mdc`（现有第三组只列 prompts 副本，此次补两处活体，因为它们是 `docs/agents/cursor-lane-gate.md` 记录的部署路径）。
   - `CHINESE` 只保留 `cursor-hooks/zh/fable-lane-pin.mdc`；`USER_RULES`、`USER_RULES_ZH` 常量删除。
   - 模块 docstring 改为描述 pin 规则的存档检查。
   - 漂移断言、`SKIP` 提示、退出码逻辑不变。
4. `python3 tests/test_user_level_archive.py` 通过：三处活体若存在须与存档逐字节一致（当前三处都存在且一致，见 `docs/agents/cursor-lane-gate.md`）。
5. `python3 tests/test_lane_family_gate.py` 仍通过（它自己也读 `cursor-hooks/fable-lane-pin.mdc`）。
6. 仓库其他位置对 `user-rules/` 的引用只剩 `AGENTS.md`、`docs/agents/cursor-lane-gate.md`（主代理改）与历史 ADR / `.scratch` 记录；`rg -n "user-rules" plugin/ tests/ cursor-hooks/ README.md` 无输出。

## 约束

- 不改 `cursor-hooks/fable-lane-family-gate.py`、`cursor-hooks/fable-lane-pin.mdc`、`cursor-hooks/hooks.example.json`。
- 不改 `AGENTS.md`、`docs/**`、`plugin/**`。
- 不改用户目录活体，不改 prompts 仓库。
- 不执行 `git commit`。`git mv` 与 `git rm` 允许（只改索引与工作树）。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
test ! -d user-rules && echo "user-rules removed"
test -f cursor-hooks/zh/fable-lane-pin.mdc && rg -n "不是活体" cursor-hooks/zh/fable-lane-pin.mdc
python3 tests/test_user_level_archive.py
python3 tests/test_lane_family_gate.py
rg -n "user-rules" plugin/ tests/ cursor-hooks/ README.md ; echo "exit=$?"   # 期望无输出、exit=1
git status --short -- user-rules cursor-hooks tests
```
