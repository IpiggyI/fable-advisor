"""重数 cc-usage 会话（2026-09-28）各来源的检查次数，runner 回执里的检查除外。

用法：python3 recount_all.py
来源：codex 车道票 01、13 及其子代理的 rollout，grok 车道票 02、03 和三次探索，
4 个 claude 车道 worker，主会话。会话编号、rollout 时间窗和路径都写死在下面，换会话要改。
codex 的命令同时取 `cmd` 和 `command` 字段：FastCtx 的 `run`、`run_background` 用的是
`command`，只认 `cmd` 会漏计（problem-report.md 第 2 节）。
"""
import json,re,sys,glob,os,collections
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recount.py')).read().split('src=sys.argv[1]')[0])
def codex_runs(f):
    for line in open(f):
        d=json.loads(line); p=d.get('payload',{})
        if p.get('type') not in ('function_call','custom_tool_call'): continue
        raw=p.get('arguments') or p.get('input') or ''
        raw=raw if isinstance(raw,str) else json.dumps(raw)
        for c in re.findall(r'(?:cmd|command)\\?"?\s*[:=]\s*\\?"((?:[^"\\]|\\.)*)\\?"',raw):
            try: c=json.loads('"'+c+'"')
            except Exception: pass
            for s in segs(c):
                k=kind(s)
                if k: yield d['timestamp'][11:19],k,s
def grok_runs(f):
    for line in open(f):
        try: e=json.loads(line)
        except: continue
        for tc in e.get('tool_calls') or []:
            try: a=json.loads(tc.get('arguments') or '{}')
            except: a={}
            c=a.get('command') or a.get('cmd')
            if not c: continue
            c=c if isinstance(c,str) else ' '.join(c)
            for s in segs(c):
                k=kind(s)
                if k: yield '',k,s
def claude_runs(f):
    for ts,c in claude_cmds(f):
        for s in segs(c):
            k=kind(s)
            if k: yield ts,k,s
rows=[]
def add(label,it):
    c=collections.Counter(k for _,k,_ in it); rows.append((label,c))
CX=os.path.expanduser('~/.codex/sessions/2026/09/28/')
G=os.path.expanduser('~/.grok/sessions/%2Fhome%2Fhyy%2Fdevelop%2Fpersonal%2FGitHub%2Fcc-usage/')
S=os.path.expanduser('~/.claude-a/projects/-home-hyy-develop-personal-GitHub-cc-usage/a39e68e3-be6d-48dd-b2ed-cd04dd6960ec')
for sid,label in [('01a0e7fc','codex 01+返工'),('01a0e84c','codex 13+返工')]:
    fs=glob.glob(CX+'*'+sid+'*.jsonl'); add(label+f' [{len(fs)} file]', [r for f in fs for r in codex_runs(f)])
# codex subagents: rollouts started during lane windows, excluding the lane threads themselves
for lo,hi,label in [('20-27','20-53','codex 01 子代理'),('21-55','23-01','codex 13 子代理')]:
    fs=[f for f in glob.glob(CX+'rollout-2026-09-28T*.jsonl') if lo<=os.path.basename(f)[19:24]<=hi and '01a0e7fc' not in f and '01a0e84c' not in f]
    add(label+f' [{len(fs)} file]', [r for f in fs for r in codex_runs(f)])
for sid,label in [('56898090-05ff-4578-93ab-a774dc39c71d','grok 02+返工'),('8a7028e0-302a-4dcc-96f5-31fc9d3cf702','grok 03'),('60c9a713-a783-4896-93fe-876a80972590','grok 探索1'),('aee3f514-12c3-4bef-8166-e971ad99edf6','grok 探索2'),('884ebda6-d8dd-4693-8844-4c1c34a61194','grok 探索3')]:
    f=G+sid+'/chat_history.jsonl'; add(label, list(grok_runs(f)) if os.path.exists(f) else [])
for a,label in [('aaf3021fb3d6e6f1f','worker 04/05'),('a9c44bc8fccea40e6','worker 06-09'),('a47ef5d708f45395a','worker 10'),('a23931579a2fa19e9','worker 11')]:
    add(label, list(claude_runs(f'{S}/subagents/agent-{a}.jsonl')))
add('主会话', [r for r in claude_runs(S+'.jsonl') if not re.search(r'pending/|cat > /tmp/t',r[2])])
tot=collections.Counter()
for label,c in rows:
    tot+=c; print(f'{label:28s} total={sum(c.values()):3d}', dict(c))
print('ALL (excl. runner 18):', sum(tot.values()), dict(tot))
