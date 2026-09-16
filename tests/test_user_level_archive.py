#!/usr/bin/env python3
"""Pin-rule and routing-profile archive: English byte-identical to live copies, Chinese twins present."""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROMPTS_RULES = "/mnt/d/Development/Local/prompts/current-prompts/rules"

ENGLISH = [
    (
        os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-pin.mdc"),
        [
            os.path.expanduser("~/.cursor/rules/fable-lane-pin.mdc"),
            "/mnt/c/Users/Shy/.cursor/rules/fable-lane-pin.mdc",
            os.path.join(PROMPTS_RULES, "fable-lane-pin.cursor.mdc"),
        ],
    ),
    (
        os.path.join(REPO_ROOT, "docs", "agents", "fable-advisor-routing.md"),
        [
            os.path.expanduser("~/.claude/docs/fable-advisor-routing.md"),
            "/mnt/c/Users/Shy/.claude/docs/fable-advisor-routing.md",
            "/mnt/d/Development/Local/prompts/current-prompts/docs/fable-advisor-routing.md",
        ],
    ),
]

CHINESE = [
    os.path.join(REPO_ROOT, "cursor-hooks", "zh", "fable-lane-pin.mdc"),
]

# Routing zh is a profile translation, not a pin-rule backup: no 不是活体.
ROUTING_ZH = os.path.join(REPO_ROOT, "docs", "agents", "fable-advisor-routing.zh.md")


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

    routing_zh_rel = os.path.relpath(ROUTING_ZH, REPO_ROOT)

    def routing_zh_ok(path=ROUTING_ZH, name=routing_zh_rel):
        assert os.path.isfile(path), "missing %s" % name
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        assert body.strip(), "%s is empty" % name
        assert has_cjk(body), "%s has no Chinese" % name

    check("chinese twin %s" % routing_zh_rel, routing_zh_ok)

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
