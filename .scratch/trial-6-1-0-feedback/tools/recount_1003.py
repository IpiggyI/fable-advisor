"""重数 cc-usage 会话 be93294f（2026-10-02 至 10-03，加载 6.1.0）各来源的检查次数。

用法：python3 recount_1003.py [detail]
口径同 ../../verification-defaults/problem-report.md 第 2 节：一次检查是一条命令段的一次执行；
只读命令和 heredoc 正文不计。在那份口径上加三类：render（bun 运行 capture.ts 或 render-09.ts）、
setup（serve-copy.sh 起隔离服务）、package（build-nsis 打包）。
runner 的检查不在这里：回执随工作树删除，契约的 verification 列表取自会话记录，见问题报告第 2 节。
不识别经包装脚本发出的测试：worker 02 用 /tmp/cc02/mutate.py 和内联 python 的 subprocess
跑了 11 次测试（记录第 235、241、247、253 行，按 2、4、3、2 次），问题报告第 2 节手工计入。
带 detail 参数时逐条列出。
"""
import json,re,os,glob,collections
TOOLS=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','verification-defaults','tools')
exec(open(os.path.join(TOOLS,'recount.py')).read().split('src=sys.argv[1]')[0])
_kind=kind
def kind(s):
    k=_kind(s)
    if k: return k
    if re.match(r'bun\s+\S*(capture|render-09)\.ts',s): return 'render'
    if re.match(r'(bash\s+)?\S*serve-copy\.sh',s): return 'setup'
    if re.match(r'\S*build-nsis\.sh|powershell\S*\s.*build-nsis\.ps1',s): return 'package'
    return None
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
def claude_runs(f):
    for ts,c in claude_cmds(f):
        for s in segs(c):
            k=kind(s)
            if k: yield ts,k,s
S=os.path.expanduser('~/.claude/projects/-home-hyy-develop-personal-GitHub-cc-usage/be93294f-4abe-4bbe-a2df-73aa8fe76cda')
CX=os.path.expanduser('~/.codex/sessions/2026/10/03/')
rows=[]
def add(label,it):
    it=list(it); rows.append((label,collections.Counter(k for _,k,_ in it),it))
for a,label in [('afdfced88a1d10c0a','worker 01（02 半途）'),('a520167d9972b3917','worker 02'),('aa31c9b6551b4c5ad','worker 03、04、05、05返工、03返工、10')]:
    add(label, claude_runs(f'{S}/subagents/agent-{a}.jsonl'))
for sid,label in [('01a0fd90-6bef','codex 06、06修正、07、07返工、批次修复'),('01a0fd90-6c00','codex 08、08返工两次')]:
    fs=glob.glob(CX+'*'+sid+'*.jsonl'); add(label, [r for f in fs for r in codex_runs(f)])
add('主会话', [r for r in claude_runs(S+'.jsonl') if not re.search(r'pending/|cat > ',r[2])])
tot=collections.Counter()
for label,c,it in rows:
    tot+=c; print(f'{label:34s} 共 {sum(c.values()):3d}', dict(c))
print(f'{"合计（不含 runner）":34s} 共 {sum(tot.values()):3d}', dict(tot))
import sys
if len(sys.argv)>1:
    for label,c,it in rows:
        print('=====',label)
        for ts,k,s in it: print(' ',ts,k,'|',s[:120])
