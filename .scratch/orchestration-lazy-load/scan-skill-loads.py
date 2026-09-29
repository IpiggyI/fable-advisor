"""List Claude Code sessions that loaded fable-advisor:orchestration or read the routing profile.

Usage: python3 scan-skill-loads.py [YYYY-MM-DD]   (default: 2026-09-28)
Per session: the human message index of the first skill load and of the first
routing-profile read, and the number of dispatches (Agent/Task calls or CLI
runner invocations) in the whole session.
"""
import glob, json, os, sys, time

since = time.mktime(time.strptime(sys.argv[1] if len(sys.argv) > 1 else '2026-09-28', '%Y-%m-%d'))
root = os.path.expanduser('~/.claude/projects')


def is_human(record):
    content = (record.get('message') or {}).get('content')
    if isinstance(content, str):
        return not content.startswith('<')
    return isinstance(content, list) and any(
        isinstance(x, dict) and x.get('type') == 'text' and not x.get('text', '').startswith('<') for x in content)


for path in sorted(glob.glob(root + '/*/*.jsonl'), key=os.path.getmtime):
    if os.path.getmtime(path) < since:
        continue
    human, skill_at, route_at, dispatches, first = 0, None, None, 0, ''
    for line in open(path, encoding='utf-8'):
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get('isSidechain'):
            continue
        if record.get('type') == 'user' and is_human(record):
            human += 1
            if not first:
                content = record['message']['content']
                first = content if isinstance(content, str) else next(
                    x['text'] for x in content if isinstance(x, dict) and x.get('type') == 'text')
        content = (record.get('message') or {}).get('content')
        if record.get('type') != 'assistant' or not isinstance(content, list):
            continue
        for item in content:
            if item.get('type') != 'tool_use':
                continue
            text = json.dumps(item.get('input'))
            if item.get('name') == 'Skill' and 'orchestration' in text and skill_at is None:
                skill_at = human
            if 'fable-advisor-routing' in text and route_at is None:
                route_at = human
            if item.get('name') in ('Agent', 'Task') or 'run-codex' in text or 'run-grok' in text:
                dispatches += 1
    if skill_at is not None or route_at is not None:
        print(time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(path))), path.split('/')[-2][-32:],
              'skill@', skill_at, 'profile@', route_at, 'dispatches', dispatches, '|', first.replace('\n', ' ')[:60])
