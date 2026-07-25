#!/usr/bin/env python3
"""Regression tests for hooks/receipt-gate.py (process-boundary behavior)."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO_ROOT, "hooks", "receipt-gate.py")


def run_hook(cwd, stdin_payload):
    """Run receipt-gate.py with the given stdin (str or dict). Returns CompletedProcess."""
    if isinstance(stdin_payload, dict):
        stdin_text = json.dumps(stdin_payload)
    else:
        stdin_text = stdin_payload
    return subprocess.run(
        [sys.executable, HOOK],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def write_pending_spec(tmpdir, name, content):
    pending_dir = os.path.join(tmpdir, ".fable-advisor", "pending")
    os.makedirs(pending_dir, exist_ok=True)
    path = os.path.join(pending_dir, name)
    data = content if isinstance(content, bytes) else content.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return path, data


def write_receipt(tmpdir, spec_bytes, receipt_obj):
    digest = hashlib.sha256(spec_bytes).hexdigest()
    receipts_dir = os.path.join(tmpdir, ".fable-advisor", "receipts")
    os.makedirs(receipts_dir, exist_ok=True)
    path = os.path.join(receipts_dir, digest + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt_obj, f)
    return path


def case_1_no_pending_dir():
    """pending dir missing, stop_hook_active absent → exit 0"""
    with tempfile.TemporaryDirectory() as tmp:
        r = run_hook(tmp, {"cwd": tmp})
        assert r.returncode == 0, "expected exit 0, got %s stderr=%r" % (
            r.returncode,
            r.stderr,
        )


def case_2_complete_receipt():
    """pending spec with complete receipt, stop_hook_active absent → exit 0"""
    with tempfile.TemporaryDirectory() as tmp:
        _, spec_bytes = write_pending_spec(tmp, "job.json", b'{"task":"x"}')
        write_receipt(tmp, spec_bytes, {"error_class": "complete"})
        r = run_hook(tmp, {"cwd": tmp})
        assert r.returncode == 0, "expected exit 0, got %s stderr=%r" % (
            r.returncode,
            r.stderr,
        )


def case_3_no_receipt_blocks():
    """pending spec without receipt, stop_hook_active absent → exit 2, stderr names spec"""
    with tempfile.TemporaryDirectory() as tmp:
        write_pending_spec(tmp, "orphan.json", b'{"task":"orphan"}')
        r = run_hook(tmp, {"cwd": tmp})
        assert r.returncode == 2, "expected exit 2, got %s" % r.returncode
        assert r.stderr, "expected non-empty stderr"
        assert "orphan.json" in r.stderr, "stderr should name the spec: %r" % r.stderr


def case_4_false_still_blocks():
    """pending spec without receipt, stop_hook_active false → exit 2, stderr non-empty"""
    with tempfile.TemporaryDirectory() as tmp:
        write_pending_spec(tmp, "still.json", b'{"task":"still"}')
        r = run_hook(tmp, {"cwd": tmp, "stop_hook_active": False})
        assert r.returncode == 2, "expected exit 2, got %s" % r.returncode
        assert r.stderr, "expected non-empty stderr"


def case_5_active_bypasses():
    """pending spec without receipt, stop_hook_active true → exit 0"""
    with tempfile.TemporaryDirectory() as tmp:
        write_pending_spec(tmp, "active.json", b'{"task":"active"}')
        r = run_hook(tmp, {"cwd": tmp, "stop_hook_active": True})
        assert r.returncode == 0, "expected exit 0 when stop_hook_active, got %s stderr=%r" % (
            r.returncode,
            r.stderr,
        )


def case_6_timeout_receipt_blocks():
    """pending spec with timeout receipt, stop_hook_active false → exit 2, stderr has timeout"""
    with tempfile.TemporaryDirectory() as tmp:
        _, spec_bytes = write_pending_spec(tmp, "slow.json", b'{"task":"slow"}')
        write_receipt(tmp, spec_bytes, {"error_class": "timeout"})
        r = run_hook(tmp, {"cwd": tmp, "stop_hook_active": False})
        assert r.returncode == 2, "expected exit 2, got %s" % r.returncode
        assert r.stderr, "expected non-empty stderr"
        assert "timeout" in r.stderr, "stderr should mention timeout: %r" % r.stderr


def case_7_invalid_json_fail_open():
    """invalid stdin JSON → exit 0 (fail-open)"""
    with tempfile.TemporaryDirectory() as tmp:
        r = run_hook(tmp, "not json")
        assert r.returncode == 0, "expected exit 0 on bad JSON, got %s stderr=%r" % (
            r.returncode,
            r.stderr,
        )


CASES = [
    ("1: no pending dir → exit 0", case_1_no_pending_dir),
    ("2: complete receipt → exit 0", case_2_complete_receipt),
    ("3: no receipt → exit 2 + stderr names spec", case_3_no_receipt_blocks),
    ("4: stop_hook_active false → exit 2", case_4_false_still_blocks),
    ("5: stop_hook_active true → exit 0", case_5_active_bypasses),
    ("6: timeout receipt → exit 2 + stderr has timeout", case_6_timeout_receipt_blocks),
    ("7: invalid JSON → exit 0 (fail-open)", case_7_invalid_json_fail_open),
]


def main():
    passed = 0
    failed = 0
    for desc, fn in CASES:
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
    total = passed + failed
    print("%d/%d passed, %d failed" % (passed, total, failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
