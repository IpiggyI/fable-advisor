#!/usr/bin/env python3
"""User-level live-copy archive: English byte-identical to live, Chinese twins present."""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_RULES = os.path.join(REPO_ROOT, "user-rules")
USER_RULES_ZH = os.path.join(USER_RULES, "zh")

ENGLISH = [
    (
        os.path.join(USER_RULES, "claude-fable-advisor.md"),
        [
            os.path.expanduser("~/.claude/rules/fable-advisor.md"),
            "/mnt/c/Users/Shy/.claude/rules/fable-advisor.md",
        ],
    ),
    (
        os.path.join(USER_RULES, "cursor-fable-advisor.mdc"),
        [
            os.path.expanduser("~/.cursor/rules/fable-advisor.mdc"),
            "/mnt/c/Users/Shy/.cursor/rules/fable-advisor.mdc",
        ],
    ),
]

CHINESE = [
    os.path.join(USER_RULES_ZH, "claude-fable-advisor.md"),
    os.path.join(USER_RULES_ZH, "cursor-fable-advisor.mdc"),
    os.path.join(USER_RULES_ZH, "fable-lane-pin.mdc"),
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

    for archive, _lives in ENGLISH:
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

    seen = 0
    for archive, lives in ENGLISH:
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
        print("SKIP  no live fill-table copies present")

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
