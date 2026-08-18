#!/usr/bin/env python3
"""Regression tests for cursor-hooks/fable-lane-family-gate.py."""
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-family-gate.py")

LIVE_COPIES = [
    os.path.expanduser("~/.cursor/hooks/fable-lane-family-gate.py"),
    "/mnt/c/Users/Shy/.cursor/hooks/fable-lane-family-gate.py",
]


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

    with open(HOOK, "rb") as fh:
        archived = fh.read()

    seen = 0
    for live in LIVE_COPIES:
        if not os.path.isfile(live):
            continue
        if os.path.samefile(live, HOOK):
            continue
        seen += 1

        def drift(path=live):
            with open(path, "rb") as fh:
                body = fh.read()
            assert body == archived, "drift vs %s (%d bytes live, %d bytes archive)" % (
                path,
                len(body),
                len(archived),
            )

        check("matches live %s" % live, drift)

    if seen == 0:
        print("SKIP  no live copies present")

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
