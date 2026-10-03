"""PreToolUse hook: deny a role-pool dispatch whose route line is wrong.

An Agent whose subagent_type starts with fable-advisor:, and a SendMessage to
such an agent, must open with a route line. The role matches the agent file.
The dial matches the derived dial. mainstay, crux, and rescue require that
dial in the Claude Code cell; same-model is only a worker whose model is the
session model. A tier above mainstay requires a basis of an allowed kind.
Unreadable or unparseable stdin, profile, or agent file is a deny. Print a
deny decision, or print nothing to allow.
"""
import json
import os
import re
import sys


PREFIX = "fable-advisor:"
REASON = "fable-advisor route gate: "
HEADER = ["Role", "`mainstay`", "`crux`", "`rescue`"]
TIERS = ("mainstay", "crux", "rescue")
ALIAS_ANCHORS = {
    "haiku": "haiku-4-5",
    "sonnet": "sonnet-5-5",
    "opus": "opus-5-5",
    "fable": "fable-5-1",
}
TRUTHY = ("1", "true", "yes", "on")
MAINSTAY_BASIS = ("key-difficulty", "failure", "user-declaration", "low-confidence")
BASIS = {
    ("explorer", "crux"): ("key-difficulty", "failure", "user-declaration"),
    ("worker", "crux"): ("key-difficulty", "failure", "user-declaration"),
    ("advisor", "crux"): ("low-confidence", "user-declaration"),
    ("explorer", "rescue"): ("failure", "user-declaration"),
    ("worker", "rescue"): ("failure", "user-declaration"),
    ("advisor", "rescue"): ("user-declaration",),
}
CANDIDATE_SEP = " \u203a "
AGENT_NAME_RE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$")
AGENT_ID_RE = re.compile(r"^a[0-9a-f]{16}$")
ROUTE_RE = re.compile(
    r"^Route: role=(\S+) tier=(\S+) dial=(\S+)(?: basis=(\S+) ref=(.*))?$"
)
CANDIDATE_RE = re.compile(r"^([^\[\s]+)(?:\[([^\]]+)\])?$")
BRACKET_SUFFIX_RE = re.compile(r"\[[^\]]*\]$")
DATE_SUFFIX_RE = re.compile(r"-\d{8}$")
ROW_SEP_RE = re.compile(r":?-{3,}:?")

__all__ = ["parse_routing_profile"]


def normalize_model(model):
    """Lowercase; drop a leading claude-, a trailing bracket suffix, and a trailing date."""
    text = model.strip().lower()
    if text.startswith("claude-"):
        text = text[len("claude-"):]
    text = BRACKET_SUFFIX_RE.sub("", text)
    text = DATE_SUFFIX_RE.sub("", text)
    return text


def expand_candidate(candidate):
    match = CANDIDATE_RE.fullmatch(candidate.strip())
    if not match:
        raise ValueError("unparseable candidate %r" % candidate)
    model, efforts = match.group(1), match.group(2)
    if efforts is None:
        return [model]
    dials = []
    for item in efforts.split(","):
        effort = item.strip().replace("*", "")
        if not effort:
            raise ValueError("empty effort in %r" % candidate)
        dials.append("%s[%s]" % (model, effort))
    return dials


def expand_cell(cell):
    dials = []
    seen = set()
    for part in cell.split(CANDIDATE_SEP):
        candidate = part.strip()
        if not candidate:
            continue
        for dial in expand_candidate(candidate):
            if dial not in seen:
                seen.add(dial)
                dials.append(dial)
    dials.sort()
    return dials


def split_row(line):
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [part.strip() for part in stripped.strip("|").split("|")]


def parse_routing_profile(text):
    """Return {"claude_code": {role: {tier: [sorted dials]}}} from profile markdown."""
    if not isinstance(text, str):
        raise ValueError("profile text is not a string")
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "## Claude Code candidates":
            start = index + 1
            break
    if start is None:
        raise ValueError("heading '## Claude Code candidates' is missing")
    header_at = None
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            break
        if split_row(lines[index]) == HEADER:
            header_at = index
            break
    if header_at is None:
        raise ValueError("Claude Code role table is missing")
    limit = len(lines)
    for index in range(header_at + 1, len(lines)):
        if lines[index].startswith("## "):
            limit = index
            break
    table = {}
    for line in lines[header_at + 1:limit]:
        cells = split_row(line)
        if cells is None:
            continue
        if cells and all(ROW_SEP_RE.fullmatch(cell) for cell in cells):
            continue
        if len(cells) != 4:
            raise ValueError("role row does not have 3 tiers")
        role = cells[0]
        if not role or role in table:
            raise ValueError("duplicate or empty role %r" % role)
        table[role] = {}
        for tier, cell in zip(TIERS, cells[1:]):
            table[role][tier] = expand_cell(cell)
    if not table:
        raise ValueError("Claude Code role table has no rows")
    return {"claude_code": table}


def bare_model_ids(table):
    """Models written without brackets anywhere in the Claude Code table."""
    found = set()
    for tiers in table["claude_code"].values():
        for dials in tiers.values():
            for dial in dials:
                if "[" not in dial:
                    found.add(dial)
    return found


def models_in_profile(table):
    """Model ids that appear in any Claude Code cell."""
    found = set()
    for tiers in table["claude_code"].values():
        for dials in tiers.values():
            for dial in dials:
                found.add(dial.split("[", 1)[0])
    return found


def dial_for_agent(model, effort, bare):
    if model in bare:
        return model
    return "%s[%s]" % (model, effort)


def dial_for_record(model, effort, bare):
    """Bare when the assistant record has no effort, or the model is written bare."""
    if model in bare or not effort:
        return model
    return "%s[%s]" % (model, effort)


def parse_route(line):
    match = ROUTE_RE.match(line)
    if not match:
        return None
    role, tier, dial, kind, ref = match.groups()
    if kind is not None and (ref is None or ref.strip() == ""):
        return None
    return (role, tier, dial, kind, ref)


def classify_route(text):
    if not isinstance(text, str) or text == "":
        return None, "route line is missing"
    lines = text.splitlines()
    line = lines[0] if lines else ""
    if line == "" or not line.startswith("Route:"):
        return None, "route line is missing"
    parsed = parse_route(line)
    if parsed is None:
        return None, "route line is malformed"
    return parsed, None


def plugin_root(env):
    root = env.get("CLAUDE_PLUGIN_ROOT")
    if isinstance(root, str) and root.strip():
        return root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_profile(root):
    path = os.path.join(root, "skills", "orchestration", "routing-profile.md")
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        return None, "routing profile unreadable: %s" % exc
    try:
        return parse_routing_profile(text), None
    except ValueError as exc:
        return None, "routing profile unparseable: %s" % exc


def effort_from_frontmatter(text):
    if text.startswith("\ufeff"):
        text = text[1:]
    if not text.startswith("---"):
        return None, "frontmatter is missing"
    end = text.find("\n---", 3)
    if end < 0:
        return None, "frontmatter is not closed"
    for line in text[3:end].splitlines():
        if not line.startswith("effort:"):
            continue
        raw = line.split(":", 1)[1].strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
            raw = raw[1:-1].strip()
        elif raw:
            raw = raw.split()[0]
        if not raw:
            return None, "effort is missing"
        return raw, None
    return None, "effort is missing"


def load_agent(root, agent_name):
    if not AGENT_NAME_RE.fullmatch(agent_name or ""):
        return None, None, "agent name is invalid: %s" % agent_name
    path = os.path.join(root, "agents", agent_name + ".md")
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        return None, None, "agent file unreadable: %s (%s)" % (agent_name, exc)
    effort, err = effort_from_frontmatter(text)
    if err:
        return None, None, "agent file %s: %s" % (agent_name, err)
    return agent_name.split("-", 1)[0], effort, None


SYNTHETIC_MODEL = "<synthetic>"


def message_model_raw(record):
    message = record.get("message")
    if not isinstance(message, dict):
        return None
    raw = message.get("model")
    if not isinstance(raw, str):
        return None
    return raw.strip()


def last_assistant_record(path):
    """Last assistant record with a real message.model.

    Transcripts are large; read from the end. A message.model of <synthetic>
    is not a model. When every assistant record is synthetic, return None.
    """
    with open(path, "rb") as handle:
        handle.seek(0, os.SEEK_END)
        pos = handle.tell()
        if pos == 0:
            return None
        buf = b""
        while True:
            if pos > 0:
                step = min(65536, pos)
                pos -= step
                handle.seek(pos)
                buf = handle.read(step) + buf
            if pos > 0:
                cut = buf.find(b"\n")
                if cut < 0:
                    continue
                chunk = buf[cut + 1:]
                buf = buf[:cut]
            else:
                chunk = buf
                buf = b""
            for raw in reversed(chunk.split(b"\n")):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if isinstance(obj, dict) and obj.get("type") == "assistant":
                    if message_model_raw(obj) == SYNTHETIC_MODEL:
                        continue
                    return obj
            if pos <= 0:
                return None


def model_of_record(record):
    raw = message_model_raw(record)
    if not raw or raw == SYNTHETIC_MODEL:
        return None
    return normalize_model(raw) or None


def effort_of_record(record):
    effort = record.get("effort")
    if not isinstance(effort, str) or not effort.strip():
        return None
    return effort.strip()


def read_session_model(path):
    # The current turn is not in the file yet. The previous assistant record is the session model.
    if not isinstance(path, str) or not path:
        return None, "transcript_path is missing"
    try:
        record = last_assistant_record(path)
    except OSError as exc:
        return None, "transcript unreadable: %s" % exc
    if record is None:
        return None, "no assistant record in the transcript"
    model = model_of_record(record)
    if not model:
        return None, "assistant record has no message.model"
    return model, None


def env_text(env, name):
    raw = env.get(name, "")
    if raw is None:
        return ""
    if not isinstance(raw, str):
        raw = str(raw)
    return raw.strip()


def env_is_force(env):
    return env_text(env, "CLAUDE_CODE_SUBAGENT_MODEL_FORCE").lower() in TRUTHY


def model_token_under_force(env, session_model, session_error):
    """CLAUDE_CODE_SUBAGENT_MODEL when set and not inherit; otherwise the session model."""
    raw = env_text(env, "CLAUDE_CODE_SUBAGENT_MODEL")
    if raw and raw.lower() != "inherit":
        return raw, None
    if session_error or not session_model:
        return None, "session model unavailable: %s" % (session_error or "no assistant record")
    return session_model, None


def resolve_model(token, session_model, env):
    """Alias: session model in that family, else the redirect variable, else the anchor."""
    if not isinstance(token, str) or not token.strip():
        return None, "model is empty"
    key = token.strip().lower()
    if key in ALIAS_ANCHORS:
        if isinstance(session_model, str) and session_model.startswith(key + "-"):
            return session_model, None
        redirected = env_text(env, "ANTHROPIC_DEFAULT_%s_MODEL" % key.upper())
        if redirected:
            model = normalize_model(redirected)
            if not model:
                return None, "redirected model is empty"
            return model, None
        return ALIAS_ANCHORS[key], None
    model = normalize_model(token)
    if not model:
        return None, "model is empty"
    return model, None


def select_agent_model(tool_input, env, session_model, session_error):
    known = session_model if not session_error else None
    if env_is_force(env):
        # FORCE ignores tool_input model.
        token, err = model_token_under_force(env, session_model, session_error)
        if err:
            return None, err
    else:
        if "model" not in tool_input or tool_input.get("model") in (None, ""):
            return None, "model is required"
        raw = tool_input.get("model")
        if not isinstance(raw, str):
            return None, "model is not a string"
        token = raw
    return resolve_model(token, known, env)


def role_pool_name(subagent_type):
    if not isinstance(subagent_type, str) or not subagent_type.startswith(PREFIX):
        return None
    return subagent_type[len(PREFIX):]


def name_is_set(tool_input):
    return "name" in tool_input


def legal_suffix(table, role, tier):
    if tier not in TIERS or not role:
        return ""
    tiers = table.get("claude_code", {}).get(role)
    if not isinstance(tiers, dict) or tier not in tiers:
        return ""
    return "; legal dials: %s" % ", ".join(tiers[tier])


def with_legal_dials(reason, table, role, tier):
    """A parsed mainstay, crux, or rescue deny names that cell's dials once."""
    if not reason or "legal dials:" in reason:
        return reason
    suffix = legal_suffix(table, role, tier)
    if not suffix:
        return reason
    return reason + suffix


def basis_error(role, tier, kind, ref):
    if tier == "mainstay":
        if kind is None:
            return None
        if kind not in MAINSTAY_BASIS:
            return "basis kind %s is not allowed at mainstay; allowed: %s" % (
                kind, ", ".join(MAINSTAY_BASIS))
        if ref is None or ref.strip() == "":
            return "basis ref is empty"
        return None
    if tier == "same-model":
        if kind != "same-model" or ref is None or ref.strip() == "":
            return "same-model requires basis kind same-model and a non-empty ref"
        return None
    allowed = BASIS.get((role, tier))
    if allowed is None:
        return "basis is not defined for %s at %s" % (role, tier)
    if kind is None:
        return "basis is required at %s" % tier
    if kind not in allowed:
        return "basis kind %s is not allowed for %s at %s; allowed: %s" % (
            kind, role, tier, ", ".join(allowed))
    if ref is None or ref.strip() == "":
        return "basis ref is empty"
    return None


def tier_error(role, tier, dial, kind, ref, model, session_model, session_error, agent_name, table):
    if tier == "same-model":
        if not agent_name.startswith("worker-"):
            return "same-model applies only to a worker agent"
        err = basis_error(role, tier, kind, ref)
        if err:
            return err
        if session_error or not session_model:
            return "session model unavailable: %s" % (session_error or "no assistant record")
        if model != session_model:
            return "same-model requires session model %s; derived model is %s" % (
                session_model, model)
        # The cell check is waived. The derived model still has to appear in the table.
        if model not in models_in_profile(table):
            return "derived model %s is not in the profile" % model
        return None
    if tier not in TIERS:
        return "tier %s is not a routing tier" % tier
    cell = table["claude_code"].get(role, {}).get(tier)
    if cell is None:
        return "no Claude Code cell for %s at %s" % (role, tier)
    if dial not in cell:
        return "derived dial %s is outside %s %s; legal dials: %s" % (
            dial, role, tier, ", ".join(cell))
    return basis_error(role, tier, kind, ref)


def match_route(parsed, role, dial, model, session_model, session_error, agent_name, table):
    route_role, tier, route_dial, kind, ref = parsed
    if route_role != role:
        return "route role %s does not match agent role %s" % (route_role, role)
    if route_dial != dial:
        return "route dial %s does not match derived dial %s%s" % (
            route_dial, dial, legal_suffix(table, role, tier))
    return tier_error(
        role, tier, dial, kind, ref, model, session_model, session_error, agent_name, table)


def role_of_name(agent_name):
    if not agent_name or "-" not in agent_name:
        return None
    return agent_name.split("-", 1)[0]


def check_agent(data, env):
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return "tool_input is missing"
    agent_name = role_pool_name(tool_input.get("subagent_type"))
    if agent_name is None:
        return None
    parsed, route_err = classify_route(tool_input.get("prompt"))
    root = plugin_root(env)
    table, err = load_profile(root)

    def finish(reason):
        if not reason or parsed is None or table is None:
            return reason
        return with_legal_dials(reason, table, role_of_name(agent_name), parsed[1])

    if err:
        return err
    if name_is_set(tool_input):
        return finish("name is set, so the agent file effort does not apply")
    role, effort, err = load_agent(root, agent_name)
    if err:
        return finish(err)
    session_model, session_error = read_session_model(data.get("transcript_path"))
    model, err = select_agent_model(tool_input, env, session_model, session_error)
    if err:
        return finish(err)
    if route_err:
        return route_err
    dial = dial_for_agent(model, effort, bare_model_ids(table))
    return finish(match_route(
        parsed, role, dial, model, session_model, session_error, agent_name, table))


def is_subscription(tool_input):
    if tool_input.get("notify_when_idle") is not True:
        return False
    if "message" not in tool_input:
        return True
    message = tool_input.get("message")
    return message is None or message == ""


def safe_segment(text):
    return text != "" and "/" not in text and "\\" not in text and ".." not in text


def meta_path_for(transcript, to):
    if not isinstance(transcript, str) or not transcript:
        return None
    if transcript.endswith(".jsonl"):
        base = transcript[: -len(".jsonl")]
    else:
        base = transcript
    return os.path.join(base, "subagents", "agent-%s.meta.json" % to)


def read_meta(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        return None, "target record unreadable: %s" % exc
    except json.JSONDecodeError:
        return None, "target record is unparseable"
    if not isinstance(data, dict):
        return None, "target record is unparseable"
    return data, None


def target_dial(meta, meta_path, effort, bare, env, session_model, session_error):
    jsonl = meta_path[: -len(".meta.json")] + ".jsonl"
    record = None
    if os.path.isfile(jsonl):
        try:
            record = last_assistant_record(jsonl)
        except OSError as exc:
            return None, None, "subagent transcript unreadable: %s" % exc
    if record is not None:
        model = model_of_record(record)
        if not model:
            return None, None, "subagent assistant record has no message.model"
        return model, dial_for_record(model, effort_of_record(record), bare), None
    raw = meta.get("model")
    if isinstance(raw, str) and raw.strip():
        token = raw.strip()
    else:
        token, err = model_token_under_force(env, session_model, session_error)
        if err:
            return None, None, err
    known = session_model if not session_error else None
    model, err = resolve_model(token, known, env)
    if err:
        return None, None, err
    return model, dial_for_agent(model, effort, bare), None


def target_reason(reason, dial):
    if not reason or not dial:
        return reason
    return "%s; target dial is %s" % (reason, dial)


def check_send(data, env):
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return "tool_input is missing"
    if is_subscription(tool_input):
        return None
    to = tool_input.get("to")
    if not isinstance(to, str) or not safe_segment(to):
        return None
    meta_path = meta_path_for(data.get("transcript_path"), to)
    if meta_path is None or not os.path.isfile(meta_path):
        if AGENT_ID_RE.fullmatch(to):
            return "target record agent-%s.meta.json is missing" % to
        return None
    meta, err = read_meta(meta_path)
    if err:
        return err
    agent_name = role_pool_name(meta.get("agentType"))
    if agent_name is None:
        return None
    root = plugin_root(env)
    table, err = load_profile(root)
    if err:
        return err
    role, effort, agent_err = load_agent(root, agent_name)
    message = tool_input.get("message") if "message" in tool_input else None
    parsed = None
    route_err = None
    if isinstance(message, str):
        parsed, route_err = classify_route(message)
    else:
        route_err = "message is not a string"

    def finish(reason, known_dial):
        if not reason:
            return None
        if parsed is not None:
            reason = with_legal_dials(reason, table, role or role_of_name(agent_name), parsed[1])
        return target_reason(reason, known_dial)

    if agent_err:
        return finish(agent_err, None)
    session_model, session_error = read_session_model(data.get("transcript_path"))
    bare = bare_model_ids(table)
    model, dial, err = target_dial(
        meta, meta_path, effort, bare, env, session_model, session_error)
    if err:
        return finish(err, dial)
    if route_err:
        return target_reason(route_err, dial)
    return finish(match_route(
        parsed, role, dial, model, session_model, session_error, agent_name, table), dial)


def evaluate(raw):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return "stdin is not valid JSON"
    if not isinstance(data, dict):
        return "stdin is not a JSON object"
    tool = data.get("tool_name")
    if tool == "Agent":
        return check_agent(data, os.environ)
    if tool == "SendMessage":
        return check_send(data, os.environ)
    return None


def emit_deny(reason):
    if not reason.startswith(REASON):
        reason = REASON + reason
    body = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(body))
    sys.stdout.write("\n")


def main():
    try:
        reason = evaluate(sys.stdin.read())
    except Exception as exc:
        reason = "unexpected error: %s" % exc
    if reason:
        emit_deny(reason)


if __name__ == "__main__":
    main()
