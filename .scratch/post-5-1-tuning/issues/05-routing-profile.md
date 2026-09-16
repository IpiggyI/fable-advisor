# 05: 路由档案重写——首轮池取值、Cursor 映射、基准数据、调整方法

**What to build:** 主代理读到的路由档案按 2026-09-16 的表给出每格拨盘（新记法），说明前两列是首轮池、第三列有门；Cursor 表按机制映射同一份取值；Resource preferences 含基准数据与声明日期；末节写明调整方法（改格、跑安装器），椰椰之后改格即生效，不改 doctrine、不改插件。

**Blocked by:** None (can start immediately)。协调件，架构师可亲写或派发。

**Status:** ready-for-agent

来源：`../spec.md` 实现决定第 18–22 条。范围：`docs/agents/fable-advisor-routing.md` 与 `.zh.md`。安装到活体由工单 03 的安装器完成（发布票执行）。

- [ ] 结构：声明日期与锚定模型 → 首轮池说明 → Claude Code 表 → Cursor 表 → 升级梯引用（指向技能，不复述）→ Resource preferences → 调整方法
- [ ] Claude Code 表按 spec 第 19 条取值与候选顺序（grok › codex › claude，specialty 只作平手裁决）写出，拨盘用 `model[a*, b, c]`
- [ ] advisor 默认格：决策形状 standard、验收形状 light；升到 senior 只在 verdict 自报低置信或用户声明时
- [ ] 每个 claude 车道拨盘标注对应的 agent 文件名；haiku 注明无 effort 维度
- [ ] Cursor 表：GPT 行经 codex runner（Shell）；grok medium / high 经 grok runner（Shell）、xhigh 可钉 allowlist 的 grok slug；Claude 行只取 allowlist 有的 slug 变体（fable 只在 senior 格；standard advisor 首选 astra[medium] 经 codex runner）；explorer @ light 首位 composer-2.5-fast 经 `explore`（cursor lane）；写明 slug 来自本轮 allowlist、不持久化
- [ ] Resource preferences：保留四条偏好与两条声明规则；新增 2026-09-16 的依据（型号差距大于 effort 差距；opus-5[high] 73%±2%、opus-5[medium] 69%±1%、sonnet-5[high] 48%±5%、sonnet-5[medium] 40%±3%）
- [ ] 调整方法一节：改格 → 跑安装器；技能在档案变化时重读
- [ ] 旧句删除：`advisor (default senior)`、角色默认 effort 句、`|` 记法
- [ ] `.zh.md` 同步改写，含中文且不安装
