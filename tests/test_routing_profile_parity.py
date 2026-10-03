#!/usr/bin/env python3
"""Both routing-profile parsers against a hand-written table of the real profile.

The table is a literal: model[e1*, e2] is model[e1] and model[e2], a bare model
is one dial, and each cell is sorted. It is not built by either parser.
Optional argv: a profile path, defaulting to the real profile. The expected
table stays the real profile's table.
"""
import importlib.util
import json
import os
import subprocess
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO_ROOT, "plugin", "hooks", "route-gate.py")
JS = os.path.join(REPO_ROOT, "plugin", "scripts", "routing-profile.mjs")
DEFAULT_PROFILE = os.path.join(
    REPO_ROOT, "plugin", "skills", "orchestration", "routing-profile.md")
ROLES = ("explorer", "worker", "advisor")
TIERS = ("mainstay", "crux", "rescue")

# Hand-written from plugin/skills/orchestration/routing-profile.md.
CLAUDE_CODE = {
    "explorer": {
        "mainstay": [
            "gpt-6-luna[high]",
            "gpt-6-luna[xhigh]",
            "grok-4.7[high]",
            "grok-4.7[medium]",
            "haiku-4-5",
        ],
        "crux": [
            "gpt-6-luna[max]",
            "grok-4.7[xhigh]",
            "sonnet-5-5[high]",
            "sonnet-5-5[medium]",
        ],
        "rescue": [
            "gpt-6.1-sol[high]",
            "gpt-6.1-sol[xhigh]",
            "opus-5-5[high]",
            "opus-5-5[xhigh]",
        ],
    },
    "worker": {
        "mainstay": [
            "gpt-6.1-sol[high]",
            "gpt-6.1-sol[medium]",
            "grok-4.7[high]",
            "grok-4.7[xhigh]",
            "sonnet-5-5[high]",
            "sonnet-5-5[xhigh]",
        ],
        "crux": [
            "gpt-6-astra[low]",
            "gpt-6-astra[medium]",
            "gpt-6.1-sol[max]",
            "gpt-6.1-sol[xhigh]",
            "opus-5-5[high]",
            "opus-5-5[medium]",
        ],
        "rescue": [
            "gpt-6-astra[high]",
            "gpt-6-astra[xhigh]",
            "opus-5-5[xhigh]",
        ],
    },
    "advisor": {
        "mainstay": [
            "fable-5-1[low]",
            "fable-5-1[medium]",
            "gpt-6-astra[low]",
            "gpt-6-astra[medium]",
            "gpt-6.1-sol[high]",
            "gpt-6.1-sol[medium]",
            "opus-5-5[high]",
            "opus-5-5[medium]",
        ],
        "crux": [
            "fable-5-1[high]",
            "gpt-6-astra[high]",
            "gpt-6.1-sol[xhigh]",
            "opus-5-5[xhigh]",
        ],
        "rescue": [
            "fable-5-1[xhigh]",
            "gpt-6-astra[xhigh]",
        ],
    },
}

CURSOR = {
    "explorer": {
        "mainstay": [
            "composer-2.5-fast",
            "gpt-6-luna[high]",
            "gpt-6-luna[xhigh]",
            "grok-4.7[high]",
            "grok-4.7[medium]",
            "haiku-4-5",
        ],
        "crux": [
            "gpt-6-luna[max]",
            "grok-4.7[xhigh]",
            "sonnet-5-5[high]",
            "sonnet-5-5[medium]",
        ],
        "rescue": [
            "gpt-6.1-sol[high]",
            "gpt-6.1-sol[xhigh]",
            "opus-5-5[high]",
            "opus-5-5[xhigh]",
        ],
    },
    "worker": {
        "mainstay": [
            "gpt-6.1-sol[high]",
            "gpt-6.1-sol[medium]",
            "grok-4.7[high]",
            "grok-4.7[xhigh]",
            "sonnet-5-5[high]",
            "sonnet-5-5[xhigh]",
        ],
        "crux": [
            "gpt-6-astra[low]",
            "gpt-6-astra[medium]",
            "gpt-6.1-sol[max]",
            "gpt-6.1-sol[xhigh]",
            "opus-5-5[high]",
            "opus-5-5[medium]",
        ],
        "rescue": [
            "gpt-6-astra[high]",
            "gpt-6-astra[xhigh]",
            "opus-5-5[xhigh]",
        ],
    },
    "advisor": {
        "mainstay": [
            "fable-5-1[low]",
            "fable-5-1[medium]",
            "gpt-6-astra[low]",
            "gpt-6-astra[medium]",
            "gpt-6.1-sol[high]",
            "gpt-6.1-sol[medium]",
            "opus-5-5[high]",
            "opus-5-5[medium]",
        ],
        "crux": [
            "fable-5-1[high]",
            "gpt-6-astra[high]",
            "gpt-6.1-sol[xhigh]",
            "opus-5-5[xhigh]",
        ],
        "rescue": [
            "fable-5-1[xhigh]",
            "gpt-6-astra[xhigh]",
        ],
    },
}


def profile_arg():
    if len(sys.argv) > 2:
        print("usage: test_routing_profile_parity.py [profile-path]", file=sys.stderr)
        sys.exit(2)
    if len(sys.argv) == 2:
        return sys.argv[1]
    return DEFAULT_PROFILE


def capture(fn):
    try:
        return fn(), None
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)


def parse_python(path):
    spec = importlib.util.spec_from_file_location("route_gate_parity", HOOK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    return module.parse_routing_profile(text)


def parse_js(path):
    result = subprocess.run(
        ["node", JS, "--dump", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or "exit %s" % result.returncode)
    return json.loads(result.stdout)


def assert_shape(section, expected, label):
    if not isinstance(section, dict):
        raise AssertionError("%s is not an object" % label)
    if set(section) != set(expected):
        raise AssertionError("%s roles expected %s got %s" % (
            label, sorted(expected), sorted(section)))
    for role in ROLES:
        tiers = section[role]
        if not isinstance(tiers, dict) or set(tiers) != set(TIERS):
            got = sorted(tiers) if isinstance(tiers, dict) else tiers
            raise AssertionError("%s/%s tiers expected %s got %s" % (
                label, role, list(TIERS), got))


def assert_python(table, error):
    if error is not None:
        raise AssertionError(error)
    if not isinstance(table, dict) or "claude_code" not in table:
        raise AssertionError("missing claude_code")
    assert_shape(table["claude_code"], CLAUDE_CODE, "claude_code")


def assert_js(table, error):
    if error is not None:
        raise AssertionError(error)
    if not isinstance(table, dict):
        raise AssertionError("output is not an object")
    for key, expected in (("claude_code", CLAUDE_CODE), ("cursor", CURSOR)):
        if key not in table:
            raise AssertionError("missing %s" % key)
        assert_shape(table[key], expected, key)


def assert_cell(table, error, section, role, tier, expected):
    if error is not None:
        raise AssertionError("parser did not run: %s" % error)
    if not isinstance(table, dict) or not isinstance(table.get(section), dict):
        raise AssertionError("missing %s" % section)
    roles = table[section]
    if role not in roles or not isinstance(roles[role], dict) or tier not in roles[role]:
        raise AssertionError("missing %s/%s" % (role, tier))
    got = roles[role][tier]
    if got != expected:
        raise AssertionError("expected %s got %s" % (expected, got))


def cell_check(table, error, section, role, tier, expected):
    def run():
        assert_cell(table, error, section, role, tier, expected)
    return run


def add_cells(checks, label, table, error, section, expected):
    for role in ROLES:
        for tier in TIERS:
            desc = "%d: %s %s/%s" % (len(checks) + 1, label, role, tier)
            checks.append((
                desc,
                cell_check(table, error, section, role, tier, expected[role][tier]),
            ))


def main():
    path = profile_arg()
    py_table, py_error = capture(lambda: parse_python(path))
    js_table, js_error = capture(lambda: parse_js(path))
    checks = []
    checks.append(("%d: python parser runs" % (len(checks) + 1),
                   lambda: assert_python(py_table, py_error)))
    checks.append(("%d: js parser runs" % (len(checks) + 1),
                   lambda: assert_js(js_table, js_error)))
    add_cells(checks, "python claude_code", py_table, py_error, "claude_code", CLAUDE_CODE)
    add_cells(checks, "js claude_code", js_table, js_error, "claude_code", CLAUDE_CODE)
    add_cells(checks, "js cursor", js_table, js_error, "cursor", CURSOR)

    passed = 0
    failed = 0
    for desc, fn in checks:
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
