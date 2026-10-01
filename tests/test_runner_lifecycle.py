#!/usr/bin/env python3
"""Offline regressions for inherited pipes after a lane process exits."""
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from test_runner_contract import (
    base_spec, copy_runner, fake_git, process_is_running, run_runner,
    write_executable,
)


def case_inherited_pipes(binary, mode="inherited"):
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir()
        fake_git(bin_dir)
        write_executable(bin_dir, binary, '''#!/usr/bin/env python3
import json, os, signal, subprocess, sys, time
from pathlib import Path
args = sys.argv[1:]
if args == ["--version"]:
    raise SystemExit(0)
if args == ["models"]:
    print("* grok-test (default)")
    raise SystemExit(0)
codex = "exec" in args
if codex:
    sys.stdin.read()
mode = os.environ["PIPE_MODE"]
late = ({"type": "item.completed", "item": {"type": "agent_message", "text": "tail report"}}
        if codex else {"type": "text", "data": "tail report"})
child_code = ("import time; time.sleep(0.2); print(%r, flush=True)" % json.dumps(late)
              if mode == "drain" else "import time; time.sleep(60)")
descendant = subprocess.Popen(
    [sys.executable, "-c", child_code],
    stdin=subprocess.DEVNULL, start_new_session=True,
    **({"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
       if os.environ["PIPE_MODE"] == "redirected" else {}),
)
Path(os.environ["PIDS"]).write_text(json.dumps([os.getpid(), descendant.pid]))
if mode == "kill_failed":
    time.sleep(60)
    raise SystemExit(0)
if codex:
    print(json.dumps({"type": "thread.started", "thread_id": "pipe-session"}))
    print(json.dumps({"type": "turn.completed"}))
else:
    print(json.dumps({"type": "end", "stopReason": "done"}))
sys.stdout.flush()
if mode == "interrupt":
    os.kill(os.getppid(), signal.SIGTERM)
if mode in ("timeout", "idle", "interrupt"):
    time.sleep(60)
raise SystemExit(7 if mode == "nonzero" else 0)
''')
        runner = copy_runner(tmp, "run-%s.mjs" % binary)
        env_extra = {"PIDS": str(Path(tmp) / "pids.json"), "PIPE_MODE": mode}
        if mode == "kill_failed":
            preload = Path(tmp) / "kill-failed.cjs"
            preload.write_text("process.kill = () => true;\n", encoding="utf-8")
            env_extra["NODE_OPTIONS"] = "--require=" + str(preload)
            timer = "SESSION_TIMEOUT_MS" if binary == "codex" else "PREPARATION_TIMEOUT_MS"
            runner.write_text(runner.read_text().replace(
                "const %s = 30_000;" % timer, "const %s = 100;" % timer,
            ))
        cwd = Path(tmp) / "work"
        cwd.mkdir()
        pids_path = Path(tmp) / "pids.json"
        try:
            started = time.monotonic()
            result, receipt = run_runner(
                runner, cwd,
                base_spec(
                    model=("gpt-6-astra" if mode == "kill_failed" else "gpt-6-luna")
                    if binary == "codex" else "grok-test",
                    **({"timeout_sec": 0.3} if mode == "timeout" else {}),
                    **({"idle_timeout_sec": 0.3} if mode == "idle" else {}),
                    **({"timeout_sec": 0.5, "idle_timeout_sec": 0.3}
                       if mode in ("inherited", "nonzero") else {}),
                    **({"mode": "report", "verification": []} if mode == "drain" else
                       {"verification": ["echo verified"]}),
                ),
                bin_dir, env_extra,
                pending=True, timeout=6,
            )
            elapsed = time.monotonic() - started
            expected = {
                "timeout": "timeout", "idle": "idle_timeout", "interrupt": "interrupted",
                "nonzero": binary + "_failed", "kill_failed": "preparation_stalled",
            }.get(mode, "complete")
            assert (result.returncode == 0) == (expected == "complete"), (result.stderr, receipt)
            assert receipt["error_class"] == expected, receipt
            if binary == "codex":
                assert receipt["model_used"] == (
                    "gpt-6-astra" if mode == "kill_failed" else "gpt-6-luna"
                ), receipt
            if mode == "nonzero":
                assert receipt["exit_status"] == 7, receipt
            elif expected == "complete":
                assert receipt["exit_status"] == 0, receipt
            if mode in ("timeout", "idle", "interrupt", "kill_failed"):
                assert receipt["verification"] == [], receipt
                assert receipt["fallback_reason"] is None, receipt
            if mode == "drain":
                assert receipt["report"] == "tail report", receipt
                assert receipt["end_to_close_ms"] >= 150, receipt
            elif mode != "redirected":
                assert receipt["end_to_close_ms"] is None, receipt
                assert "cleanup deadline reached" in result.stderr, result.stderr
            assert elapsed < 5, elapsed
            parent, descendant = json.loads(pids_path.read_text())
            assert process_is_running(parent) == (mode == "kill_failed"), parent
            assert process_is_running(descendant) == (mode != "drain"), descendant
            assert (cwd / ".fable-advisor/pending/job.json").exists() == (expected != "complete")
            receipts = list((cwd / ".fable-advisor/receipts").glob("*.json"))
            assert len(receipts) == 1 and json.loads(receipts[0].read_text()) == receipt
            assert list((cwd / ".fable-advisor/running").glob("*")) == []
            print("PASS pipes: %s %s completed in %.2fs" % (
                binary, mode, elapsed,
            ))
        except subprocess.TimeoutExpired:
            parent, descendant = json.loads(pids_path.read_text())
            print("OBSERVED %s %s: parent_alive=%s descendant_alive=%s" % (
                binary, mode, process_is_running(parent), process_is_running(descendant),
            ))
            raise
        finally:
            if pids_path.exists():
                for pid in json.loads(pids_path.read_text()):
                    if process_is_running(pid):
                        os.kill(pid, signal.SIGKILL)


def case_auxiliary_pipes(binary, stage):
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir()
        fixture = '''#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
name = Path(sys.argv[0]).name
preflight = sys.argv[1:] in (["--version"], ["models"])
if (os.environ["STAGE"] == "preflight" and preflight) or name == os.environ["STAGE"]:
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdin=subprocess.DEVNULL, start_new_session=True,
    )
    with open(os.environ["PIDS"], "a") as handle:
        handle.write(str(child.pid) + "\\n")
if preflight:
    print("* grok-test (default)")
elif name == "verify":
    print("verification output")
    raise SystemExit(17)
elif name == "codex":
    sys.stdin.read()
    print(json.dumps({"type": "thread.started", "thread_id": "aux-session"}))
    print(json.dumps({"type": "turn.completed"}))
elif name == "grok":
    print(json.dumps({"type": "end", "stopReason": "done"}))
'''
        for name in (binary, "git", "verify"):
            write_executable(bin_dir, name, fixture)
        runner = copy_runner(tmp, "run-%s.mjs" % binary)
        cwd = Path(tmp) / "work"
        cwd.mkdir()
        pids_path = Path(tmp) / "pids"
        try:
            result, receipt = run_runner(
                runner, cwd,
                base_spec(verification=["verify"] if stage == "verify" else ["true"]),
                bin_dir, {"PIDS": str(pids_path), "STAGE": stage},
                pending=True, timeout=8,
            )
            expected = "verification_failed" if stage == "verify" else "complete"
            assert receipt["error_class"] == expected, (receipt, result.stderr)
            assert (result.returncode == 0) == (expected == "complete")
            assert "cleanup deadline reached" in result.stderr, result.stderr
            if stage == "verify":
                assert receipt["verification"][0]["exit_code"] == 17, receipt
                assert "verification output" in receipt["verification"][0]["output_tail"]
            assert pids_path.exists()
            assert all(process_is_running(int(pid)) for pid in pids_path.read_text().split())
            print("PASS auxiliary pipes: %s %s" % (binary, stage))
        finally:
            if pids_path.exists():
                for pid in map(int, pids_path.read_text().split()):
                    if process_is_running(pid):
                        os.kill(pid, signal.SIGKILL)


def main():
    failed = 0
    for binary in ("codex", "grok"):
        for mode in ("redirected", "inherited", "nonzero", "drain", "timeout", "idle",
                     "interrupt", "kill_failed"):
            try:
                case_inherited_pipes(binary, mode)
            except Exception as error:
                failed += 1
                print("FAIL pipes: %s %s: %s: %s" % (
                    binary, mode, type(error).__name__, error,
                ))
        for stage in ("preflight", "git", "verify"):
            try:
                case_auxiliary_pipes(binary, stage)
            except Exception as error:
                failed += 1
                print("FAIL auxiliary pipes: %s %s: %s: %s" % (
                    binary, stage, type(error).__name__, error,
                ))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
