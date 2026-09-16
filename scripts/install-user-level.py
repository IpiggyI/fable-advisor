#!/usr/bin/env python3
"""Copy canonical user-level files onto live paths under one or more homes."""
import argparse
import json
import sys
from pathlib import Path

GATE_NAME = "fable-lane-family-gate.py"

MANIFEST = (
    ("docs/agents/fable-advisor-routing.md", ".claude/docs/fable-advisor-routing.md"),
    ("cursor-hooks/fable-lane-pin.mdc", ".cursor/rules/fable-lane-pin.mdc"),
    ("cursor-hooks/fable-lane-family-gate.py", ".cursor/hooks/fable-lane-family-gate.py"),
)

RETIRE = (
    ".claude/rules/fable-advisor.md",
    ".cursor/rules/fable-advisor.mdc",
)


def repo_root():
    return Path(__file__).resolve().parent.parent


def parse_user_path(text):
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def emit(kind, message):
    sys.stdout.write("%s %s\n" % (kind, message))


def pretool_commands(obj):
    found = []

    def visit_pre(value):
        if isinstance(value, dict):
            if "preToolUse" in value:
                visit_cmds(value["preToolUse"])
            for nested in value.values():
                visit_pre(nested)
        elif isinstance(value, list):
            for item in value:
                visit_pre(item)

    def visit_cmds(value):
        if isinstance(value, dict):
            command = value.get("command")
            if isinstance(command, str):
                found.append(command)
            for nested in value.values():
                visit_cmds(nested)
        elif isinstance(value, list):
            for item in value:
                visit_cmds(item)

    visit_pre(obj)
    return found


def gate_present(hooks_path):
    if not hooks_path.is_file():
        return False
    try:
        raw = hooks_path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return False
    return any(GATE_NAME in command for command in pretool_commands(data))


def dest_matches(dest, data):
    if not dest.is_file():
        return False
    try:
        return dest.read_bytes() == data
    except OSError as exc:
        raise IOError("could not read %s: %s" % (dest, exc))


def install_file(dest, data, check_only):
    if dest_matches(dest, data):
        emit("unchanged", dest)
        return False
    if check_only:
        if dest.exists():
            emit("warning", "differs %s" % dest)
        else:
            emit("warning", "missing %s" % dest)
        return True
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    except OSError as exc:
        raise IOError("could not write %s: %s" % (dest, exc))
    emit("installed", dest)
    return False


def process_retire(path, check_only):
    if not path.is_file():
        return
    if check_only:
        emit("warning", "still present %s" % path)
        return
    try:
        path.unlink()
    except OSError as exc:
        raise IOError("could not remove %s: %s" % (path, exc))
    emit("removed", path)


def process_hooks(home):
    if gate_present(home / ".cursor" / "hooks.json"):
        return
    emit(
        "warning",
        "%s: .cursor/hooks.json missing or has no preToolUse command containing %s"
        % (home, GATE_NAME),
    )


def load_source(root, rel):
    src = root / rel
    try:
        if not src.is_file():
            raise IOError("source missing: %s" % src)
        return src, src.read_bytes()
    except OSError as exc:
        raise IOError("could not read %s: %s" % (src, exc))


def process_home(home, sources, check_only):
    drifted = False
    for _src, rel, data in sources:
        dest = home / rel
        if install_file(dest, data, check_only):
            drifted = True
    for rel in RETIRE:
        process_retire(home / rel, check_only)
    process_hooks(home)
    return drifted


def process_also(also_dir, sources, check_only):
    drifted = False
    for src, _rel, data in sources:
        dest = also_dir / src.name
        if install_file(dest, data, check_only):
            drifted = True
    return drifted


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="install-user-level.py",
        description=(
            "Copy canonical user-level files onto live paths under one or more "
            "home directories. Default home is the current user."
        ),
    )
    parser.add_argument(
        "--home",
        metavar="DIR",
        action="append",
        help="home directory to process; repeatable",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare only; write nothing, delete nothing",
    )
    parser.add_argument(
        "--also",
        metavar="DIR",
        help="also write the three English sources into DIR (flat, source basenames)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    root = repo_root()
    try:
        sources = []
        for rel, dest_rel in MANIFEST:
            src, data = load_source(root, rel)
            sources.append((src, dest_rel, data))
        if args.home:
            homes = [parse_user_path(text) for text in args.home]
        else:
            homes = [Path.home()]
        drifted = False
        for home in homes:
            if process_home(home, sources, args.check):
                drifted = True
        if args.also is not None:
            if process_also(parse_user_path(args.also), sources, args.check):
                drifted = True
    except IOError as exc:
        sys.stderr.write("%s\n" % exc)
        return 1
    if args.check and drifted:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
