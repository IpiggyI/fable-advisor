# The CLI lanes in Claude Code — runners, not agents

Read this before dispatching a lane in Claude Code. Neither CLI lane has a wrapper agent: the architect drives both producers directly through deterministic runners — no subagent startup cost, no wrapper that could silently self-implement. The routine lane requires the [Grok CLI](https://x.ai/cli); the cross-vendor lane requires the codex CLI and Node. The in-house lane is the `implementer` agent — a plain subagent dispatch, no runner — which keeps the plugin self-contained when both CLIs are missing.

Same flow for both CLI lanes; the codex walkthrough is canonical, the grok deltas follow it.

## 0. The preamble reaches every lane

Both runners read `<plugin-root>/skills/orchestration/lane-preamble.md` (resolved relative to their own directory, `<plugin-root>/scripts/`) and prepend it verbatim to the lane prompt, ahead of the five parts. A missing preamble makes the runner exit non-zero before spawning anything — the executor-side contract is never silently dropped. Do not paste the preamble into the spec; the spec carries only the contract.

## 1. Write the spec

Start from a clean working tree — `git status --porcelain` empty. The runner detects the lane's changes with `git status`, so pre-existing dirt makes an empty run look like work (see `no_diff` below).

Write the five-part spec as JSON to `.fable-advisor/pending/<slug>.json` in the target repo:

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-6-astra", "effort": "medium", "service_tier": "fast", "timeout_sec": 600
}
```

The tuning fields are optional and fail-loud — an out-of-range value or unknown top-level key is rejected as `spec_invalid`, never silently coerced. The receipt records the values actually used.

- `model` — `gpt-6-astra` (default) or `gpt-5.6-luna`; the codex catalog is a static whitelist, so a retired name is `spec_invalid`.
- `effort` — `model_reasoning_effort`: `low | medium | high | xhigh | max`. The default follows the model: astra → `medium`, luna → `max`. Recommended use (doctrine, not enforced): astra at `medium` or `high`; luna only at `max`.
- `service_tier` — omit for Codex's own default; `"fast"` only when trading quality for speed.
- `timeout_sec` — wall clock for killing a stuck process; not a waiting strategy.
- `resume_session_id` — a prior codex session id; see "Rework tickets" below.

Dial the codex lane quality-first: choosing *which* lane is cost-first (grok is the default, and the lane-level comparison prices codex at its default dial, astra at `medium`), but once a task is worth the codex lane, a quality bump inside it is affordable. Escalate to `high` for unusually hard tasks. Luna is not a cheaper way into the codex lane: request it only on a user declaration, or when the task is simple and the GPT family is wanted anyway.

**Fallback.** If astra fails before a session is established (`preparation_stalled`, or `codex_failed` with no session id yet), the runner retries once on luna at luna's default effort; the receipt shows `model_requested: gpt-6-astra`, `model_used: gpt-5.6-luna`, and a non-null `fallback_reason`. Once a session exists there is no fallback — a half-finished run is not redone on another model. A direct luna request never falls back. When accepting a fallen-back run, restate the downgrade in your own words; the receipt discloses, you acknowledge.

## 2. Run the runner

This skill's base directory is `<plugin-root>/skills/orchestration`, so the runners live two levels up:

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. Wait for the runner

The lane is done when the **runner process exits** — not when the event stream shows an `end` event, and not when a sleep runs out. Two ways to wait, no third:

- Run the runner in the foreground and let Bash return on exit.
- If it was backgrounded, call `TaskOutput(task_id, block=true)` on that Bash task.

Completion evidence is the pending file disappearing or the receipt appearing under `.fable-advisor/receipts/`. Never `sleep N` and then `ls .fable-advisor/pending/` as a wait — a fixed sleep keeps burning the full interval after the runner has already exited. `timeout_sec` only kills a stuck process; a Bash `timeout` only caps a foreground block. For parallel lanes, block on each background task in turn, or run the runners in the foreground in one message.

## 4. Judge the receipt

The runner prints the receipt to stdout and writes it to `.fable-advisor/receipts/<spec_hash>.json`:

- `error_class` — `complete | spec_invalid | codex_unavailable | preparation_stalled | timeout | codex_failed | verification_failed | no_diff | git_status_failed`.
- `codex_session_id` — bound to the spawned process's event stream, immune to concurrent-session mix-ups; on a resumed run it equals the resumed id.
- `model_requested`, `model_used`, `fallback_reason` (null when none), `resumed_from` (null when none), `end_to_close_ms` (terminal event to process close; null when the terminal event was not seen — a diagnostic, not a gate).
- `changed_files`, plus the verification commands' actual exit codes and output tails.

`no_diff` means `files` was non-empty and nothing changed; the pending file stays. On an ordinary spec that is a silent no-op — investigate. On a rework ticket it is the expected answer when the lane finds the defect does not reproduce: read the report, delete the pending file, and say so. `git_status_failed` means the runner could not determine what changed; it is not `complete`.

CLI-lane acceptance = `error_class: complete`, a non-null session id, verification output you can spot-check against the working tree, **and** the diff passes the tiered acceptance in [SKILL.md](SKILL.md). A missing or non-complete receipt is not done.

For Tier 3 review, the OpenAI Codex plugin's `/codex:adversarial-review` (schema-backed verdict, read-only sandbox) is a ready-made context-clean reviewer.

The receipt is mechanically enforced: a plugin Stop hook (the **receipt gate**) blocks finishing while any spec under `.fable-advisor/pending/` lacks a `complete` receipt. On `complete` the runner deletes the pending spec itself. If you abandon or re-route a pending task, delete its pending file and say so explicitly — never let the gate be the only one who knows. The gate enforces the receipt's existence; you still judge its content.

Add `.fable-advisor/` to the target repo's `.gitignore` — receipts embed command output. Receipts are keyed by spec hash, so parallel runner invocations with distinct spec files don't collide; a pick-the-stronger-diff race is both runners as background Bash on the same spec content in two distinct pending files.

## Rework tickets

A rework ticket is a new five-part pending file that carries `resume_session_id` — the `codex_session_id` (or `grok_session_id`) from the run being reworked. The runner invokes `codex exec resume <id>` (grok: `--resume <id>`), so the lane keeps the context it already paid for; the receipt records `resumed_from` and its session id equals the resumed one. Objective = the defect, Files = the original scope, Verification = the check that failed — no fix inside (shape in [SKILL.md](SKILL.md)). After two failed rounds the task goes back through stage 1 in a fresh session: omit `resume_session_id`.

## Grok deltas

`scripts/run-grok.mjs` — same CLI contract (`--spec`, `--cwd`), same preamble, same pending/receipt flow, same receipt gate, same wait protocol.

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec keys: the five parts plus optional `model`, `timeout_sec`, and `resume_session_id` only — no `effort`/`service_tier` (the grok CLI has no such knobs).
- `model` — omit by default: unset sends no `-m` flag, so the CLI runs its own default and tracks the live catalog (currently grok-4.6, 2026-09) with zero spec edits on a generation swap. Set it only to deliberately pick a non-default catalog entry surfaced by `grok models`. When the catalog is readable, `model` is validated against every listed entry — a model not in the catalog is `spec_invalid`. An unreadable catalog is not `grok_unavailable`: the runner logs a diagnostic, skips validation, and the real run decides availability.
- Error classes mirror the codex lane's (`grok_unavailable | grok_failed | …`, plus `no_diff` and `git_status_failed`). The receipt carries the same `model_requested` / `model_used` / `fallback_reason` / `resumed_from` / `end_to_close_ms` fields (`fallback_reason` stays null — no model fallback is defined for the grok lane), and additionally records `usage` and `total_cost_usd` from grok's end event. `grok_session_id` is injected by the runner (`--session-id`), not sniffed from the stream.

## Dispatch, not probes

Never pre-probe a CLI's auth state (a `grok models` login snapshot or the like): the grok CLI refreshes its login only during a real run, and a user-side provider config can bypass auth entirely, so a logged-out snapshot is not evidence that the lane is down. The most a pre-flight may check is installation (`which grok`). Route the spec and let the runner's receipt decide — `*_unavailable` triggers the re-routing rule in [SKILL.md](SKILL.md).
