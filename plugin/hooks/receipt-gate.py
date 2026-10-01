"""Stop hook: block claiming completion while pending specs lack receipts.

Specs the architect queues for a lane runner live in <cwd>/.fable-advisor/
pending/. The runner writes a receipt keyed by the spec file's sha256 and
deletes the pending spec on success. While a runner works on a spec it
refreshes <cwd>/.fable-advisor/running/<sha256>.json; a fresh marker means the
lane is in flight, so the stop is allowed and the harness wakes the session when
the backgrounded runner exits. A pending spec with neither a `complete` receipt
nor a fresh marker means the work was neither finished nor consciously
abandoned, so the stop is blocked. Deliberately fail-open on malformed input:
this gate is a backstop, not the primary guardrail.
"""
import glob
import hashlib
import json
import os
import sys
import time

# Keep in step with MARKER_STALE_MS in scripts/run-codex.mjs and scripts/run-grok.mjs.
MARKER_STALE_SEC = 180


def runner_in_flight(cwd, digest):
    marker = os.path.join(cwd, ".fable-advisor", "running", digest + ".json")
    try:
        return time.time() - os.path.getmtime(marker) < MARKER_STALE_SEC
    except OSError:
        return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("{}")
        return
    # Harness requires Stop hooks to succeed when already active (avoid re-entry loops).
    if data.get("stop_hook_active"):
        print("{}")
        return
    cwd = data.get("cwd") or os.getcwd()
    pending_dir = os.path.join(cwd, ".fable-advisor", "pending")
    if not os.path.isdir(pending_dir):
        print("{}")
        return
    unmatched = []
    for spec_path in sorted(glob.glob(os.path.join(pending_dir, "*.json"))):
        name = os.path.basename(spec_path)
        try:
            with open(spec_path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            unmatched.append(name)
            continue
        if runner_in_flight(cwd, digest):
            continue
        receipt_path = os.path.join(cwd, ".fable-advisor", "receipts", digest + ".json")
        try:
            with open(receipt_path, encoding="utf-8") as f:
                receipt = json.load(f)
        except (OSError, ValueError):
            unmatched.append(name + " (no receipt)")
            continue
        if receipt.get("error_class") != "complete":
            unmatched.append("%s (receipt: %s)" % (name, receipt.get("error_class")))
    if unmatched:
        sys.stderr.write(
            "RECEIPT GATE: pending spec(s) without a complete receipt and with no runner in flight: "
            + ", ".join(unmatched)
            + ". Run the matching runner (`node <plugin-root>/scripts/run-codex.mjs` or "
            "`node <plugin-root>/scripts/run-grok.mjs`) --spec .fable-advisor/pending/<file> --cwd <repo> "
            "as a background Bash call, then end the turn; the harness wakes the session when it exits. "
            "If the task was re-routed or abandoned, delete the pending spec file "
            "and disclose that to the user before finishing."
        )
        sys.exit(2)
    print("{}")


if __name__ == "__main__":
    main()
