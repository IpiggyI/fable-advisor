# 0021 — 6.0.0：档位改为 mainstay / crux / rescue，换用新路由表，codex runner 不再自动换模型

- **Status**: accepted（决策 11 的词数上限已由 [ADR 0022](./0022-orchestration-load-on-events.md) 上调到 2210；决策 6、8、9 已由 [ADR 0026](./0026-sol-6-1-advisor-row-and-segments.md) 修订；决策 1 的档位划分与决策 10 已由 [ADR 0030](./0030-global-plan-route-gate-reuse-window.md) 决策 8 修订，决策 11 的词数上限已被 ADR 0030 决策 9 取代，「未采纳」中的「为观察档位使用增加标记、日志或统计」已被 ADR 0030 决策 5、6 推翻）
- **Date**: 2026-09-27
- **影响范围**: `plugin/skills/orchestration/`（`SKILL.md`、`lanes-claude-code.md`、`lanes-cursor.md`）、`plugin/agents/worker-md.md`、`plugin/agents/advisor-h.md` 与 `docs/zh/` 五份孪生、`plugin/scripts/run-codex.mjs`、`tests/test_runner_contract.py`、`tests/test_runner_lifecycle.py`、`tests/test_runner_lifecycle_windows.cjs`、`docs/agents/fable-advisor-routing.md` 与中文备份、`CONTEXT.md`、`AGENTS.md`、`README.md`、两个清单文件的描述与版本字段、`docs/manuals/6.0.0.html`（新建）。版本 6.0.0（不兼容）
- **关联**: 修订 [ADR 0018](./0018-post-5-1-tuning.md) 决策 4、6、7、10、12 与 [ADR 0020](./0020-one-executor-per-check-list.md) 头部版本说明、决策 6；沿用 [ADR 0009](./0009-grok-lane-dewrapper-runner.md)（grok 跟随 CLI 默认型号）、[ADR 0015](./0015-global-orchestration-entry.md) 与 [ADR 0017](./0017-routing-profile-edit-source.md)（取值只在路由档案）。任务件 `.scratch/tiers-and-routing-6-0/`；讨论记录 `.agent-discuss/tiers-and-consult-iteration/final.md`

## 背景

5.2.0 用了一段时间后，椰椰提出三件事。

1. 档位不符合椰椰分配工作的方式。light 与 standard 是自由选择的首轮池，senior 要两次失败才开，档位里混着型号和强度。椰椰要的是：主力档承担大多数日常工作，攻坚档处理难点，后援档只在前两档失败时用。椰椰长期观察到，换更强的模型比加强度提升大，`xhigh` 有明显跃升。
2. 路由表的型号已经换代。旧档案锚定 grok-4.6、gpt-5.6-sol、gpt-5.6-luna、opus-5；椰椰现在用 grok-4.7、gpt-6-luna、gpt-6-sol、opus-5-5。档案规定换代即重估。
3. codex runner 挡着新表。白名单只收 `gpt-6-astra` 与两个 `gpt-5.6-*`，新表的 `gpt-6-luna`、`gpt-6-sol` 会被判 `spec_invalid`。astra 在会话建立前失败时，runner 自动改用 `gpt-5.6-luna` 重跑：既不看角色和档位，换到的也是新表不用的旧型号。

决定经一次多模型讨论形成（`final.md`），椰椰在 2026-09-26 整理规格时又作了四项决定。规格第三节是完整台账；本 ADR 只记决定与理由。

## 决策

1. **三档改名并按型号划分。** `mainstay`（主力）、`crux`（攻坚）、`rescue`（后援）取代 light、standard、senior。三种角色都适用。档位由型号划分，强度只做档内细分。意图是多数任务在 `mainstay` 结束，极少到 `rescue`。
2. **首轮准入。** 新工作从 `mainstay` 开始。已识别关键难点，或要处理相互制约的条件时，首轮可以直接用 `crux`，不设使用比例。`rescue` 不作首轮选择，除非椰椰声明。修订 ADR 0018 决策 6（首轮池）。
3. **格内选择。** 第一个候选是默认。任务落在档案为某个候选声明的擅长点上时选它，价格低也是擅长点。几个候选同样合适，或需要替换候选时，按档案声明的车道默认顺序。"专长只打破平局"、Stage 2 的 Pareto 权衡句、"没有声明时取最便宜的够用候选"一并退役；没有声明时取格内第一个候选的 `*` 拨盘。理由：格内顺序是椰椰写定的偏好。worker `mainstay` 的 grok 排在更便宜的 luna 前，advisor `mainstay` 的 astra 排在更便宜的 opus 前（想听不同厂商的意见），"取最便宜"会直接推翻这两处顺序。
4. **车道默认顺序保留，只管平手和替换。** 顺序是 grok › codex › claude。整条车道不可用、单个候选不可用、codex runner 对某个型号启动失败，都按这个顺序换到同一格的另一个候选，不按书写顺序，不算能力失败，要披露。Claude Code 的 explorer 例外，按 claude › grok › codex，理由是 Claude Code 自带的 explorer 不能指定模型，本插件补上这一块；这个理由在 Cursor 不成立，所以 Cursor 的 explorer 格按车道顺序排，`composer-2.5-fast` 在 `mainstay` 首位。修订 ADR 0018 决策 10 中 Cursor composer 的位置。
5. **升级梯改为下一档语义，senior 门删除。** R1 不变。R2：返工也失败且诊断归为能力，记一次能力失败，进入下一档（`mainstay` → `crux` → `rescue` → 椰椰），新会话加接管契约；在下一档里按任务特点选型号，下限是新型号在档案排名中不低于失败的型号（没有别的候选时除外），同一型号必须提高强度，不同型号之间不比较强度名。R3：同一型号只提升一次，按完整模型标识计数。R4：较大执行问题可跳过返工，记一次能力失败，进入下一档。首轮就在 `crux` 的任务在 `crux` 失败一次即进 `rescue`。"advisor 的 verdict 顺带裁定是否上 senior"随 senior 门删除；决策类型门的五项清单不动。修订 ADR 0018 决策 6、7。
6. **排名的读法。** ≈ 按同级，≤ 保留方向：`gpt-6-sol` 与 `grok-4.7` 接近，但不当作同级。同级型号之间跨厂商换模型不算降级。`haiku-4-5` 与 `composer-2.5-fast` 不排级，从它们升档按 `crux` 格的按需规则选。`sonnet-5` 是 `sonnet-5-5` 的占位，`sonnet-5-5` 发布或 `sonnet` 别名改指其他型号时重估。
7. **两条已声明假设写进档案。** 换模型的提升大于提高强度；`xhigh` 有明显跃升。下一次模型换代时失效。2026-09-06 的资源偏好与 2026-09-16 的测试集数据退役。
8. **advisor 行映射。** 验收形状用 `mainstay` 的默认 `gpt-6-astra[low]`；决策形状用 `mainstay` 的 `medium`；verdict 自报低置信度用 `crux`；`rescue` 只凭椰椰声明。修订 ADR 0018 决策 10 中的 advisor 默认格。`advisor-h` 不再自称决策类型门与 Tier 3 的默认拨盘；`worker-md` 不再自称只在被点名时使用，因为新表 worker `crux` 的 `opus-5-5[medium]` 会被路由选中。九个 agent 文件的名字与强度不变。
9. **codex runner 不再换模型。** 白名单恰为 `gpt-6-astra`（默认）、`gpt-6-luna`、`gpt-6-sol`；`gpt-5.6-*` 判 `spec_invalid`。省略强度的默认值沿用：astra → `medium`，luna → `max`，sol → `high`。会话建立前的失败只尝试一次，回执报告该错误类，`model_requested` 与 `model_used` 都是请求的型号。换候选是路由判断，归主代理（决策 4）。两条 runner 的回执保留 `fallback_reason`，恒为 `null`，读回执的调用方不因字段消失而出错。修订 ADR 0018 决策 4。
10. **grok 继续跟随 CLI 默认型号。** 沿用 ADR 0009：派发默认不传 `model`。2026-09-27 观测到 CLI 默认就是 `grok-4.7`，所以档案写"省略 `model`，当前 `grok-4.7`"。代价：CLI 默认型号再换代时，派发会跟着变，档案要按"换代即重估"更新。
11. **`SKILL.md` 词数上限从 2110 上调到 2160，落地实测 2160 词，正好到上限，没有余量。** 新增的是首轮准入、格内选择与下一档升级梯的机制，它们必须到达每个主代理，不能沉进某个 harness 分支文件；删掉的 senior 门与 Pareto 句抵不上。不为凑字数删除无关句子。修订 ADR 0020 决策 6。
12. **版本 6.0.0，并入未发布的 5.3.0 批次。** 路由档案的列名改变、codex runner 删除旧型号并取消自动换模型，都是不兼容改动，所以升主版本。ADR 0019、0020 的改动原定 5.3.0，未单独发布，随 6.0.0 一起发。修订 ADR 0018 决策 12 与 ADR 0020 头部的版本说明。

## 记录但不启用

- **收窄的 `crux` 首轮准入**（沿用 codex-advisor 的 H4）。首轮 `crux` 只限四种情况：失败看不见（现有检查无法确认正确性）；失败代价高（一次失败会阻塞依赖工作或难以回退）；已有证据表明会失败（诊断已失败，或同一问题有失败记录）；椰椰声明。椰椰决定保留在记录中、不启用，以后凭日常观察决定是否打开。它不写进 `SKILL.md` 与档案。

## 未采纳

- **格内"越往后越依赖判断"。** codex-advisor 只有一个模型家族才有这条逻辑；本插件有多个家族，各有擅长点。
- **退役车道默认顺序，或按车道顺序、能力顺序重排椰椰写的格子。** 格内顺序是椰椰的偏好；车道顺序只管平手和替换。
- **单个候选不可用时按书写顺序换候选。** 椰椰维持"一律按车道默认顺序"（2026-09-26）。
- **同一档内换模型作为能力失败后的下一步。** 能力失败直接进下一档。
- **把 ≤ 按同级处理的三级排名。** 会丢掉椰椰原话里的方向。
- **Cursor 沿用 Claude 优先，或删除 composer、把它放到末位。** 同厂商优先的理由在 Cursor 不成立；composer 留在 explorer `mainstay` 首位。
- **Cursor 整张表按 allowlist 过滤。** allowlist 只约束钉型号的 `Task` 派发；可用性按每个候选的实际调用入口判断，slug 不写进档案。
- **为观察档位使用增加标记、日志或统计。** 椰椰接受过度路由的风险，自己观察。
- **推送前用真实 codex CLI 核对新型号。** 椰椰决定只在发布后逐拨盘核对；新增的 `gpt-6-luna`、`gpt-6-sol` 在推送前只由假 CLI 测试覆盖。
- **过程咨询、调用姿态、`SessionStart` 注入、完成前强制、逐次派发核对。** 属另开的 advisor 专题，本插件现行 advisor 功能保持。

## 宿主事实与失效检查

- claude 车道派发的 `model` 只接受别名 `haiku`、`sonnet`、`opus`、`fable`，实际型号看子代理记录的 `message.model`。2026-09-27 观测：`haiku` → `claude-haiku-4-5-20251001`，`sonnet` → `claude-sonnet-5`，`opus` → `claude-opus-5-5`；`fable` 送到 API 的是 `claude-fable-5-1`，但当次配置的账号未开通 usage credits，请求被拒（HTTP 429）。子代理记录同时带 `effort`（`sonnet`、`opus` 经 `explorer-h` 为 `high`；haiku 没有这个字段）。失效检查：派发工具的参数出现完整型号 id，或别名解析到别的型号。
- grok：会话目录 `~/.grok/sessions/<cwd 编码>/<会话 id>/` 的 `events.jsonl` 中 `turn_started.model_id` 是回合型号（2026-09-27 为 `grok-4.7`），`chat_history.jsonl` 的消息级 `model_id` 是服务端构建名（`grok-4.7-build`），另有 `reasoning_effort`。失效检查：`grok models` 的默认型号不再是 `grok-4.7`，或这些字段缺失。
- codex：会话记录 `~/.codex/sessions/**/rollout-*.jsonl` 中 `type` 为 `turn_context` 的 `payload.model` 与 `payload.effort` 是实际配置。失效检查：CLI 升级后字段缺失。
- runner 回执记录的是提交的配置，不是观测到的配置；实机核对以会话记录为证。

## 复盘条件

- `rescue` 的使用频率接近 `crux` → 首轮准入或升档下限定得太松，回到决策 2、5。
- 首轮进 `crux` 的任务多数在 `mainstay` 就能完成 → 考虑启用收窄的 `crux` 准入。
- 下一次模型换代，或 `sonnet-5-5` 发布 → 按档案的失效条件重估整张表与两条假设。
- grok CLI 默认型号换代 → 按决策 10 重估档案的 grok 格。
- `SKILL.md` 再次逼近 2160 → 按 ADR 0012 判断哪一段该沉入分支文件，而不是继续上调。
