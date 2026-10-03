#!/usr/bin/env python3
"""Offline process-boundary tests for the Codex and Grok runners."""
import hashlib
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")


def base_spec(**overrides):
    spec = {
        "role": "explorer" if overrides.get("mode") == "report" else "worker",
        "tier": "mainstay",
        "objective": "exercise the runner contract",
        "files": [],
        "interfaces": "none",
        "constraints": "none",
        "verification": ["true"],
    }
    spec.update(overrides)
    return spec


def fixture_profile():
    cell = "gpt-6-astra[low*, medium, high, xhigh] › gpt-6-luna[high, xhigh*, max] › gpt-6.1-sol[medium, high*, xhigh, max] › grok-test[low, medium, high*, xhigh]"
    table = "| Role | `mainstay` | `crux` | `rescue` |\n|---|---|---|---|\n"
    table += "".join("| %s | %s | %s | %s |\n" % (role, cell, cell, cell)
                     for role in ("explorer", "worker", "advisor"))
    return "## Tiers and choosing inside a cell\n\n" + table + "\n## Cursor candidates\n\n" + table


def prepare_grok_spec(spec):
    spec.setdefault("model", "grok-test")
    spec.setdefault("effort", "high")
    return spec


def copy_runner(tmp, name, *, preamble=True, report_preamble=True):
    plugin = Path(tmp) / "plugin"
    scripts = plugin / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "plugin" / "scripts" / name, scripts / name)
    shutil.copy2(REPO_ROOT / "plugin" / "scripts" / "routing-profile.mjs", scripts / "routing-profile.mjs")
    orch = plugin / "skills" / "orchestration"
    orch.mkdir(parents=True, exist_ok=True)
    (orch / "routing-profile.md").write_text(fixture_profile(), encoding="utf-8")
    if preamble:
        (orch / "lane-preamble.md").write_text("STUB LANE PREAMBLE", encoding="utf-8")
    if report_preamble:
        (orch / "lane-preamble-report.md").write_text("STUB REPORT PREAMBLE", encoding="utf-8")
    return scripts / name


def write_executable(directory, name, contents):
    path = Path(directory) / name
    path.write_text(contents, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def run_runner(runner, cwd, spec, path_dir, env_extra=None, *, pending=False, timeout=None, route_defaults=True):
    if runner.name == "run-grok.mjs" and route_defaults:
        prepare_grok_spec(spec)
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
        timeout=timeout,
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


def fake_git_sequence(directory, calls):
    """Successive `git status --porcelain` results as (exit_code, stdout) pairs.

    A counter file beside the script distinguishes the pre-run call from
    later ones. After the last pair, the last result repeats.
    """
    write_executable(
        directory,
        "git",
        """#!/usr/bin/env python3
import sys
from pathlib import Path
calls = %s
counter = Path(__file__).with_name(".git-status-count")
n = int(counter.read_text()) if counter.exists() else 0
counter.write_text(str(n + 1))
code, stdout = calls[n] if n < len(calls) else calls[-1]
if stdout:
    sys.stdout.write(stdout if stdout.endswith("\\n") else stdout + "\\n")
raise SystemExit(code)
""" % json.dumps(list(calls)),
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
if mode == "no_events":
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


def fake_report_cli(directory, binary):
    write_executable(
        directory, binary,
        """#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ["CALL_LOG"], "a") as handle:
    handle.write(json.dumps(args) + "\\n")
if args == ["--version"]:
    raise SystemExit(0)
if args == ["models"]:
    print("* grok-test (default)")
    raise SystemExit(0)
codex = "exec" in args
if codex and os.environ.get("REPORT_PRE_SESSION_FAILURE"):
    raise SystemExit(1)
prompt = sys.stdin.read() if codex else Path(args[args.index("--prompt-file") + 1]).read_text()
Path(os.environ["PROMPT_LOG"]).write_text(prompt)
if codex:
    print(json.dumps({"type": "thread.started", "thread_id": "report-session"}))
    for text in json.loads(os.environ.get("REPORT_CHUNKS", '["intermediate message", "Report findings."]')):
        print(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": text}}))
    print(json.dumps({"type": "turn.completed"}))
else:
    for text in json.loads(os.environ.get("REPORT_CHUNKS", '["Report ", "findings."]')):
        print(json.dumps({"type": "text", "data": text}))
    session_flag = "--resume" if "--resume" in args else "--session-id"
    print(json.dumps({"type": "end", "sessionId": args[args.index(session_flag) + 1]}))
""",
    )


def case_routing_profile_parser():
    module = REPO_ROOT / "plugin" / "scripts" / "routing-profile.mjs"
    with tempfile.TemporaryDirectory() as tmp:
        profile = Path(tmp) / "profile.md"
        text = fixture_profile().replace("grok-test[low, medium, high*, xhigh]", "bare-model › grok-test[high*, low, high]")
        profile.write_text(text)
        result = subprocess.run([NODE, str(module), "--dump", str(profile)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        tables = json.loads(result.stdout)
        assert set(tables) == {"claude_code", "cursor"}, tables
        for table in tables.values():
            assert set(table) == {"explorer", "worker", "advisor"}
            for tiers in table.values():
                assert set(tiers) == {"mainstay", "crux", "rescue"}
                for dials in tiers.values():
                    assert dials == sorted(set(dials))
                    assert {"bare-model", "grok-test[high]", "grok-test[low]"} <= set(dials)
                    assert all("*" not in dial for dial in dials)
        for malformed in ("invalid", text.replace("| advisor |", "| worker |"),
                          text.replace("high*, low, high", "high,,low"),
                          text.replace("## Cursor candidates", "## Other candidates")):
            profile.write_text(malformed)
            result = subprocess.run([NODE, str(module), "--dump", str(profile)], capture_output=True, text=True)
            assert result.returncode == 1 and str(profile) in result.stderr, result
        profile.unlink()
        result = subprocess.run([NODE, str(module), "--dump", str(profile)], capture_output=True, text=True)
        assert result.returncode == 1 and str(profile) in result.stderr
    print("ASSERT parser: two tables; sorted expanded unique dials; bare models; malformed and unreadable profiles rejected")


def case_route_validation():
    for binary in ("codex", "grok"):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            (fake_codex if binary == "codex" else fake_grok)(bin_dir)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            call_log = Path(tmp) / "calls"
            env = {"CALL_LOG": str(call_log), "PROMPT_LOG": str(Path(tmp) / "prompt")}
            spec = base_spec()
            if binary == "grok":
                prepare_grok_spec(spec)
            invalid = []
            for key in ("role", "tier"):
                missing = dict(spec)
                del missing[key]
                invalid.append(("missing " + key, missing, key))
            invalid.extend([
                ("implement advisor", dict(spec, role="advisor"), "role"),
                ("report worker", dict(spec, mode="report"), "role"),
                ("outside cell", dict(spec, effort="low" if binary == "codex" else "medium"), "legal dials"),
                ("missing basis", dict(spec, tier="crux"), "basis"),
                ("rescue advisor failure", dict(spec, mode="report", role="advisor", tier="rescue",
                    basis={"kind": "failure", "ref": "previous run"}), "user-declaration"),
                ("same-model tier", dict(spec, tier="same-model"), "tier"),
                ("unknown basis", dict(spec, basis={"kind": "unknown", "ref": "ref"}), "must be one of"),
                ("malformed basis", dict(spec, basis={"kind": "failure", "ref": " "}), "non-empty"),
            ])
            if binary == "grok":
                for key in ("model", "effort"):
                    missing = dict(spec)
                    del missing[key]
                    invalid.append(("missing " + key, missing, key))
            profile = runner.parent.parent / "skills" / "orchestration" / "routing-profile.md"
            # Remove one dial in both tables so the outside-cell case is independent of defaults.
            profile.write_text(fixture_profile().replace("low*, medium", "medium").replace("low, medium, high*", "low, high*"))
            for label, candidate, message in invalid:
                result, receipt = run_runner(runner, cwd, candidate, bin_dir, env, route_defaults=False)
                assert result.returncode != 0 and receipt["error_class"] == "spec_invalid", (label, receipt)
                assert message in result.stderr, (label, result.stderr)
                assert receipt["lane_finished_at"] is None, (label, receipt)
                assert not call_log.exists(), label + " spawned CLI"
            legal_basis = {"kind": "user-declaration", "ref": "contract route"}
            for tier in ("mainstay", "crux", "rescue"):
                legal = dict(spec, tier=tier, basis=legal_basis, verification=["sleep 2"] if tier == "crux" else ["true"])
                result, receipt = run_runner(runner, cwd, legal, bin_dir, env, route_defaults=False)
                assert result.returncode == 0 and receipt["error_class"] == "complete", (result.stderr, receipt)
                assert (receipt["role"], receipt["tier"], receipt["basis"]) == ("worker", tier, legal_basis)
                lane = datetime.fromisoformat(receipt["lane_finished_at"])
                finished = datetime.fromisoformat(receipt["finished_at"])
                if tier == "crux":
                    assert (finished - lane).total_seconds() >= 2, receipt
            call_log.unlink()
            # The Claude Code cell lacks this dial; the Cursor cell still permits it.
            claude, cursor = fixture_profile().split("## Cursor candidates")
            if binary == "codex":
                claude = claude.replace("low*, medium, high, xhigh", "low*, high, xhigh")
            else:
                claude = claude.replace("low, medium, high*, xhigh", "low, medium, xhigh")
            profile.write_text(claude + "## Cursor candidates" + cursor)
            result, receipt = run_runner(runner, cwd, spec, bin_dir, env, route_defaults=False)
            assert result.returncode == 0 and receipt["basis"] is None, (result.stderr, receipt)
            call_log.unlink()
            profile.unlink()
            result, receipt = run_runner(runner, cwd, spec, bin_dir, env, route_defaults=False)
            assert receipt["error_class"] == "spec_invalid" and str(profile) in result.stderr
            assert not call_log.exists() and receipt["lane_finished_at"] is None
            profile.write_text("invalid profile")
            result, receipt = run_runner(runner, cwd, spec, bin_dir, env, route_defaults=False)
            assert receipt["error_class"] == "spec_invalid" and str(profile) in result.stderr
            assert not call_log.exists()
            print("ASSERT route %s: legal routes and receipts; invalid routes spawn-free; lane_finished_at precedes verification by >=2s" % binary)


def case_mode_validation():
    for binary in ("codex", "grok"):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            call_log = Path(tmp) / "calls"
            invalid_specs = [
                base_spec(mode=mode) for mode in ("", "REPORT", "other", None, 7, True, [], {})
            ] + [
                base_spec(**mode, verification=[]) for mode in ({}, {"mode": "implement"})
            ] + [
                base_spec(mode="report", **fields)
                for fields in ({"files": None}, {"verification": None}, {"verification": [""]})
            ]
            for spec in invalid_specs:
                result, receipt = run_runner(
                    runner, cwd, spec, bin_dir, {"CALL_LOG": str(call_log)},
                )
                assert result.returncode != 0 and receipt["error_class"] == "spec_invalid", receipt
                assert not call_log.exists(), "invalid mode/spec spawned CLI"
                assert receipt["mode"] in ("implement", "report")
    print("ASSERT mode validation: both runners invalid=spawn-free implement verification=unchanged")


def case_report_and_implement_modes():
    scenarios = [
        ("report", [], 0, False, False, "complete"),
        ("report", ["scope.txt"], 0, False, False, "complete"),
        ("report", [], 0, True, False, "complete"),
        ("report", [], 0, False, True, "complete"),
        ("report", [], 0, False, False, "unexpected_diff"),
        ("report", [], 1, False, False, "complete"),
        ("report", [], 0, False, False, "verification_failed"),
        ("report", [], 0, False, False, "verification_diff"),
        ("implement", [], 0, False, False, "complete"),
        (None, [], 0, False, False, "complete"),
        ("implement", ["owned.txt"], 0, False, False, "no_diff"),
        (None, ["owned.txt"], 0, False, False, "no_diff"),
    ]
    for binary in ("codex", "grok"):
        for mode, files, git_exit, resume, pre_session_failure, expected in scenarios:
            with tempfile.TemporaryDirectory() as tmp:
                bin_dir = Path(tmp) / "bin"
                bin_dir.mkdir()
                fake_report_cli(bin_dir, binary)
                fake_git(bin_dir, git_exit)
                if expected == "unexpected_diff":
                    fake_git_sequence(bin_dir, [(0, ""), (0, " M scope.txt")])
                elif expected == "verification_diff":
                    write_executable(bin_dir, "git", '#!/bin/sh\nif [ -f "$2/changed" ]; then echo "?? changed"; fi\nexit 0\n')
                runner = copy_runner(tmp, "run-%s.mjs" % binary)
                cwd = Path(tmp) / "work"
                cwd.mkdir()
                call_log, prompt_log = Path(tmp) / "calls", Path(tmp) / "prompt"
                spec = base_spec(files=files)
                if mode is not None:
                    spec["mode"] = mode
                    spec["role"] = "explorer" if mode == "report" else "worker"
                if mode == "report":
                    spec["verification"] = []
                if expected == "verification_failed":
                    spec["verification"] = ["false"]
                elif expected == "verification_diff":
                    spec["verification"] = ["echo changed > changed"]
                    expected = "unexpected_diff"
                if resume:
                    spec["resume_session_id"] = "resume-123"
                if pre_session_failure and binary == "codex":
                    expected = "codex_failed"
                result, receipt = run_runner(
                    runner, cwd, spec, bin_dir,
                    {"CALL_LOG": str(call_log), "PROMPT_LOG": str(prompt_log),
                     "REPORT_PRE_SESSION_FAILURE": "1" if pre_session_failure else ""},
                    pending=True,
                )
                assert receipt["error_class"] == expected, receipt
                assert (result.returncode == 0) == (expected == "complete"), result.stderr
                assert receipt["mode"] == (mode or "implement")
                failed_before_session = pre_session_failure and binary == "codex"
                assert receipt["report"] == (
                    "" if failed_before_session else
                    "Report findings." if mode == "report" else None
                )
                assert receipt[binary + "_final_message"] == (
                    None if failed_before_session else "Report findings."
                )
                assert (cwd / ".fable-advisor" / "pending" / "job.json").exists() == (expected != "complete")
                receipt_path = cwd / ".fable-advisor" / "receipts" / (receipt["spec_hash"] + ".json")
                assert json.loads(receipt_path.read_text()) == receipt
                calls = [json.loads(line) for line in call_log.read_text().splitlines()]
                attempts = calls[1:]
                assert len(attempts) == 1, calls
                if failed_before_session:
                    assert receipt["model_requested"] == "gpt-6-astra"
                    assert receipt["model_used"] == "gpt-6-astra"
                    assert receipt["fallback_reason"] is None
                    assert not prompt_log.exists()
                    continue
                prompt = prompt_log.read_text()
                assert "[fable-advisor]" not in prompt
                assert "Files defines the read scope" not in prompt
                assert "WORKER REPORT" not in prompt
                if mode == "report":
                    assert prompt.startswith("job\n\nSTUB REPORT PREAMBLE\n\n")
                    assert "STUB LANE PREAMBLE" not in prompt
                else:
                    assert prompt.startswith("job\n\nSTUB LANE PREAMBLE\n\n")
                    assert "STUB REPORT PREAMBLE" not in prompt
                for args in attempts:
                    if mode == "report" and binary == "codex":
                        assert args.count("--sandbox") == 1
                        assert args[args.index("--sandbox") + 1] == "read-only"
                        assert "--dangerously-bypass-approvals-and-sandbox" not in args
                        if resume:
                            assert args.index("--sandbox") < args.index("resume")
                    elif mode == "report":
                        assert args[args.index("--tools") + 1] == "read_file,grep,list_dir"
                        assert args[args.index("--disallowed-tools") + 1] == "search_tool,use_tool,Agent"
                    elif binary == "grok":
                        assert "--tools" not in args and "--disallowed-tools" not in args
                    else:
                        assert args[args.index("--sandbox") + 1] == (
                            "danger-full-access" if os.name == "nt" else "workspace-write"
                        )
    print("ASSERT report: both runners readonly argv, text, clean/dirty, empty scope/checks, resume, pre-session failure, pending")
    print("ASSERT implement: explicit/omitted defaults and no_diff unchanged")


def case_runner_owns_verification_list():
    new_sentence = (
        "The runner runs these commands itself after you exit and records their "
        "exit codes and output in the receipt; a non-zero exit is your failure. "
        "Run what you need while you work; do not repeat this list as a closing step."
    )
    retired = "Run the verification command and include its actual output in your final message."
    empty_fence = "# Verification\n\n```bash\n\n```"
    for binary in ("codex", "grok"):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            prompt_log = Path(tmp) / "prompt"
            counter = Path(tmp) / "verify-count"
            spec = base_spec(verification=["echo ran >> %s" % counter])
            result, receipt = run_runner(
                runner, cwd, spec, bin_dir,
                {"CALL_LOG": str(Path(tmp) / "calls"), "PROMPT_LOG": str(prompt_log)},
            )
            assert result.returncode == 0, result.stderr
            assert receipt["error_class"] == "complete", receipt
            prompt = prompt_log.read_text()
            assert new_sentence in prompt
            assert retired not in prompt
            assert counter.read_text().splitlines() == ["ran"]

        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            prompt_log = Path(tmp) / "prompt"
            spec = base_spec(mode="report", verification=[])
            result, receipt = run_runner(
                runner, cwd, spec, bin_dir,
                {"CALL_LOG": str(Path(tmp) / "calls"), "PROMPT_LOG": str(prompt_log)},
            )
            assert result.returncode == 0, result.stderr
            assert receipt["error_class"] == "complete", receipt
            prompt = prompt_log.read_text()
            assert new_sentence not in prompt
            assert retired not in prompt
            assert empty_fence in prompt
    print("ASSERT runner owns verification: both runners new sentence iff non-empty; retired gone; list runs once")


def case_verification_output_log():
    marker = "FULL-OUTPUT-MARKER"
    for binary in ("codex", "grok"):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            receipts = cwd / ".fable-advisor" / "receipts"
            receipts.mkdir(parents=True)
            env = {"CALL_LOG": str(Path(tmp) / "calls"), "PROMPT_LOG": str(Path(tmp) / "prompt")}

            spec = base_spec(verification=[
                "echo %s; printf '%%03000d\\n' 0; exit 3" % marker,
                "echo second",
            ])
            if binary == "grok":
                prepare_grok_spec(spec)
            spec_hash = hashlib.sha256(json.dumps(spec).encode("utf-8")).hexdigest()
            logs = [".fable-advisor/receipts/%s.verification-%d.log" % (spec_hash, n) for n in (1, 2)]
            (cwd / logs[1]).write_text("STALE\n", encoding="utf-8")
            result, receipt = run_runner(runner, cwd, spec, bin_dir, env)
            assert receipt["error_class"] == "verification_failed", (receipt, result.stderr)
            first, second = receipt["verification"]
            assert first["exit_code"] == 3, first
            assert marker not in first["output_tail"], first
            assert [first["output_log"], second["output_log"]] == logs, receipt
            full = (cwd / logs[0]).read_text(encoding="utf-8")
            assert full.startswith(marker + "\n") and full.endswith(first["output_tail"]), full[:80]
            assert (cwd / logs[1]).read_text(encoding="utf-8") == "second\n"

            spec = base_spec(verification=["echo kept"])
            if binary == "grok":
                prepare_grok_spec(spec)
            spec_hash = hashlib.sha256(json.dumps(spec).encode("utf-8")).hexdigest()
            (receipts / ("%s.verification-1.log" % spec_hash)).mkdir()
            result, receipt = run_runner(runner, cwd, spec, bin_dir, env)
            assert receipt["error_class"] == "complete", (receipt, result.stderr)
            assert receipt["verification"] == [
                {"command": "echo kept", "exit_code": 0, "output_tail": "kept\n", "output_log": None},
            ], receipt
            assert "could not write verification log" in result.stderr, result.stderr
    print("ASSERT verification output log: both runners stream full output to numbered logs; unwritable log is null, verdict unchanged")


def case_empty_report():
    for binary in ("codex", "grok"):
        for chunks in ([], [""], [" \t\n"], [" Findings. \n"]):
            for mode in ("report", "implement", None):
                for dirty in (False, True):
                    with tempfile.TemporaryDirectory() as tmp:
                        bin_dir = Path(tmp) / "bin"
                        bin_dir.mkdir()
                        fake_report_cli(bin_dir, binary)
                        fake_git(bin_dir)
                        if dirty:
                            write_executable(bin_dir, "git", "#!/bin/sh\necho ' M scope.txt'\n")
                        runner = copy_runner(tmp, "run-%s.mjs" % binary)
                        cwd = Path(tmp) / "work"
                        cwd.mkdir()
                        spec = base_spec()
                        if mode is not None:
                            spec["mode"] = mode
                            spec["role"] = "explorer" if mode == "report" else "worker"
                        result, receipt = run_runner(
                            runner, cwd, spec, bin_dir,
                            {"CALL_LOG": str(Path(tmp) / "calls"),
                             "PROMPT_LOG": str(Path(tmp) / "prompt"),
                             "REPORT_CHUNKS": json.dumps(chunks)},
                            pending=True,
                        )
                        text = "".join(chunks)
                        expected = "complete"
                        if mode == "report":
                            expected = "complete" if text.strip() else "empty_report"
                        assert receipt["error_class"] == expected, receipt
                        if dirty:
                            assert receipt["dirty_baseline"] is True
                        assert receipt["report"] == (text if mode == "report" else None), receipt
                        assert (result.returncode == 0) == (expected == "complete"), result.stderr
                        pending_path = cwd / ".fable-advisor" / "pending" / "job.json"
                        assert pending_path.exists() == (expected != "complete")
                        receipt_path = cwd / ".fable-advisor" / "receipts" / (receipt["spec_hash"] + ".json")
                        assert json.loads(receipt_path.read_text()) == receipt
    print("ASSERT empty_report: both runners absent/empty/whitespace rejected; dirty_baseline skips unexpected_diff; text preserved; implement unchanged")


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

        _, luna = run_runner(codex, cwd, base_spec(model="gpt-6-luna"), bin_dir)
        assert (luna["error_class"], luna["model_requested"], luna["model_used"], luna["effort"]) == (
            "codex_unavailable", "gpt-6-luna", "gpt-6-luna", "max",
        )

        _, sol = run_runner(codex, cwd, base_spec(model="gpt-6.1-sol"), bin_dir)
        assert (sol["error_class"], sol["model_requested"], sol["model_used"], sol["effort"]) == (
            "codex_unavailable", "gpt-6.1-sol", "gpt-6.1-sol", "high",
        )
        assert sol["fallback_reason"] is None

        fake_codex(bin_dir)
        fake_git(bin_dir)
        call_log = Path(tmp) / "retired-model-calls"
        cli_env = {
            "CALL_LOG": str(call_log),
            "PROMPT_LOG": str(Path(tmp) / "retired-model-prompt"),
        }
        for retired in ("gpt-5.6-luna", "gpt-5.6-sol", "gpt-6-sol"):
            _, receipt = run_runner(codex, cwd, base_spec(model=retired), bin_dir, cli_env)
            assert receipt["error_class"] == "spec_invalid", receipt
            assert not call_log.exists(), "%s spawned codex" % retired

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

        for runner in (codex, grok):
            _, bad_idle = run_runner(
                runner, cwd, base_spec(idle_timeout_sec=0), bin_dir,
            )
            assert bad_idle["error_class"] == "spec_invalid"
            _, bad_idle_neg = run_runner(
                runner, cwd, base_spec(idle_timeout_sec=-1), bin_dir,
            )
            assert bad_idle_neg["error_class"] == "spec_invalid"
            _, bad_timeout = run_runner(
                runner, cwd, base_spec(timeout_sec=0), bin_dir,
            )
            assert bad_timeout["error_class"] == "spec_invalid"
        print(
            "ASSERT schema: gpt-6 defaults accepted retired=spec_invalid+spawn-free "
            "terra=spec_invalid unknown_key=spec_invalid empty_resume=spec_invalid "
            "idle_timeout_sec=spec_invalid"
        )


def case_grok_effort():
    valid_efforts = ("low", "medium", "high", "xhigh")
    invalid_efforts = ("max", "none", "HIGH", " high ", "", None, 7, True, [], {})
    for overrides in (
        *(dict(effort=value) for value in valid_efforts),
        *(dict(effort=value) for value in invalid_efforts),
        {},
    ):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_grok(bin_dir)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-grok.mjs")
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            call_log = Path(tmp) / "calls"
            result, receipt = run_runner(
                runner, cwd, base_spec(model="grok-test", **overrides), bin_dir,
                {"CALL_LOG": str(call_log), "PROMPT_LOG": str(Path(tmp) / "prompt")},
                route_defaults=False,
            )
            effort = overrides.get("effort")
            if effort not in valid_efforts:
                assert result.returncode != 0, result.stderr
                assert receipt["error_class"] == "spec_invalid", receipt
                assert receipt["effort"] is None
                assert not call_log.exists(), "invalid effort spawned grok"
                continue
            assert result.returncode == 0, result.stderr
            assert receipt["error_class"] == "complete", receipt
            assert receipt["effort"] == effort
            calls = [json.loads(line) for line in call_log.read_text().splitlines()]
            assert len(calls) == 2 and calls[0] == ["models"], calls
            execution = calls[1]
            if overrides:
                assert execution.count("--effort") == 1, execution
                assert execution[execution.index("--effort") + 1] == effort
            else:
                assert "--effort" not in execution, execution
            receipt_path = cwd / ".fable-advisor" / "receipts" / (
                receipt["spec_hash"] + ".json"
            )
            assert json.loads(receipt_path.read_text()) == receipt
    print("ASSERT grok effort: valid=low,medium,high,xhigh invalid=spawn-free omitted=spec_invalid,spawn-free")


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

        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            marker = Path(tmp) / "spawned"
            write_executable(
                bin_dir,
                binary,
                "#!/bin/sh\ntouch '%s'\n" % marker,
            )
            runner = copy_runner(tmp, name, report_preamble=False)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            result, receipt = run_runner(
                runner, cwd, base_spec(mode="report", verification=[]), bin_dir,
            )
            assert result.returncode != 0 and receipt is None
            assert "lane-preamble-report.md" in result.stderr
            assert not marker.exists()
            assert not (cwd / ".fable-advisor" / "receipts").exists()

        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            fake_git(bin_dir)
            runner = copy_runner(tmp, name, report_preamble=False)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            result, receipt = run_runner(
                runner, cwd, base_spec(), bin_dir,
                {"CALL_LOG": str(Path(tmp) / "calls"),
                 "PROMPT_LOG": str(Path(tmp) / "prompt")},
            )
            assert result.returncode == 0, result.stderr
            assert receipt["error_class"] == "complete"
            assert (Path(tmp) / "prompt").read_text().startswith(
                "job\n\nSTUB LANE PREAMBLE\n\n"
            )


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
            expected_model = "gpt-6-astra" if "codex" in name else "grok-test"
            assert receipt["model_requested"] == expected_model
            assert receipt["model_used"] == expected_model
            assert receipt["fallback_reason"] is None
            assert receipt["resumed_from"] is None
            assert receipt["end_to_close_ms"] is None
            assert receipt["max_idle_ms"] is None


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
                "job\n\nSTUB LANE PREAMBLE\n\n"
            )
            assert "[fable-advisor]" not in prompt_log.read_text()
            print(
                "ASSERT resume: runner=%s argv_id=resume-123 receipt_id=resume-123"
                % name
            )


def case_codex_no_model_switch():
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
        assert len(attempts) == 1
        assert receipt["model_requested"] == "gpt-6-astra"
        assert receipt["model_used"] == "gpt-6-astra"
        assert receipt["model"] == "gpt-6-astra"
        assert receipt["effort"] == "medium"
        assert receipt["fallback_reason"] is None
        assert receipt["error_class"] == "codex_failed"
        assert "model_reasoning_effort=medium" in attempts[0]
        print(
            "ASSERT no fallback: error=codex_failed model_used=gpt-6-astra "
            "fallback_reason=null attempts=1"
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


def case_codex_no_model_switch_boundaries():
    with tempfile.TemporaryDirectory() as tmp:
        receipt, attempts = run_codex_mode(
            tmp,
            base_spec(model="gpt-6-luna"),
            "fail_before_session",
        )
        assert len(attempts) == 1
        assert receipt["model_requested"] == "gpt-6-luna"
        assert receipt["model_used"] == "gpt-6-luna"
        assert receipt["effort"] == "max"
        assert receipt["fallback_reason"] is None
        assert "model_reasoning_effort=max" in attempts[0]

    with tempfile.TemporaryDirectory() as tmp:
        receipt, attempts = run_codex_mode(
            tmp,
            base_spec(model="gpt-6.1-sol"),
            "fail_before_session",
        )
        assert len(attempts) == 1
        assert receipt["model_requested"] == "gpt-6.1-sol"
        assert receipt["model_used"] == "gpt-6.1-sol"
        assert receipt["effort"] == "high"
        assert receipt["fallback_reason"] is None
        assert "model_reasoning_effort=high" in attempts[0]

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
            "no_events",
        )
        assert len(attempts) == 1
        assert receipt["model_requested"] == "gpt-6-astra"
        assert receipt["model_used"] == "gpt-6-astra"
        assert receipt["fallback_reason"] is None
        assert receipt["error_class"] == "preparation_stalled"
        print(
            "ASSERT no fallback boundaries: direct_luna=1 direct_sol=1 "
            "session_established=1 preparation_stalled=1"
        )


def fake_stream(directory, binary):
    write_executable(
        directory,
        binary,
        """#!/usr/bin/env python3
import json, os, subprocess, sys, time
from pathlib import Path
args = sys.argv[1:]
if args == ["--version"]:
    raise SystemExit(0)
if args == ["models"]:
    print("Default model: grok-test")
    print("* grok-test (default)")
    raise SystemExit(0)
if "exec" in args:
    sys.stdin.read()
mode = os.environ["STREAM_MODE"]
codex = "exec" in args
session = {"type": "thread.started", "thread_id": "stream-session"} if codex else {
    "type": "end", "sessionId": "stream-session", "stopReason": "done"}
terminal = {"type": "turn.completed"} if codex else session
if mode == "no_events":
    print("not json", flush=True)
    time.sleep(0.1)
    raise SystemExit(1)
if mode.startswith("interrupt"):
    descendant = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    if mode != "interrupt_no_events":
        print(json.dumps(session), flush=True)
    Path(os.environ["READY"]).write_text(json.dumps([os.getpid(), descendant.pid]))
    time.sleep(60)
    raise SystemExit(0)
time.sleep(0.5 if mode == "initial_gap" else 0.1)
print(json.dumps(session), flush=True)
for delay in ([0.02, 0.02] if mode == "initial_gap" else [0.2, 0.5]):
    time.sleep(delay)
    print(json.dumps({"type": "progress"}), flush=True)
time.sleep(0.2)
print(json.dumps(terminal), flush=True)
time.sleep(0.9)
""",
    )


def case_idle_diagnostic():
    for binary in ("codex", "grok"):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_stream(bin_dir, binary)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            for mode in ("initial_gap", "event_gap", "no_events"):
                result, receipt = run_runner(
                    runner, cwd,
                    base_spec(**({"model": "gpt-6-luna"} if binary == "codex" else {})),
                    bin_dir, {"STREAM_MODE": mode},
                )
                assert receipt["receipt_version"] == 1
                if mode == "no_events":
                    assert receipt["max_idle_ms"] is None
                    assert result.returncode != 0
                else:
                    assert result.returncode == 0
                    assert receipt["error_class"] == "complete"
                    assert type(receipt["max_idle_ms"]) is int
                    assert 450 <= receipt["max_idle_ms"] < 800, receipt
                    assert receipt["end_to_close_ms"] >= 850, receipt
                print("ASSERT idle: runner=%s mode=%s max_idle_ms=%s" % (
                    binary, mode, receipt["max_idle_ms"],
                ))


def process_is_running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    status = Path("/proc/%d/stat" % pid)
    if status.exists():
        try:
            return status.read_text().rsplit(")", 1)[1].split()[0] != "Z"
        except FileNotFoundError:
            return False
    return True


def case_interrupted_receipt_and_process_tree():
    for binary in ("codex", "grok"):
        for signum in (signal.SIGTERM, signal.SIGINT):
            for mode in ("interrupt", "interrupt_no_events", "interrupt_resume"):
                with tempfile.TemporaryDirectory() as tmp:
                    bin_dir = Path(tmp) / "bin"
                    bin_dir.mkdir()
                    fake_stream(bin_dir, binary)
                    fake_git(bin_dir)
                    runner = copy_runner(tmp, "run-%s.mjs" % binary)
                    cwd = Path(tmp) / "work"
                    cwd.mkdir()
                    ready = Path(tmp) / "ready"
                    marker = cwd / "verified"
                    spec = base_spec(verification=["echo ran > verified"])
                    if mode == "interrupt_resume":
                        spec["resume_session_id"] = "resume-123"
                    spec_path = cwd / ".fable-advisor" / "pending" / "job.json"
                    spec_path.parent.mkdir(parents=True)
                    if binary == "grok":
                        prepare_grok_spec(spec)
                    raw = json.dumps(spec).encode()
                    spec_path.write_bytes(raw)
                    env = os.environ.copy()
                    env.update({
                        "PATH": os.pathsep.join((str(bin_dir), str(Path(sys.executable).parent))),
                        "STREAM_MODE": mode,
                        "READY": str(ready),
                    })
                    process = subprocess.Popen(
                        [NODE, str(runner), "--spec", str(spec_path), "--cwd", str(cwd)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                        env=env, start_new_session=True,
                    )
                    pids = []
                    try:
                        deadline = time.monotonic() + 5
                        while not ready.exists() and time.monotonic() < deadline:
                            assert process.poll() is None, "runner exited before ready"
                            time.sleep(0.01)
                        assert ready.exists(), "CLI did not become ready"
                        time.sleep(0.15)
                        pids = json.loads(ready.read_text())
                        os.killpg(process.pid, signum)
                        stdout, stderr = process.communicate(timeout=5)
                        assert process.returncode != 0, stderr
                        receipt = json.loads(stdout)
                        receipt_path = cwd / ".fable-advisor" / "receipts" / (
                            hashlib.sha256(raw).hexdigest() + ".json"
                        )
                        assert json.loads(receipt_path.read_text()) == receipt
                        assert receipt["error_class"] == "interrupted", receipt
                        assert receipt["verification"] == []
                        assert not marker.exists()
                        assert spec_path.read_bytes() == raw
                        assert receipt["fallback_reason"] is None
                        session = receipt[binary + "_session_id"]
                        if mode == "interrupt_resume":
                            assert session == "resume-123"
                        elif mode == "interrupt":
                            assert session == "stream-session"
                        elif binary == "codex":
                            assert session is None
                        else:
                            assert isinstance(session, str) and session
                        if mode == "interrupt_no_events":
                            assert receipt["max_idle_ms"] is None
                        else:
                            assert type(receipt["max_idle_ms"]) is int
                        deadline = time.monotonic() + 2
                        while any(process_is_running(pid) for pid in pids) and time.monotonic() < deadline:
                            time.sleep(0.01)
                        assert not any(process_is_running(pid) for pid in pids), pids
                    finally:
                        if process.poll() is None:
                            process.kill()
                            process.communicate(timeout=5)
                        for pid in pids:
                            if process_is_running(pid):
                                os.kill(pid, signal.SIGKILL)
                    print("ASSERT interrupted: runner=%s signal=%s mode=%s tree=dead receipt=disk" % (
                        binary, signum.name, mode,
                    ))


def fake_deadline(directory, binary):
    write_executable(
        directory,
        binary,
        """#!/usr/bin/env python3
import json, os, sys, time
args = sys.argv[1:]
if args == ["--version"]:
    raise SystemExit(0)
if args == ["models"]:
    print("Default model: grok-test")
    print("* grok-test (default)")
    raise SystemExit(0)
if "exec" in args:
    sys.stdin.read()
codex = "exec" in args
first = {"type": "thread.started", "thread_id": "stream-session"} if codex else {
    "type": "text", "data": "x"}
progress = {"type": "progress"}
terminal = {"type": "turn.completed"} if codex else {
    "type": "end", "sessionId": "stream-session", "stopReason": "done"}
mode = os.environ["DEADLINE_MODE"]
interval = float(os.environ.get("DEADLINE_INTERVAL", "0.08"))
count = int(os.environ.get("DEADLINE_COUNT", "12"))
hang = float(os.environ.get("DEADLINE_HANG", "60"))

def emit(payload):
    print(json.dumps(payload), flush=True)

if mode == "no_events":
    time.sleep(hang)
    raise SystemExit(0)
emit(first)
if mode == "silence_after":
    emit(progress)
    time.sleep(hang)
    raise SystemExit(0)
if mode == "forever":
    while True:
        time.sleep(interval)
        emit(progress)
for _ in range(count):
    time.sleep(interval)
    emit(progress)
emit(terminal)
""",
    )


def run_deadline(binary, spec, env_extra, *, pending=True, timeout=8, dirty=False):
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir()
        fake_deadline(bin_dir, binary)
        if dirty:
            write_executable(
                bin_dir,
                "git",
                "#!/bin/sh\necho '?? owned.txt'\nexit 0\n",
            )
        else:
            fake_git(bin_dir)
        runner = copy_runner(tmp, "run-%s.mjs" % binary)
        cwd = Path(tmp) / "work"
        cwd.mkdir()
        started = time.monotonic()
        result, receipt = run_runner(
            runner, cwd, spec, bin_dir, env_extra, pending=pending, timeout=timeout,
        )
        elapsed = time.monotonic() - started
        pending_kept = (cwd / ".fable-advisor" / "pending" / "job.json").is_file()
        verified = (cwd / "verified").exists()
        return result, receipt, elapsed, pending_kept, verified


def case_idle_and_wall_deadlines():
    idle = 0.5
    for binary in ("codex", "grok"):
        spec_model = {"model": "gpt-6-luna"} if binary == "codex" else {}
        live_env = {
            "DEADLINE_MODE": "live",
            "DEADLINE_INTERVAL": "0.08",
            "DEADLINE_COUNT": "12",
        }

        result, receipt, elapsed, pending_kept, _ = run_deadline(
            binary,
            base_spec(idle_timeout_sec=idle, **spec_model),
            live_env,
        )
        assert result.returncode == 0, result.stderr
        assert receipt["error_class"] == "complete", receipt
        assert receipt["idle_timeout_sec"] == idle
        assert receipt["timeout_sec"] is None
        assert elapsed > idle
        assert not pending_kept
        print("ASSERT live-past-idle: runner=%s elapsed=%.2f complete" % (
            binary, elapsed,
        ))

        result, receipt, elapsed, pending_kept, verified = run_deadline(
            binary,
            base_spec(
                idle_timeout_sec=idle,
                verification=["echo ran > verified"],
                **spec_model,
            ),
            {"DEADLINE_MODE": "silence_after", "DEADLINE_HANG": "60"},
        )
        assert result.returncode != 0, result.stderr
        assert receipt["error_class"] == "idle_timeout", receipt
        assert receipt["verification"] == []
        assert receipt["idle_timeout_sec"] == idle
        assert receipt["timeout_sec"] is None
        assert pending_kept
        assert not verified
        assert elapsed < 4, elapsed
        print("ASSERT idle-kill: runner=%s elapsed=%.2f idle_timeout pending=kept" % (
            binary, elapsed,
        ))

        result, receipt, elapsed, pending_kept, verified = run_deadline(
            binary,
            base_spec(
                idle_timeout_sec=5,
                timeout_sec=idle,
                verification=["echo ran > verified"],
                **spec_model,
            ),
            {"DEADLINE_MODE": "forever", "DEADLINE_INTERVAL": "0.08"},
        )
        assert result.returncode != 0, result.stderr
        assert receipt["error_class"] == "timeout", receipt
        assert receipt["verification"] == []
        assert receipt["timeout_sec"] == idle
        assert receipt["idle_timeout_sec"] == 5
        assert pending_kept
        assert not verified
        assert elapsed < 4, elapsed
        print("ASSERT wall-timeout: runner=%s elapsed=%.2f timeout pending=kept" % (
            binary, elapsed,
        ))

        # No timeout_sec means no absolute ceiling: keep emitting past idle
        # (the scaled stand-in for the old 600s wall default) and still complete.
        result, receipt, elapsed, pending_kept, _ = run_deadline(
            binary,
            base_spec(idle_timeout_sec=idle, **spec_model),
            live_env,
        )
        assert result.returncode == 0, result.stderr
        assert receipt["error_class"] == "complete", receipt
        assert "timeout_sec" in receipt and receipt["timeout_sec"] is None
        assert elapsed > idle
        assert not pending_kept
        print("ASSERT no-wall-default: runner=%s elapsed=%.2f timeout_sec=null" % (
            binary, elapsed,
        ))

        result, receipt, elapsed, pending_kept, verified = run_deadline(
            binary,
            base_spec(
                idle_timeout_sec=idle,
                resume_session_id="resume-123",
                verification=["echo ran > verified"],
                **spec_model,
            ),
            {"DEADLINE_MODE": "no_events", "DEADLINE_HANG": "60"},
        )
        assert result.returncode != 0, result.stderr
        assert receipt["error_class"] == "idle_timeout", receipt
        assert receipt["error_class"] != "preparation_stalled"
        assert receipt["verification"] == []
        assert pending_kept
        assert not verified
        assert elapsed < 4, elapsed
        print("ASSERT resume-first-event: runner=%s elapsed=%.2f idle_timeout" % (
            binary, elapsed,
        ))

        result, receipt, elapsed, pending_kept, verified = run_deadline(
            binary,
            base_spec(
                idle_timeout_sec=idle,
                verification=["echo ran > verified"],
                **spec_model,
            ),
            {"DEADLINE_MODE": "no_events", "DEADLINE_HANG": "1.2"},
        )
        assert result.returncode != 0, result.stderr
        assert receipt["error_class"] == "preparation_stalled", receipt
        assert receipt["verification"] == []
        assert pending_kept
        assert not verified
        assert elapsed < 5, elapsed
        print("ASSERT non-resume-silent: runner=%s elapsed=%.2f preparation_stalled" % (
            binary, elapsed,
        ))

        result, receipt, elapsed, pending_kept, verified = run_deadline(
            binary,
            base_spec(
                idle_timeout_sec=5,
                resume_session_id="resume-123",
                files=["owned.txt"],
                verification=["echo ran > verified"],
                **spec_model,
            ),
            {"DEADLINE_MODE": "no_events", "DEADLINE_HANG": "0.05"},
            dirty=True,
        )
        assert result.returncode != 0, result.stderr
        assert receipt["error_class"] == "preparation_stalled", receipt
        assert receipt["verification"] == []
        assert pending_kept
        assert not verified
        assert elapsed < 2, elapsed
        print("ASSERT resume-silent-exit: runner=%s elapsed=%.2f preparation_stalled" % (
            binary, elapsed,
        ))


def case_dirty_baseline():
    dirty = " M scope.txt"

    def run_case(binary, spec, git_calls, extra_env=None):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            fake_git_sequence(bin_dir, git_calls)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            env = {
                "CALL_LOG": str(Path(tmp) / "calls"),
                "PROMPT_LOG": str(Path(tmp) / "prompt"),
            }
            if extra_env:
                env.update(extra_env)
            result, receipt = run_runner(runner, cwd, spec, bin_dir, env)
            return result, receipt

    for binary in ("codex", "grok"):
        result, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(0, dirty), (0, dirty)],
        )
        assert result.returncode == 0, result.stderr
        assert receipt["error_class"] == "complete", receipt
        assert receipt["dirty_baseline"] is True
        assert receipt["changed_files"] == ["scope.txt"]

        _, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(0, dirty), (0, "")],
        )
        assert receipt["error_class"] == "complete", receipt
        assert receipt["dirty_baseline"] is True
        assert receipt["changed_files"] == []

        result, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(0, ""), (0, dirty)],
        )
        assert result.returncode != 0
        assert receipt["error_class"] == "unexpected_diff", receipt
        assert receipt["dirty_baseline"] is False
        assert receipt["changed_files"] == ["scope.txt"]

        _, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(1, ""), (0, "")],
        )
        assert receipt["error_class"] == "complete", receipt
        assert receipt["dirty_baseline"] is None

        result, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(1, ""), (0, dirty)],
        )
        assert receipt["error_class"] == "unexpected_diff", receipt
        assert receipt["dirty_baseline"] is None

        result, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(0, ""), (1, "")],
        )
        assert result.returncode == 0, result.stderr
        assert receipt["error_class"] == "complete", receipt
        assert receipt["dirty_baseline"] is False

        _, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(1, ""), (1, "")],
            {"REPORT_CHUNKS": json.dumps([])},
        )
        assert receipt["error_class"] == "empty_report", receipt
        assert receipt["dirty_baseline"] is None

        _, receipt = run_case(
            binary,
            base_spec(mode="report", verification=[]),
            [(0, dirty), (0, dirty)],
            {"REPORT_CHUNKS": json.dumps([])},
        )
        assert receipt["error_class"] == "empty_report", receipt
        assert receipt["dirty_baseline"] is True
        assert receipt["changed_files"] == ["scope.txt"]

        _, receipt = run_case(
            binary,
            base_spec(mode="implement", files=["owned.txt"]),
            [(0, dirty), (0, dirty)],
        )
        assert receipt["error_class"] == "complete", receipt
        assert receipt["dirty_baseline"] is True
        assert receipt["changed_files"] == ["scope.txt"]

        _, receipt = run_case(
            binary,
            base_spec(mode="implement", files=["owned.txt"]),
            [(0, ""), (0, "")],
        )
        assert receipt["error_class"] == "no_diff", receipt
        assert receipt["dirty_baseline"] is False

        _, receipt = run_case(
            binary,
            base_spec(mode="implement", files=["owned.txt"]),
            [(0, ""), (1, "")],
        )
        assert receipt["error_class"] == "git_status_failed", receipt
        assert receipt["dirty_baseline"] is False

        _, receipt = run_case(
            binary,
            base_spec(mode="implement"),
            [(0, ""), (0, "")],
        )
        assert receipt["error_class"] == "complete", receipt
        assert receipt["dirty_baseline"] is False
    print("ASSERT dirty_baseline: report skips unexpected_diff iff true; clean-then-dirty still unexpected_diff; report git fail is complete or empty_report; implement unchanged; pre-fail=null")


def case_title():
    invalid_titles = ("", None, 7, True, [], {})
    for binary in ("codex", "grok"):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake_report_cli(bin_dir, binary)
            fake_git(bin_dir)
            runner = copy_runner(tmp, "run-%s.mjs" % binary)
            cwd = Path(tmp) / "work"
            cwd.mkdir()
            call_log = Path(tmp) / "calls"
            prompt_log = Path(tmp) / "prompt"
            env = {"CALL_LOG": str(call_log), "PROMPT_LOG": str(prompt_log)}

            result, receipt = run_runner(
                runner, cwd, base_spec(title="Scout the dirty tree"), bin_dir, env,
            )
            assert result.returncode == 0, result.stderr
            assert receipt["error_class"] == "complete", receipt
            prompt = prompt_log.read_text()
            assert prompt.startswith("Scout the dirty tree\n\nSTUB LANE PREAMBLE\n\n")
            assert prompt.splitlines()[0] == "Scout the dirty tree"
            assert prompt.splitlines()[1] == ""
            assert "[fable-advisor]" not in prompt
            assert "# Scout" not in prompt.splitlines()[0]
            prompt_log.unlink()
            call_log.unlink()

            result, receipt = run_runner(
                runner, cwd, base_spec(title="# not a heading"), bin_dir, env,
            )
            assert result.returncode == 0, result.stderr
            prompt = prompt_log.read_text()
            assert prompt.startswith("# not a heading\n\nSTUB LANE PREAMBLE\n\n")
            assert "[fable-advisor]" not in prompt
            prompt_log.unlink()
            call_log.unlink()

            result, receipt = run_runner(runner, cwd, base_spec(), bin_dir, env)
            assert result.returncode == 0, result.stderr
            prompt = prompt_log.read_text()
            assert prompt.startswith("job\n\nSTUB LANE PREAMBLE\n\n")
            assert "# Objective" in prompt
            assert prompt.index("STUB LANE PREAMBLE") < prompt.index("# Objective")
            assert "[fable-advisor]" not in prompt
            prompt_log.unlink()
            if call_log.exists():
                call_log.unlink()

            for title in invalid_titles:
                result, receipt = run_runner(
                    runner, cwd, base_spec(title=title), bin_dir, env,
                )
                assert result.returncode != 0, title
                assert receipt["error_class"] == "spec_invalid", (title, receipt)
                assert not call_log.exists(), "invalid title spawned CLI: %r" % (title,)
    print("ASSERT title: first line verbatim; omitted=slug; empty/non-string=spec_invalid spawn-free; no [fable-advisor]")


def case_real_preamble_files():
    orchestration = REPO_ROOT / "plugin" / "skills" / "orchestration"
    worker = orchestration / "lane-preamble.md"
    report = orchestration / "lane-preamble-report.md"
    worker_text = worker.read_text(encoding="utf-8")
    report_text = report.read_text(encoding="utf-8")
    assert worker.is_file() and worker_text.strip(), worker
    assert report.is_file() and report_text.strip(), report
    assert "WORKER REPORT" in worker_text
    assert "WORKER REPORT" not in report_text
    assert worker_text.startswith("**Posture.**")
    assert report_text.startswith("**Posture.**")
    print("ASSERT real preambles: worker has WORKER REPORT; report does not; both start **Posture.**")


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


def fake_marker_cli(directory, binary):
    write_executable(
        directory,
        binary,
        """#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
if args == ["--version"]:
    raise SystemExit(0)
if args == ["models"]:
    print("* grok-test (default)")
    raise SystemExit(0)
with open(os.environ["CALL_LOG"], "a", encoding="utf-8") as handle:
    handle.write(json.dumps(args) + "\\n")
codex = "exec" in args
if codex:
    sys.stdin.read()
    print(json.dumps({"type": "thread.started", "thread_id": "marker-session"}), flush=True)
else:
    print(json.dumps({"type": "text", "data": "working"}), flush=True)
time.sleep(0.5)
markers = {path.name: json.loads(path.read_text())
           for path in Path(os.environ["RUNNING_DIR"]).glob("*.json")}
Path(os.environ["SEEN"]).write_text(json.dumps({"ppid": os.getppid(), "markers": markers}))
if codex:
    print(json.dumps({"type": "turn.completed"}), flush=True)
else:
    session = args[args.index("--session-id") + 1]
    print(json.dumps({"type": "end", "sessionId": session, "stopReason": "done"}), flush=True)
""",
    )


def case_running_marker():
    for binary in ("codex", "grok"):
        for scenario in ("fresh_run", "duplicate", "stale_marker"):
            with tempfile.TemporaryDirectory() as tmp:
                bin_dir = Path(tmp) / "bin"
                bin_dir.mkdir()
                fake_marker_cli(bin_dir, binary)
                fake_git(bin_dir)
                runner = copy_runner(tmp, "run-%s.mjs" % binary)
                runner.write_text(runner.read_text().replace(
                    "const HEARTBEAT_MS = 60_000;", "const HEARTBEAT_MS = 100;",
                ))
                cwd = Path(tmp) / "work"
                cwd.mkdir()
                spec = base_spec()
                if binary == "grok":
                    prepare_grok_spec(spec)
                spec_hash = hashlib.sha256(json.dumps(spec).encode("utf-8")).hexdigest()
                running_dir = cwd / ".fable-advisor" / "running"
                marker = running_dir / ("%s.json" % spec_hash)
                if scenario != "fresh_run":
                    running_dir.mkdir(parents=True)
                    marker.write_text('{"runner": "other"}', encoding="utf-8")
                    if scenario == "stale_marker":
                        stamp = time.time() - 200
                        os.utime(marker, (stamp, stamp))
                call_log = Path(tmp) / "calls.jsonl"
                seen_path = Path(tmp) / "seen.json"
                result, receipt = run_runner(
                    runner, cwd, spec, bin_dir,
                    {"CALL_LOG": str(call_log), "RUNNING_DIR": str(running_dir),
                     "SEEN": str(seen_path)},
                    pending=True, timeout=8,
                )
                if scenario == "duplicate":
                    assert result.returncode == 1, (result.returncode, result.stderr)
                    assert receipt is None, receipt
                    assert "another runner is running this spec" in result.stderr, result.stderr
                    assert not call_log.exists(), call_log.read_text()
                    assert not (cwd / ".fable-advisor" / "receipts").exists()
                    assert (cwd / ".fable-advisor" / "pending" / "job.json").exists()
                    assert marker.read_text(encoding="utf-8") == '{"runner": "other"}'
                else:
                    assert receipt["error_class"] == "complete", (receipt, result.stderr)
                    seen = json.loads(seen_path.read_text())
                    in_flight = seen["markers"]["%s.json" % spec_hash]
                    assert in_flight["runner"] == binary, in_flight
                    assert in_flight["pid"] == seen["ppid"], (in_flight, seen)
                    assert in_flight["phase"] == "cli", in_flight
                    assert in_flight["events"] >= 1, in_flight
                    assert "phase cli; " in result.stderr, result.stderr
                    assert list(running_dir.glob("*")) == [], list(running_dir.glob("*"))
                print("ASSERT running marker: runner=%s scenario=%s" % (binary, scenario))


CASES = [
    ("routing profile parser", case_routing_profile_parser),
    ("route validation", case_route_validation),
    ("mode validation", case_mode_validation),
    ("report and implement modes", case_report_and_implement_modes),
    ("runner owns verification list", case_runner_owns_verification_list),
    ("verification output log", case_verification_output_log),
    ("empty report", case_empty_report),
    ("dirty baseline", case_dirty_baseline),
    ("spec title", case_title),
    ("real preamble files", case_real_preamble_files),
    ("schema defaults and validation", case_schema_defaults_and_validation),
    ("grok effort", case_grok_effort),
    ("missing preamble is spawn-free", case_preamble_missing_is_spawn_free),
    ("unavailable receipt fields", case_unavailable_receipt_fields),
    ("no_diff and git_status_failed", case_no_diff_and_git_status_failed),
    ("resume invocations and preamble", case_resume_invocations_and_preamble),
    ("codex no model switch", case_codex_no_model_switch),
    ("codex no model switch boundaries", case_codex_no_model_switch_boundaries),
    ("last terminal event drives timing", case_last_terminal_event_drives_timing),
    ("idle diagnostic", case_idle_diagnostic),
    ("interrupted receipt and process tree", case_interrupted_receipt_and_process_tree),
    ("idle and wall deadlines", case_idle_and_wall_deadlines),
    ("running marker", case_running_marker),
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
