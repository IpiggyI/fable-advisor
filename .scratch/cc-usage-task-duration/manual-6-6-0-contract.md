# 契约：6.6.0 版本说明书

依据：`docs/agents/plugin-release.md` 第 0 节；本版包含 [ADR 0034](../../docs/adr/0034-lane-session-title-marker.md)（已在 `a852289` 提交，未单独发布）与 [ADR 0035](../../docs/adr/0035-lane-pre-exit-checks-and-wait-cuts.md)。

## 路由

`Route: role=worker tier=mainstay dial=sonnet-5-5[high]`。worker 格的首选 `grok-4.7[high]` 与 `gpt-6.1-sol[medium]` 都走 runner，runner 的实施模式要求工作树干净；本仓工作树里有椰椰在途的未跟踪文件，不能清理，所以换到格内的 claude 车道候选。

## 五部

1. **Objective**：新建 `docs/manuals/6.6.0.html`，自包含的中文 HTML，结构照 `docs/manuals/6.5.0.html`：「本版完整行为」与「相对上一版的变化」两部分。验收：
   - 「本版完整行为」以 6.5.0 为底，凡是被 ADR 0034、ADR 0035 改变的行为，按当前 `plugin/**` 的文字改写：车道会话名的 `[车道] ` 前缀；车道退出前自检与 runner 那一遍证据；`timeout_sec` 只在当前请求给出时限时才写；静默截止管不到无进展的长跑，主代理去哪里看车道输出、何时停它；实施契约的 Files 写具体路径；串行要写理由；契约检查列表带上廉价的类型检查或 lint；宽检查的完整输出写文件、开跑时机、返工后先跑失败文件、批次最后再跑一次。
   - 「相对上一版的变化」列出这两份 ADR 的每项变化：改了什么、为什么、对应的 ADR 与问题单（`.scratch/cc-usage-task-duration/issues/01`、`03`、`04`）；写明问题单 02、05 本版没改、原因没查实；写明「主会话直接修类型错误」先观察，不在本版。
   - 标题与页内版本号是 6.6.0。
2. **Files**：`docs/manuals/6.6.0.html`（新建）。
3. **Interfaces**：无。
4. **Constraints**：只读其他文件，只写上面这一个文件。不改版本号，不提交，不推送。说明书写给椰椰：一个概念一个名字，短句，主动语态；术语按 `CONTEXT.md`。
5. **Verification**：
   - `python3 -c "import html.parser,sys;p=html.parser.HTMLParser();p.feed(open('docs/manuals/6.6.0.html').read());print('parsed')"`
   - `grep -c "6.6.0" docs/manuals/6.6.0.html` 大于 0。
   - `grep -n "timeout_sec\|车道\]\|类型检查" docs/manuals/6.6.0.html | head` 有输出。

## 结果

（待回填）
