#!/usr/bin/env python3
"""One-to-one existence: every plugin/**/*.md has a docs/zh/<same relative path> twin."""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugin")
ZH = os.path.join(REPO_ROOT, "docs", "zh")


def collect_md(root):
    rels = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".md"):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                rels.append(rel)
    rels.sort()
    return rels


def main():
    plugin_files = collect_md(PLUGIN)
    zh_files = collect_md(ZH)
    plugin_set = set(plugin_files)
    zh_set = set(zh_files)

    passed = 0
    failed = 0

    for rel in plugin_files:
        twin = os.path.join(ZH, *rel.split("/"))
        if os.path.isfile(twin):
            print("PASS  plugin/%s → docs/zh/%s" % (rel, rel))
            passed += 1
        else:
            print("FAIL  missing twin: docs/zh/%s" % rel)
            failed += 1

    for rel in sorted(zh_set - plugin_set):
        print("FAIL  orphan twin: docs/zh/%s" % rel)
        failed += 1

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
