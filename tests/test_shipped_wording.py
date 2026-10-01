#!/usr/bin/env python3
"""Shipped text under plugin/** and its docs/zh/** twins: no known remark about
the text itself (AGENTS.md "Wording of shipped text"), and models and dials in
canonical form (AGENTS.md "Canonical notation for the user's declarations")."""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ("plugin", os.path.join("docs", "zh"))
SUFFIXES = (".md", ".json", ".py", ".mjs", ".toml", ".yaml", ".yml", ".sh")
PROFILE = "skills/orchestration/routing-profile.md"
WORDING = 'AGENTS.md "Wording of shipped text"'
NOTATION = 'AGENTS.md "Canonical notation for the user\'s declarations"'

# Each pattern names one known way of talking about the text instead of
# stating a result: what it lists or omits, why it exists, what it replaced,
# and dated or unverified observations.
WORDING_PATTERNS = [
    (r"\b(?:is|are) not listed\b", 0),
    (r"\bnot persisted\b", 0),
    (r"\bthis file carries\b", re.I),
    (r"reason to exist", re.I),
    (r"\breason does not hold\b", re.I),
    (r"\breplaces [\"“]", 0),
    (r"\bretired\b", re.I),
    (r"kept for compatibility", re.I),
    (r", not (?:one|two|three|four)\b", re.I),
    (r"\bwritten against\b", 0),
    (r"\bobserved\b[^\n]{0,30}?\d{4}-\d{2}", re.I),
    (r"\bcurrently\b[^\n]{0,40}?\d{4}-\d{2}", re.I),
    (r"\bis unverified\b", re.I),
    (r"\bdesigned as if\b", re.I),
    (r"\bexample may name\b", re.I),
    (r"\bcurrent (?:Task )?enum\b", 0),
    (r"\bapply as written\b", re.I),
    (r"\bratchet\b", re.I),
    (r"不列[：:]", 0),
    (r"不写进本(?:档案|文件)", 0),
    (r"本文件承载", 0),
    (r"存在的全部理由", 0),
    (r"理由在[^。\n]{0,20}不成立", 0),
    (r"取代[\"“]", 0),
    (r"已退役", 0),
    (r"为兼容保留", 0),
    (r"[一二两三四五][层条个种]，不是[一二两三四五][层条个种]", 0),
    (r"不等于今天不可用|按[^。\n]{0,20}来写", 0),
    (r"\d{4}-\d{2}(?:-\d{2})?\s*观测", 0),
    (r"当前为[^。\n]{0,40}\d{4}-\d{2}", 0),
    (r"未经核实", 0),
    (r"按「[^」]*」来设计", 0),
    (r"可能点名", 0),
    (r"当前 ?`?Task`? ?枚举", 0),
    (r"按原文适用", 0),
    (r"棘轮", 0),
]
WORDING_RES = [(re.compile(p, f), p) for p, f in WORDING_PATTERNS]

EFFORTS = ("low", "medium", "high", "xhigh", "max")
EFFORT = r"(?:%s)\*?" % "|".join(EFFORTS)
# Matches loose dials too (missing comma, missing or extra `*`) so they can be
# rejected; a bracket without effort names is not a dial.
DIAL_RE = re.compile(r"([A-Za-z0-9][A-Za-z0-9.-]*)\[(%s(?:[ ,]+%s)*)\]" % (EFFORT, EFFORT))
LOOSE_RES = [
    re.compile(r"\b(?:haiku|sonnet|opus|fable)[ -]?\d+\.\d+", re.I),
    re.compile(r"\b(?:haiku|sonnet|opus|fable|grok)\d", re.I),
    re.compile(r"(?<![\w.-])(?:6(?:\.\d)?-)?(?:sol|luna|astra)\b(?!-)"),
    re.compile(r"\bGPT-\d+(?:\.\d+)? (?:Luna|Sol|Astra)\b"),
]
ANCHOR_ID_RE = re.compile(r"^[a-z]+(?:-[0-9a-z.]+)+$")


def collect():
    rels = []
    for root in ROOTS:
        base = os.path.join(REPO_ROOT, root)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for name in filenames:
                if name.endswith(SUFFIXES):
                    full = os.path.join(dirpath, name)
                    rels.append(os.path.relpath(full, REPO_ROOT).replace(os.sep, "/"))
    rels.sort()
    return rels


def read_lines(rel):
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as fh:
        return fh.read().splitlines()


def profile_anchors(rel):
    """Backticked ids in the profile's anchor sentence."""
    for line in read_lines(rel):
        match = re.search(r"anchored to (.*?)\.(?:\s|$)|锚定(.*?)。", line)
        if match:
            return re.findall(r"`([^`]+)`", match.group(1) or match.group(2))
    return []


def check_dial(model, efforts, anchors):
    items = [e for e in re.split(r"[ ,]+", efforts) if e]
    problems = []
    if model not in anchors:
        problems.append("model %r is not an anchored id" % model)
    if efforts != ", ".join(items):
        problems.append("efforts must be separated by ', '")
    stars = sum(e.endswith("*") for e in items)
    if len(items) > 1 and stars != 1:
        problems.append("a multi-effort dial needs exactly one '*'")
    if len(items) == 1 and stars:
        problems.append("a single-effort dial takes no '*'")
    return problems


def table_cells(lines):
    """Model cells of the fill tables and the segment table."""
    cells, kind = [], None
    for number, line in enumerate(lines, 1):
        if not line.startswith("|"):
            kind = None
            continue
        parts = [c.strip() for c in line.strip().strip("|").split("|")]
        if kind is None:
            head = parts[0]
            kind = "fill" if head in ("Role", "角色") else "segment" if head in ("Family", "家族") else "other"
            continue
        if set(parts[0]) <= set("-") or kind == "other":
            continue
        row = parts[1:] if kind == "fill" else parts[1:-1]
        for cell in row:
            for candidate in cell.split("›"):
                cells.append((number, candidate.strip()))
    return cells


def main():
    passed = 0
    failed = 0

    def fail(message):
        nonlocal failed
        print("FAIL  " + message)
        failed += 1

    anchors = profile_anchors("plugin/" + PROFILE)
    zh_anchors = profile_anchors("docs/zh/" + PROFILE)
    bad_ids = [a for a in anchors if not ANCHOR_ID_RE.match(a)]
    if not anchors or bad_ids or anchors != zh_anchors:
        fail("profile anchors %r (zh %r) must be canonical ids and equal in both twins — %s"
             % (anchors, zh_anchors, NOTATION))
    else:
        print("PASS  profile anchors: %s" % ", ".join(anchors))
        passed += 1
    anchor_set = set(anchors)

    for rel in ("plugin/" + PROFILE, "docs/zh/" + PROFILE):
        bad = []
        for number, cell in table_cells(read_lines(rel)):
            model = cell.split("[", 1)[0]
            if model != "—" and model not in anchor_set:
                bad.append("%s:%d cell %r" % (rel, number, cell))
        if bad:
            for item in bad:
                fail("%s is not an anchored id — %s" % (item, NOTATION))
        else:
            print("PASS  table cells: %s" % rel)
            passed += 1

    # README.md carries upgrade history, so it gets the notation checks only.
    for rel in collect() + ["README.md"]:
        problems = []
        for number, line in enumerate(read_lines(rel), 1):
            for regex, pattern in WORDING_RES:
                if rel != "README.md" and regex.search(line):
                    problems.append("%s:%d matches %r — %s" % (rel, number, pattern, WORDING))
            for match in DIAL_RE.finditer(line):
                for problem in check_dial(match.group(1), match.group(2), anchor_set):
                    problems.append("%s:%d %r: %s — %s" % (rel, number, match.group(0), problem, NOTATION))
            for regex in LOOSE_RES:
                match = regex.search(line)
                if match:
                    problems.append("%s:%d loose model name %r — %s" % (rel, number, match.group(0), NOTATION))
        if problems:
            for problem in problems:
                fail(problem)
        else:
            print("PASS  %s" % rel)
            passed += 1

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
