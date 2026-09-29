#!/usr/bin/env python3
"""Command-line boundary tests for scripts/install-user-level.py."""
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "scripts", "install-user-level.py")

MANIFEST = [
    (
        os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-pin.mdc"),
        (".cursor", "rules", "fable-lane-pin.mdc"),
    ),
    (
        os.path.join(REPO_ROOT, "cursor-hooks", "fable-lane-family-gate.py"),
        (".cursor", "hooks", "fable-lane-family-gate.py"),
    ),
]


def run_cli(args, env_home, cwd=None):
    env = os.environ.copy()
    env["HOME"] = env_home
    env["USERPROFILE"] = env_home
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
        env=env,
    )


def dest_path(home, parts):
    return os.path.join(home, *parts)


def prefixed(stdout, prefix):
    token = prefix + " "
    return [ln[len(token) :] for ln in stdout.splitlines() if ln.startswith(token)]


def source_bytes(src):
    with open(src, "rb") as fh:
        return fh.read()


def assert_byte_identical(home):
    for src, parts in MANIFEST:
        path = dest_path(home, parts)
        assert os.path.isfile(path), "missing %s" % path
        with open(path, "rb") as fh:
            got = fh.read()
        expected = source_bytes(src)
        assert got == expected, "bytes differ for %s (%d live, %d source)" % (
            path,
            len(got),
            len(expected),
        )


def list_regular_files(root):
    found = set()
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            found.add(os.path.relpath(full, root))
    return found


def assert_exact_files(home, plus=()):
    expected = {os.path.join(*parts) for _src, parts in MANIFEST} | set(plus)
    actual = list_regular_files(home)
    assert actual == expected, "unexpected file set under %s: %r vs expected %r" % (
        home,
        actual,
        expected,
    )


def assert_exact_also(also_dir):
    expected = {os.path.basename(src) for src, _parts in MANIFEST}
    actual = list_regular_files(also_dir)
    assert actual == expected, "unexpected file set under %s: %r vs expected %r" % (
        also_dir,
        actual,
        expected,
    )


def write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def write_hooks(home, command):
    payload = {
        "version": 1,
        "hooks": {
            "preToolUse": [
                {"command": command, "matcher": "Task", "timeout": 10}
            ]
        },
    }
    path = dest_path(home, (".cursor", "hooks.json"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


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

    def fresh_home():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as cwd:
            r = run_cli([], home, cwd=cwd)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            installed = prefixed(r.stdout, "installed")
            assert len(installed) == 2, "expected 2 installed, got %r" % installed
            for src, parts in MANIFEST:
                path = dest_path(home, parts)
                assert any(path in line for line in installed), (
                    "no installed line for %s in %r" % (path, installed)
                )
            assert_byte_identical(home)
            assert_exact_files(home)

    def check_then_overwrite():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as decoy:
            r = run_cli(["--home", home], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            pin = dest_path(home, (".cursor", "rules", "fable-lane-pin.mdc"))
            with open(pin, "wb") as fh:
                fh.write(b"modified live copy\n")
            c = run_cli(["--check", "--home", home], decoy)
            assert c.returncode != 0, "expected non-zero on drift, stdout=%r" % c.stdout
            assert pin in c.stdout, "check did not name %s in %r" % (pin, c.stdout)
            with open(pin, "rb") as fh:
                still = fh.read()
            assert still == b"modified live copy\n", "--check wrote to %s" % pin
            f = run_cli(["--home", home], decoy)
            assert f.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                f.returncode,
                f.stdout,
                f.stderr,
            )
            installed = prefixed(f.stdout, "installed")
            unchanged = prefixed(f.stdout, "unchanged")
            assert len(installed) == 1 and pin in installed[0], installed
            assert len(unchanged) == 1, unchanged
            for parts in (
                (".cursor", "hooks", "fable-lane-family-gate.py"),
            ):
                path = dest_path(home, parts)
                assert any(path in line for line in unchanged), unchanged
            assert_byte_identical(home)
            assert_exact_files(home)

    def also_writes():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as decoy, tempfile.TemporaryDirectory() as also:
            r = run_cli(["--home", home, "--also", also], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            for src, _parts in MANIFEST:
                path = os.path.join(also, os.path.basename(src))
                assert os.path.isfile(path), "missing --also file %s" % path
                with open(path, "rb") as fh:
                    got = fh.read()
                assert got == source_bytes(src), "bytes differ for --also %s" % path
                assert any(
                    ln.startswith("installed ") and path in ln
                    for ln in r.stdout.splitlines()
                ), "no installed line for %s in %r" % (path, r.stdout)
            assert_exact_files(home)
            assert_exact_also(also)

    def hooks_missing_warns():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as decoy:
            r = run_cli(["--home", home], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            warnings = [
                ln for ln in r.stdout.splitlines() if ln.startswith("warning ")
            ]
            assert warnings, "expected a hooks warning, stdout=%r" % r.stdout
            assert any(home in ln for ln in warnings), warnings
            hooks = dest_path(home, (".cursor", "hooks.json"))
            assert not os.path.exists(hooks), "installer created %s" % hooks
            assert_exact_files(home)

    def hooks_without_gate_warns():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as decoy:
            write_hooks(home, "python3 /tmp/unrelated.py")
            r = run_cli(["--home", home], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            warnings = [
                ln for ln in r.stdout.splitlines() if ln.startswith("warning ")
            ]
            assert warnings, "expected a hooks warning, stdout=%r" % r.stdout
            assert any(home in ln for ln in warnings), warnings
            hooks = dest_path(home, (".cursor", "hooks.json"))
            with open(hooks, encoding="utf-8") as fh:
                body = fh.read()
            assert "unrelated.py" in body, "installer modified hooks.json"
            assert_exact_files(home, plus={os.path.join(".cursor", "hooks.json")})

    def hooks_with_gate_silent():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as decoy:
            write_hooks(
                home,
                "python3 %s/.cursor/hooks/fable-lane-family-gate.py" % home,
            )
            r = run_cli(["--home", home], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            warnings = [
                ln for ln in r.stdout.splitlines() if ln.startswith("warning ")
            ]
            assert warnings == [], "unexpected warning lines: %r" % warnings
            c = run_cli(["--check", "--home", home], decoy)
            assert c.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                c.returncode,
                c.stdout,
                c.stderr,
            )
            check_warnings = [
                ln for ln in c.stdout.splitlines() if ln.startswith("warning ")
            ]
            assert check_warnings == [], "unexpected check warnings: %r" % check_warnings
            assert_exact_files(home, plus={os.path.join(".cursor", "hooks.json")})

    def two_homes():
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as decoy:
            r = run_cli(["--home", a, "--home", b], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            for home in (a, b):
                assert_byte_identical(home)
                assert_exact_files(home)
                for src, parts in MANIFEST:
                    path = dest_path(home, parts)
                    assert any(
                        ln.startswith("installed ") and path in ln
                        for ln in r.stdout.splitlines()
                    ), "no installed line for %s in %r" % (path, r.stdout)

    def pre_existing_files_preserved():
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as decoy:
            notes_rel = (".claude", "docs", "notes.md")
            other_rel = (".cursor", "rules", "other.mdc")
            notes = dest_path(home, notes_rel)
            other = dest_path(home, other_rel)
            write_file(notes, b"neutral notes\n")
            write_file(other, b"neutral rule\n")
            neutral_plus = {os.path.join(*notes_rel), os.path.join(*other_rel)}
            r = run_cli(["--home", home], decoy)
            assert r.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                r.returncode,
                r.stdout,
                r.stderr,
            )
            assert not any(
                ln.startswith("removed ") for ln in r.stdout.splitlines()
            ), r.stdout
            for path, data in ((notes, b"neutral notes\n"), (other, b"neutral rule\n")):
                with open(path, "rb") as fh:
                    assert fh.read() == data, "install run modified %s" % path
            assert_exact_files(home, plus=neutral_plus)
            c = run_cli(["--check", "--home", home], decoy)
            assert c.returncode == 0, "exit %s stdout=%r stderr=%r" % (
                c.returncode,
                c.stdout,
                c.stderr,
            )
            assert not any(
                ln.startswith("removed ") for ln in c.stdout.splitlines()
            ), c.stdout
            for path, data in ((notes, b"neutral notes\n"), (other, b"neutral rule\n")):
                with open(path, "rb") as fh:
                    assert fh.read() == data, "--check run modified %s" % path
            assert_exact_files(home, plus=neutral_plus)

    check("fresh home installs two byte-identical files", fresh_home)
    check("modified live copy fails check then is overwritten", check_then_overwrite)
    check("--also writes source basenames", also_writes)
    check("missing hooks.json warns and exits 0", hooks_missing_warns)
    check("hooks.json without gate warns and exits 0", hooks_without_gate_warns)
    check("hooks.json with gate entry has no warning", hooks_with_gate_silent)
    check("two --home directories are both written", two_homes)
    check("pre-existing neutral files survive install and --check", pre_existing_files_preserved)

    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
