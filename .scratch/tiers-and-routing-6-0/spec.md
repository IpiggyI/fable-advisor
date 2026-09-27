# 6.0.0：档位改为 mainstay / crux / rescue，换用新路由表，codex runner 不再自动换模型

Status: ready-for-agent

日期：2026-09-26。目标版本 `6.0.0`（不兼容：路由档案的列名改变，codex runner 删除旧型号、取消自动换模型）。基线：`HEAD` `e5d65a4d8843ef28fd528dbc2d1f89da3af979e8`（未推送；`origin/main` 停在 `9ac6dee`）。执行者：本检出里的主代理，编排姿态。词表：`CONTEXT.md`，由工单 03 改写相关词条。决策记录：ADR 0021，由工单 03 写。

实施入口：本文件与 `issues/`。`.agent-discuss/tiers-and-consult-iteration/` 只作溯源，其中 `final.md` 是本规格据以展开的决定记录，已关闭，不能再改，也不指向本目录。本目录与讨论目录都未被 git 跟踪，只在本检出可达；是否提交见 O1。

## 一、材料

### 实施必读与必看

路径相对仓库根目录，另注明的除外。"版本"一栏：已跟踪文件以基线提交为准（2026-09-26 核对：这些路径在基线之后没有未提交改动）；未跟踪文件给 SHA-256。

| 材料 | 路径 | 版本 | 用途 | 适用工单 |
|---|---|---|---|---|
| 本规格 | `.scratch/tiers-and-routing-6-0/spec.md` | 本文件 | 当前全部要求、归属与验收 | 全部 |
| 工单 | `.scratch/tiers-and-routing-6-0/issues/01-*.md` … `05-*.md` | — | 各票范围、适用材料、验收与证据记录 | 全部 |
| 讨论结论 | `.agent-discuss/tiers-and-consult-iteration/final.md` | SHA-256 `f4ad0ac60ebb665b0614eda72d7d9b996e37f601354a997cfe45786a0978b91b`（未跟踪） | 本规格据以展开的决定记录；与本规格不一致时以本规格为准（见"权威与冲突"） | 02、03 |
| 词表 | `CONTEXT.md` | 基线 | 统一取词；工单 03 改写 | 全部 |
| 决策记录 | `docs/adr/0014-role-pool-posture.md` 至 `docs/adr/0020-one-executor-per-check-list.md` | 基线 | 本次修订的对象：0018 的决策 4、6、7、10、12，0020 的版本说明与决策 6 | 01、03 |
| 编排技能 | `plugin/skills/orchestration/SKILL.md` | 基线（SHA-256 `1ffe75247cc4beb603e1cc3fd3af2356d819eb3acaf7ba43ac91ec77164d34a8`，2106 词） | 档位、路由、升级梯的现行文字 | 03 |
| 车道文档 | `plugin/skills/orchestration/lanes-claude-code.md`、`plugin/skills/orchestration/lanes-cursor.md` 及 `docs/zh/skills/orchestration/` 下的孪生 | 基线 | codex 车道白名单、回退段、返工与升级引用 | 01、03 |
| agent 文件 | `plugin/agents/worker-md.md`、`plugin/agents/advisor-h.md` 及 `docs/zh/agents/` 下的孪生 | 基线 | 两处自述要改（实现决定 AG-2、AG-3） | 03 |
| codex runner | `plugin/scripts/run-codex.mjs` | 基线 | 白名单（`DEFAULT_EFFORTS`、`VALID_MODELS`）与自动回退（`shouldFallback` 分支） | 01 |
| grok runner | `plugin/scripts/run-grok.mjs` | 基线 | 回执字段 `fallback_reason` 的现行做法（恒为 `null`）；spec 键 `model`、`effort` | 01、02 |
| runner 测试 | `tests/test_runner_contract.py`、`tests/test_runner_lifecycle.py`、`tests/test_runner_lifecycle_windows.cjs` | 基线 | 进程边界的契约与生命周期测试 | 01 |
| 路由档案（编辑源） | `docs/agents/fable-advisor-routing.md`、`docs/agents/fable-advisor-routing.zh.md` | 基线（英文版 SHA-256 `8b5ca0448c4f1c2576d1ed791e43f43ad5fe5ddd6aa55ecd846e5ec6da70f07f`） | 现行表与结构 | 03 |
| 伴生安装器 | `scripts/install-user-level.py`；`tests/test_user_level_archive.py`、`tests/test_install_user_level.py` | 基线 | 把档案装到活体；`--check` 比对 | 03、05 |
| 仓库规则 | `AGENTS.md`、`docs/agents/issue-tracker.md`、`docs/agents/plugin-release.md`、`docs/agents/domain.md` | 基线 | 产物类别、中文孪生、票据格式与批次验收、发布步骤 | 全部 |
| 视觉基准 | `docs/manuals/5.2.0.html` | 提交 `e5d65a4`，SHA-256 `c939d7cd7e34a387c54bb2397136b93a9019f4630d7478d871496ed289b4346e` | 6.0.0 说明书的视觉体系（见第十节）。不得修改 | 04 |
| 5.2.0 发布内容 | 提交 `89b0b52`（发布）与 `9ac6dee`（发布记录） | — | "相对上一版"的比较起点 | 04 |
| 未发布批次 | 提交 `e5d65a4`；`.scratch/verification-batching/spec.md` 与其 `issues/` | 基线 | ADR 0019、0020 的改动随 6.0.0 发布（决定 N1），说明书要列出 | 03、04 |
| 无头浏览器 | `~/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome` | 2026-09-26 在本机存在 | 视觉验收截图；可用等价工具 | 04 |

### 溯源材料（不约束实施）

| 材料 | 路径 | 版本 | 用途 |
|---|---|---|---|
| 交接文档 | `docs/fable-advisor-tier-and-consult-handoff-2026-09.md` | SHA-256 `5c9ba7159016f68311b0f59e5e9e3f7a883b6dda58abcb1329d33b8877346e13`（未跟踪） | 第一节是用户原话（已逐字摘入第二节）；第二节是 codex-advisor 已定内容 H1–H19 |
| 讨论记录 | `.agent-discuss/tiers-and-consult-iteration/`：`request-001.md` 至 `request-004.md`、`claude/001.md`、`claude/002.md`、`gpt/001.md`、`gpt/002.md`、`gpt/003.md` | `request-004.md` SHA-256 `9477932fa0718b009c36648190ffb7012e028bdebe500a1bff8a4abd22a0c3f6`（目录未跟踪，讨论已关闭，不得编辑） | 决定的形成过程 |
| 执行者承接审查 | `.agent-discuss/tiers-and-consult-iteration/handoff-review.md` | SHA-256 `1e5130dabafc71fd77ab2e1c27baaf2569b9b5280c0208a50c39cdb677cd4968`（未跟踪） | 第 1 轮审查以 `final.md` 为入口，未读本规格；处理结果见本文件 Comments "2026-09-26 — 承接审查第 1 轮的处理" |
| codex-advisor 规格 | `/home/hyy/develop/personal/GitHub/codex-advisor/.scratch/tiers-and-advisor-consult/spec.md` | 交接时 SHA-256 `35bad6333d963baffef313f5f7509cd974079bb2010091246c0386212cba5939`；2026-09-26 复查已变为 `f9bd9bd102258ba08034fae292ee5d757216575a9c5c2fb2b3e9dbd38d8b53a4`（556 行，另一仓库仍在修改，未提交） | 沿用条目 H2–H7、H17 的原始条文 TR-3 至 TR-9、AC-11。它在变动中，C1–C7 以本规格第八节与 `final.md` 第二节的文字为准 |

溯源材料都未被 git 跟踪，只在本机这个检出里可达。本规格已把影响交付的用户原话逐字摘入第二节，实施不依赖它们。是否提交它们由用户决定（决定 O1）。

### 权威与冲突

- 本规格表达当前全部要求。`final.md` 是讨论结论；之后用户又在 2026-09-26 整理规格时作了四项决定（第二节 C）。两者不一致时以本规格为准。
- 本任务没有原型，也没有设计稿。唯一的视觉基准是上表的 `5.2.0.html`：它约束 6.0.0 说明书的视觉体系；内容由本规格约束。工单 04 拍的截图是验收证据，不是基准。
- 文字、截图、原型之外的冲突，凡本规格未给处理依据的，保持未决并回报用户，不自行取舍。

## 二、原始需求原文（逐字留档）

本节只放原文，不作摘要。摘要与台账在第三节。

### A. 交接文档第一节：用户原话

来源：交接文档第 26–46 行（SHA-256 见第一节）。其中"思考一点"一句属于 advisor 专题，本规格不处理（决定 U13）。

```text
> 还有就是fable-advisor插件也需要进行类似的迭代，本轮讨论已经确定的内容可以提取出来交接过去，请出一份新的讨论文档。下面是一些不一样的地方：
> explorer优先使用同厂商的模型
> 路由表：
> explorer：
> - mainstay：haiku-4.5 / luna[high*, xhigh] / grok-4.7[medium*, high]
> - crux档：sonnet-5[high] / luna[max] / grok-4.7[xhigh]
> - rescue：opus-5-5[high*, xhigh] / 6-sol[high*, xhigh]
> worker：
> - mainstay：grok-4.7[high*, xhigh] / luna[xhigh*, max] / sol[high]
> - crux档：sol[xhigh*, max] / opus-5-5[medium*, high] / astra[low, medium]
> - rescue：opus5-5[xhigh] / astra[high*, xhigh]
> advisor：
> - mainstay：astra[low*, medium] / opus-5-5[medium] / fable-5-1[medium]
> - crux档：opus-5-5[high*, xhigh] / astra[high] / fable-5-1[high]
> - rescue：astra[xhigh] / fable-5-1[xhigh]
> 模型排名：
> 能力：gpt-6-luna < grok-4.7 ≤ gpt-6-sol < opus-5-5 ≈ gpt-6-astra ≈ fable-5-1
> 价格：gpt-6-luna << grok-4.7 < gpt-6-sol < opus-5-5 < gpt-6-astra < fable-5-1
> 速度：没有明显差异，不再列出
> gpt-6-sol和grok-4.7接近但grok-4.7更便宜
> 思考一点：在Claude Code中插件的advisor模式如何和内置的advisor共存？
```

### B. 讨论中的用户决定

来源：`request-004.md` 中"用户决定"各段（request-002 至 request-004 新增）。其中"用户选定"开头的句子是用户在选项中选定的内容；"措辞来自 `gpt/001`"的两条，用户原话缺失（见 D）。

```text
## 用户决定（request-002 新增）

### 讨论范围

用户原话（逐字）：

> 在Codex的codex-advisor中新实现的advisor功能不需要照抄过来，那边是因为Codex没有内置的advisor功能，因此“H8\9\10”在Claude Code中都不需要，advisor部分需要单独剥离出来讨论，不能全听文档中的，本插件的advisor功能我认为没有什么问题

用户选定"另开讨论"：本讨论只谈档位和路由表；advisor 部分另开一个讨论。

### 档内候选顺序

用户原话（逐字）：

> fable-advisor和codex-advisor最大的不同就是后者只有一种模型因此有“越往后月依赖判断”的逻辑而本次可以认为没有，不同家族模型有各自擅长点，根据需要选择

> - explorer rescue 把 opus-5-5 放在较弱的 gpt-6-sol 前面；因为在fable-advisor中优先使用同厂商模型所以我把Claude系的放前面了
> - worker mainstay 把 grok-4.7 放在更便宜的 luna 前面；因为grok-4.7的“价智比”更高所以我希望优先选用它
> - advisor mainstay 把 astra 放在更便宜的 opus-5-5 前面。因为我希望看到不同厂商模型的意见

> “擅长点”是多样的哈，比如对于相对简单但量大的任务`gpt-6-luna`的优先级就非常高，便宜也是擅长点

### 模型排名补充

用户原话（逐字）：

> haiku-4.5仅在explorer中作为最基础的调查员出现，不需要参与模型能力排名，sonnet-5能力≈gpt-6-luna，价格和opus-5-5接近。

### Cursor

用户选定"只更新路由表"：Cursor 侧本轮只更新路由表。

### advisor 行的列名映射

用户选定"按现行用法映射"：验收形状用 `mainstay` 的默认 `gpt-6-astra[low]`；决策形状用 `mainstay` 的 `medium` 强度；verdict 低置信度时用 `crux`；`rescue` 只凭用户声明。

## 用户决定（request-003 新增）

### 车道默认顺序与同厂商优先

用户原话（逐字）：

> “车道默认顺序"grok › codex › claude"”要退役吗？我认为这点依然适用呀

> 仅是explorer优先使用同厂商的模型

> explorer默认用原厂模型是因为Claude Code本身就有explorer能力只是不能指定模型而本插件补上了这一部分

用户选定"保留原表写法"：各格子都按用户写的顺序；车道默认顺序只在多个候选同样合适时，或换车道时起作用。

### sonnet-5

用户原话（逐字）：

> sonnet-5是为了即将推出的sonnet-5-5做准备的，所以现在路由表看着有些奇怪问题不大

## 用户决定（request-004 新增）

### 能力失败后的升档与 codex runner 回退

用户在 gpt 会话中确认以下两条；用户选定按 `gpt/001` 的转述写入，措辞来自 `gpt/001`：

> - `explorer` 和 `worker` 在同模型、同强度返工后仍因能力失败时，进入下一档，再按任务特点选择模型。
> - 退役 Astra 自动回退到 Luna 的机制。运行器报告失败，由主会话按当前角色和档位选择替代候选。

### Cursor 的 explorer 顺序

用户选定"Cursor 按车道顺序"：同厂商优先只在 Claude Code 成立；Cursor 的 explorer 格按 grok › codex › claude 排序。

### 版本号

用户选定 `6.0.0`。
```

### B2. 讨论收尾时的用户决定（未写入共享请求）

起草 `final.md` 时，用户在选项问题"现行 Cursor 表的 explorer light 格以 composer-2.5-fast（cursor 车道）开头。新表没有 composer……怎么处理？"中选定"保留在 explorer mainstay 首位"，选项原文："Cursor 的 explorer mainstay 格以 composer-2.5-fast 开头，其后按 grok › codex › claude；composer 不参与能力排名，升档时按 crux 格的按需选择规则选。"记录于 `final.md` 一.8。

### C. 整理本规格时的用户决定（2026-09-26）

用户在四个选项问题中的选定项，照录选项原文：

1. 测试接缝：选定"按这七项（推荐）"——"全部沿用现有接缝，不新建测试文件；文字规则靠票内扫描命令验收。"七项为：① runner 契约测试（假 CLI，进程边界）验白名单和"不再回退"；② 生命周期测试只迁移型号；③ 伴生安装器 `--check` 验档案；④ 中文镜像测试；⑤ 票内脚本化文字扫描（旧档位词、旧型号零命中、词数）；⑥ 无头 Chromium 截图对照说明书；⑦ 发布后实机逐拨盘派发一次，记录实际模型。
2. 本规格新增的五条推导：选定"全部确认（推荐）"——"五条在规格里标为已确认。"五条为：随 6.0.0 发布 0019/0020；保留 `fallback_reason` 恒为 `null`；改 `worker-md` 自述；删"verdict 裁定上 senior"一句；视觉基准用 `e5d65a4` 版说明书。
3. `SKILL.md` 词数上限：选定"允许上调到 2160（推荐）"——"新 ADR 记录上调理由；不为凑字数删无关句子。先例：ADR 0020 把 1960 上调到 2110。超过 2160 仍要停下来问椰椰。"
4. `advisor-h` 的自述：选定"本轮一并修正"——"改 advisor-h 的自述，让它不再声称是默认拨盘；默认值以路由档案为准。"

### C2. 处理承接审查后的用户决定（2026-09-26）

针对 O3（是否修改 D6）与 O4（推送前是否用真实 codex CLI 各跑一次 `gpt-6-luna`、`gpt-6-sol`），用户原话（逐字）：

```text
维持D6+不要
```

同一次回复中，用户对 N9、N10、N11（本规格新增、未单独询问的推导，回复前已请用户说明是否推翻）没有提出推翻。

### D. 缺失的原文

- 能力失败后的升档规则、退役 astra 自动回退：用户在 gpt 会话中确认，原话未留存；共享请求按用户选定写入 `gpt/001` 的转述（见 B）。不补写原话。

### E. 讨论中被取代的选择

- 讨论第一轮，用户在"Claude Code 里，插件的过程咨询和内置 advisor 怎样共存？"中选定"(a) 用内置 advisor（推荐）"。随后用户说明 H8、H9、H10 在 Claude Code 中不需要、advisor 部分另开讨论（B"讨论范围"），该选择由 U13 取代，不进入本规格。

## 三、决定台账

状态：**已确认**（用户决定，或经用户确认的推导与沿用）；**已替代**（旧规则被本次决定取代）；**已否决**；**未决**。"依据"指向第二节原文或记录。

### 用户决定

| 编号 | 内容 | 状态 | 依据 |
|---|---|---|---|
| U1 | 三档名称：主力 `mainstay`、攻坚 `crux`、后援 `rescue`，取代 light、standard、senior | 已确认 | A（路由表）；`final.md` 一.1 |
| U2 | Claude Code 路由表按第六节 RP-2 的内容与顺序 | 已确认 | A；`final.md` 一.2 |
| U3 | 能力与价格排名（RP-4） | 已确认 | A；B"模型排名补充" |
| U4 | `sonnet-5` 是 `sonnet-5-5` 的占位，表看着奇怪问题不大 | 已确认 | B"sonnet-5" |
| U5 | 格内按擅长点按需选择，不沿用"越往后越依赖判断"；擅长点多样，价格低也是；三个格子的排序理由 | 已确认 | B"档内候选顺序" |
| U6 | 车道默认顺序 grok › codex › claude 仍适用；各格保留用户写的顺序；车道默认顺序只在多个候选同样合适时或换车道时起作用 | 已确认 | B"车道默认顺序与同厂商优先" |
| U7 | 只有 explorer 优先同厂商模型，且只在 Claude Code 成立；理由：Claude Code 本身有 explorer 能力但不能指定模型 | 已确认 | B"车道默认顺序与同厂商优先"、"Cursor 的 explorer 顺序" |
| U8 | Cursor 本轮只更新路由表；Cursor 的 explorer 格按车道顺序；`composer-2.5-fast` 保留在 explorer `mainstay` 首位 | 已确认 | B"Cursor"、"Cursor 的 explorer 顺序"；B2；`final.md` 一.8 |
| U9 | advisor 行映射：验收用 `mainstay` 默认 `gpt-6-astra[low]`；决策用 `mainstay` 的 `medium`；verdict 低置信度用 `crux`；`rescue` 只凭用户声明 | 已确认 | B"advisor 行的列名映射" |
| U10 | explorer 与 worker 同模型、同强度返工后仍因能力失败时，进入下一档，再按任务特点选择模型 | 已确认 | B（措辞来自 `gpt/001`） |
| U11 | 退役 codex runner 的 astra 自动回退到 luna；runner 报告失败，主会话按角色与档位选替代候选 | 已确认 | B（措辞来自 `gpt/001`） |
| U12 | 版本号 `6.0.0` | 已确认 | B"版本号" |
| U13 | 不照搬 codex-advisor 的过程咨询；Claude Code 中不需要 H8、H9、H10；现行 advisor 功能保持；advisor 部分另开讨论 | 已确认 | B"讨论范围" |
| U14 | 测试接缝按七项（第九节） | 已确认 | C.1 |
| U15 | `SKILL.md` 词数上限上调到 2160，由新 ADR 记录；超过仍停 | 已确认 | C.3 |
| U16 | 修正 `advisor-h` 自述：不再声称默认拨盘，默认值以路由档案为准 | 已确认 | C.4 |
| U17 | 维持 D6：任何换候选（整条车道不可用、单个候选不可用、codex runner 对某型号启动失败）都按车道默认顺序，Claude Code 的 explorer 按 D7 | 已确认 | C2"维持D6" |
| U18 | 推送前不加真实 CLI 核对；逐拨盘核对只在发布后执行（REL-4），不符按 S1 处理 | 已确认 | C2"不要"；U14 ⑦ |

### 沿用 codex-advisor 已定内容（随 `final.md` 确认）

用户要求把 codex-advisor 已定内容交接过来（A 第一句）；以下条目在 `final.md` 第二节列出，用户以"确认关闭"接受。

| 编号 | 内容 | 状态 | 依据 |
|---|---|---|---|
| C1 | H2 前半：第一个候选是默认；未标默认值的格子以第一个列出的强度为默认 | 已确认 | `final.md` 二；codex-advisor TR-3、TR-4 |
| C2 | H3 首轮准入 | 已确认 | `final.md` 二；TR-5 |
| C3 | H4 收窄选项：保留在记录中，不启用 | 已确认 | `final.md` 二；TR-6 |
| C4 | H5 升档下限 | 已确认 | `final.md` 二；TR-7 |
| C5 | H6 失败计数与路径，R3 | 已确认 | `final.md` 二；codex-advisor TR-8（含"较大执行问题可跳过返工，记一次失败"，交接文档 H6 的摘要漏了这一句）；现行 R4 |
| C6 | H7 两条已声明假设 | 已确认 | `final.md` 二；TR-9 |
| C7 | H17 不增加观察用的标记、日志或统计 | 已确认 | `final.md` 二；AC-11 |

### 推导

| 编号 | 内容 | 状态 | 依据 |
|---|---|---|---|
| D1 | 名称对应；claude 车道 `model` 只接受别名，实际模型从子代理记录的 `message.model` 观测 | 已确认（随 `final.md`） | `final.md` 三.1 |
| D2 | worker `crux` 的 `gpt-6-astra` 默认 `low` | 已确认（随 `final.md`） | `final.md` 三.2；C1 |
| D3 | 三个 `rescue` 格各两个候选是有意为之 | 已确认（随 `final.md`） | `final.md` 三.3 |
| D4 | 升档下限的比较：≈ 同级，≤ 保留方向，同级跨厂商换模型不算降级，不同模型之间不比较强度名，R3 按完整模型标识计数 | 已确认（随 `final.md`） | `final.md` 三.4 |
| D5 | `haiku-4-5` 只作基础调查候选；从它升档按 `crux` 格的按需选择规则选 | 已确认（随 `final.md`） | `final.md` 三.5 |
| D6 | 同一格内换候选只用于车道不可用或超时，不算失败，按车道默认顺序换；codex runner 报告启动失败后按此换 | 已确认（随 `final.md`） | `final.md` 三.6 |
| D7 | Claude Code 中 explorer 在平手和换车道时按 claude › grok › codex | 已确认（随 `final.md`） | `final.md` 三.7 |
| D8 | Cursor 的 explorer 行（RP-8） | 已确认（随 `final.md`） | `final.md` 三.8 |
| D9 | Cursor 按每个候选的实际调用入口判断可用性 | 已确认（随 `final.md`） | `final.md` 三.9 |
| D10 | `sonnet-5` 占位的失效条件：`sonnet-5-5` 发布，或 `sonnet` 别名改指其他型号 | 已确认（随 `final.md`） | `final.md` 三.10 |
| D11 | 退役"Luna 当 worker"限制、"专长只打破平局"、2026-09-16 测试集数据、速度排名 | 已确认（随 `final.md`） | `final.md` 三.11 |
| D12 | agent 文件保留按（角色，强度）命名 | 已确认（随 `final.md`） | `final.md` 三.12 |
| D13 | codex 白名单改为三个 `gpt-6-*`，删除 `gpt-5.6-*`；强度校验不变 | 已确认（随 `final.md`） | `final.md` 三.13 |
| N1 | 未发布的 ADR 0019、0020 批次（原定 5.3.0）随 6.0.0 发布，说明书第二部分列出 | 已确认 | C.2；ADR 0020 头部"与后续改动攒齐一起发" |
| N2 | 两条 runner 的回执保留 `fallback_reason` 字段，恒为 `null` | 已确认 | C.2；grok runner 现行做法 |
| N3 | `worker-md` 不再自称"只在被点名时使用"；新表 worker `crux` 的 `opus-5-5[medium]` 由路由选中 | 已确认 | C.2；U2 |
| N4 | 升级梯中"advisor 的 verdict 顺带裁定是否上 senior"随 senior 门删除；决策类型门清单不动 | 已确认 | C.2；C5 |
| N5 | 视觉基准为 `e5d65a4` 版 `docs/manuals/5.2.0.html` | 已确认 | C.2 |
| N7 | 实机核对的安排：逐拨盘核对在发布后执行（REL-4）；发布前只核对档案文字依赖的两项事实——grok CLI 默认型号与四个 claude 别名（PRB-1、PRB-2） | 已确认（U14 ⑦ 的执行安排；前置核对依据"先验证前提再做依赖工作"，未单独询问） | C.1 ⑦；RP-7 依赖这两项事实 |
| N8 | 说明书不复述档案的逐格取值与排名（MAN-2） | 已确认（沿用本仓库先例，未单独询问） | 5.2.0 说明书"路由档案"一节原文："本说明书不复述档案里的型号排名。那些排序是用户在声明日写下的判断，随格子而变。" |
| N9 | 退役"cheapest adequate"默认规则：技能正文 Stage 2 的"No declarations → the cheapest adequate fill"、档案的"take the cheapest adequate candidate at its `*` dial"与"use the cheapest adequate candidate at its listed dial"；没有声明时取格内第一个候选的 `*` 拨盘；价格是擅长点之一 | 已确认（C1、U5 的直接推论；2026-09-26 请用户说明是否推翻，用户未推翻，见 C2） | C1"第一个候选是默认"；U5 的排序理由与"取最便宜"直接冲突：worker `mainstay` 的 grok 排在更便宜的 luna 前，advisor `mainstay` 的 astra 排在更便宜的 opus 前 |
| N10 | 现行档案的专长说明（前端偏 claude 车道、后端偏 codex 车道、复杂任务偏 codex 车道）作为擅长点示例保留 | 已确认（沿用现行用户声明；2026-09-26 请用户说明是否推翻，用户未推翻，见 C2） | 这些是用户 2026-09-06 声明的取值，本次没有撤回；三.11 只撤回"只打破平局"这一用法（`final.md` 三.11） |
| N11 | grok 型号沿用 ADR 0009 的做法：派发默认不传 `model`，跟随 CLI 默认型号；工单 02 观测默认型号；是 `grok-4.7` 时照旧省略，不是时派发传 `model: grok-4.7`；车道文档与 README 中"currently grok-4.6"改为观测结果；回执在省略 `model` 时记 `null` 的现行语义不变，实际型号以会话记录为证 | 已确认（ADR 0009 与 U2 的合并推论；2026-09-26 请用户说明是否推翻，用户未推翻，见 C2） | ADR 0009（运行时目录，型号换代零代码改动）；`lanes-claude-code.md` 第 140 行；U2 表中写的是 `grok-4.7`。已知限制：CLI 默认型号以后再换代时，派发会跟着变，表需按"换代即重估"更新，写入 ADR 0021 |
| N6 | 车道文档不再把内置 Explore 说成任何档位的候选（DOC-1） | 已确认（U2 的直接推论，未单独询问） | 新表未列内置 Explore；把它改称 `mainstay` 候选会给用户的表加一个候选，与 U2 冲突，所以只能删除这一说法 |

### 已替代

| 编号 | 旧规则 | 被什么取代 |
|---|---|---|
| R1 | 首轮池（light 与 standard 自由选）与 senior 门（ADR 0018 决策 6、7） | C2 首轮准入、C5 路径 |
| R2 | "格内候选顺序即车道默认顺序"与"专长只打破平局"（现行档案） | U5、U6 |
| R3 | codex runner astra 启动失败自动改用 luna（ADR 0018 决策 4 保留的回退） | U11 |
| R4 | advisor 默认格：决策 standard、验收 light、低置信或声明时 senior（ADR 0018 决策 10） | U9 |
| R5 | Cursor 表 composer 在 explorer light 首位（ADR 0018 决策 10） | U8 |
| R6 | `SKILL.md` 词数上限 2110（ADR 0020 决策 6） | U15 |
| R7 | 未发布批次的版本号 5.3.0（ADR 0020 头部） | U12、N1 |
| R8 | 2026-09-06 的资源偏好与 2026-09-16 的测试集数据 | U3、C6 |
| R9 | 讨论第一轮的"(a) 用内置 advisor"选择（第二节 E） | U13 |

### 已否决（不得以任何形式回流，包括作为兜底）

- H2 后半"越往后越依赖判断"。
- 退役车道默认顺序。
- 按车道顺序或能力顺序重排用户写的格子，或重排后保留 `opus-5-5` 作 worker `rescue`、advisor `crux` 的默认。
- Cursor explorer 沿用 Claude 优先；删除 composer，或把它放到末位。
- advisor 行映射留到 advisor 专题。
- 版本号 `5.3.0`。
- 把 ≤ 按同级处理的三级排名。
- Cursor 整张表按 `allowlist` 过滤。
- 同一档内换模型作为能力失败后的下一步（codex-advisor 已否决，C4 沿用）。
- 为观察效果增加标记、日志或统计（C7）。
- 单个候选不可用时改按书写顺序换候选（U17 维持 D6）。
- 推送前用真实 codex CLI 核对新增型号（U18）。
- 在本任务中引入过程咨询、调用姿态、`SessionStart` 注入、完成前强制、逐次派发核对（交接文档 H8–H16，归 advisor 专题）。

### 未决

| 编号 | 事项 | 归属 | 是否阻塞 |
|---|---|---|---|
| O1 | 是否提交未跟踪的材料：本任务记录 `.scratch/tiers-and-routing-6-0/`，以及溯源材料（交接文档、`.agent-discuss/tiers-and-consult-iteration/`） | 用户 | 不阻塞在本检出实施；发布时询问 |
| O2 | advisor 专题：交接文档 H8–H16、第五节第 5–9 问、与 Claude Code 内置 advisor 的共存 | 用户另开讨论 | 不属本任务 |

## 四、问题陈述

椰椰在 5.2.0 的使用中遇到三件事：

1. **档位不符合椰椰分配工作的方式。** 5.2.0 的 light、standard 是自由选择的首轮池，senior 要两次失败才开，档位混着型号和强度。椰椰要的是：主力档承担大多数日常工作，攻坚档处理难点，后援档只在前两档失败时用。椰椰长期观察到换更强的模型比加强度提升大，`xhigh` 有明显跃升。
2. **路由表的型号已经换代。** 现行档案锚定 grok-4.6、gpt-5.6-sol、gpt-5.6-luna、opus-5；椰椰现在用 grok-4.7、gpt-6-luna、gpt-6-sol、opus-5-5。档案规定型号换代要重估，已经触发。
3. **codex runner 挡着新表。** 白名单只收 `gpt-6-astra`、`gpt-5.6-luna`、`gpt-5.6-sol`，新表的 `gpt-6-luna`、`gpt-6-sol` 会被判 `spec_invalid`；astra 启动失败时 runner 自动改用 `gpt-5.6-luna` 重跑，既不看角色和档位，换到的也是新表不用的旧型号。

## 五、方案

1. **档位。** 三档改名为 `mainstay`、`crux`、`rescue`，按模型划分，强度只做档内细分。新工作从 `mainstay` 开始；已识别关键难点或要处理相互制约的条件时，首轮可以直接用 `crux`；`rescue` 只经 `crux` 或用户声明进入。
2. **格内选择。** 第一个候选是默认；任务落在某个候选的擅长点上时选它；几个候选同样合适，或需要换车道时，按车道默认顺序。只有 Claude Code 里的 explorer 优先 Claude 模型。
3. **升级。** 一次能力失败（完整尝试加一次同拨盘返工都失败，诊断归为能力）进入下一档，再按任务特点选型号，型号级别不降，同一型号必须提高强度。
4. **路由档案。** 换成用户的新表、新排名、两条已声明假设和 advisor 行映射；Cursor 用同一张表，explorer 行按车道顺序、composer 在首位。
5. **codex runner。** 白名单换成三个 `gpt-6-*`；启动失败只报告，不换型号，主会话按格内换候选。
6. **文档与发布。** 技能正文、车道文档、两个 agent 文件、词表、ADR、README、清单描述随之改写；写 6.0.0 版本说明书，视觉体系对照 5.2.0 说明书；发布 6.0.0，连同未发布的 ADR 0019、0020 批次。

## 六、约束实现取舍的理由

这些理由决定要求没写死的取舍。满足字面却违背理由的实现是错的。

- **档位按模型分，强度只做细分。** 依据是 C6 的两条假设：换模型的提升大于加强度；`xhigh` 有明显跃升。所以升档不降型号级别，同型号升档必须提高强度。
- **首轮可以直接进 `crux`。** 已知困难的任务不该先浪费一次 `mainstay` 尝试。用户接受过度路由的风险，自己观察，所以不加计数机制（C7）。
- **格内顺序是用户的偏好，不是能力排名。** fable-advisor 有多个模型家族，各有擅长点；顺序由用户写定，理由写在档案里。实现不得按能力或价格重排。
- **explorer 同厂商优先只在 Claude Code 成立。** 理由是 Claude Code 自带的 explorer 不能指定模型，本插件补上这一块；这个理由在 Cursor 不成立。
- **runner 不换型号。** 自动换型号会让主会话点名的型号静默变成另一个；换候选是路由判断，归主会话，按格内规则并披露。
- **型号与取值只写在档案里。** 技能正文只写机制（ADR 0015、0017）；用户改格不需要改插件。
- **回执结构不变。** 保留 `fallback_reason` 并恒为 `null`，读回执的调用方不因字段消失而出错。

## 七、用户故事

1. 作为椰椰，我想三档叫 `mainstay`、`crux`、`rescue`，以便名字就说明每档该多常用。
2. 作为主代理，我想档案按椰椰的表原样列出每格候选与拨盘，以便不必从散文里重建表。
3. 作为主代理，我想新工作默认进 `mainstay`，以便多数任务跑在便宜的型号上。
4. 作为主代理，我想在已识别关键难点或相互制约的条件时首轮直接用 `crux`，以便不在明知困难的任务上浪费一次尝试。
5. 作为主代理，我想 `crux` 没有使用比例限制，以便档位跟着任务走。
6. 作为椰椰，我想首轮 `rescue` 只凭我的声明，以便后援档保持少用。
7. 作为椰椰，我想收窄的首轮 `crux` 准入只留在记录里、不启用，以便以后凭观察决定是否打开。
8. 作为主代理，我想格内第一个候选就是默认，以便没有特别理由时不用再判断。
9. 作为主代理，我想在任务落在某个候选的擅长点上时选它，比如简单量大的任务选 `gpt-6-luna`，以便价格和特长都能用上。
10. 作为主代理，我想几个候选同样合适时按车道默认顺序取，以便平手有唯一答案。
11. 作为主代理，我想车道不可用或超时时，按车道默认顺序换到格内另一个候选并披露，以便换车道不算失败。
12. 作为 Claude Code 里的主代理，我想 explorer 在平手和换车道时按 claude › grok › codex，以便调查员优先用插件补上的 Claude 型号。
13. 作为 Cursor 里的主代理，我想 explorer 格按 grok › codex › claude 排、composer 在 `mainstay` 首位，以便 Cursor 不套用 Claude Code 的同厂商理由。
14. 作为主代理，我想一次能力失败定义为完整尝试加一次同拨盘返工都失败且诊断归为能力，以便环境问题和契约缺口不推动升档。
15. 作为主代理，我想能力失败后进入下一档再按任务特点选型号，以便不在同一档里挨个试。
16. 作为主代理，我想下一档的型号在档案排名里不低于失败的型号，以便升档不变成降级。
17. 作为主代理，我想同型号升档必须提高强度，以便每次升档都改变了什么。
18. 作为主代理，我想同一型号只提升一次，以便不在一个型号上连升强度。
19. 作为主代理，我想较大的执行问题可以跳过返工直接记一次失败进入下一档，以便跑飞的车道不再耗一轮返工。
20. 作为主代理，我想 `rescue` 失败后交给椰椰，以便没有第四档。
21. 作为主代理，我想首轮就在 `crux` 的任务失败一次即可进 `rescue`，以便困难任务不被卡在 `crux`。
22. 作为主代理，我想从 `haiku-4-5` 或 `composer-2.5-fast` 升档时按 `crux` 格的按需规则选，以便未排名的基础候选也有明确的下一步。
23. 作为主代理，我想 ≈ 按同级、≤ 保留方向，以便跨厂商升档的判断忠于椰椰的原话。
24. 作为椰椰，我想档案写明 `sonnet-5` 是占位和它的失效条件，以便 `sonnet-5-5` 发布时记得重估。
25. 作为椰椰，我想档案记下两条已声明假设和失效条件，以便下一次换代时强制重估。
26. 作为主代理，我想 advisor 的验收、决策、低置信度各自对应新列里的哪一格写明白，以便改名后 advisor 用法不变。
27. 作为主代理，我想 claude 车道的每个拨盘对应到现有 agent 文件，并知道 `model` 只接受别名，以便派发时知道实际型号要从记录里核对。
28. 作为主代理，我想 codex runner 接受 `gpt-6-luna` 与 `gpt-6-sol`，以便按新表派发不被判 `spec_invalid`。
29. 作为主代理，我想 `gpt-5.6-*` 被判 `spec_invalid`，以便退役型号不会被悄悄使用。
30. 作为主代理，我想 astra 启动失败时 runner 只报告失败、不换型号，以便我点名的型号不被替换。
31. 作为读回执的调用方，我想 `fallback_reason` 字段仍在且为 `null`，以便解析逻辑不用改。
32. 作为主代理，我想 `worker-md` 不再说自己只在被点名时使用，以便它和新表的 `opus-5-5[medium]` 不矛盾。
33. 作为主代理，我想 `advisor-h` 不再说自己是默认拨盘，以便 advisor 的默认只有档案一个来源。
34. 作为主代理，我想车道文档不再把内置 Explore 说成某一档的候选，以便候选只来自档案。
35. 作为仓库维护者，我想 `SKILL.md` 不超过 2160 词，且上调写进 ADR，以便词数预算仍然受控。
36. 作为仓库维护者，我想每个改动的运行时 Markdown 同一次更新中文孪生，以便 `test_zh_mirror` 持续通过。
37. 作为仓库维护者，我想一份 ADR 记下本次决定并点名它修订的 ADR 0018、0020 条目，以便以后的读者知道为什么。
38. 作为椰椰，我想 README 的升级段写明 6.0.0 的不兼容点和"更新后跑伴生安装器"，以便升级时不漏步骤。
39. 作为椰椰，我想 6.0.0 说明书写清本版完整行为和相对 5.2.0 的全部变化，包括 ADR 0019、0020 那一批，以便不用翻 ADR 就知道装上的是什么。
40. 作为椰椰，我想 6.0.0 说明书看起来和 5.2.0 说明书是同一套样式，并且有人实际看过两者截图，以便视觉一致不是靠猜。
41. 作为椰椰，我想发布后新表的每个拨盘在对应车道实际跑一次、以会话记录证明实际型号，以便知道装上的表每一格都能用。
42. 作为主代理，我想在写档案前确认 grok CLI 的默认型号和四个 claude 别名的实际型号，以便档案里的到达方式写得对。
43. 作为椰椰，我想提交、推送、两侧更新和运行安装器都等我当次授权，以便发布由我控制。

## 八、实现决定

要求编号供工单引用。"依据"见第三节。

### 档位与路由机制（技能正文 `SKILL.md`）

- **TR-1 档位。** 档位为 `mainstay`、`crux`、`rescue`，取代 `light`、`standard`、`senior`，三种角色都适用，任一角色可在任一档位。档位由型号划分，强度是档内细分。意图写明：多数任务在 `mainstay` 结束，极少到 `rescue`。（U1、C6）
- **TR-2 首轮准入。** 新工作从 `mainstay` 开始；已识别关键难点，或要处理相互制约的条件时，首轮可以直接用 `crux`；不设使用比例；`rescue` 不作首轮选择，除非用户声明。（C2）
- **TR-3 收窄选项不进正文。** C3 的收窄条件只写进 ADR 0021，不写进 `SKILL.md` 与档案的现行规则。（C3）
- **TR-4 格内选择（Stage 2）。** 格内第一个候选是默认；任务落在档案为某个候选声明的擅长点上时选它（价格算擅长点）；几个候选同样合适，或需要换车道时，按档案声明的车道顺序。"specialty only breaks ties"一句删除；Stage 2 的 Pareto 权衡句与"No declarations → the cheapest adequate fill, lanes compared at their default dials only"删除，没有声明时取格内第一个候选的 `*` 拨盘（N9）。正文不写车道顺序的具体值和 explorer 例外，这些值在档案。（U5、U6、U7、C1、N9）
- **TR-5 换车道。** 车道不可用或超时——包括 codex runner 报告启动失败——的契约原样交给同一格的另一个候选，按档案声明的车道顺序（D6；Claude Code 的 explorer 按 D7），披露；不算能力失败。这条顺序对整条车道不可用、单个候选不可用、codex runner 对某型号启动失败都适用（U17）。两条 CLI 车道都不可用时转 claude 车道并说明失去的跨厂商复核（现行规则保留）。（D6、U11、U17）
- **TR-6 升级梯。** R1 不变。R2：返工也失败且归因能力，记一次能力失败，进入下一档（`mainstay` → `crux` → `rescue` → 用户），新会话加接管契约；在下一档里按任务特点选型号，下限是：下一拨盘的型号在档案排名中不低于失败拨盘的型号（除非没有别的候选），同一型号必须提高强度，不同型号之间不比较强度名。R3：同一型号只提升一次，按完整模型标识计数。R4：较大执行问题（工具反复失败、跑飞、触碰保留项）可跳过返工，记一次能力失败，进入下一档。环境问题和契约缺口不算失败。`rescue` 只经 `crux` 或用户声明进入；首轮就在 `crux` 的任务在 `crux` 失败一次即进 `rescue`；`rescue` 失败交给用户。（U10、C4、C5、D4）
- **TR-7 删除 senior 门。** "Senior gate"整句删除，包括"advisor 的 verdict 顺带裁定是否上 senior"。决策类型门的五项清单及其文字不变。（N4）
- **TR-8 正文不写取值。** `SKILL.md` 不新增型号名、型号排名或拨盘取值；排名与取值只在档案。（理由见第六节）
- **TR-9 词数。** `SKILL.md` 改后不超过 2160 词（`wc -w`）；上调由 ADR 0021 记录；不为凑字数删除无关句子。（U15）
- **TR-10 不加观察机制。** 本任务不增加任何为观察档位使用而设的标记、日志或统计。（C7）

### 路由档案（编辑源 `docs/agents/fable-advisor-routing.md` 与中文备份）

- **RP-1 声明与锚定。** 声明日期 2026-09-26；锚定型号 `grok-4.7`、`gpt-6-luna`、`gpt-6-sol`、`gpt-6-astra`、`haiku-4-5`、`sonnet-5`、`opus-5-5`、`fable-5-1`、`composer-2.5-fast`；保留"任一相关型号换代时重估"。
- **RP-2 Claude Code 表。** 逐格如下（顺序即用户写的顺序，`›` 分隔候选，`*` 为默认强度；worker `crux` 中 astra 的 `low*` 是 D2）：

  | 角色 | `mainstay` | `crux` | `rescue` |
  |---|---|---|---|
  | explorer | `haiku-4-5` › `gpt-6-luna[high*, xhigh]` › `grok-4.7[medium*, high]` | `sonnet-5[high]` › `gpt-6-luna[max]` › `grok-4.7[xhigh]` | `opus-5-5[high*, xhigh]` › `gpt-6-sol[high*, xhigh]` |
  | worker | `grok-4.7[high*, xhigh]` › `gpt-6-luna[xhigh*, max]` › `gpt-6-sol[high]` | `gpt-6-sol[xhigh*, max]` › `opus-5-5[medium*, high]` › `gpt-6-astra[low*, medium]` | `opus-5-5[xhigh]` › `gpt-6-astra[high*, xhigh]` |
  | advisor | `gpt-6-astra[low*, medium]` › `opus-5-5[medium]` › `fable-5-1[medium]` | `opus-5-5[high*, xhigh]` › `gpt-6-astra[high]` › `fable-5-1[high]` | `gpt-6-astra[xhigh]` › `fable-5-1[xhigh]` |

- **RP-3 格内选择的取值。** 车道默认顺序 grok › codex › claude，只用于平手和换车道；Claude Code 的 explorer 例外，按 claude › grok › codex，写明理由（Claude Code 自带 explorer 不能指定模型，本插件补上）；记下用户给的三条排序理由；擅长点只列示例：简单量大的任务优先 `gpt-6-luna`、价格低、前端偏 claude 车道、后端和复杂任务偏 codex 车道（来自现行档案的用户声明，N10）、希望听到不同厂商的意见。换候选的顺序按 D6、D7，写明它对单个候选不可用同样适用（U17）。（U5–U7、D6、D7、N10、U17）
- **RP-4 排名。** 能力：`gpt-6-luna` ≈ `sonnet-5` < `grok-4.7` ≤ `gpt-6-sol` < `opus-5-5` ≈ `gpt-6-astra` ≈ `fable-5-1`，写明 ≈ 按同级、≤ 保留方向。价格：`gpt-6-luna` << `grok-4.7` < `gpt-6-sol` < `opus-5-5` < `gpt-6-astra` < `fable-5-1`，`sonnet-5` 价格接近 `opus-5-5`。`gpt-6-sol` 与 `grok-4.7` 能力接近，`grok-4.7` 更便宜。`haiku-4-5` 与 `composer-2.5-fast` 不排级，从它们升档按 `crux` 格的按需规则选。速度不列。`sonnet-5` 是 `sonnet-5-5` 的占位，失效条件为 `sonnet-5-5` 发布或 `sonnet` 别名改指其他型号。（U3、U4、D4、D5、D10）
- **RP-5 已声明假设。** 换模型的提升大于加强度；`xhigh` 有明显跃升；失效条件：下一次模型换代。（C6）
- **RP-6 advisor 映射。** 验收形状用 `mainstay` 默认 `gpt-6-astra[low]`；决策形状用 `mainstay` 的 `medium` 强度；verdict 低置信度用 `crux`；`rescue` 只凭用户声明。（U9）
- **RP-7 Claude Code 的到达方式。** grok 经 grok runner，GPT 经 codex runner；claude 车道经本插件 agent 文件加每次派发的 `model`。写明 `model` 只接受别名 `haiku`、`sonnet`、`opus`、`fable`，别名是指针，实际型号以子代理记录的 `message.model` 为准；写明每个 claude 拨盘对应的 agent 文件（`explorer-h`、`explorer-xh`、`worker-md`、`worker-h`、`worker-xh`、`advisor-md`、`advisor-h`、`advisor-xh`），`haiku-4-5` 经 `explorer-h`、无强度维度。grok 按 N11：工单 02 观测到 CLI 默认型号是 `grok-4.7` 时写"省略 `model`，跟随 CLI 默认"，不是时写"spec 传 `model: grok-4.7`"。（D1、N11）
- **RP-8 Cursor 部分。** worker 与 advisor 行同 RP-2。explorer 行：`mainstay` 为 `composer-2.5-fast` › `grok-4.7[medium*, high]` › `gpt-6-luna[high*, xhigh]` › `haiku-4-5`；`crux` 为 `grok-4.7[xhigh]` › `gpt-6-luna[max]` › `sonnet-5[high]`；`rescue` 为 `gpt-6-sol[high*, xhigh]` › `opus-5-5[high*, xhigh]`。可用性按实际调用入口：GPT 候选经 Shell 走 codex runner；`grok-4.7` 的 `medium`、`high` 经 Shell 走 grok runner，`xhigh` 经钉型号的 `Task`；Claude 候选与 `composer-2.5-fast` 经钉型号的 `Task`；当回合 `allowlist` 只约束钉型号的 `Task` 派发；缺少的变体跳过并披露；slug 不写进档案。（U8、D8、D9）
- **RP-9 退役内容不再出现。** 首轮池与 senior 门一节；"Candidate order inside a cell is the lane default order"；"Specialty only breaks ties"；"Luna as a worker"限制；2026-09-06 资源偏好与 2026-09-16 测试集数据；grok-4.6、gpt-5.6-*、opus-5 等旧锚定；"With no reason to do otherwise, take the cheapest adequate candidate at its `*` dial"与"use the cheapest adequate candidate at its listed dial"（N9）；用旧拨盘写的典型升级路径"`grok-4.6[medium]` → `grok-4.6[xhigh]` → `gpt-6-astra[medium]`"；Cursor 部分的"a cell lists only the variants the allowlist carries"（改为 RP-8 的按入口判断）、"Fable appears only in the senior cell…"一段、"On 2026-09-16 the allowlist carried…"的 slug 快照（D9；slug 不写进档案）。（R1、R2、R8、D9、D11、N9）
- **RP-10 保留内容。** 口头声明的易变状态（额度、期限；其中"没有声明时取最便宜"改为"取格内第一个候选的 `*` 拨盘"，N9）；handoff 声明；调整方法（改这里、跑伴生安装器、更新声明日期）。
- **RP-11 不复述机制。** 档案引用技能的准入与升级梯，不复述规则；可以给一条用新拨盘的示例路径。
- **RP-12 中文备份。** `.zh.md` 同步为中文，内容一致，不安装。

### codex runner

- **RN-1 白名单。** 模型恰为 `gpt-6-astra`（默认）、`gpt-6-luna`、`gpt-6-sol`；`gpt-5.6-luna`、`gpt-5.6-sol` 及其他名字判 `spec_invalid`，不启动子进程。（D13）
- **RN-2 省略强度的默认值。** astra → `medium`，luna → `max`，sol → `high`（沿用现值）。这是 runner 的省略默认，不是档案默认。
- **RN-3 不换型号。** 会话建立前的失败（`preparation_stalled`，或 `codex_failed` 且尚无会话 id）只尝试一次：回执报告该错误类，`model_requested` 与 `model_used` 都是请求的型号。（U11）
- **RN-4 回执字段。** 两条 runner 的回执保留 `fallback_reason`，恒为 `null`。（N2）
- **RN-5 强度校验不变。** 全局集合 `low`、`medium`、`high`、`xhigh`、`max`。
- **RN-6 车道文档。** `lanes-claude-code.md` 的 codex 段：型号清单与默认强度按 RN-1、RN-2；"Fallback"段改为"runner 不换型号，报告失败，主代理按 `SKILL.md` 的换车道规则处理"；回执字段说明写明 `fallback_reason` 恒为 `null`、为兼容保留。中文孪生同步。

### agent 文件

- **AG-1 不改名。** 九个 agent 文件的名字、数量、文件头的 `effort` 不变。（D12）
- **AG-2 `worker-md`。** `description` 与正文不再说它是"只在被点名时使用的备用拨盘"、"不会被自动选中"；写明它服务于档案点名的任何 `medium` worker 拨盘。正文中替档案决定路由的句子（如"普通契约去 `worker-h`"）删除。中文孪生同步。（N3）
- **AG-3 `advisor-h`。** `description` 与正文不再说它是决策类型门与 Tier 3 验收的默认拨盘；写明哪个 advisor 拨盘由档案决定。其他 advisor 文件不动。中文孪生同步。（U16）

### 其他文档

- **DOC-1 车道文档的档位引用。** `lanes-claude-code.md` 与 `lanes-cursor.md` 中"the senior gate applies"、"the senior tier only through its gate"、"a raise … same model at higher effort, or another model"改为 TR-6 的下一档语义；"built-in Explore agent remains a light-explorer fill"不再把内置 Explore 说成任何档位的候选（新表没有它），成本说明保留；`lanes-claude-code.md` grok 段 `model` 条的"currently grok-4.6, 2026-09"按 N11 与工单 02 的观测改写。中文孪生同步。
- **DOC-2 词表 `CONTEXT.md`。** 改写"档位""升级梯""填充表"：三档名称与含义、首轮准入、下一档路径与下限、格内选择（第一个默认、按擅长点、车道顺序只管平手和换车道）；"升级梯"中的 senior 门与"verdict 顺带裁定"删除；为 light、standard、senior、首轮池、senior 门加 `_Avoid_`。
- **DOC-3 ADR 0021。** 记录本规格的决定；点名修订 ADR 0018 决策 4（回退）、6（首轮池）、7（senior 门）、10（advisor 默认格、Cursor composer 位置）、12（版本），ADR 0020 决策 6（词数上限）与头部版本说明（5.3.0 并入 6.0.0）；记录 C3 收窄选项（不启用）；记录宿主事实及失效检查：claude 车道 `model` 只接受别名；Codex 会话记录 `turn_context` 与 grok 会话目录可读出实际型号与强度；工单 02 的观测结果。
- **DOC-4 `AGENTS.md`。** 开头的"light / standard / senior tiers"与"User routing profile"段"light and standard columns are the first-round pool; senior is gated"改为新档位与准入的一句话摘要，指向 `CONTEXT.md`。
- **DOC-5 `README.md`。** codex 车道行与安装说明中关于型号、默认强度、回退的部分归工单 01，其余归工单 03。描述当前行为的段落改为新档位、准入与升级（第 5、20、78 行附近）；grok 车道行"catalog default, currently grok-4.6"按 N11 与工单 02 的观测改写；codex 车道行与安装说明的型号、默认强度按 RN-1、RN-2，删除"Only astra falls back (to luna)"；升级段新增 v6.0.0：不兼容点（档案列名、白名单型号、取消回退）、并入的 ADR 0019、0020 改动、"更新后运行伴生安装器"。旧版本的历史描述不改。
- **DOC-6 清单描述。** `plugin/.claude-plugin/plugin.json` 的 `description` 与 `.claude-plugin/marketplace.json` 的两处 `description` 改为新档位，删除"the senior tier is gated"。版本字段由工单 05 改。

### 版本说明书

- **MAN-1 形态。** `docs/manuals/6.0.0.html`：自包含中文 HTML，两部分"本版完整行为"与"相对上一版的变化"，按 `docs/agents/plugin-release.md` 第 0 步。
- **MAN-2 第一部分覆盖。** 角色、档位、车道、姿态；首轮准入、格内选择、换车道、升级梯；路由档案一节：位置（正典、活体、中文备份）、结构、调整方法、格内选择规则与 advisor 映射的含义，不复述逐格取值与排名（N8）；两条 runner 的 spec 键、回执字段（含恒为 `null` 的 `fallback_reason`）、错误类与报告模式语义（含 ADR 0019）；契约检查清单由 runner 执行一次（ADR 0020）；claude 车道 agent 文件与别名；用户级文件与伴生安装器；测试清单；已知限制（claude 车道只能按别名指定、grok 观测方式、Cursor slug 未核实等，按工单 02 的结果）。
- **MAN-3 第二部分覆盖。** 相对 5.2.0（提交 `89b0b52`）的每项变化，写改了什么、为什么、对应 ADR 与工单：ADR 0019、ADR 0020 批次（提交 `e5d65a4`，含说明书样式改版）与 ADR 0021 的全部决定；写明原定 5.3.0 未单独发布；升级步骤。
- **MAN-4 语言。** 全文中文；标识符、路径、型号名保持原文。
- **MAN-5 视觉。** 按第十节。基准文件不改。

### 发布

- **REL-1 版本字段。** `plugin/.claude-plugin/plugin.json` 的 `version` 与 `.claude-plugin/marketplace.json` 的 `plugins[0].version` 都改为 `6.0.0`。
- **REL-2 授权。** 提交、推送、两侧 `claude plugin` 更新、两侧运行伴生安装器，每一步都需要用户在当次请求中明确授权；没有授权就停在工作树并报告。
- **REL-3 安装核对。** 两侧缓存出现 `6.0.0` 且抽查命中本版新增短语；两个家目录的 `--check` 通过。
- **REL-4 发布后逐拨盘实机核对（U14 ⑦）。** 用已安装的插件，新表每个拨盘各派发一次，报告模式或只读最小任务，记录实际型号：
  - codex 车道（codex runner）：`gpt-6-luna` 的 `high`、`xhigh`、`max`；`gpt-6-sol` 的 `high`、`xhigh`、`max`；`gpt-6-astra` 的 `low`、`medium`、`high`、`xhigh`。证据：Codex 会话记录（`~/.codex/sessions/**/rollout-*.jsonl`）中 `type` 为 `turn_context` 的 `payload.model` 与 `payload.effort`。
  - grok 车道（grok runner）：`grok-4.7` 的 `medium`、`high`、`xhigh`，按 PRB-1 的结果决定是否传 `model`。证据：grok 会话目录（`~/.grok/sessions/<cwd 编码>/<会话 id>/`）中的 `model_id` 与 `reasoning_effort`。
  - claude 车道（本插件 agent 文件加别名）：表中每个 claude 拨盘各一次——`explorer-h` 配 `haiku`、`sonnet`、`opus`，`explorer-xh` 配 `opus`，`worker-md`、`worker-h`、`worker-xh` 配 `opus`，`advisor-md`、`advisor-h`、`advisor-xh` 各配 `opus` 与 `fable`。证据：子代理记录中的 `message.model`；强度不可观测，照实记录。
  - 回执记录的是提交的配置，不能单独作为证据。

### 发布前的前置核对（工单 02）

只核对档案文字依赖的事实；逐拨盘核对按 U14 ⑦ 在发布后执行（REL-4）。

- **PRB-1 grok 默认型号。** 用工作树的 grok runner 不传 `model` 跑一次最小报告任务，从 grok 会话目录读出 `model_id`；不是 `grok-4.7` 时，再传 `model: grok-4.7` 跑一次，确认可用。结果决定 RP-7 是否写"spec 传 `model`"。
- **PRB-2 claude 别名。** 用本插件的 agent 文件，别名 `haiku`、`sonnet`、`opus`、`fable` 各派发一次只读最小任务。证据：子代理记录中的 `message.model`，期望依次为 `claude-haiku-4-5-20251001`、`claude-sonnet-5`、`claude-opus-5-5`、`claude-fable-5-1`。结果决定 RP-7 的别名说明是否成立。
- **PRB-3 Cursor。** 由用户在 Cursor 中查看当回合 `allowlist`：`grok-4.7` 的 `xhigh`、`opus-5-5` 各强度、`fable-5-1` 各强度、`sonnet-5`、`haiku-4-5`、`composer-2.5-fast` 是否有 slug。执行者无法到达 Cursor；结果回报前标为未核实，不阻塞发布。

## 九、测试决定

好测试只看外部行为：runner 在进程边界（假 CLI、真实 spec 与回执），安装器在命令行边界（临时家目录），文档在文字扫描与渲染画面。不读内部函数名。

1. **runner 契约测试（现有接缝，`test_runner_contract.py`）。**
   - 白名单：`gpt-6-luna`、`gpt-6-sol` 被接受，省略强度时提交 RN-2 的默认值；`gpt-5.6-luna`、`gpt-5.6-sol` 判 `spec_invalid` 且不启动子进程。
   - 不换型号：astra 在会话建立前失败（两种错误类各一例）时，假 CLI 只被调用一次，回执报告该错误类，`model_used` 为 `gpt-6-astra`，`fallback_reason` 为 `null`。现有两个回退用例和报告模式的回退断言改写成验证这一行为，不得只删除。
   - 正常调用用例中的旧型号输入迁移到新型号；拒绝用例（如 Terra）保留。
2. **runner 生命周期测试（现有接缝，`test_runner_lifecycle.py`、`test_runner_lifecycle_windows.cjs`）。** 只迁移型号输入；迁移后用例必须真正走到进程阶段，而不是在参数校验处退出。
3. **伴生安装器（现有接缝）。** 档案改完后，装进一个临时家目录，再对它跑 `--check` 退出 0；`test_install_user_level.py` 与 `test_user_level_archive.py`（中文备份存在性检查）通过。真实家目录的 `--check` 属发布（工单 05）。
4. **中文镜像（现有接缝，`test_zh_mirror.py`）。** 每票改动运行时 Markdown 后运行。
5. **文字扫描（票内命令，不新建测试文件）。**
   - 各票只扫自己拥有的文件；全仓扫描在工单 05 作为批次检查执行。
   - 全仓扫描范围：`plugin/`、`docs/zh/`、`README.md`、`CONTEXT.md`、`AGENTS.md`、`docs/agents/`、两个清单文件。零命中：档位含义的 `light`、`standard`、`senior`，`first-round pool`、`senior gate`、`首轮池`、`senior 门`（`CONTEXT.md` 的 `_Avoid_` 条目、README 的历史升级描述、ADR 与旧说明书除外）；`gpt-5.6-`、`grok-4.6`（测试里的拒绝用例与 README 的历史升级描述除外）；`falls back (to luna)`、`retries once on luna`；`cheapest adequate`。中文副本（`docs/zh/`、`docs/agents/fable-advisor-routing.zh.md`）同样零命中现行中文译法：`首轮池`、`帕累托`、`专长只作决胜项`、`最便宜的充分填充`、`仍是 light`、`格内候选顺序即车道默认顺序`、`专长只作平手裁决`、`最便宜的够用候选`、`一格只列 allowlist 里有的变体`、`Fable 只出现在 senior 格`、`2026-09-16 的 allowlist`。`test_zh_mirror.py` 只查孪生是否存在，不查内容，所以中文副本靠这组扫描。
   - `light`、`standard`、`senior` 也有非档位的用法（例如普通英文词）；扫描命中逐条判断，在 Comments 里列出保留的命中及理由。
   - `SKILL.md` 词数 ≤ 2160。
6. **视觉对照（第十节）。**
7. **实机核对（工单 02 的前置核对，工单 05 的 REL-4 逐拨盘核对）。** 证据来自会话记录，不来自回执。这些检查只证明派发与接线，不证明质量或成本；每次用最小提示。

先例：`.scratch/post-5-1-tuning/`（票据格式、文字扫描、行为验证记录）；`.scratch/verification-batching/`（批次验收记录）；`test_runner_contract.py` 的假 CLI 模式。

## 十、视觉验收（版本说明书）

- **基准。** `docs/manuals/5.2.0.html`，提交 `e5d65a4`，SHA-256 `c939d7cd7e34a387c54bb2397136b93a9019f4630d7478d871496ed289b4346e`。只有浅色方案（`color-scheme: light`，无暗色媒体查询）。
- **场景。** 两个页面用相同参数渲染：
  - V1：1440×900，页首（侧栏加首屏）。
  - V2：1440×900，"路由档案"一节滚到视口顶端。基准的元素 id 为 `heading-12`；6.0.0 取同名一节，其 id 在工单 04 记录。
  - V3：1440×900，"相对上一版的变化"下第一节滚到视口顶端。基准的元素 id 为 `heading-13`；6.0.0 的 id 在工单 04 记录。
  - V4：390×844，页首（低于 600px 断点）。
  - V5：1024×768，页首（900px 与 1150px 断点之间）。
  - V6：1680×1050，页首（1600px 以上断点）。
- **必须与基准一致。** 字体栈、配色变量、侧栏加正文的布局、目录的当前位置高亮、标题、卡片、表格、提示框、代码样式、各断点行为、打印样式（`@media print` 规则逐条保留）、自包含（无外部请求）。
- **允许不同。** 文字、节数与顺序、表格行数与卡片数、用现有组件组合出的新节、版本标签。
- **方法。**
  - 用 `.scratch/tiers-and-routing-6-0/visual/capture.mjs` 截图：`node .scratch/tiers-and-routing-6-0/visual/capture.mjs <html 路径> <输出 png> <宽> <高> [元素 id]`。它经 Chrome DevTools 协议把元素立即滚到视口顶端后截图，浏览器默认取本机 Playwright 缓存的 Chromium，可用环境变量 `CHROME` 覆盖。2026-09-26 已用基准验证：V2（`heading-12`）、V3（`heading-13`）、V4 的画面分别是目标一节与手机版页首。
  - 不要用 URL 的 `#锚点` 加 `--screenshot` 截 V2、V3：2026-09-26 实测，基准页设了平滑滚动，这样截到的仍是页首。
  - 截图存到 `.scratch/tiers-and-routing-6-0/visual/`，命名 `<场景>-baseline.png`、`<场景>-6.0.0.png`。
  - 逐对打开查看，在工单 04 的 Comments 里写每个场景的观察与通过或不通过。
  - 功能检查（HTML 结构、两部分齐全、无外部请求）另做，不能代替视觉对照。
  - 视觉不通过时改 `6.0.0.html`，不改基准。基准组件表达不了所需内容时停下（S6）。

## 十一、边界

- **必须遵守。** 第八节全部要求；第三节状态为已确认的全部条目；已否决条目不得回流。
- **可自行选择。**（在工单 Comments 记录选择与理由）
  - runner 改动的内部结构与测试组织；
  - 各文档的具体措辞（在要求范围内），`SKILL.md` 的句子安排（在 TR-9 内）；
  - ADR 0021 与 README 的篇幅与结构；
  - 说明书的节序与组件组合（在第十节内）；
  - 截图工具与锚点定位方式；
  - 本批各票派发到哪条车道与拨盘（按已安装的 5.2.0 技能和现行活体档案，不按本规格的新表——新表在工单 05 之前没有安装）。
- **需要用户决定。** 修改任何已确认条目；第十二节的任何停止条件；REL-2 的每个发布步骤；O1；需要基准没有的视觉样式。

## 十二、停止并回报

出现以下情况，停止受影响的工作，把证据写进工单 Comments，回报用户。不得用已否决的做法替代。

- **S1** 新表的某个拨盘在其车道不能以该型号与强度运行（工单 05 的 REL-4）。不得换型号或改表；已发布的版本是否回退由用户决定。
- **S2** claude 车道某个别名实际解析的型号不是表中型号（工单 02 的 PRB-2）。
- **S3** grok 会话记录显示的型号不是 `grok-4.7`，且传 `model` 也不能使其成为 `grok-4.7`（工单 02 的 PRB-1）。
- **S4** `SKILL.md` 改写后超过 2160 词。回报时附词数与候选删减。
- **S5** 看起来必须改动某个已确认条目。
- **S6** 说明书内容无法用基准的组件表达。
- **S7** 某个发布步骤没有用户当次授权。

## 十三、要求归属

| 要求 | 建立 | 沿用 | 何时、由谁验收 | 可观察证据 |
|---|---|---|---|---|
| RN-1 至 RN-6；DOC-5 中 codex 车道行与安装说明的部分 | 01 | 03、04 | 01 结束，主代理 | 契约与生命周期测试输出；改写后的用例对"自动换型号"变红一次的记录；`lanes-claude-code.md` 与 README 的路径限定 diff |
| PRB-1、PRB-2 | 02 | 03（RP-7、ADR 宿主事实）、04（已知限制） | 02 结束，主代理 | 工单 02 Comments 的观测表（会话记录中的型号） |
| PRB-3 | 02（用户执行） | 04 | 用户回报时；回报前标为未核实 | 工单 02 Comments 中用户回报的 slug 清单 |
| TR-1 至 TR-10；AG-1 至 AG-3；RP-1 至 RP-12；DOC-1 至 DOC-6（DOC-5 的 codex 部分除外） | 03 | 04（路由档案一节等）、05（安装与全仓扫描） | 03 结束，主代理；技能与 agent 散文是同家族 diff，按 Tier 3 交 advisor 验收形状 | `wc -w`；表逐格对照 RP-2 与 RP-8；临时家目录 `--check` 退出 0；`test_zh_mirror.py`；本票文件的文字扫描；ADR 点名的修订条目齐全；README 升级段逐项对照 DOC-5；advisor verdict |
| MAN-1 至 MAN-5；第十节 | 04 | 05 | 04 结束，主代理 | 截图对与逐场景观察；功能检查输出 |
| REL-1 至 REL-4；全仓文字扫描；全部测试 | 05 | — | 05，主代理；发布步骤需用户授权 | 测试输出；`git diff --check`；全仓扫描零命中；两侧缓存与 `--check`；逐拨盘观测表（会话记录中的型号与强度） |

## 十四、偏离目标的检查

以下每一项都可能满足部分验收文字却偏离目标，须在所属工单和工单 05 各排除一次：

- runner 换了个名字继续自动换型号，或回退到任何型号。
- 白名单仍接受 `gpt-5.6-*`，或拒绝 `gpt-6-*`。
- 回退测试被直接删除，而不是改写成验证"不换型号"。
- 生命周期测试因型号被拒而在参数校验处提前退出，看似通过。
- `SKILL.md` 换了名字保留首轮池或 senior 门，或把车道顺序写成格内顺序，或写进型号与取值。
- 档案按能力、价格或车道顺序重排了用户的格子。
- 档案把 ≤ 写成同级，或把 haiku、composer 放进能力排名。
- Cursor explorer 行保留 Claude 优先，或丢了 composer。
- advisor 映射写错格（例如决策用 `crux`）。
- `worker-md` 仍自称不会被自动选中；`advisor-h` 仍自称默认拨盘；车道文档仍把内置 Explore 说成候选。
- 实机核对只以回执为证据（回执记录的是提交的配置），没有读会话记录。
- 只改了活体档案，没改编辑源。
- 说明书通过功能检查但视觉不是基准体系，或没人看过截图；第二部分漏了 ADR 0019、0020；基准文件被改动。
- README 升级段漏了不兼容点或"运行伴生安装器"。
- 表格与原话逐格一致、测试全过，但档案或技能正文仍写"cheapest adequate"，主代理据此把 advisor `mainstay` 派给更便宜的 `opus-5-5[medium]`，违背"想看不同厂商意见"。
- 车道文档或 README 仍写"currently grok-4.6"，或档案写"跟随 CLI 默认"而工单 02 观测到默认不是 `grok-4.7`。
- 换候选的顺序偏离 D6、D7（U17），例如单个候选不可用时改按书写顺序。
- 为观察效果加了日志、标记或统计。
- 引入了 advisor 专题的内容（过程咨询、姿态注入、完成前强制、逐次派发核对）。

## 十五、范围外

- advisor 专题（O2）：过程咨询、调用姿态、采纳规则、常驻注入、完成前强制、逐次派发核对、验收顾问按档位选择、与 Claude Code 内置 advisor 的共存。`advisor-h` 之外的 advisor 文件文字。
- 启用 C3 的收窄准入。
- 质量、成本、稳定性的度量。
- Cursor 门禁脚本与 pin 规则：已核对门禁脚本的版本号拆分正则是通用的（`\d+\.\d+`），`grok-4.7` 的 slug 不需要改脚本；pin 规则不含档位或型号。
- 未跟踪的无关文件：`ONBOARDING.md`、`docs/fable-advisor-healthcheck-2026-09.md`、`docs/fable-advisor-orchestration-handoff-2026-09.md`、`outputs/`、`__pycache__/`。发布时不暂存。
- 上游同步。

## 十六、补充说明

- **姿态。** 本任务有任务件，编排姿态。协调件由主代理直接写：本目录、路由档案与中文备份、`CONTEXT.md`、`AGENTS.md`、ADR、版本字段。交付物经 worker：`plugin/**`、`tests/**`、`README.md`、`docs/zh/**`、`docs/manuals/**`、`.claude-plugin/marketplace.json` 的描述。技能与 agent 散文（工单 03）用同模派发。
- **顺序。** 01 与 02 可同时开始；03 需等 01、02；04 需等 03；05 需等 04。工单 03 覆盖多个产物类别：技能与 agent 散文用同模派发，README 与清单描述经 worker，路由档案、词表、`AGENTS.md`、ADR 由主代理直接写。
- **已记录的假设（2026-09-26，带失效检查）。**
  - claude 车道派发的 `model` 只接受 `haiku`、`sonnet`、`opus`、`fable`（本会话 Agent 工具的参数定义）。失效检查：派发工具的参数定义出现完整型号 id。
  - 本会话主模型设为 `opus` 时实际为 `claude-opus-5-5`；项目里更早的一次会话中 `opus` 曾解析为 `claude-opus-5`。PRB-2 在执行时重新确认。
  - Codex 会话记录的 `turn_context` 有 `model`、`effort`；grok 会话目录有 `model_id`、`reasoning_effort`（本机 2026-09-26 抽查）。失效检查：CLI 升级后字段缺失。
  - codex runner 的强度校验是全局集合（基线代码）。
  - 本机有 Playwright 缓存的 Chromium（`chromium-1243`）。失效检查：路径不存在时改用等价工具并在工单 04 记录。
- **本批派发的路由。** 在工单 05 安装之前，已安装的是 5.2.0 技能与旧档案；本批工单的派发按它们路由。不要用已安装插件派发新档位名称。

## Comments

### 2026-09-26 — 规划自查（主代理）

- 路径与版本：规格与各票引用的路径全部可达（`.agent-discuss/` 下的发布以目录内相对名引用）；SHA-256 核对通过：`SKILL.md`、路由档案、`5.2.0.html`、`final.md`、`request-004.md`、交接文档。codex-advisor 规格与交接时的哈希不一致（另一会话仍在修改），已在材料表注明，C1–C7 以本规格文字为准。
- 路由表：脚本把交接文档第一节的九个格子按 D1 规范名称、按 C1 补默认 `*` 后，与 RP-2 逐格比对，零差异；RP-2 与 `final.md` 一.2 零差异；RP-8 的 Cursor explorer 行与 `final.md` 三.8 一致。
- 要求覆盖：第八节 49 个要求编号，每个都出现在至少一张工单的"负责的要求"与第十三节归属表中。
- 否决项回流：`SessionStart`、过程咨询、完成前强制、逐次派发核对、三级排名、`5.3.0`、"越往后越依赖判断"只出现在原文留档、台账、否决与范围外条目中。
- 视觉方法：URL `#锚点` 加 `--screenshot` 截到的仍是页首（基准页平滑滚动）；`visual/capture.mjs` 以立即滚动截图，已用基准验证 V2（`heading-12`）、V3（`heading-13`）、V4 画面正确。
- 自查中修正：原稿把逐拨盘实机核对放在发布前、发布后只派一次，与 U14 ⑦ 不符，已改为发布后逐拨盘（REL-4），发布前只核对档案依赖的两项事实（N7）；原稿要求说明书写冻结路由表，与 5.2.0 说明书"不复述档案里的型号排名"的先例冲突，已改为沿用先例（N8）；补记 composer 决定的原文（第二节 B2）与被取代的"(a) 用内置 advisor"（第二节 E）。
- 文件语言：本规格与各票的标题与说明用中文；`Status:`、`Blocked by:`、`## Comments`、`## Held for batch acceptance` 按 `docs/agents/issue-tracker.md` 的约定保留原文。上一份规格（`post-5-1-tuning`）用英文模板标题，本规格按单一语言的要求改为中文。

### 2026-09-26 — 票据重排为五张纵切片（用户确认）

- 原八张按层拆分（技能正文、档案、词表与 ADR、README 各一张），任一张单独落地都会让仓库前后矛盾。按用户确认改为五张：01 codex runner（并入 README 的 codex 车道部分）；02 写档案前的核对（前置依赖改为无）；03 三档与新路由表端到端（合并原 03–06）；04 说明书（原 07）；05 发布（原 08）。
- 前置依赖：01、02 无；03 ← 01、02；04 ← 03；05 ← 04。规格中的票号引用、归属表与 `.scratch/verification-batching/spec.md` 的发布安排评论已同步。

### 2026-09-26 — 承接审查第 1 轮的处理

审查文件：`.agent-discuss/tiers-and-consult-iteration/handoff-review.md`（SHA-256 `1e5130da…4968`）。审查以 `final.md` 为入口，没有读本规格；下表按原始需求、第三节有效决定与本规格逐条核对。

| 审查条目 | 结论 | 依据 | 处理位置 |
|---|---|---|---|
| 问题 1：入口不能直接实施，`final.md` 不指向本目录 | 部分成立。正式规划已存在；`final.md` 已关闭不能再改，入口要由用户指给执行者 | `final.md` 八；讨论协议（关闭后不再修改） | 规格开头新增"实施入口"一段；O1 扩到本任务记录 |
| 问题 2：档案里"cheapest adequate"与第一个候选为默认冲突 | 成立，规格原先漏了；技能正文 Stage 2 也有同一句 | C1、U5；`SKILL.md` 第 78 行，档案第 7、45 行 | N9；TR-4、RP-9、RP-10；第九节扫描；第十四节；工单 03 |
| 问题 2：Cursor 部分"a cell lists only the variants the allowlist carries" | 成立 | D9 | RP-9 补退役句（连同 Fable 注释、2026-09-16 slug 快照、旧拨盘的典型路径）；工单 03 |
| 问题 2：专长说明保留还是删除 | 规格已处理（RP-3 作为擅长点示例保留），补记依据 | 用户 2026-09-06 声明未撤回；三.11 只撤回"只打破平局" | N10；RP-3 |
| 问题 2：易变状态、handoff 声明 | 规格已处理 | RP-10 | 无 |
| 问题 3：grok 未钉 `grok-4.7`，回执不记实际型号 | 部分成立。回执不记实际型号是现行语义，规格以会话记录为证（REL-4、PRB-1）；"currently grok-4.6"两处未列入改动范围，确为缺口；默认跟随 CLI 还是钉定，现行 ADR 0009 已有依据 | ADR 0009；`lanes-claude-code.md` 第 140 行；README 第 26 行 | N11；RP-7、DOC-1、DOC-5；第九节扫描加 `grok-4.6`；工单 02、03 |
| 问题 4：advisor verdict 是否参与进入 `rescue` | 已由用户决定：不参与（解读 A），决策类型门照旧触发 | 第二节 C.2；N4；TR-7 | 无 |
| 问题 5：实机核实是否是发布关口 | 部分成立。逐拨盘核对按用户决定在发布后（U14 ⑦，REL-4）；推送前是否加真实 CLI 核对属于改变已确认决定的范围与成本 | U14 ⑦ | O4（未决，阻塞推送一步）；S8；工单 05 |
| 推导：换候选时车道顺序与书写顺序结果不同 | 后果属实。D6 已随 `final.md` 确认为按车道顺序；审查指出的结果差异用户在确认时可能没有看到，是否修改 D6 由用户决定 | D6；U6"车道默认顺序只在……换车道时起作用" | O3（未决，决定前按 D6）；TR-5、RP-3 注明；工单 03 |
| 推导：R1、R2 接管包、R3 保留 | 与规格一致 | TR-6 | 无 |
| 低：composer 决定在 request 里找不到 | 规格已处理 | 第二节 B2 | 无 |
| 低：H6 的"较大执行问题"来源标注 | 内容无误，来源是 codex-advisor TR-8 与现行 R4 | TR-8 原文 | C5 依据补全 |
| 预期成品：认为"本任务不是视觉任务" | 误读 | 第十节；U14 ⑥；N5：6.0.0 说明书要与 5.2.0 说明书逐场景截图对照 | 无 |
| 可自行选择：H4 写在 ADR 或档案 | 误读 | TR-3：只写进 ADR 0021 | 无 |
| 可自行选择：`DEFAULT_EFFORTS` 中 luna、sol 的取值 | 误读 | RN-2：沿用现值（luna `max`、sol `high`） | 无 |
| 推断的四层工单边界 | 已被取代 | 用户确认的五张纵切片（见上一条 Comments） | 无 |
| 预期成品未含的部分 | 审查范围所限 | 本规格另有：README 与清单描述（DOC-5、DOC-6）、说明书（MAN）、发布后逐拨盘核对（REL-4）、随 6.0.0 发布 ADR 0019 与 0020（N1）、`worker-md` 与 `advisor-h` 自述（N3、U16）、词数上限 2160（U15） | 无 |

### 2026-09-26 — O3、O4 的决定

- 用户回复"维持D6+不要"（第二节 C2）。O3 结论为 U17：维持 D6，任何换候选都按车道默认顺序，Claude Code 的 explorer 按 D7；codex runner 启动失败算哪一种因此不再影响结果。O4 结论为 U18：推送前不加真实 CLI 核对，逐拨盘核对只在发布后执行，不符按 S1 处理。
- 相应修改：第三节加 U17、U18，删未决 O3、O4，已否决加两条；TR-5、RP-3 写明顺序对单个候选同样适用；删除 S8；第十一节与第十四节同步。上一条 Comments 表中关于 O3、O4、S8 的说明是当时状态，以本条为准。
- N9、N10、N11 请用户说明是否推翻，用户未推翻，状态注明。
- 已知风险由用户接受：新增的 `gpt-6-luna`、`gpt-6-sol` 在推送前只由假 CLI 测试覆盖；若发布后 REL-4 发现跑不起来，按 S1 停下，是否回退由用户决定。

### 2026-09-27 — 实施记录（主代理）

- 01、02、03、04 已完成并验收，证据在各票 Comments。05 已完成发布前检查（版本字段、测试、全仓扫描、第十四节排除、code-review）；椰椰授权本地提交，O1 选定"只提交任务记录"（本目录，含 `visual/` 截图）。推送、两侧 `claude plugin` 更新、两侧运行伴生安装器未获授权，未执行；REL-3（安装核对）、REL-4（发布后逐拨盘实机核对）与真实家目录的 `test_user_level_archive.py` 因此待定。
- 未核实项：PRB-3（Cursor allowlist slug）未回报；`fable` 别名在当前账号未开通 usage credits，派发被拒（HTTP 429），REL-4 的 fable 拨盘需在开通 credits 的配置下执行；原生 Windows 生命周期测试在本机跳过。
- 与规格假设不同的观测：claude 子代理记录带 `effort` 字段，claude 拨盘的强度可以观测（工单 02）。
- 遗留（范围外，未改）：`SKILL.md` 车道表与 `lanes-cursor.md` 第 3 行把 Cursor 的 Grok 只写成钉型号派发（5.2.0 即如此）；`lanes-cursor.md` 第 14 行与中文车道文档多处用 tier/档位 指强度；`worker-h`、`worker-xh`、`advisor-md`、`advisor-xh`、`advisor-l`、`explorer-h` 仍有替档案做路由选择的句子；`CONTEXT.md` "worker 的高档位"；测试准备代码重复；`run-codex.mjs` 的 `processStopped` 已无读者；说明书侧栏在 900px 高度下不自动滚到当前项（基准脚本相同）。
- `SKILL.md` 实测 2160 词，零余量；下一次改正文前要先按 ADR 0012 判断沉降。
