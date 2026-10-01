"""按 rustpad 的命令模式，统计 rustpad 会话（2026-10-01）各车道内部的检查次数。

用法：python3 count_rustpad.py [主会话 .jsonl]
不带参数时只统计车道：grok 车道票 01、02、04，codex 车道票 03、05 和 05 的返工
（05 的 rollout 以 2026-10-01T11:24:18 为界拆成首轮与返工）。
带上主会话路径时另外分类主代理的 Bash 命令，但这一部分不是台账的口径：循环里的
`node scripts/$t.browser.mjs` 只算一次，契约 JSON 里的命令文本会被误计。台账记的主代理
34 次是手工逐项计数。会话编号与路径写死在下面，换会话要改。
"""
import json,sys,re,collections,os
RULES=[
 ("浏览器测试脚本", r"^node (\./)?scripts/\w+\.browser\.mjs"),
 ("单元测试 node --test/npm test", r"^(node --test|npm (run )?test$|npm test\b)"),
 ("类型检查 tsc", r"^(npx tsc|tsc\b|npm run check)"),
 ("prettier --check", r"^npx prettier.*--check"),
 ("前端构建", r"^(npm run build|npx vite build)"),
 ("cargo test", r"^cargo(\.exe)? test"),
 ("cargo build/check", r"^(/\S*/)?cargo(\.exe)? (build|check)"),
 ("cargo fmt --check", r"^cargo fmt.*--check"),
 ("bash -n 语法检查", r"^bash -n"),
 ("打包脚本", r"^bash scripts/package-intranet\.sh"),
 ("Windows 发布检查", r"^bash scripts/check-intranet-release\.sh"),
 ("手工运行服务端（错误场景等）", r"^(\S*/)?target/(debug|release)/rustpad-server|^cargo run|^\S*rustpad\.exe"),
 ("临时探针（node 内联/临时脚本）", r"^node (-e|--input-type|/tmp/|<<|-)\b|^node$"),
]
def segments(cmd):
    for seg in re.split(r"\s*(?:&&|\|\||;|\n|\|)\s*", cmd):
        seg=seg.strip().lstrip("( ").strip()
        seg=re.sub(r"^\w+=\$\(","",seg)        # out=$(cmd
        seg=re.sub(r"^\$\(","",seg)
        seg=re.sub(r"^(\w+=\S+\s+)+","",seg)   # env prefixes
        seg=re.sub(r"^timeout \d+\s+","",seg)
        if seg: yield seg
def classify(cmd):
    out=[]
    for seg in segments(cmd):
        for name,pat in RULES:
            if re.search(pat,seg): out.append(name); break
    return out
def grok(d):
    for line in open(os.path.join(d,"chat_history.jsonl")):
        e=json.loads(line)
        for tc in e.get("tool_calls") or []:
            try: a=json.loads(tc.get("arguments") or "{}")
            except Exception: continue
            c=a.get("command")
            if c: yield c
def codex(f, since=None, until=None):
    for line in open(f):
        e=json.loads(line); p=e.get("payload",{})
        if p.get("type") not in ("function_call","custom_tool_call"): continue
        ts=e.get("timestamp","")
        if since and ts<since: continue
        if until and ts>=until: continue
        a=p.get("arguments") or p.get("input") or ""
        found=False
        for m in re.finditer(r'(?:cmd|command)\s*:\s*"((?:[^"\\]|\\.)*)"', a):
            found=True; yield bytes(m.group(1),"utf-8").decode("unicode_escape","ignore")
        if not found:
            try:
                j=json.loads(a); c=j.get("cmd") or j.get("command")
                if c: yield c if isinstance(c,str) else " ".join(c)
            except Exception: pass
G=os.path.expanduser("~/.grok/sessions/%2Fhome%2Fhyy%2Fdevelop%2Fpersonal%2FGitHub%2Frustpad/")
C=os.path.expanduser("~/.codex/sessions/2026/10/01/")
import glob
c03=glob.glob(C+"rollout-2026-10-01T16-43-02-*.jsonl")[0]
c05=glob.glob(C+"rollout-2026-10-01T18-20-53-*.jsonl")[0]
lanes=[("01 grok",grok(G+"b379332c-89d6-4c8c-a37d-85091cfc4e90")),
       ("02 grok",grok(G+"10c755c6-7647-42e9-85d6-313325175415")),
       ("03 codex",codex(c03)),
       ("04 grok",grok(G+"0e04a75e-ddcb-4cbd-b46a-63d4b36ae548")),
       ("05 codex",codex(c05,until="2026-10-01T11:24:18")),
       ("05 返工 codex",codex(c05,since="2026-10-01T11:24:18"))]
tot=collections.Counter()
for name,cmds in lanes:
    cmds=list(cmds); cnt=collections.Counter()
    for c in cmds:
        for k in classify(c): cnt[k]+=1
    tot.update(cnt)
    print(f"{name}: shell 命令 {len(cmds)} 条；测试执行 {sum(cnt.values())} 次 ->", dict(cnt.most_common()))
print("车道内部合计:", sum(tot.values()), dict(tot.most_common()))

def claude(f):
    for line in open(f):
        try: e=json.loads(line)
        except Exception: continue
        m=e.get("message") or {}
        if m.get("role")!="assistant": continue
        for c in m.get("content") or []:
            if isinstance(c,dict) and c.get("type")=="tool_use" and c.get("name")=="Bash":
                cmd=(c.get("input") or {}).get("command")
                if cmd: yield cmd
if len(sys.argv)>1:
    cmds=list(claude(sys.argv[1])); cnt=collections.Counter()
    for c in cmds:
        for k in classify(c): cnt[k]+=1
    print(f"主代理: Bash 调用 {len(cmds)} 次；测试执行 {sum(cnt.values())} 次 ->", dict(cnt.most_common()))
