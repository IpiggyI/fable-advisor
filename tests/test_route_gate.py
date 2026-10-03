#!/usr/bin/env python3
"""Regression tests for hooks/route-gate.py (process-boundary behavior)."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO_ROOT, "plugin", "hooks", "route-gate.py")
HOOKS_JSON = os.path.join(REPO_ROOT, "plugin", "hooks", "hooks.json")
SEP = " \u203a "
MODEL_ENV = (
    "CLAUDE_CODE_SUBAGENT_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL_FORCE",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_FABLE_MODEL",
)


def cell(*candidates):
    return SEP.join(candidates)


PROFILE = "\n".join([
    "# fixture",
    "",
    "## Claude Code candidates",
    "",
    "| Role | `mainstay` | `crux` | `rescue` |",
    "|---|---|---|---|",
    "| explorer | %s | %s | %s |" % (
        cell("haiku-4-5", "gpt-6-luna[high*, xhigh]"),
        cell("sonnet-5-5[medium*, high]", "grok-4.7[xhigh]"),
        cell("opus-5-5[high*, xhigh]"),
    ),
    "| worker | %s | %s | %s |" % (
        cell("grok-4.7[high*, xhigh]", "gpt-6.1-sol[high]"),
        cell("opus-5-5[medium*, high]"),
        "opus-5-5[xhigh]",
    ),
    "| advisor | %s | %s | %s |" % (
        cell("opus-5-5[medium*, high]", "fable-5-1[low*, medium]"),
        cell("opus-5-5[xhigh]", "fable-5-1[high]"),
        "fable-5-1[xhigh]",
    ),
    "",
    "## Cursor candidates",
    "",
    "| Role | `mainstay` | `crux` | `rescue` |",
    "|---|---|---|---|",
    "| explorer | composer-2.5-fast | sonnet-5-5[high] | opus-5-5[xhigh] |",
    "",
])

AGENTS = {
    "explorer-h": "high",
    "worker-h": "high",
    "advisor-xh": "xhigh",
}


def load_hook():
    spec = importlib.util.spec_from_file_location("route_gate", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_hook(payload, plugin_root, extra_env=None):
    env = os.environ.copy()
    for key in MODEL_ENV:
        env.pop(key, None)
    env["CLAUDE_PLUGIN_ROOT"] = plugin_root
    if extra_env:
        for key, value in extra_env.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
    if isinstance(payload, dict):
        text = json.dumps(payload)
    else:
        text = payload
    return subprocess.run(
        [sys.executable, HOOK],
        input=text,
        capture_output=True,
        text=True,
        env=env,
        cwd=plugin_root,
    )


def assert_allow(result):
    assert result.returncode == 0, "exit %s stderr=%r stdout=%r" % (
        result.returncode, result.stderr, result.stdout)
    assert result.stdout == "", "expected empty stdout, got %r" % result.stdout
    assert result.stderr == "", "expected empty stderr, got %r" % result.stderr


def assert_deny(result, fragment):
    assert result.returncode == 0, "exit %s stderr=%r stdout=%r" % (
        result.returncode, result.stderr, result.stdout)
    assert result.stderr == "", result.stderr
    data = json.loads(result.stdout)
    output = data["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse", output
    assert output["permissionDecision"] == "deny", output
    reason = output["permissionDecisionReason"]
    assert reason.startswith("fable-advisor route gate: "), reason
    assert fragment in reason, reason


def route(role, tier, dial, kind=None, ref="stated"):
    line = "Route: role=%s tier=%s dial=%s" % (role, tier, dial)
    if kind is not None:
        line += " basis=%s ref=%s" % (kind, ref)
    return line


def prompt_of(line):
    return line + "\nRead the preamble."


def agent_id(nibble):
    return "a" + (nibble * 16)


def assistant(model, effort="high"):
    record = {"type": "assistant", "message": {"model": model, "content": []}}
    if effort is not None:
        record["effort"] = effort
    return record


def user(text="next"):
    return {"type": "user", "message": {"role": "user", "content": text}}


def write_jsonl(path, records):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record))
            handle.write("\n")


class Fix(object):
    def __init__(self, root):
        self.root = root
        self.plugin = os.path.join(root, "plugin")
        self.n = 0

    def transcript(self, records):
        self.n += 1
        path = os.path.join(self.root, "work", "s%d.jsonl" % self.n)
        write_jsonl(path, records)
        return path

    def subagents(self, transcript):
        folder = os.path.join(transcript[: -len(".jsonl")], "subagents")
        os.makedirs(folder, exist_ok=True)
        return folder

    def meta(self, transcript, agent, agent_type, model=None):
        folder = self.subagents(transcript)
        body = {"agentType": agent_type, "description": "fixture"}
        if model is not None:
            body["model"] = model
        path = os.path.join(folder, "agent-%s.meta.json" % agent)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(body, handle)
        return path

    def sub_jsonl(self, transcript, agent, records):
        folder = self.subagents(transcript)
        path = os.path.join(folder, "agent-%s.jsonl" % agent)
        write_jsonl(path, records)
        return path


class fixture(object):
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        plugin = os.path.join(self.tmp.name, "plugin")
        os.makedirs(os.path.join(plugin, "skills", "orchestration"))
        os.makedirs(os.path.join(plugin, "agents"))
        profile = os.path.join(plugin, "skills", "orchestration", "routing-profile.md")
        with open(profile, "w", encoding="utf-8") as handle:
            handle.write(PROFILE)
        for name, effort in AGENTS.items():
            path = os.path.join(plugin, "agents", name + ".md")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("---\nname: %s\ndescription: fixture\neffort: %s\n---\n\n# %s\n" % (
                    name, effort, name))
        self.fx = Fix(self.tmp.name)
        return self.fx

    def __exit__(self, exc_type, exc, tb):
        self.tmp.cleanup()


def agent_call(prompt, subagent_type, model=None, name=None, transcript=None):
    tool = {
        "description": "dispatch",
        "prompt": prompt,
        "subagent_type": subagent_type,
    }
    if model is not None:
        tool["model"] = model
    if name is not None:
        tool["name"] = name
    data = {
        "session_id": "sess",
        "cwd": "/tmp",
        "hook_event_name": "PreToolUse",
        "tool_name": "Agent",
        "tool_input": tool,
    }
    if transcript:
        data["transcript_path"] = transcript
    return data


def send_call(to, message, transcript, notify=None, content=None, include_message=True):
    tool = {"to": to, "summary": "ping", "type": "message", "recipient": to}
    if include_message:
        tool["message"] = message
    if notify is not None:
        tool["notify_when_idle"] = notify
    if content is not None:
        tool["content"] = content
    return {
        "session_id": "sess",
        "cwd": "/tmp",
        "hook_event_name": "PreToolUse",
        "tool_name": "SendMessage",
        "transcript_path": transcript,
        "tool_input": tool,
    }


def case_parse_profile():
    """Parser returns claude_code role → tier → sorted dials, and stops before Cursor."""
    module = load_hook()
    table = module.parse_routing_profile(PROFILE)
    assert set(table) == {"claude_code"}, table.keys()
    mainstay = table["claude_code"]["explorer"]["mainstay"]
    assert mainstay == ["gpt-6-luna[high]", "gpt-6-luna[xhigh]", "haiku-4-5"]
    assert mainstay == sorted(mainstay)
    assert "sonnet-5-5[medium]" in table["claude_code"]["explorer"]["crux"]
    assert "sonnet-5-5[high]" in table["claude_code"]["explorer"]["crux"]
    assert "composer-2.5-fast" not in json.dumps(table)
    assert module.bare_model_ids(table) == {"haiku-4-5"}
    assert module.normalize_model("claude-haiku-4-5-20251001") == "haiku-4-5"
    assert module.normalize_model("claude-sonnet-4-5-20250929") == "sonnet-4-5"
    assert module.normalize_model("Claude-Opus-5-5[1m]") == "opus-5-5"
    assert module.normalize_model("claude-sonnet-4-5-20250929[1m]") == "sonnet-4-5"


def case_agent_mainstay():
    """Legal mainstay route for a bare haiku dial."""
    with fixture() as fx:
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="haiku")
        assert_allow(run_hook(payload, fx.plugin))


def case_agent_crux():
    """Legal crux route with a basis."""
    with fixture() as fx:
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty", "shared constraint")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="sonnet")
        assert_allow(run_hook(payload, fx.plugin))


def case_agent_missing_route():
    with fixture() as fx:
        payload = agent_call("Read the scope.", "fable-advisor:explorer-h", model="haiku")
        assert_deny(run_hook(payload, fx.plugin), "route line is missing")


def case_agent_malformed_route():
    with fixture() as fx:
        bad = "Route: role=explorer dial=haiku-4-5 tier=mainstay"
        payload = agent_call(prompt_of(bad), "fable-advisor:explorer-h", model="haiku")
        assert_deny(run_hook(payload, fx.plugin), "route line is malformed")


def case_agent_name():
    with fixture() as fx:
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(
            prompt_of(line), "fable-advisor:explorer-h", model="haiku", name="custom")
        assert_deny(run_hook(payload, fx.plugin), "name is set")


def case_agent_name_empty():
    with fixture() as fx:
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="haiku")
        payload["tool_input"]["name"] = ""
        assert_deny(run_hook(payload, fx.plugin), "name is set")


def case_agent_name_null():
    with fixture() as fx:
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="haiku")
        payload["tool_input"]["name"] = None
        assert_deny(run_hook(payload, fx.plugin), "name is set")


def case_agent_no_model():
    with fixture() as fx:
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h")
        assert_deny(run_hook(payload, fx.plugin), "model is required")


def case_agent_crux_no_model_lists_dials():
    """A parsed crux route with no model lists that cell's legal dials."""
    with fixture() as fx:
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h")
        result = run_hook(payload, fx.plugin)
        assert_deny(result, "legal dials:")
        reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        assert reason.count("legal dials:") == 1, reason


def case_agent_role_mismatch():
    with fixture() as fx:
        line = route("worker", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="haiku")
        assert_deny(run_hook(payload, fx.plugin), "does not match agent role explorer")


def case_agent_dial_mismatch():
    """Route dial is in the cell, but it is not the derived dial."""
    with fixture() as fx:
        line = route("explorer", "crux", "sonnet-5-5[medium]", "key-difficulty")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="sonnet")
        assert_deny(run_hook(payload, fx.plugin), "does not match derived dial sonnet-5-5[high]")


def case_agent_dial_outside_cell():
    """Derived dial matches the route and is outside the cell."""
    with fixture() as fx:
        line = route("explorer", "mainstay", "opus-5-5[high]")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="opus")
        result = run_hook(payload, fx.plugin)
        assert_deny(result, "outside")
        assert_deny(result, "legal dials:")
        assert_deny(result, "haiku-4-5")


def case_agent_basis_missing():
    with fixture() as fx:
        line = route("explorer", "crux", "sonnet-5-5[high]")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="sonnet")
        assert_deny(run_hook(payload, fx.plugin), "basis is required at crux")


def case_agent_basis_kind():
    """Advisor at rescue rejects basis kind failure."""
    with fixture() as fx:
        line = route("advisor", "rescue", "fable-5-1[xhigh]", "failure", "receipt-1")
        payload = agent_call(prompt_of(line), "fable-advisor:advisor-xh", model="fable")
        result = run_hook(payload, fx.plugin)
        assert_deny(result, "not allowed")
        assert_deny(result, "user-declaration")


def case_agent_redirect():
    """ANTHROPIC_DEFAULT_SONNET_MODEL points at a model outside the profile."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-opus-5-5", "high"), user()])
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty")
        payload = agent_call(
            prompt_of(line), "fable-advisor:explorer-h", model="sonnet", transcript=transcript)
        result = run_hook(payload, fx.plugin, {
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-0",
        })
        assert_deny(result, "sonnet-4-0")


def case_agent_family():
    """Session model claude-sonnet-4-5-20250929 and alias sonnet derive sonnet-4-5."""
    with fixture() as fx:
        records = [
            assistant("claude-sonnet-5-5", "high"),
            user("pad " + ("x" * 80000)),
            assistant("claude-sonnet-4-5-20250929", None),
            user("done"),
        ]
        transcript = fx.transcript(records)
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty")
        payload = agent_call(
            prompt_of(line), "fable-advisor:explorer-h", model="sonnet", transcript=transcript)
        result = run_hook(payload, fx.plugin, {
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-0",
        })
        assert_deny(result, "derived dial sonnet-4-5[high]")


def case_agent_force():
    """FORCE with CLAUDE_CODE_SUBAGENT_MODEL=sonnet and no model derives sonnet-5-5."""
    with fixture() as fx:
        transcript = fx.transcript([
            assistant("claude-haiku-4-5-20251001", None),
            user(),
        ])
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty")
        payload = agent_call(
            prompt_of(line), "fable-advisor:explorer-h", transcript=transcript)
        result = run_hook(payload, fx.plugin, {
            "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1",
            "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet",
        })
        assert_allow(result)


def case_agent_same_model_skips_synthetic():
    """The last assistant record is synthetic; same-model uses the real record before it."""
    with fixture() as fx:
        transcript = fx.transcript([
            assistant("claude-sonnet-5-5", "high"),
            assistant("<synthetic>", None),
            user("done"),
        ])
        line = route("worker", "same-model", "sonnet-5-5[high]", "same-model", "plugin/**")
        payload = agent_call(
            prompt_of(line), "fable-advisor:worker-h", model="sonnet", transcript=transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_agent_same_model():
    """same-model allows a profile model whose dial is outside the worker cells."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-sonnet-5-5", "high"), user()])
        line = route("worker", "same-model", "sonnet-5-5[high]", "same-model", "plugin/**")
        payload = agent_call(
            prompt_of(line), "fable-advisor:worker-h", model="sonnet", transcript=transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_agent_same_model_not_in_profile():
    """same-model denies a derived model that the Claude Code table does not contain."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-haiku-9-9", "high"), user()])
        line = route("worker", "same-model", "haiku-9-9[high]", "same-model", "plugin/**")
        payload = agent_call(
            prompt_of(line), "fable-advisor:worker-h", model="haiku", transcript=transcript)
        assert_deny(run_hook(payload, fx.plugin), "derived model haiku-9-9 is not in the profile")


def case_agent_same_model_explorer():
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-haiku-9-9", "high"), user()])
        line = route("explorer", "same-model", "haiku-9-9[high]", "same-model", "plugin/**")
        payload = agent_call(
            prompt_of(line), "fable-advisor:explorer-h", model="haiku", transcript=transcript)
        assert_deny(run_hook(payload, fx.plugin), "same-model applies only to a worker agent")


def case_agent_same_model_other():
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-haiku-9-9", "high"), user()])
        line = route("worker", "same-model", "sonnet-5-5[high]", "same-model", "plugin/**")
        payload = agent_call(
            prompt_of(line), "fable-advisor:worker-h", model="sonnet", transcript=transcript)
        assert_deny(run_hook(payload, fx.plugin), "session model haiku-9-9")


def case_agent_same_model_no_assistant():
    with fixture() as fx:
        transcript = fx.transcript([user("only a user")])
        line = route("worker", "same-model", "haiku-4-5", "same-model", "plugin/**")
        payload = agent_call(
            prompt_of(line), "fable-advisor:worker-h", model="haiku", transcript=transcript)
        assert_deny(run_hook(payload, fx.plugin), "no assistant record")


def case_agent_other_type():
    with fixture() as fx:
        payload = agent_call("Do anything.", "general-purpose")
        assert_allow(run_hook(payload, fx.plugin))


def case_send_matches_record():
    """Route matches the target's last assistant record, not an earlier one or content."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-opus-5-5", "high"), user()])
        agent = agent_id("1")
        fx.meta(transcript, agent, "fable-advisor:advisor-xh", model="fable")
        fx.sub_jsonl(transcript, agent, [
            assistant("claude-opus-5-5", "xhigh"),
            assistant("claude-fable-5-1-20251001", "high"),
            user("tool result"),
        ])
        line = route("advisor", "crux", "fable-5-1[high]", "low-confidence", "the verdict")
        payload = send_call(
            agent, prompt_of(line), transcript, content="Route: role=explorer tier=rescue dial=nope")
        assert_allow(run_hook(payload, fx.plugin))


def case_send_skips_synthetic():
    """The target's last record is synthetic; the route matches the real record before it."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-opus-5-5", "high"), user()])
        agent = agent_id("6")
        fx.meta(transcript, agent, "fable-advisor:advisor-xh", model="fable")
        fx.sub_jsonl(transcript, agent, [
            assistant("claude-opus-5-5", "xhigh"),
            assistant("claude-fable-5-1-20251001", "high"),
            assistant("<synthetic>", "high"),
            user("tool result"),
        ])
        line = route("advisor", "crux", "fable-5-1[high]", "low-confidence", "the verdict")
        payload = send_call(agent, prompt_of(line), transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_send_missing_route():
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-opus-5-5", "high"), user()])
        agent = agent_id("1")
        fx.meta(transcript, agent, "fable-advisor:advisor-xh", model="fable")
        fx.sub_jsonl(transcript, agent, [
            assistant("claude-fable-5-1-20251001", "high"),
            user(),
        ])
        good = route("advisor", "crux", "fable-5-1[high]", "low-confidence")
        payload = send_call(agent, "continue the work", transcript, content=good)
        assert_deny(run_hook(payload, fx.plugin), "target dial is fable-5-1[high]")


def case_send_record_without_effort():
    """A record with no effort writes a bare dial, including for a bracketed model."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-opus-5-5", "high"), user()])
        agent = agent_id("4")
        fx.meta(transcript, agent, "fable-advisor:explorer-h", model="sonnet")
        fx.sub_jsonl(transcript, agent, [
            assistant("claude-sonnet-5-5", None),
            user(),
        ])
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty")
        payload = send_call(agent, prompt_of(line), transcript)
        assert_deny(run_hook(payload, fx.plugin), "does not match derived dial sonnet-5-5;")


def case_send_meta_without_model():
    """meta.json with no model derives as under FORCE."""
    with fixture() as fx:
        transcript = fx.transcript([
            assistant("claude-haiku-4-5-20251001", None),
            user(),
        ])
        agent = agent_id("5")
        fx.meta(transcript, agent, "fable-advisor:explorer-h")
        line = route("explorer", "crux", "sonnet-5-5[high]", "key-difficulty")
        payload = send_call(agent, prompt_of(line), transcript)
        assert_allow(run_hook(payload, fx.plugin, {
            "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1",
            "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet",
        }))


def case_send_meta_fallback():
    """No assistant record yet: meta.json model and the agent file derive the dial."""
    with fixture() as fx:
        transcript = fx.transcript([assistant("claude-opus-5-5", "high"), user()])
        agent = agent_id("2")
        fx.meta(transcript, agent, "fable-advisor:explorer-h", model="sonnet")
        line = route("explorer", "crux", "sonnet-5-5[high]", "failure", "receipt-2")
        payload = send_call(agent, prompt_of(line), transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_send_unknown_id():
    with fixture() as fx:
        transcript = fx.transcript([user("hi")])
        agent = agent_id("0")
        payload = send_call(agent, "hello", transcript)
        assert_deny(run_hook(payload, fx.plugin), "agent-%s.meta.json is missing" % agent)


def case_send_name():
    with fixture() as fx:
        transcript = fx.transcript([user("hi")])
        payload = send_call("planner", "hello", transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_send_main():
    with fixture() as fx:
        transcript = fx.transcript([user("hi")])
        payload = send_call("main", "hello", transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_send_subscription():
    with fixture() as fx:
        transcript = fx.transcript([user("hi")])
        payload = send_call(agent_id("0"), "", transcript, notify=True, content="preview")
        assert_allow(run_hook(payload, fx.plugin))


def case_send_other_type():
    with fixture() as fx:
        transcript = fx.transcript([user("hi")])
        agent = agent_id("b")
        fx.meta(transcript, agent, "general-purpose")
        payload = send_call(agent, "hello", transcript)
        assert_allow(run_hook(payload, fx.plugin))


def case_send_message_not_string():
    with fixture() as fx:
        transcript = fx.transcript([user("hi")])
        agent = agent_id("3")
        fx.meta(transcript, agent, "fable-advisor:explorer-h", model="haiku")
        payload = send_call(agent, None, transcript)
        payload["tool_input"]["message"] = {"text": "nope"}
        assert_deny(run_hook(payload, fx.plugin), "message is not a string")


def case_unreadable_profile():
    with fixture() as fx:
        os.remove(os.path.join(fx.plugin, "skills", "orchestration", "routing-profile.md"))
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="haiku")
        assert_deny(run_hook(payload, fx.plugin), "routing profile unreadable")


def case_unparseable_profile():
    with fixture() as fx:
        path = os.path.join(fx.plugin, "skills", "orchestration", "routing-profile.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("no table here\n")
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-h", model="haiku")
        assert_deny(run_hook(payload, fx.plugin), "routing profile unparseable")


def case_unreadable_agent():
    with fixture() as fx:
        line = route("explorer", "mainstay", "haiku-4-5")
        payload = agent_call(prompt_of(line), "fable-advisor:explorer-xh", model="haiku")
        assert_deny(run_hook(payload, fx.plugin), "agent file unreadable")


def case_taskstop():
    with fixture() as fx:
        payload = {"hook_event_name": "PreToolUse", "tool_name": "TaskStop", "tool_input": {}}
        assert_allow(run_hook(payload, fx.plugin))


def case_bad_stdin():
    with fixture() as fx:
        assert_deny(run_hook("not json", fx.plugin), "stdin is not valid JSON")


def case_hooks_json():
    with open(HOOKS_JSON, encoding="utf-8") as handle:
        data = json.load(handle)
    entry = data["hooks"]["PreToolUse"][0]
    assert entry["matcher"] == "Agent|SendMessage", entry
    command = entry["hooks"][0]["command"]
    assert "route-gate.py" in command, command
    assert "Stop" in data["hooks"]
    stop = data["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert "receipt-gate.py" in stop, stop
    assert "route-gate.py" not in stop


CASES = [
    ("1: parse profile shape", case_parse_profile),
    ("2: Agent legal mainstay allows", case_agent_mainstay),
    ("3: Agent legal crux with basis allows", case_agent_crux),
    ("4: Agent missing route denies", case_agent_missing_route),
    ("5: Agent malformed route denies", case_agent_malformed_route),
    ("6: Agent name present denies", case_agent_name),
    ("6b: Agent name empty string denies", case_agent_name_empty),
    ("6c: Agent name null denies", case_agent_name_null),
    ("7: Agent no model denies", case_agent_no_model),
    ("7b: Agent parsed crux route with no model lists legal dials", case_agent_crux_no_model_lists_dials),
    ("8: Agent role mismatch denies", case_agent_role_mismatch),
    ("9: Agent dial mismatch denies", case_agent_dial_mismatch),
    ("10: Agent dial outside the cell denies", case_agent_dial_outside_cell),
    ("11: Agent basis missing at crux denies", case_agent_basis_missing),
    ("12: Agent advisor rescue kind failure denies", case_agent_basis_kind),
    ("13: Agent alias redirect outside the profile denies", case_agent_redirect),
    ("14: Agent family rule derives sonnet-4-5 and denies", case_agent_family),
    ("15: Agent FORCE derives sonnet-5-5 and allows", case_agent_force),
    ("16: Agent same-model legal allows", case_agent_same_model),
    ("16b: Agent same-model skips a trailing synthetic record", case_agent_same_model_skips_synthetic),
    ("16c: Agent same-model model outside the profile denies", case_agent_same_model_not_in_profile),
    ("17: Agent same-model on explorer denies", case_agent_same_model_explorer),
    ("18: Agent same-model other model denies", case_agent_same_model_other),
    ("19: Agent same-model no assistant record denies", case_agent_same_model_no_assistant),
    ("20: Agent non-role-pool subagent_type allows", case_agent_other_type),
    ("21: SendMessage route matches last assistant record allows", case_send_matches_record),
    ("21b: SendMessage skips a trailing synthetic record", case_send_skips_synthetic),
    ("22: SendMessage missing route denies", case_send_missing_route),
    ("23: SendMessage meta.json fallback allows", case_send_meta_fallback),
    ("23b: SendMessage record without effort is a bare dial", case_send_record_without_effort),
    ("23c: SendMessage meta.json without model derives under FORCE", case_send_meta_without_model),
    ("24: SendMessage unknown agentId denies", case_send_unknown_id),
    ("25: SendMessage name target allows", case_send_name),
    ("26: SendMessage main allows", case_send_main),
    ("27: SendMessage subscription allows", case_send_subscription),
    ("28: SendMessage non-role-pool target allows", case_send_other_type),
    ("29: SendMessage non-string message denies", case_send_message_not_string),
    ("30: unreadable profile denies", case_unreadable_profile),
    ("31: unparseable profile denies", case_unparseable_profile),
    ("32: unreadable agent file denies", case_unreadable_agent),
    ("33: TaskStop allows", case_taskstop),
    ("34: unparseable stdin denies", case_bad_stdin),
    ("35: hooks.json PreToolUse matcher", case_hooks_json),
]


def main():
    passed = 0
    failed = 0
    for desc, fn in CASES:
        try:
            fn()
            print("PASS  %s" % desc)
            passed += 1
        except AssertionError as exc:
            print("FAIL  %s — %s" % (desc, exc))
            failed += 1
        except Exception as exc:
            print("FAIL  %s — unexpected %s: %s" % (desc, type(exc).__name__, exc))
            failed += 1
    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
