"""列出 cc-usage 会话 be93294f 里每次复用车道会话时的间隔与缓存命中。

用法：python3 cache_reuse_1003.py
codex 车道：每个回合（turn_context）的开始时刻、型号、强度，以及该回合第一次请求的
input_tokens 与 cached_input_tokens（rollout 里 token_count 事件的 last_token_usage）。
claude 车道：worker 记录里每条以 "The coordinator sent a message" 开头的 user 记录是一次
`SendMessage` 续派。列出续派时刻、距上一条 assistant 记录的间隔，以及其后第一次响应的
cache_read_input_tokens 与 cache_creation_input_tokens。按 assistant 记录之间的间隔判断续派
不可靠：长工具调用也会留下间隔，间隔很短的续派又会被漏掉。
时刻都是 UTC。codex 的 rollout 文件名用本地时间（CST），所以在 2026/10/03 目录下。
"""
import glob
import json
import os
from datetime import datetime

CODEX = os.path.expanduser('~/.codex/sessions/2026/10/03/')
SUBAGENTS = os.path.expanduser(
    '~/.claude/projects/-home-hyy-develop-personal-GitHub-cc-usage/'
    'be93294f-4abe-4bbe-a2df-73aa8fe76cda/subagents/')


def parse(ts):
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


for sid in ('01a0fd90-6bef-7c92-b316-d31d273db53f', '01a0fd90-6c00-74e0-9b11-39afb11ecaf1'):
    path = glob.glob(CODEX + '*' + sid + '.jsonl')[0]
    print('codex', sid)
    waiting = False
    last_end = None
    for line in open(path):
        record = json.loads(line)
        payload = record.get('payload', {})
        ts = record.get('timestamp', '')
        if record.get('type') == 'turn_context':
            gap = f'{(parse(ts) - last_end).total_seconds() / 60:.1f} 分钟' if last_end else '-'
            print(f'  回合开始 {ts[11:19]}  距上回合结束 {gap}  {payload.get("model")}[{payload.get("effort")}]')
            waiting = True
        elif record.get('type') == 'event_msg' and payload.get('type') == 'token_count' and payload.get('info') and waiting:
            usage = payload['info'].get('last_token_usage') or {}
            print(f'    第一次请求 input={usage.get("input_tokens")} cached={usage.get("cached_input_tokens")}')
            waiting = False
        elif record.get('type') == 'event_msg' and payload.get('type') == 'task_complete':
            last_end = parse(ts)

for agent in ('afdfced88a1d10c0a', 'a520167d9972b3917', 'aa31c9b6551b4c5ad'):
    meta = json.load(open(f'{SUBAGENTS}agent-{agent}.meta.json'))
    print('claude', agent, meta.get('agentType'), meta.get('model'), meta.get('description'))
    last_assistant = None
    pending = '首次派发'
    for line in open(f'{SUBAGENTS}agent-{agent}.jsonl'):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = record.get('message', {}).get('content')
        if record.get('type') == 'user':
            text = content if isinstance(content, str) else ' '.join(
                (block.get('text') or '') for block in content or [] if isinstance(block, dict))
            if text.startswith('The coordinator sent a message'):
                gap = (parse(record['timestamp']) - last_assistant).total_seconds() / 60 if last_assistant else None
                pending = f'续派 {record["timestamp"][11:19]}，距上一条输出 {gap:.1f} 分钟' if gap is not None else '续派'
            continue
        if record.get('type') != 'assistant':
            continue
        if pending:
            usage = record['message'].get('usage', {})
            print(f'  {pending}：第一次响应 cache_read={usage.get("cache_read_input_tokens")}'
                  f' cache_create={usage.get("cache_creation_input_tokens")}')
            pending = None
        last_assistant = parse(record['timestamp'])
    print(f'  最后一条输出 {last_assistant.isoformat()[11:19]}')
