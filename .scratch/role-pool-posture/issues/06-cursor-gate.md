# 06: Cursor 家族门放宽 + Task pin 规则改写

**What to build:** Cursor 会话派 `fable-advisor` 时，门只要求 `model` 显式且非 `inherit`——缺 `model` 或 `inherit` 被拒，任意显式型号（不限 Fable 家族）放行；`generalPurpose` / `explore` 派发不论有无 `model` 都放行；原 `implementer` 分支删除。用户级 pin 规则文本同步：去掉 `implementer` 与家族措辞，改为"具名 agent `fable-advisor` 必须显式 pin；worker 用 `generalPurpose` + 显式 `model`；同模派发省略 `model`"。

**Blocked by:** None（可立即开始）

**Status:** ready-for-agent

上游：`.scratch/role-pool-posture/spec.md` "Cursor" 节；`docs/agents/cursor-lane-gate.md`；[ADR 0011](../../../docs/adr/0011-cursor-lane-family-gate-user-level.md)（门的存在理由：防静默继承）。范围：`cursor-hooks/**`、`tests/test_lane_family_gate.py`；`docs/agents/cursor-lane-gate.md` 若有家族措辞一并改。

- [ ] `cursor-hooks/fable-lane-family-gate.py`：`fable-advisor` 派发缺 `model` → 拒绝；`model: inherit` → 拒绝；任意显式非 inherit 字串 → 放行；非具名 agent 派发 → 放行；不再含 `implementer` 与家族匹配逻辑
- [ ] 拒绝消息说明"需要显式非 inherit 的 model"，不再提家族
- [ ] `tests/test_lane_family_gate.py` 用例随之改写（删 `implementer` 与错家族用例，加"非 Fable 显式型号放行"用例）；`python3 tests/test_lane_family_gate.py` 绿
- [ ] `cursor-hooks/fable-lane-pin.mdc` 改写；`cursor-hooks/hooks.example.json` 若引用名字随之更新
- [ ] `docs/agents/cursor-lane-gate.md` 与新行为一致
