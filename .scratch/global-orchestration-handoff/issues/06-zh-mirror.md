# 06: 中文镜像同步

**What to build:** 工单 01、02、03 改动的六个运行时 md 的中文孪生同步：`docs/zh/skills/orchestration/{SKILL,lanes-claude-code,lanes-cursor,lane-preamble}.md`、`docs/zh/agents/{fable-advisor,worker}.md`。只改这六个文件。

**Status:** needs-triage

**Blocked by:** 01、02、03

## 验收标准（全部为必须）

1. 每个孪生按对应英文文件的当前内容重译或局部修订，段落一一对应；英文删除的段落中文也删除，英文新增的句子中文也新增。
2. 术语按根目录 `CONTEXT.md` 取词：explorer / worker / advisor 保留英文代码体；姿态、档位、拨盘、填充表、决策类型门、交付契约、契约缺口、返工票用词表定义。
3. 代码体标识符、命令、路径、字段名（`model_used`、`mode: "report"`、`git worktree`、`--agents` 等）字符原样。
4. 中文文件中不再出现与英文已删内容对应的句子（"最高单价"、"长于接口签名的代码块"、"多步交付物完成前"、"TaskOutput(task_id"、"以质量换速度"等）。
5. `python3 tests/test_zh_mirror.py` 通过。

## 约束

- 不改英文文件，不改其他目录。
- 不执行 `git commit`。

## 验证

```bash
cd /home/hyy/develop/personal/GitHub/fable-advisor
python3 tests/test_zh_mirror.py
rg -n "最高单价|接口签名|多步交付物完成前|TaskOutput\(task_id|以质量换速度|用户规则里|user's rules" docs/zh/ ; echo "exit=$?"   # 期望无输出、exit=1
for f in SKILL lanes-claude-code lanes-cursor lane-preamble; do echo "$f: en $(grep -c '^#' plugin/skills/orchestration/$f.md) zh $(grep -c '^#' docs/zh/skills/orchestration/$f.md)"; done   # 标题数一致
for f in fable-advisor worker; do echo "$f: en $(grep -c '^#' plugin/agents/$f.md) zh $(grep -c '^#' docs/zh/agents/$f.md)"; done
git diff --stat -- docs/zh/
```
