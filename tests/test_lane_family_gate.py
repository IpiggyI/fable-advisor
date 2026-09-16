#!/usr/bin/env python3
"""Process-boundary tests for the Cursor Task pin gate plus live-archive drift."""
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-family-gate.py")

LIVE_ARTIFACTS = [
    (
        HOOK,
        [
            os.path.expanduser("~/.cursor/hooks/fable-lane-family-gate.py"),
            "/mnt/c/Users/Shy/.cursor/hooks/fable-lane-family-gate.py",
        ],
    ),
    (
        os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-pin.mdc"),
        [
            os.path.expanduser("~/.cursor/rules/fable-lane-pin.mdc"),
            "/mnt/c/Users/Shy/.cursor/rules/fable-lane-pin.mdc",
        ],
    ),
]


def _task(tool_input):
    return json.dumps({"tool_name": "Task", "tool_input": tool_input}).encode("utf-8")


def run_hook(raw):
    result = subprocess.run(
        [sys.executable, HOOK],
        input=raw,
        capture_output=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, "exit %s stdout=%r stderr=%r" % (
        result.returncode,
        result.stdout,
        result.stderr,
    )
    return json.loads(result.stdout)


def assert_permission(raw, expected):
    out = run_hook(raw)
    got = out.get("permission")
    assert got == expected, "permission %r expected %r out=%r" % (got, expected, out)
    return out


def assert_omit_deny(out):
    joined = "%s %s" % (out.get("agent_message") or "", out.get("user_message") or "")
    lower = joined.lower()
    assert "explicit" in lower, "deny missing explicit: %r" % joined
    assert "non-inherit" in lower, "deny missing non-inherit: %r" % joined
    assert "family" not in lower, "deny still mentions family: %r" % joined


def main():
    passed = 0
    failed = 0

    def check(desc, fn):
        nonlocal passed, failed
        try:
            fn()
            print("PASS  %s" % desc)
            passed += 1
        except AssertionError as e:
            print("FAIL  %s — %s" % (desc, e))
            failed += 1
        except Exception as e:
            print("FAIL  %s — unexpected %s: %s" % (desc, type(e).__name__, e))
            failed += 1

    def self_test():
        result = subprocess.run(
            [sys.executable, HOOK, "--self-test"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "exit %s stdout=%r stderr=%r" % (
            result.returncode,
            result.stdout,
            result.stderr,
        )

    check("--self-test", self_test)

    def advisor_missing_model():
        out = assert_permission(_task({"subagent_type": "advisor-h"}), "deny")
        assert_omit_deny(out)

    def advisor_inherit():
        out = assert_permission(
            _task({"subagent_type": "advisor-l", "model": "inherit"}), "deny"
        )
        assert_omit_deny(out)

    def advisor_empty_model():
        out = assert_permission(
            _task({"subagent_type": "advisor-md", "model": ""}), "deny"
        )
        assert_omit_deny(out)

    def advisor_non_fable_explicit():
        assert_permission(
            _task(
                {
                    "subagent_type": "advisor-xh",
                    "model": "cursor-grok-4.6-xhigh",
                }
            ),
            "allow",
        )

    def advisor_fable_explicit():
        assert_permission(
            _task(
                {
                    "subagent_type": "advisor-h",
                    "model": "claude-fable-5-1-thinking-high",
                }
            ),
            "allow",
        )

    def advisor_resume_skips_pin():
        assert_permission(
            _task({"subagent_type": "advisor-h", "resume": "abc"}), "allow"
        )

    def worker_not_gated():
        assert_permission(_task({"subagent_type": "worker-h"}), "allow")
        assert_permission(
            _task({"subagent_type": "worker-md", "model": "inherit"}), "allow"
        )

    def unknown_advisor_dial():
        # The gate matches the advisor prefix, so a dial added after this test
        # was written is guarded without touching the hook.
        out = assert_permission(
            _task({"subagent_type": "advisor-future", "model": "inherit"}), "deny"
        )
        assert_omit_deny(out)

    def general_purpose_omitted():
        assert_permission(_task({"subagent_type": "generalPurpose"}), "allow")

    def general_purpose_inherit():
        assert_permission(
            _task({"subagent_type": "generalPurpose", "model": "inherit"}), "allow"
        )

    def explore_omitted():
        assert_permission(_task({"subagent_type": "explore"}), "allow")

    def empty_stdin():
        assert_permission(b"", "deny")

    def parent_envelope_model_ignored():
        raw = json.dumps(
            {
                "tool_name": "Task",
                "hook_event_name": "preToolUse",
                "model": "cursor-grok-4.6-xhigh",
                "tool_input": {"subagent_type": "advisor-h"},
            }
        ).encode("utf-8")
        out = assert_permission(raw, "deny")
        assert_omit_deny(out)

    check("advisor-h missing model denies", advisor_missing_model)
    check("advisor-l inherit denies", advisor_inherit)
    check("advisor-md empty model denies", advisor_empty_model)
    check("advisor-xh non-Fable explicit model allows", advisor_non_fable_explicit)
    check("advisor-h Fable explicit model allows", advisor_fable_explicit)
    check("advisor-h resume skips pin", advisor_resume_skips_pin)
    check("worker dial is out of the gate's scope", worker_not_gated)
    check("unknown advisor dial still denies", unknown_advisor_dial)
    check("generalPurpose omitted model allows", general_purpose_omitted)
    check("generalPurpose inherit allows", general_purpose_inherit)
    check("explore omitted model allows", explore_omitted)
    check("empty stdin denies", empty_stdin)
    check("envelope parent model is not the child pin", parent_envelope_model_ignored)

    seen = 0
    for archive, lives in LIVE_ARTIFACTS:
        with open(archive, "rb") as fh:
            archived = fh.read()
        for live in lives:
            if not os.path.isfile(live):
                continue
            if os.path.samefile(live, archive):
                continue
            seen += 1

            def drift(path=live, expected=archived):
                with open(path, "rb") as fh:
                    body = fh.read()
                assert body == expected, "drift vs %s (%d bytes live, %d bytes archive)" % (
                    path,
                    len(body),
                    len(expected),
                )

            check("matches live %s" % live, drift)

    if seen == 0:
        print("SKIP  no live copies present")

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
