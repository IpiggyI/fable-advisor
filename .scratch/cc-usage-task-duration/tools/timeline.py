import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, ts, classify_bash, text_of
from datetime import datetime, timezone, timedelta
P=os.path.expanduser('~/.claude/projects/-home-hyy-develop-personal-GitHub-cc-usage')
def lt(T): return datetime.fromtimestamp(T, timezone(timedelta(hours=8))).strftime('%H:%M')
E=[e for e in load(f'{P}/{sys.argv[1]}.jsonl') if e.get('timestamp')]
t0=ts(E[0]['timestamp']); t1=max(ts(e['timestamp']) for e in E)
api={}; prev=t0; tools={}; res={}; trig=[]; bg={}; notif={}
for e in E:
    T=ts(e['timestamp']); typ=e['type']
    if typ=='assistant':
        mid=e['message'].get('id')
        if mid not in api: api[mid]=[prev,T]
        api[mid][1]=T
        for b in e['message'].get('content') or []:
            if b.get('type')=='tool_use': tools[b['id']]=(T,b['name'],b.get('input',{}))
        continue
    if typ in ('user','queue-operation','attachment','system'): prev=T
    if typ=='user':
        c=e['message'].get('content'); o=(e.get('origin') or {}).get('kind')
        if isinstance(c,list):
            for b in c:
                if isinstance(b,dict) and b.get('type')=='tool_result':
                    res[b['tool_use_id']]=T
                    m=re.search(r'running in background with ID: (\w+)',text_of(b.get('content')))
                    if m: bg[b['tool_use_id']]=m.group(1)
        if o in('human','task-notification','peer'): trig.append((T,o))
        if o=='task-notification':
            m=re.search(r'<task-id>(\w+)</task-id>',text_of(c))
            if m: notif.setdefault(m.group(1),T)
    if typ=='queue-operation' and e.get('operation')=='enqueue':
        c=str(e.get('content',''))
        k='task-notification' if c.startswith('<task-notification') else 'peer' if 'agent-message' in c else 'wakeup' if not c.startswith('/') else 'human'
        trig.append((T,k))
trig.sort()
# intervals
iv=[]
for x,y in api.values(): iv.append((x,y,'model'))
for k,(T,n,inp) in tools.items():
    if k in res and k not in bg:
        c=classify_bash(inp.get('command','')) if n=='Bash' else n
        iv.append((T,res[k],'tool:'+c))
# sweep by second
N=int(t1-t0)+1; lab=['idle']*N
for x,y,l in sorted(iv,key=lambda v: v[2]=='model'):  # tools win over model
    for s in range(int(x-t0),int(y-t0)):
        if lab[s]=='idle' or (lab[s]=='model' and l!='model'): lab[s]=l
# BG running intervals
bgiv=[]
for tid,b in bg.items():
    T,n,inp=tools[tid]; e2=notif.get(b)
    if e2:
        c=classify_bash(inp.get('command','')) if n=='Bash' else n
        bgiv.append((T,e2,c))
agent_iv=[]
# idle segments
segs=[]; s=0
while s<N:
    if lab[s]=='idle':
        e2=s
        while e2<N and lab[e2]=='idle': e2+=1
        end=t0+e2; nxt=[k for T,k in trig if end-3<=T<=end+60]
        segs.append((t0+s,e2-s,nxt[0] if nxt else 'other'))
        s=e2
    else: s+=1
from collections import Counter
cnt=Counter(lab)
# refine idle labels by what ended them; mark bg full tests
for a,d,k in segs:
    for x in range(int(a-t0),int(a-t0)+d): lab[x]='idle:'+('user' if k=='human' else 'other' if k=='other' else 'wait-lane/subagent')
for x,y,c in bgiv:
    if c=='test-full':
        for q in range(int(x-t0),int(y-t0)):
            if lab[q].startswith('idle'): lab[q]='bg:test-full'
json.dump({'t0':t0,'lab':lab},open(f'/tmp/lab-{sys.argv[1][:8]}.json','w'))
print(f'wall={(t1-t0)/60:.0f}m')
cnt=Counter(lab)
for k,v in sorted(cnt.items(),key=lambda kv:-kv[1]):
    if v>60: print(f'  {k:22s}{v/60:6.1f}m')
ic=Counter()
for a,d,k in segs: ic[k]+=d
print('  idle split by what ended it:', {k:round(v/60,1) for k,v in ic.items()})
print('  background runs:', Counter(c for *_,c in bgiv), 'bg test time', round(sum(y-x for x,y,c in bgiv if c.startswith('test'))/60,1),'m')
