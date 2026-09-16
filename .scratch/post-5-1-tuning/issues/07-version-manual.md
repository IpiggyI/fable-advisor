# 07: 版本说明书 5.2.0

**What to build:** 椰椰打开一个自包含的中文 HTML 就知道 5.2.0 装上的是什么：第一部分是本版本的完整行为说明，第二部分是相对 5.1.0 的逐条改动点（改了什么、为什么、对应 ADR 与工单）。样式与 `outputs/` 里现有的 show-me 文件相近。此后每版一份。

**Blocked by:** 01、02、03、04、05、06（说明的是最终状态）

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 26–29 条；`CONTEXT.md` 词条 版本说明书。范围：说明书目录下的 `5.2.0.html`、`docs/agents/plugin-release.md`（发布流程加一步）。

- [x] 自包含 HTML：内联样式、`lang="zh-CN"`、编号二级标题、表格与要点框；不依赖外部资源
- [x] 第一部分（完整说明）覆盖：角色 / 档位 / 车道 / 姿态；首轮池、升级梯、决策类型门、验证三层；两条 runner 的 spec 键、receipt 字段、错误类与报告模式语义；claude 车道 agent 文件清单；用户级文件与伴生安装器用法；测试清单
- [x] 第二部分（相对 5.1.0 的改动点）逐条：脏基线、标题键、前言分流、sol、伴生安装器与旧规则退役、首轮池与 senior 门、升级梯、记法、cursor lane、grok runner 经 Shell；每条给理由与 ADR / 工单引用
- [x] 文件放在说明书目录、以版本号命名，进仓库，不进 `plugin/`
- [x] `plugin-release.md` 在 bump 版本号之前加"写本版说明书"一步，并写明说明书是发布的前置条件
- [x] 全文一种语言（中文），标识符与路径保持原文

## Comments

### 2026-09-16 — 实施记录（grok 车道，`cursor-grok-4.6-xhigh`，requested, not confirmed）

- `docs/manuals/5.2.0.html`（53 KB，13 个编号二级标题，第 13 节 12 条改动 + 升级后要做什么）；`plugin-release.md` 加第 0 步。
- 验收：架构师核对标题清单与字段名命中（`dirty_baseline`、错误类、`resume_session_id`、`service_tier`、`lane-preamble-report`、agent 文件名、安装器旗标、新记法）；`html.parser` 平衡检查无未闭合。浏览器渲染未验证：Cursor 内置浏览器拒绝 `file://`，也连不上 WSL 的本地 HTTP 服务；留给椰椰打开文件确认。
- 架构师修一处语言纯度：`plugin-release.md` 第 0 步中的中文词 "版本说明书" 改为 "version manual"（英文文档）。
