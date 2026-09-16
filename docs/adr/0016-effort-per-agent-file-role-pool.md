# 0016 — 档位入文件名：claude 车道角色池落成 9 个 agent 定义，模型留给按次参数

- **Status**: accepted（2026-09-16 用户口述路由表并指定落在 `plugin/agents/`；advisor 裁定 A′；同日用户追加三项裁定：档位后缀改缩写、新增 `worker-md`、退役两个裸名并把 Cursor 门改成守 advisor 系）
- **Date**: 2026-09-16
- **影响范围**: `plugin/agents/`（9 个文件，删除 `worker.md` 与 `fable-advisor.md`）、`plugin/skills/orchestration/{lanes-claude-code,SKILL,lanes-cursor}.md`、`cursor-hooks/**`、`tests/test_lane_family_gate.py`、`README.md`、对应 `docs/zh/**` 孪生；版本维持 5.1.0（两个字段不动）。不改 runner、`plugin/hooks/**`、其余测试。
- **关联**: [ADR 0014](./0014-role-pool-posture.md)（角色池与姿态——本次把角色池从"概念加两个 agent"落成可派发的 8 格）、[ADR 0015](./0015-global-orchestration-entry.md)（填充表迁到用户档案、决策 6 的"submitted, not observed"措辞、决策 7 把 explorer agent 推给工单 08——本次定案）、[ADR 0012](./0012-orchestration-skill-progressive-disclosure.md)（`SKILL.md` 词数预算，本次沿用）。核对记录 `.scratch/global-orchestration-handoff/issues/08-explorer-probe.md`（第四、五轮）。

## 背景

用户给出 Claude 系路由表（2026-09-16 口述，权威输入）：

```
tier|light|standard|senior
explorer|haiku-4-5|sonnet-5[high*,xhigh]|opus-5[high*,xhigh]
worker|sonnet-5[high]|opus-5[high*,xhigh]
advisor|fable-5-1[low]|fable-5-1[medium]|fable-5-1[high*,xhigh]
```

`*` 标默认档位，`,` 后是升级档位；worker 无 senior 格（走 codex 车道）。要让这张表在 claude 车道可达，宿主只给了两个可控维度，且两者的控制入口不同——这是本次决策的全部约束来源：

1. **`effort` 没有按次参数。** `Agent` 工具入参只有 `description`、`prompt`、`subagent_type`、`model`、`isolation`。档位只能来自 agent 定义的 frontmatter `effort:`，或 CLI 启动时的 `--effort`（整会话级）。
2. **按次 `model` 可靠生效**，haiku / sonnet / opus 三个实测精确命中。

于是档位是"每个取值一个文件"的维度，模型是"按次给"的维度。这不是风格选择，是宿主入参形状的直接推论。

同一轮核对还证伪了仓内三处既有表述：没写 `effort` 的 agent 是掉回**运行模型**在 `settings.json` 里的档位，不是"继承会话 effort"；`/tasks` 只列具名 teammate 的成员名与状态，不显示模型与 effort，也完全不列后台子代理；`worker.md` 的 `effort: medium` 与 `fable-advisor.md` 的 `effort: high` 在新增 8 个文件后不再是"本车道的角色默认档位"。

## 决策

1. **9 个 `<角色>-<档位缩写>` 文件。** 档位后缀用缩写：`low`→`l`、`medium`→`md`、`high`→`h`、`xhigh`→`xh`。文件为 `explorer-h`、`explorer-xh`、`worker-md`、`worker-h`、`worker-xh`、`advisor-l`、`advisor-md`、`advisor-h`、`advisor-xh`。缩写只用于文件名与 `name:`，frontmatter 的 `effort:` 值保持全称，因为那是宿主读取的字段。explorer 的 light 格用 `haiku-4-5`，该模型没有 effort 维度，因此不单设 `explorer-l`，用 `explorer-h` 配按次 `model: haiku` 派即可。`worker-md` 不对应填充表任何一格（worker 只有 light 与 standard 两格，档位均为 high 加 xhigh 升级位），它是用户指定保留的显式备用档，只在调用方主动指名时到达 —— 与被退役的裸名不同，它不会被静默命中。
2. **模型只在恒定时才钉进文件。** explorer 与 worker 逐档换模型（haiku / sonnet / opus），六个文件不写 `model:`，由按次参数给；advisor 一行恒为 fable，四个文件写 `model: fable`。常量钉在文件里，变量留给调用方。
3. **两个裸名退役：删除 `plugin/agents/worker.md` 与 `plugin/agents/fable-advisor.md`。** 中间态曾是"`worker.md` 改 `effort: high` 并标为别名"（advisor 裁定 A′ 的最小缓解，理由是 `medium` 不在路由表里、裸名会成为第三个无人维护的取值）；用户随后裁定直接退役，因为四个 `advisor-*` 已完全覆盖 `fable-advisor.md`，而裸名 `worker` 在缩写命名下无法自洽命名（按真实档位命名即与 `worker-h` 撞名，改成 `worker-md` 则与它的 `high` 档位不符）。退役是破坏性变更，见决策 7。
4. **`model: fable` 写成请求值，不写成执行保证。** 沿用决策 6 的"submitted, not observed"措辞；advisor 的能力边界由"authority is the code it reads, not the model it runs on"兜底，不靠模型稳定性。这一条是普适原则，与下面的具体成因无关，成因解决后仍然保留。

   **现象已消失，成因未证（2026-09-16 当日）。** 决策当时观测到的降级——请求 fable 共 9 次，4 次首轮跑 `claude-fable-5-1` 后中途切 `claude-sonnet-5`，4 次从头就是 sonnet，仅 1 次整程留在 fable，且 9 次里只有 1 次留下 `diagnostics.cache_miss_reason = {"type":"model_changed", ...}` 标记——在账户启用 usage credits 之后不再复现。

   已确立三件事。一、宿主自报 Fable 5.1 作为 advisor 计费走 usage credits 且需先启用：`/advisor fable` 返回 "Fable 5.1 as the advisor bills to usage credits, which need to be set up for your account. Run /model fable to review and enable, then set it as the advisor."，`/model fable` 返回 "Set model to `Fable 5.1` … Draws from usage credits"；启用后 `~/.claude/settings.json` 新增 `advisorModel: "fable"` 键。二、启用后 3 次请求 3 次整程跑在 `claude-fable-5-1` 上、无 `model_changed` 标记（本 ADR 的 advisor 验收派发 38 条 assistant 记录全为 fable，effort 与 perTurnEffort 均 high；另一会话两个与启用前失败样本逐字同参数的对照探针各 2 段全为 fable）。三、启用前 9 次请求里只有 1 次整程。

   **未确立：credits 门禁是否就是全部降级的成因。** 它不是作用于每次派发的确定性预检。时间戳对照（UTC）为证：credits 启用点是 `10:24:11Z`，而探针 g1（项目级定义 `effort: low`、按次 `model: fable`）首条 assistant 记录在 `10:05:59Z`，即启用前 18 分钟，两段全程跑在 `claude-fable-5-1` 上、无 `model_changed`；另有一次派发（c5，`09:22Z`）第一段真的跑在 fable 上才切走。按未证成因处理：上面那组计数只当启用前的历史，不再描述当前行为；同时不把 credits 写成已验证的因果。

   **两条残余未知。** 一、启用前第一段成功后才切走这个模式无法解释，硬性计费预检预测不出它，成因未验证，不做机制猜测。二、启用 credits 之后具名 teammate 路径零样本，启用前那次"从头 sonnet"不能沿用，该路径上 fable 是否可达现为未测 —— 用户已裁定不补跑该探针，此格是有意留白，不是疏漏。

   g1 这个反例经另一会话读本机文件独立核实（两段记录 `10:05:59.447Z` 与 `10:06:00.590Z` 均为 `claude-fable-5-1`、effort `low`、无 `model_changed`；settings mtime `10:24:11Z`，相差 18 分 11 秒），双方就"强相关、成因未证、软门禁与概率性门禁现有证据无法分辨"达成一致。
5. **派发种类写进 doctrine。** 传不传 `Agent` 的 `name` 参数是唯一分流开关：不传是后台子代理派发，frontmatter `effort:` 生效；传了是具名 teammate 派发（该参数仅在 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 的会话存在），frontmatter `effort:` 不生效且静默回落到运行模型的设置档位。因此按路由表派发一律不传 `name`。
6. **三处错误表述改准**，并记下新增 agent 文件只在会话启动时加载（中途新建报 `Agent type not found`），改完须重启才生效。
7. **版本维持 5.1.0（用户裁定）。** 本 ADR 的内容与 ADR 0015 的内容合并在同一个未发布的 5.1.0 里发布。架构师先后提过 5.2.0（理由：5.1.0 的语义由 ADR 0015 钉住，折进去会让该号对不上自己的 ADR）与 6.0.0（理由：退役 `fable-advisor:worker` 与 `fable-advisor:fable-advisor` 两个已随 5.0.0 发布的派发入口属破坏性变更，`docs/agents/plugin-release.md` 的版本规则为此类变更指定 major），用户裁定维持 5.1.0。

   **残余风险，由 README 承担。** 版本号不再为这次破坏性变更提供信号：从 5.0.0 升到 5.1.0 的使用者若仍按 `fable-advisor:worker` 或 `fable-advisor:fable-advisor` 派发，会在无版本号提示的情况下遇到 `Agent type not found`。因此升级说明必须在 `README.md` 的升级段落里点名这两个入口的退役与替代名，这一条不是可选的文档润色。

8. **Cursor 门的触发名跟随 advisor 集合。** `cursor-hooks/fable-lane-family-gate.py` 原先以单一常量 `NAMED_AGENT = "fable-advisor"` 判定"需要显式非 inherit 模型"的派发；该名字退役后门会守空气，而真正需要守的四个 `advisor-*` 不在触发名单里。改为覆盖本角色池的全部 advisor 文件，并要求新增 advisor 档位时不漏守；`resume` 豁免、输入形状兼容（`tool_input` / `toolInput` / `arguments` / 字符串化 JSON）、deny 文案格式一律不变。连带更新 `cursor-hooks/fable-lane-pin.mdc` 及其中文备份、`tests/test_lane_family_gate.py` 的断言、`README.md` 与 `CONTEXT.md` 的门描述。

9. **仓外活副本须由用户部署。** `tests/test_lane_family_gate.py` 与 `tests/test_user_level_archive.py` 对 `~/.cursor/` 与 `/mnt/c/Users/Shy/.cursor/` 的活副本做漂移检查。改了 `cursor-hooks/` 之后，这两项在部署前必然失败；实施方不得为让检查变绿而写仓外路径，失败项如实报告并留给用户执行。

## 未采纳

- **只做默认档位 5 个文件**：放弃 `xhigh` 升级位的可达性，而升级位是路由表明确写出的格，不做等于表不可达。
- **每格一个文件、连模型一起钉死**：explorer 与 worker 的 standard / senior 两档共享同一 effort 取值、只换模型，钉死模型会把 4 个文件变成 8 个，且把可靠的按次维度写成不可覆盖的文件常量。
- **退役现有 `worker.md` 与 `fable-advisor.md`**：连带要改 `SKILL.md`、`README.md`、测试与已发布 5.0.0 用户的引用，收益只是少两个别名。别名加一句说明即可。
- **不新增、承认档位列不可达**：等于放弃路由表。

## 复盘条件

- 宿主给 `Agent` 加上按次 `effort` 参数：8 个文件应折回 3 个（每角色一个），档位改按次给。
- 宿主给出可靠的模型回退信号字段：决策 4 的措辞可收紧。
- 具名 teammate 派发开始执行 frontmatter `effort:`：决策 5 的"一律不传 `name`"随之失效。
- 启用 credits 后补到一个具名 teammate 路径的 fable 样本：决策 4 第二条残余未知随之关闭；若该路径仍不可达，则需在 doctrine 里按路径分别写明。

## 备注

插件级 agent 文件的 frontmatter `effort:` 只直接实测过 `medium` 与 `high` 两个取值；`low` 与 `xhigh` 是从项目级 agent 文件的实测结果外推的（项目级四个取值全部命中）。这两格属于"我们外推的"而非"我们验证的"，须在 5.2.0 安装后重启会话各派一次探针、读子代理转写的 `effort` 字段来确认。
