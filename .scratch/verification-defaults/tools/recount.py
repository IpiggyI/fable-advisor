"""按 cc-usage 的命令模式，列出一份记录里跑过的每一次检查。

用法：python3 recount.py <claude 会话 .jsonl | grok 的 chat_history.jsonl>
每行输出：时刻、类别（typecheck、targeted、full、palette、script、cargo）和命令段。
一次检查指一条命令段的一次执行（problem-report.md 第 2 节）。
类别规则只认 cc-usage 的命令（bun、tsc、validate_palette.js、cargo），换仓库要改 kind()。
recount_all.py 执行本文件里读取命令行参数之前的部分。
"""
import json,re,sys,os
# heredoc 正文是写进文件的文本，不是命令；例如写票时正文里的验证命令
HEREDOC=re.compile(r"(<<-?\s*(['\"]?)(\w+)\2[^\n]*\n).*?^[ \t]*\3[ \t]*$", re.S|re.M)
def segs(cmd):
    cmd=HEREDOC.sub(r'\1', cmd)
    for s in re.split(r'\s*(?:&&|\|\||;|\n)\s*', cmd):
        s=s.strip().lstrip('( ')
        s=re.sub(r'^cd \S+$','',s); s=re.sub(r'^(\w+=\S+\s+)+','',s); s=re.sub(r'^timeout \d+\s+','',s)
        if s: yield s
def kind(s):
    if re.match(r'(bun run typecheck|(npx |bunx )?tsc\b)',s): return 'typecheck'
    m=re.match(r'bun (run )?test\b(.*)',s)
    if m:
        rest=m.group(2).split('|')[0].strip()
        rest=re.sub(r'2>&1|>\s*\S+','',rest).strip()
        return 'targeted' if re.search(r'\S',rest) else 'full'
    if re.match(r'node\s+\S*validate_palette\.js',s): return 'palette'
    if re.match(r'bun\s+\S*scripts/(verify|bench)-',s): return 'script'
    if re.match(r'cargo (check|test|build)',s): return 'cargo'
    return None
def claude_cmds(f):
    for line in open(f):
        try: d=json.loads(line)
        except: continue
        m=d.get('message',{}); c=m.get('content')
        if d.get('type')=='assistant' and isinstance(c,list):
            for x in c:
                if x.get('type')=='tool_use' and x.get('name')=='Bash':
                    yield d.get('timestamp','')[11:19], x['input'].get('command','')
def grok_cmds(f):
    for line in open(f):
        try: e=json.loads(line)
        except: continue
        for tc in e.get('tool_calls') or []:
            try: a=json.loads(tc.get('arguments') or '{}')
            except: a={}
            c=a.get('command') or a.get('cmd')
            if c: yield '', c if isinstance(c,str) else ' '.join(c)
src=sys.argv[1]
it=grok_cmds(src) if src.endswith('chat_history.jsonl') else claude_cmds(src)
for ts,cmd in it:
    ks=[(kind(s),s) for s in segs(cmd)]; ks=[(k,s) for k,s in ks if k]
    for k,s in ks: print(ts, k, '|', s[:110])
