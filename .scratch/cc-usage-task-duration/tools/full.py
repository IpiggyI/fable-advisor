import sys, os, json, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, ts, text_of
from datetime import datetime, timezone, timedelta
P=os.path.expanduser('~/.claude/projects/-home-hyy-develop-personal-GitHub-cc-usage')
def lt(T): return datetime.fromtimestamp(T, timezone(timedelta(hours=8))).strftime('%H:%M')
FULL=re.compile(r'bun (?:run )?test(?=\s*($|[>|;&)2]))',re.M)
RAN=re.compile(r'(\d+) pass|(\d+) fail|Ran (\d+) tests? across (\d+) files?\. \[([\d.]+)(ms|s)\]')
s=sys.argv[1]
for path in [f'{P}/{s}.jsonl']+sorted(glob.glob(f'{P}/{s}/subagents/*.jsonl')):
    lab='MAIN' if 'subagents' not in path else 'SUB'
    E=[e for e in load(path) if e.get('timestamp')]
    tools={}; lasttext=''; bgmap={}; out=[]
    for e in E:
        T=ts(e['timestamp'])
        if e['type']=='assistant':
            for b in e['message'].get('content') or []:
                if b.get('type')=='text': lasttext=b['text']
                if b.get('type')=='tool_use' and b['name']=='Bash':
                    c=b['input'].get('command','')
                    if FULL.search(c): tools[b['id']]=(T,c,lasttext,b['input'].get('run_in_background'))
        elif e['type']=='user':
            c=e['message'].get('content')
            if isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get('type')=='tool_result' and b['tool_use_id'] in tools:
                        T0,cmd,why,isbg=tools[b['tool_use_id']]; txt=text_of(b.get('content'))
                        m=re.search(r'running in background with ID: (\w+)',txt)
                        if m: bgmap[m.group(1)]=(T0,cmd,why); continue
                        out.append((T0,T-T0,cmd,why,txt))
            if (e.get('origin') or {}).get('kind')=='task-notification':
                txt=text_of(c); m=re.search(r'<task-id>(\w+)</task-id>',txt)
                if m and m.group(1) in bgmap:
                    T0,cmd,why=bgmap.pop(m.group(1)); out.append((T0,T-T0,cmd,why,txt))
    for T0,d,cmd,why,txt in sorted(out):
        p=re.findall(r'(\d+) pass',txt); f=re.findall(r'(\d+) fail',txt)
        print(f'{lab} {lt(T0)} {d/60:4.1f}m pass={p[-1] if p else "?"} fail={f[-1] if f else "?"} | why: {why.strip().replace(chr(10)," ")[:150]}')
