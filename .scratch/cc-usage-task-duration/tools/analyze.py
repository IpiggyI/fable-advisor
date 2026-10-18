import json, re, sys, os, glob
from datetime import datetime

def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()

def load(path):
    out = []
    with open(path) as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

TEST_RE = re.compile(r'\bbun (run )?test\b([^|;&\n]*)')
RAN_RE = re.compile(r'Ran (\d+) tests? across (\d+) files?\. \[([\d.]+)(ms|s)\]')

def classify_bash(cmd):
    c = cmd
    if 'run-codex.mjs' in c or 'run-grok' in c or 'run-lane' in c:
        return 'lane-dispatch'
    for m in TEST_RE.finditer(c):
        args = re.split(r'\s+(?:\d?>|\|)', m.group(2))[0].split()
        args = [a for a in args if a not in ('2>&1',)]
        if not args or args == ['test/'] or args == ['test']:
            return 'test-full'
    if TEST_RE.search(c) and re.search(r'bun (run )?test\s+\S*test/\S+', c):
        return 'test-targeted'
    if 'typecheck' in c or 'tsc ' in c:
        return 'typecheck'
    if 'chrome' in c or 'cdp' in c.lower() or 'render' in c or 'playwright' in c:
        return 'render'
    if 'cargo' in c or 'nsis' in c.lower() or 'pack' in c:
        return 'build/pack'
    if re.search(r'\bsleep\b', c):
        return 'sleep/poll'
    if 'bun run start' in c or 'src/index.ts' in c:
        return 'app-run'
    if c.strip().startswith('git '):
        return 'git'
    return 'bash-other'

def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                if b.get('type') == 'text':
                    parts.append(b.get('text', ''))
                elif b.get('type') == 'tool_result':
                    parts.append(text_of(b.get('content')))
        return '\n'.join(parts)
    return ''

def analyze_transcript(path, label, main=True):
    E = load(path)
    tool_uses = {}   # id -> (ts, name, input)
    results = {}     # id -> (ts, text)
    bg_launch = {}   # task id -> tool_use id
    notifs = {}      # task id -> ts
    turn_durs = []
    turn_starts = [] # (ts, kind, snippet)
    stamps = []
    for e in E:
        t = e.get('timestamp')
        if not t:
            continue
        T = ts(t)
        stamps.append(T)
        typ = e.get('type')
        if typ == 'assistant':
            for b in e.get('message', {}).get('content', []) or []:
                if isinstance(b, dict) and b.get('type') == 'tool_use':
                    tool_uses[b['id']] = (T, b['name'], b.get('input', {}))
        elif typ == 'user':
            c = e.get('message', {}).get('content')
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get('type') == 'tool_result':
                        txt = text_of(b.get('content'))
                        results[b['tool_use_id']] = (T, txt, e.get('toolUseResult'))
                        m = re.search(r'running in background with ID: (\w+)', txt)
                        if m:
                            bg_launch[m.group(1)] = b['tool_use_id']
            o = (e.get('origin') or {}).get('kind')
            s = text_of(c)
            if o == 'task-notification':
                m = re.search(r'<task-id>(\w+)</task-id>', s)
                if m:
                    notifs.setdefault(m.group(1), T)
            if o in ('human', 'task-notification', 'peer') or (o is None and isinstance(c, str) and not e.get('isMeta') and not s.startswith('This session is being continued')):
                turn_starts.append((T, o or 'other', s[:80].replace('\n', ' ')))
        elif typ == 'system' and e.get('subtype') == 'turn_duration':
            turn_durs.append((T, e.get('durationMs') or 0))
    wall = (max(stamps) - min(stamps)) if stamps else 0
    # foreground tool durations
    cats = {}
    tests = []
    for tid, (T, name, inp) in tool_uses.items():
        r = results.get(tid)
        if not r:
            continue
        d = r[0] - T
        txt = r[1]
        bgid = None
        m = re.search(r'running in background with ID: (\w+)', txt)
        if m:
            bgid = m.group(1)
        if name == 'Bash':
            cat = classify_bash(inp.get('command', ''))
        elif name in ('Agent', 'Task'):
            cat = 'Agent(fg)'
        else:
            cat = name
        if bgid:
            # count background separately
            dn = notifs.get(bgid)
            bd = (dn - T) if dn else None
            cats.setdefault('BG:' + cat, []).append(bd or 0)
            if cat.startswith('test') or cat == 'typecheck':
                tests.append((T, cat, bd, inp.get('command', '')[:200], 'bg', bgid))
        else:
            cats.setdefault(cat, []).append(d)
            if cat.startswith('test') or cat == 'typecheck':
                rr = RAN_RE.findall(txt)
                tests.append((T, cat, d, inp.get('command', '')[:200], 'fg', rr))
    return dict(label=label, wall=wall, turn_durs=turn_durs, turn_starts=turn_starts,
                cats=cats, tests=tests, tool_uses=tool_uses, results=results, notifs=notifs,
                bg_launch=bg_launch, first=min(stamps) if stamps else 0, last=max(stamps) if stamps else 0)

def fmt(sec):
    if sec is None:
        return '   ?'
    return f'{sec/60:6.1f}m'

if __name__ == '__main__':
    path = sys.argv[1]
    r = analyze_transcript(path, os.path.basename(path))
    print('WALL', fmt(r['wall']), 'active(turn_duration sum)', fmt(sum(d for _, d in r['turn_durs'])/1000), 'turns', len(r['turn_durs']))
    print('-- tool categories (count, total)')
    for k, v in sorted(r['cats'].items(), key=lambda kv: -sum(kv[1])):
        print(f'  {k:22s} n={len(v):4d} total={fmt(sum(v))} max={fmt(max(v))}')
