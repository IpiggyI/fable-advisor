#!/usr/bin/env python3
"""Canonical archives exist, Chinese twins present, live homes match via installer --check."""
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(REPO_ROOT, "scripts", "install-user-level.py")

ENGLISH = [
    os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-pin.mdc"),
    os.path.join(REPO_ROOT, "docs", "agents", "fable-advisor-routing.md"),
]

CHINESE = [
    os.path.join(REPO_ROOT, "cursor-hooks", "zh", "fable-lane-pin.mdc"),
]

# Routing zh is a profile translation, not a pin-rule backup: no 不是活体.
ROUTING_ZH = os.path.join(REPO_ROOT, "docs", "agents", "fable-advisor-routing.zh.md")

HOMES = [
    os.path.expanduser("~"),
    "/mnt/c/Users/Shy",
]


def has_cjk(text):
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


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

    for archive in ENGLISH:
        rel = os.path.relpath(archive, REPO_ROOT)

        def exists(path=archive, name=rel):
            assert os.path.isfile(path), "missing %s" % name

        check("archive exists %s" % rel, exists)

    for zh_path in CHINESE:
        rel = os.path.relpath(zh_path, REPO_ROOT)

        def zh_ok(path=zh_path, name=rel):
            assert os.path.isfile(path), "missing %s" % name
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            assert body.strip(), "%s is empty" % name
            assert has_cjk(body), "%s has no Chinese" % name
            assert "不是活体" in body, "%s missing live-copy disclaimer" % name

        check("chinese twin %s" % rel, zh_ok)

    routing_zh_rel = os.path.relpath(ROUTING_ZH, REPO_ROOT)

    def routing_zh_ok(path=ROUTING_ZH, name=routing_zh_rel):
        assert os.path.isfile(path), "missing %s" % name
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        assert body.strip(), "%s is empty" % name
        assert has_cjk(body), "%s has no Chinese" % name

    check("chinese twin %s" % routing_zh_rel, routing_zh_ok)

    for home in HOMES:
        if not os.path.isdir(home):
            print("SKIP  home missing %s" % home)
            continue

        def drift(path=home):
            result = subprocess.run(
                [sys.executable, INSTALLER, "--check", "--home", path],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            if result.returncode != 0:
                output = result.stdout
                if result.stderr:
                    output += result.stderr
                raise AssertionError("exit %s\n%s" % (result.returncode, output))

        check("install --check %s" % home, drift)

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
