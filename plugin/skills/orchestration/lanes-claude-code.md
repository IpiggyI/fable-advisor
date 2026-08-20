# The CLI lanes in Claude Code — runners, not agents

Read this before dispatching a lane in Claude Code. Neither CLI lane has a wrapper agent: the architect drives both producers directly through deterministic runners — no subagent startup cost, no wrapper that could silently self-implement. The routine lane requires the [Grok CLI](https://x.ai/cli); the cross-vendor lane requires the codex CLI and Node. The in-house lane is the `implementer` agent — a plain subagent dispatch, no runner — which keeps the plugin self-contained when both CLIs are missing.

Same flow for both CLI lanes; the codex walkthrough is canonical, the grok deltas follow it.

## 1. Write the spec

Write the five-part spec as JSON to `.fable-advisor/pending/<slug>.json` in the target repo:

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-5.6-sol", "effort": "high", "service_tier": "fast", "timeout_sec": 600
}
```

The three tuning fields are optional and fail-loud — an out-of-range value or unknown top-level key is rejected as `spec_invalid`, never silently coerced. The receipt records the values actually used.

- `model` — `gpt-5.6-sol` (default, ≈ flagship), `gpt-5.6-terra` (≈ Sonnet), or `gpt-5.6-luna` (≈ Haiku).
- `effort` — `model_reasoning_effort`: `low | medium | high | xhigh | max`, default `high`.
- `service_tier` — omit for Codex's own default; `"fast"` only when trading quality for speed.

Dial the codex lane quality-first: choosing *which* lane is still cost-first (grok is the default), but once a task is worth the codex lane, a quality bump inside it is affordable. Default `gpt-5.6-sol` at `high`; escalate effort to `xhigh`/`max` only for unusually hard tasks (both noticeably slow completion); drop to `terra`/`luna` or a lower effort only when the codex-family task is genuinely simple — that does not replace grok as the routine default.

## 2. Run the runner

This skill's base directory is `<plugin-root>/skills/orchestration`, so the runners live two levels up:

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. Judge the receipt

The runner prints the receipt to stdout and writes it to `.fable-advisor/receipts/<spec_hash>.json`: `error_class` (`complete | spec_invalid | codex_unavailable | preparation_stalled | timeout | codex_failed | verification_failed`), `codex_session_id` (bound to the spawned process's event stream — immune to concurrent-session mix-ups), `changed_files`, and the verification commands' actual exit codes and output tails.

CLI-lane acceptance = `error_class: complete`, a non-null session id, verification output you can spot-check against the working tree, **and** the diff passes the tiered acceptance in [SKILL.md](SKILL.md). A missing or non-complete receipt is not done.

For Tier 3 review, the OpenAI Codex plugin's `/codex:adversarial-review` (schema-backed verdict, read-only sandbox) is a ready-made context-clean reviewer.

The receipt is mechanically enforced: a plugin Stop hook (the **receipt gate**) blocks finishing while any spec under `.fable-advisor/pending/` lacks a `complete` receipt. On `complete` the runner deletes the pending spec itself. If you abandon or re-route a pending task, delete its pending file and say so explicitly — never let the gate be the only one who knows. The gate enforces the receipt's existence; you still judge its content.

Add `.fable-advisor/` to the target repo's `.gitignore` — receipts embed command output. Receipts are keyed by spec hash, so parallel runner invocations with distinct spec files don't collide; a pick-the-stronger-diff race is both runners as background Bash on the same spec content in two distinct pending files.

## Grok deltas

`scripts/run-grok.mjs` — same CLI contract (`--spec`, `--cwd`), same pending/receipt flow, same receipt gate.

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec keys: the five parts plus optional `model` and `timeout_sec` only — no `effort`/`service_tier` (the grok CLI has no such knobs).
- `model` — omit by default: unset sends no `-m` flag, so the CLI runs its own default and tracks the live catalog (grok-4.6 today) with zero spec edits on a generation swap. Set it only to deliberately pick a non-default catalog entry surfaced by `grok models`. When the catalog is readable, `model` is validated against every listed entry — a model not in the catalog is `spec_invalid`. An unreadable catalog is not `grok_unavailable`: the runner logs a diagnostic, skips validation, and the real run decides availability.
- Error classes mirror the codex lane's (`grok_unavailable | grok_failed | …`). The receipt additionally records `usage` and `total_cost_usd` from grok's end event, and `grok_session_id` is injected by the runner (`--session-id`), not sniffed from the stream.

## Dispatch, not probes

Never pre-probe a CLI's auth state (a `grok models` login snapshot or the like): the grok CLI refreshes its login only during a real run, and a user-side provider config can bypass auth entirely, so a logged-out snapshot is not evidence that the lane is down. The most a pre-flight may check is installation (`which grok`). Route the spec and let the runner's receipt decide — `*_unavailable` triggers the re-routing rule in [SKILL.md](SKILL.md).
