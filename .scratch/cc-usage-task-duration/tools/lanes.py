import json, glob, os, re, sys
from datetime import datetime
def ts(s): return datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
R='/home/hyy/develop/personal/GitHub/cc-usage/.fable-advisor/receipts'
W={'S1':(ts('2026-10-15T01:36:00Z'),ts('2026-10-15T10:05:00Z')),'S2':(ts('2026-10-12T08:39:00Z'),ts('2026-10-12T14:21:00Z'))}
GD=os.path.expanduser('~/.grok/sessions/%2Fhome%2Fhyy%2Fdevelop%2Fpersonal%2FGitHub%2Fcc-usage')
FULL=re.compile(r'bun (run )?test(?!\s+(\S*test/|\S+\.test\.ts|-t))')
def grok_window(sid, a, b):
    ph={}; last=None
    for line in open(f'{GD}/{sid}/events.jsonl'):
        e=json.loads(line); t=ts(e['ts'])
        if t<a-1 or t>b+1: continue
        if e['type']=='phase_changed':
            if last: ph[last[0]]=ph.get(last[0],0)+t-last[1]
            last=(e['phase'],t)
        elif e['type'] in ('turn_ended',):
            if last: ph[last[0]]=ph.get(last[0],0)+t-last[1]; last=None
    if last: ph[last[0]]=ph.get(last[0],0)+b-last[1]
    # commands
    cmds=[]
    for line in open(f'{GD}/{sid}/chat_history.jsonl'):
        e=json.loads(line)
        for tc in e.get('tool_calls') or []:
            if tc['name'] in ('bash','run_terminal_cmd','shell','terminal','run_command'):
                try: c=json.loads(tc['arguments']).get('command','')
                except: c=''
                cmds.append(c)
    return ph, cmds
def codex_window(sid, a, b):
    f=glob.glob(os.path.expanduser(f'~/.codex/sessions/*/*/*/rollout-*{sid}.jsonl'))[0]
    calls={}; execs=[]
    for line in open(f):
        e=json.loads(line); t=ts(e['timestamp'])
        if t<a-1 or t>b+1: continue
        p=e.get('payload',{})
        if p.get('type') in ('custom_tool_call','function_call'):
            calls[p.get('call_id')]=(t, p.get('input') or p.get('arguments') or '')
        elif p.get('type') in ('custom_tool_call_output','function_call_output'):
            c=calls.pop(p.get('call_id'),None)
            if c: execs.append((t-c[0], c[1]))
    return execs
tot={}
for f in sorted(glob.glob(f'{R}/*.json'), key=lambda f: json.load(open(f)).get('started_at') or ''):
    d=json.load(open(f)); st=d.get('started_at')
    if not st: continue
    for k,(a,b) in W.items():
        if not (a<=ts(st)<=b): continue
        lf=d.get('lane_finished_at') or d.get('finished_at'); A,B=ts(st),ts(lf)
        sid=d.get('grok_session_id') or d.get('codex_session_id') or d.get('thread_id') or d.get('session_id')
        line=f"{k} {st[11:16]}Z {d['producer']:5s} {d['error_class']:20s} lane={(B-A)/60:5.1f}m"
        if d['producer']=='grok':
            ph,_=grok_window(sid,A,B)
            model=sum(v for p,v in ph.items() if p in('waiting_for_model','streaming_reasoning','streaming_text'))
            tool=ph.get('tool_execution',0); perm=ph.get('permission_prompt',0)
            line+=f" model={model/60:5.1f}m tool={tool/60:5.1f}m perm={perm/60:4.1f}m"
            print(line)
        else:
            ex=codex_window(sid,A,B)
            tsum=sum(s for s,_ in ex); tests=[(s,c) for s,c in ex if re.search(r'bun (run )?test',c)]
            full=[(s,c) for s,c in tests if FULL.search(c)]
            line+=f" model~{((B-A)-tsum)/60:5.1f}m tool={tsum/60:5.1f}m bun-test-runs={len(tests)} ({sum(s for s,_ in tests)/60:.1f}m) full={len(full)} ({sum(s for s,_ in full)/60:.1f}m)"
            print(line)
            for s,c in full: print('      FULL', f'{s:.0f}s', re.findall(r'bun (?:run )?test[^"\\]{0,80}',c))
