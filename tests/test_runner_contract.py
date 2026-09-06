#!/usr/bin/env python3
"""Offline process-boundary tests for the Codex and Grok runners."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")


def base_spec(**overrides):
    spec = {
        "objective": "exercise the runner contract",
        "files": [],
        "interfaces": "none",
        "constraints": "none",
        "verification": ["true"],
    }
    spec.update(overrides)
    return spec


def copy_runner(tmp, name, *, preamble=True):
    plugin = Path(tmp) / "plugin"
    scripts = plugin / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "plugin" / "scripts" / name, scripts / name)
    if preamble:
        preamble_path = plugin / "skills" / "orchestration" / "lane-preamble.md"
        preamble_path.parent.mkdir(parents=True, exist_ok=True)
        preamble_path.write_text("STUB LANE PREAMBLE", encoding="utf-8")
    return scripts / name


def write_executable(directory, name, contents):
    path = Path(directory) / name
    path.write_text(contents, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def run_runner(runner, cwd, spec, path_dir, env_extra=None, *, pending=False):
    spec_path = (
        Path(cwd) / ".fable-advisor" / "pending" / "job.json"
        if pending
        else Path(cwd) / "job.json"
    )
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join((str(path_dir), str(Path(sys.executable).parent)))
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        [NODE, str(runner), "--spec", str(spec_path), "--cwd", str(cwd)],
        capture_output=True,
        text=True,
        env=env,
    )
    receipt = None
    if result.stdout.strip():
        receipt = json.loads(result.stdout)
    return result, receipt


def fake_git(directory, exit_code=0):
    write_executable(
        directory,
        "git",
        "#!/bin/sh\nexit %d\n" % exit_code,
    )


def fake_codex(directory):
    write_executable(
        directory,
        "codex",
        """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["CALL_LOG"], "a", encoding="utf-8") as handle:
    handle.write(json.dumps(args) + "\\n")
if args == ["--version"]:
    raise SystemExit(0)
mode = os.environ.get("CODEX_MODE", "success")
model = args[args.index("--model") + 1]
if mode == "fail_before_session":
    raise SystemExit(1)
if mode == "second_preparation":
    if model == "gpt-6-astra":
        raise SystemExit(1)
    raise SystemExit(0)
prompt = sys.stdin.read()
if prompt:
    with open(os.environ["PROMPT_LOG"], "w", encoding="utf-8") as handle:
        handle.write(prompt)
print(json.dumps({"type": "thread.started", "thread_id": "fresh-session"}))
if mode == "fail_after_session":
    raise SystemExit(1)
if mode == "multi_terminal":
    import time
    print(json.dumps({"type": "turn.completed"}), flush=True)
    time.sleep(0.12)
    print(json.dumps({"type": "turn.completed"}), flush=True)
    time.sleep(0.02)
else:
    print(json.dumps({"type": "turn.completed"}))
""",
    )


def fake_grok(directory):
    write_executable(
        directory,
        "grok",
        """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["CALL_LOG"], "a", encoding="utf-8") as handle:
    handle.write(json.dumps(args) + "\\n")
if args == ["models"]:
    print("Default model: grok-test")
    print("* grok-test (default)")
    raise SystemExit(0)
prompt_path = args[args.index("--prompt-file") + 1]
with open(prompt_path, encoding="utf-8") as source:
    prompt = source.read()
with open(os.environ["PROMPT_LOG"], "w", encoding="utf-8") as handle:
    handle.write(prompt)
session_id = args[args.index("--resume") + 1] if "--resume" in args else args[args.index("--session-id") + 1]
reported_id = os.environ.get("GROK_REPORTED_SESSION", session_id)
print(json.dumps({"type": "end", "sessionId": reported_id, "stopReason": "done"}))
""",
    )


def case_schema_defaults_and_validation():
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir()
        codex = copy_runner(tmp, "run-codex.mjs")
        cwd = Path(tmp) / "work"
        cwd.mkdir()

        _, astra = run_runner(codex, cwd, base_spec(), bin_dir)
        assert astra["error_class"] == "codex_unavailable"
        assert (astra["model_requested"], astra["model_used"], astra["effort"]) == (
            "gpt-6-astra", "gpt-6-astra", "medium",
        )

        _, luna = run_runner(codex, cwd, base_spec(model="gpt-5.6-luna"), bin_dir)
        assert luna["effort"] == "max"

        _, sol = run_runner(codex, cwd, base_spec(model="gpt-5.6-sol"), bin_dir)
        assert sol["error_class"] == "spec_invalid"

        _, terra = run_runner(codex, cwd, base_spec(model="gpt-5.6-terra"), bin_dir)
        assert terra["error_class"] == "spec_invalid"

        _, unknown = run_runner(codex, cwd, base_spec(surprise=True), bin_dir)
        assert unknown["error_class"] == "spec_invalid"

        _, empty_resume = run_runner(
            codex, cwd, base_spec(resume_session_id=""), bin_dir,
        )
        assert empty_resume["error_class"] == "spec_invalid"

        _, bad_resume = run_runner(
            codex, cwd, base_spec(resume_session_id=7), bin_dir,
        )
        assert bad_resume["error_class"] == "spec_invalid"

        grok = copy_runner(tmp, "run-grok.mjs")
        _, bad_grok_resume = run_runner(
            grok, cwd, base_spec(resume_session_id=[]), bin_dir,
        )
        assert bad_grok_resume["error_class"] == "spec_invalid"
        print(
            "ASSERT schema: terra=spec_invalid unknown_key=spec_invalid "
            "empty_resume=spec_invalid"
        )


def case_preamble_missing_is_spawn_free():
    for name, binary in (("run-codex.mjs", "codex"), ("run-grok.mjs", "grok")):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            marker = Path(tmp) / "spawned"
            write_executable(
                bin_dir,
                binary,
                "#!/bin/sh\ntouch '%s'\n" % marker,
            )
            runner = copy_runner(tmp, name, preamble=False)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            result, receipt = run_runner(runner, cwd, base_spec(), bin_dir)
            assert result.returncode != 0 and receipt is None
            assert "lane-preamble.md" in result.stderr
            assert not marker.exists()
            assert not (cwd / ".fable-advisor" / "receipts").exists()


def case_unavailable_receipt_fields():
    for name, error_class in (
        ("run-codex.mjs", "codex_unavailable"),
        ("run-grok.mjs", "grok_unavailable"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            runner = copy_runner(tmp, name)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            _, receipt = run_runner(runner, cwd, base_spec(), bin_dir)
            assert receipt["error_class"] == error_class
            expected_model = "gpt-6-astra" if "codex" in name else None
            assert receipt["model_requested"] == expected_model
            assert receipt["model_used"] == expected_model
            assert receipt["fallback_reason"] is None
            assert receipt["resumed_from"] is None
            assert receipt["end_to_close_ms"] is None


def case_no_diff_and_git_status_failed():
    for name, make_binary in (
        ("run-codex.mjs", fake_codex),
        ("run-grok.mjs", fake_grok),
    ):
        for git_exit, expected in ((0, "no_diff"), (1, "git_status_failed")):
            with tempfile.TemporaryDirectory() as tmp:
                bin_dir = Path(tmp) / "bin"
                bin_dir.mkdir()
                make_binary(bin_dir)
                fake_git(bin_dir, git_exit)
                runner = copy_runner(tmp, name)
                cwd = Path(tmp) / "work"
                cwd.mkdir()
                env = {
                    "CALL_LOG": str(Path(tmp) / "calls"),
                    "PROMPT_LOG": str(Path(tmp) / "prompt"),
                }
                _, receipt = run_runner(
                    runner,
                    cwd,
                    base_spec(files=["owned.txt"]),
                    bin_dir,
                    env,
                    pending=git_exit == 0,
                )
                assert receipt["error_class"] == expected
                assert isinstance(receipt["end_to_close_ms"], int)
                if expected == "no_diff":
                    assert (
                        cwd / ".fable-advisor" / "pending" / "job.json"
                    ).is_file()
                    print("ASSERT no_diff: pending_spec=preserved runner=%s" % name)


def case_resume_invocations_and_preamble():
    for name, make_binary, session_key in (
        ("run-codex.mjs", fake_codex, "codex_session_id"),
        ("run-grok.mjs", fake_grok, "grok_session_id"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            make_binary(bin_dir)
            fake_git(bin_dir)
            runner = copy_runner(tmp, name)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            call_log = Path(tmp) / "calls"
            prompt_log = Path(tmp) / "prompt"
            env = {"CALL_LOG": str(call_log), "PROMPT_LOG": str(prompt_log)}
            if "grok" in name:
                env["GROK_REPORTED_SESSION"] = "different-session"
            result, receipt = run_runner(
                runner,
                cwd,
                base_spec(resume_session_id="resume-123"),
                bin_dir,
                env,
            )
            calls = [json.loads(line) for line in call_log.read_text().splitlines()]
            execution = calls[-1]
            assert receipt["error_class"] == "complete"
            assert receipt[session_key] == "resume-123"
            assert receipt["resumed_from"] == "resume-123"
            if "codex" in name:
                assert execution[:2] == ["exec", "resume"]
                assert "resume-123" in execution
                assert "--sandbox" not in execution and "--cd" not in execution
            else:
                assert "--resume" in execution and "--session-id" not in execution
                assert "session id mismatch" in result.stderr
            assert prompt_log.read_text().startswith(
                "STUB LANE PREAMBLE\n\n[fable-advisor]"
            )
            print(
                "ASSERT resume: runner=%s argv_id=resume-123 receipt_id=resume-123"
                % name
            )


def case_codex_single_hop_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir()
        fake_codex(bin_dir)
        fake_git(bin_dir)
        runner = copy_runner(tmp, "run-codex.mjs")
        cwd = Path(tmp) / "work"
        cwd.mkdir()
        call_log = Path(tmp) / "calls"
        _, receipt = run_runner(
            runner,
            cwd,
            base_spec(),
            bin_dir,
            {
                "CALL_LOG": str(call_log),
                "PROMPT_LOG": str(Path(tmp) / "prompt"),
                "CODEX_MODE": "fail_before_session",
            },
        )
        calls = [json.loads(line) for line in call_log.read_text().splitlines()]
        attempts = [args for args in calls if args != ["--version"]]
        assert len(attempts) == 2
        assert receipt["model_requested"] == "gpt-6-astra"
        assert receipt["model_used"] == "gpt-5.6-luna"
        assert receipt["model"] == "gpt-5.6-luna"
        assert receipt["effort"] == "max"
        assert receipt["fallback_reason"] == "codex_failed"
        assert receipt["error_class"] == "codex_failed"
        print(
            "ASSERT fallback: model_used=gpt-5.6-luna "
            "fallback_reason=codex_failed attempts=2 second_error=codex_failed"
        )


def run_codex_mode(tmp, spec, mode):
    bin_dir = Path(tmp) / "bin"
    bin_dir.mkdir()
    fake_codex(bin_dir)
    fake_git(bin_dir)
    runner = copy_runner(tmp, "run-codex.mjs")
    cwd = Path(tmp) / "work"
    cwd.mkdir()
    call_log = Path(tmp) / "calls"
    _, receipt = run_runner(
        runner,
        cwd,
        spec,
        bin_dir,
        {
            "CALL_LOG": str(call_log),
            "PROMPT_LOG": str(Path(tmp) / "prompt"),
            "CODEX_MODE": mode,
        },
    )
    calls = [json.loads(line) for line in call_log.read_text().splitlines()]
    attempts = [args for args in calls if args != ["--version"]]
    return receipt, attempts


def case_codex_fallback_boundaries():
    with tempfile.TemporaryDirectory() as tmp:
        receipt, attempts = run_codex_mode(
            tmp,
            base_spec(model="gpt-5.6-luna"),
            "fail_before_session",
        )
        assert len(attempts) == 1
        assert receipt["model_used"] == "gpt-5.6-luna"
        assert receipt["fallback_reason"] is None

    with tempfile.TemporaryDirectory() as tmp:
        receipt, attempts = run_codex_mode(
            tmp,
            base_spec(),
            "fail_after_session",
        )
        assert len(attempts) == 1
        assert receipt["codex_session_id"] == "fresh-session"
        assert receipt["fallback_reason"] is None

    with tempfile.TemporaryDirectory() as tmp:
        receipt, attempts = run_codex_mode(
            tmp,
            base_spec(),
            "second_preparation",
        )
        assert len(attempts) == 2
        assert receipt["fallback_reason"] == "codex_failed"
        assert receipt["error_class"] == "preparation_stalled"
        print(
            "ASSERT fallback boundaries: direct_luna=1 "
            "session_established=1 second_error=preparation_stalled"
        )


def case_last_terminal_event_drives_timing():
    with tempfile.TemporaryDirectory() as tmp:
        receipt, attempts = run_codex_mode(tmp, base_spec(), "multi_terminal")
        assert len(attempts) == 1
        assert receipt["error_class"] == "complete"
        assert 0 <= receipt["end_to_close_ms"] < 80
        print(
            "ASSERT terminal timing: last turn.completed used; "
            "end_to_close_ms=%d" % receipt["end_to_close_ms"]
        )


CASES = [
    ("schema defaults and validation", case_schema_defaults_and_validation),
    ("missing preamble is spawn-free", case_preamble_missing_is_spawn_free),
    ("unavailable receipt fields", case_unavailable_receipt_fields),
    ("no_diff and git_status_failed", case_no_diff_and_git_status_failed),
    ("resume invocations and preamble", case_resume_invocations_and_preamble),
    ("codex single-hop fallback", case_codex_single_hop_fallback),
    ("codex fallback boundaries", case_codex_fallback_boundaries),
    ("last terminal event drives timing", case_last_terminal_event_drives_timing),
]


def main():
    failed = 0
    for description, case in CASES:
        try:
            case()
            print("PASS  %s" % description)
        except Exception as error:
            failed += 1
            print("FAIL  %s — %s: %s" % (description, type(error).__name__, error))
    print("%d/%d passed, %d failed" % (len(CASES) - failed, len(CASES), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
