# The runners — the codex lane and the grok lane

Read this before the first runner run. The main agent drives both CLI producers directly through deterministic runners. The grok lane requires the [Grok CLI](https://x.ai/cli); the codex lane requires the codex CLI and Node. Same flow for both CLI lanes; the codex walkthrough is canonical, the grok deltas follow it. Both runners serve the worker role by default and the read-only roles in report mode (see "Report mode" below).

## 0. The route and the preamble reach every lane

Both runners read the preamble their `mode` names — `lane-preamble.md` for implement, `lane-preamble-report.md` for report (resolved relative to their own directory, `<plugin-root>/scripts/`) — and prepend it verbatim to the lane prompt, ahead of the five parts. A missing preamble for the current mode makes the runner exit non-zero before spawning anything — the executor-side contract is never silently dropped. A runner's route is its spec: the keys `role`, `tier` and `basis`, with the dial from `model` and `effort` (section 1).

## 1. Write the spec

In implement mode, start from a clean working tree — `git status --porcelain` empty. The runner detects the lane's changes with `git status`, so pre-existing dirt makes an empty run look like work (see `no_diff` below).

Write the five-part spec as JSON to `.fable-advisor/pending/<slug>.json` in the target repo:

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "role": "worker", "tier": "crux", "basis": {"kind": "key-difficulty", "ref": "…"},
  "model": "gpt-6-astra", "effort": "medium", "service_tier": "fast", "idle_timeout_sec": 600
}
```

The route keys are required on both runners:

- `role` — implement mode takes `worker`; report mode takes `explorer` or `advisor`.
- `tier` — `mainstay`, `crux` or `rescue`. The runners reject `same-model`: same-model dispatch is a claude-lane dial.
- `basis` — `{"kind": …, "ref": …}`, required above `mainstay` and optional at it: a kind SKILL.md accepts for the role and tier, and a non-empty ref.
- The dial, `model` with `effort`, sits in the profile's cell for that role and tier, taken as the union of the Claude Code and Cursor tables, because a runner runs on both hosts. The codex runner checks the effective dial: an omitted `model` or `effort` counts as its omission default below. The grok runner requires both `model` and `effort` (see "Grok deltas").

A spec whose route fails these checks is rejected as `spec_invalid` before the CLI starts. The checks verify that a basis is present and well formed, not that it is true.

The tuning fields are optional and fail-loud — an out-of-range value or unknown top-level key is rejected as `spec_invalid`, never silently coerced. The receipt records the values the runner submitted to the CLI.

- `model` — `gpt-6-astra` (default), `gpt-6-luna`, or `gpt-6.1-sol`; the codex catalog is a static whitelist, so any other name is `spec_invalid`.
- `effort` — `model_reasoning_effort`: `low | medium | high | xhigh | max`. When omitted, the runner submits a per-model default: `gpt-6-astra` → `medium`, `gpt-6-luna` → `max`, `gpt-6.1-sol` → `high`; these are the runner's omission defaults, not the profile's. Which dial a task gets is the fill table's call.
- `title` — optional; first prompt line, verbatim plain text, no Markdown marker. When absent, that line is the spec file's basename without `.json` (the slug). The CLI's session list shows this line as the session name, so the user is its reader: one short phrase in the user's language that names the session goal, at most 12 Chinese characters or 6 English words, for example "Token renewal API". It carries no ticket number, slug, layer tag such as "(backend)", list of sub-items, or colon followed by detail; the five parts carry those details.
- `service_tier` — omit for Codex's own default; `"fast"` is Codex's speed mode: about 1.5× faster at about 2.5× the ChatGPT credit consumption, with no loss of intelligence. It does not apply on API-key billing.
- `profile` — omit by default; set it only when the user explicitly asks for a Codex profile. The runner passes `--profile <name>` right after `exec`, so Codex layers `$CODEX_HOME/<name>.config.toml` (for example, the provider that profile names) on top of the base config, on fresh and resumed runs alike.
- `idle_timeout_sec` — the silence deadline (default 600 s): how long after the *last* event a stalled CLI child is killed. A lane that keeps emitting events runs as long as it takes; only silence is cut, and that path skips verification, so a lane cut here loses its verification evidence entirely.
- `timeout_sec` — an optional absolute cap on the whole run; no default, so omitting it leaves the run uncapped.
- `resume_session_id` — a prior codex session id; see "Rework tickets" below.
- `mode` — `implement` (default) or `report`; see "Report mode" below.

**No model switch.** The runner never switches models. A failure before a session exists (`preparation_stalled`, or `codex_failed` with no session id yet) is tried once and reported: the receipt carries that error class, with `model_requested` and `model_used` both the requested model. The main agent re-routes it per the re-routing rule in [SKILL.md](SKILL.md).

## 2. Run the runner

This skill's base directory is `<plugin-root>/skills/orchestration`, so the runners live two levels up:

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. Wait for the runner

The lane is done when the **runner process exits** — not when the event stream shows an `end` event, and not when a sleep runs out.

Completion evidence is the pending file disappearing or the receipt appearing under `.fable-advisor/receipts/`.

While it works, the runner keeps a running marker at `.fable-advisor/running/<spec_hash>.json` (runner, pid, spec path, start time, phase `preparing | cli | verifying`, event count) and refreshes it every 60 seconds. Each refresh also writes one progress line to stderr, such as `[run-grok] running 4m00s; phase cli; 132 events; last event 0m12s ago`. The runner deletes the marker on every exit it observes; a marker not refreshed for 180 seconds belongs to a dead runner. A runner started on a spec whose marker is fresh exits with status 1, without a receipt and without starting the CLI: one spec has at most one runner at a time.

After the CLI process exits, the runner stops its execution timers and allows up to two seconds for inherited output pipes to drain. It then releases any remaining pipes, records a diagnostic, and continues to verification and the receipt using the observed exit status. Preflight, Git checks, and verification commands use the same drain bound; this does not impose a runtime limit on a verification command that is still running.

Timeouts and interrupts start an independent two-second cleanup deadline before attempting to kill the process tree. Windows `taskkill` has its own two-second runtime limit and two-second cleanup bound. A failed kill cannot leave either wait pending forever. If the diagnostic says exit was not observed, confirm and stop the surviving process before resuming or dispatching another writer; the failure receipt does not prove tree cleanup.

Letting the runner finish is always cheaper than killing it. The CLI child is spawned detached, in its own process group, so it survives a signal aimed at the runner's process group. The runner traps SIGTERM and SIGINT, kills the child tree and writes an `interrupted` receipt — but a SIGKILL of the runner still leaves the CLI running and editing the repo, with no receipt at all.

A CLI lane has no channel for a message while it runs: the runner hands the prompt over once. To correct one mid-run, stop its runner with `kill <pid>`, the pid in its running marker: that sends SIGTERM and lets the interrupt path finish. In Claude Code, `TaskStop` on the runner's background task also sends SIGTERM but force-kills shortly after, which can cut off the receipt. Then delete the old pending spec and queue the corrected contract with `resume_session_id` set to the `interrupted` receipt's session id; the lane resumes with its context.

### Waiting through Bash (Claude Code only)

Two ways to wait, no third:

- Run the runner in the foreground and let Bash return on exit. This suits a ticket expected to finish well inside the Bash `timeout`.
- Run the runner itself as a background Bash call (`run_in_background: true`), then end the turn or go on with independent work. The harness wakes the session when that process exits; judge the receipt then. The receipt gate lets the turn end while the runner is in flight.

Only the main session waits by ending its turn. A subagent that ends its turn returns its report to its parent, and the receipt gate does not run on that stop, so a subagent runs the runner in the foreground.

Write no wait loop of your own: no `sleep`, `while`, `until` or `pgrep` polling, neither in the foreground nor wrapped into a background call. A background call that wraps a loop around the runner hands the exit notice to the loop instead of the runner, and `pgrep -f <pattern>` matches the shell that runs it, so a loop on it never ends. Re-reading the output file is not a wait either, and neither is `TaskOutput`, which is officially deprecated.

For parallel lanes, start each runner as its own background call in one message, or run them in the foreground in one message.

Three independent clocks run over a dispatch, and each one can end it:

- **The runner's idle deadline** (`idle_timeout_sec`, default 600 s) kills the CLI child once the event stream has been silent that long, skips verification, and leaves an `idle_timeout` receipt. An explicit `timeout_sec` adds an absolute cap on top, with a `timeout` receipt; without it the runner imposes no total limit.
- **The harness Bash tool's `timeout`** (default 600000 ms, maximum 3600000 ms) kills the foreground call. The runner never gets to write anything, so there is no receipt at all and the pending spec stays behind. Since the runner caps nothing by default, this is the real ceiling on a foreground dispatch: a ticket expected to run long needs an explicit larger Bash `timeout`.
- **The background call** kills nothing and has no deadline of its own: only the runner's deadlines bound it. A ticket that may outlast 60 minutes runs in the background, because a single foreground call can never exceed that.

## 4. Judge the receipt

The runner prints the receipt to stdout and writes it to `.fable-advisor/receipts/<spec_hash>.json`:

- `error_class` — `complete | spec_invalid | codex_unavailable | preparation_stalled | idle_timeout | timeout | interrupted | codex_failed | verification_failed | no_diff | unexpected_diff | empty_report | git_status_failed`.
- `codex_session_id` — bound to the spawned process's event stream, immune to concurrent-session mix-ups; on a resumed run it equals the resumed id.
- `model_requested`, `model_used`, `fallback_reason` (always null), `resumed_from` (null when none), `end_to_close_ms` (terminal event to natural process close; null when the terminal event was not seen or pipes were forcibly released — a diagnostic, not a gate), `max_idle_ms` (the longest gap between consecutive events on the CLI's stream, measured from child spawn to the last event; null when no event was observed — a diagnostic, not a gate: after an `idle_timeout` it says whether the idle deadline was too tight, on a clean run how much headroom was left), `idle_timeout_sec` and `timeout_sec` (the values actually in force; `timeout_sec` null when the run was uncapped). Three layers: `model_requested` is the value the spec asked for; `model_used` and `effort` are the values the runner submitted to the CLI; the runner does not read the CLI's run events for the configuration it actually executed, so that stays unknown — when you cite a receipt's model or effort, write "submitted, not observed".
- `dirty_baseline` — `true` when the pre-run `git status --porcelain` was non-empty, `false` when it was empty, `null` when that pre-run `git status` itself failed (the run continues). Recorded in both modes on both runners.
- `role`, `tier` and `basis` — the route as the spec submitted it. `lane_finished_at` — the time the CLI process exited, recorded before the runner's verification; it is the time source for the reuse window (see "Rework tickets").
- `changed_files`, plus each verification command's actual `exit_code`, its `output_tail` (the last 2,000 characters of its combined output), and its `output_log`: the path, relative to `--cwd`, of `.fable-advisor/receipts/<spec_hash>.verification-<n>.log`, which holds that command's complete output; `null` when the runner could not write the file.

On `complete` the runner deletes the pending spec itself.

`no_diff` means `files` was non-empty and nothing changed in implement mode; the pending file stays. On an ordinary spec that is a silent no-op — investigate. On a rework ticket it is the expected answer when the lane finds the defect does not reproduce: read the report, delete the pending file, and say so. `git_status_failed` means the runner could not determine what changed in implement mode; it is not `complete`. Report mode does not raise it: a failed post-run `git status` leaves `changed_files` empty and keeps the recorded `dirty_baseline`, then `empty_report` and `complete` are decided as usual.

`idle_timeout` and `timeout` mean a clock cut the lane, not that its work is wrong — and because both paths skip verification, the receipt carries no verification evidence to judge. The cut session's data is intact on disk, so the clean recovery within the reuse window (see "Rework tickets") is a rework ticket carrying that receipt's session id in `resume_session_id`: the lane resumes and finishes its own verification. Hand-verifying a cut lane's working tree yourself is not the recovery path.

The runner is the executor of the contract's check list: it runs `verification` itself after the CLI exits, so the lane is told not to repeat it, and the receipt's output is that one run. Read a failed check's cases from its `output_log` and re-run only those; re-running the list to see what failed repeats the most expensive step. A `complete` receipt is evidence for its own contract — never acceptance of it, and never of the task.

CLI-lane acceptance = `error_class: complete`, a non-null session id, verification output you can spot-check against the working tree, **and** the diff passes the tiered acceptance in [SKILL.md](SKILL.md). A missing or non-complete receipt is not done. Tier 3 is the advisor's acceptance shape; which fill answers it is the fill table's row for the advisor.

Add `.fable-advisor/` to the target repo's `.gitignore` — receipts embed command output. Receipts are keyed by spec hash, so parallel runner invocations with distinct spec files don't collide on the receipt — but two executors in one working tree overwrite each other's edits, and distinct pending file names are not isolation. A pick-the-stronger-diff race needs one isolated working directory per contestant (`git worktree add`), each holding its own pending spec and receiving its own receipt, with the runner's `--cwd` pointing at that worktree. Contracts that run at the same time get the same isolation: each runs in its own working directory (`git worktree add`), with the runner's `--cwd` pointing into it. A worktree's `.fable-advisor/receipts/` holds its receipts and verification logs, so save them elsewhere before removing the worktree.

### The receipt gate (Claude Code only)

The receipt is mechanically enforced: a plugin Stop hook (the **receipt gate**) blocks finishing while any spec under `.fable-advisor/pending/` lacks a `complete` receipt and has no fresh running marker. A fresh marker lets the turn end, because the harness wakes the session when the backgrounded runner exits. If you abandon or re-route a pending task, delete its pending file and say so explicitly — never let the gate be the only one who knows. The gate enforces the receipt's existence; you still judge its content.

## Rework tickets

A rework ticket is a new five-part pending file that carries `resume_session_id` — the `codex_session_id` (or `grok_session_id`) from the run being reworked. The runner invokes `codex exec resume <id>` (grok: `--resume <id>`), so the lane keeps the context it already paid for; the receipt records `resumed_from` and its session id equals the resumed one. Objective = the defect, Files = the original scope, Verification = the smallest runnable check covering the failing cases and the fix's reach — no fix inside (shape in [SKILL.md](SKILL.md)). When the rework ticket also fails, attribution decides (SKILL.md "Escalation"): a contract gap keeps `resume_session_id` under a corrected contract, within the rework limit (SKILL.md "Session reuse"); a capability failure is a raise to the next tier per the SKILL.md ladder, in a fresh session — omit `resume_session_id`, and give the takeover contract the original contract, the prior lane's report, and its receipt.

Every reuse of a lane session happens only within the lane's reuse window (SKILL.md "Session reuse"; the values are in the routing profile's "Session reuse windows"). This covers `resume_session_id` on a rework ticket, a corrected contract or a resumption after a clock cut, and any `SendMessage` to a claude-lane subagent. The window counts from the lane's last activity. For a runner lane, that is the receipt's `lane_finished_at`. Never use a receipt's `finished_at`: it is recorded after verification. Past the window or the rework limit, omit `resume_session_id` and dispatch a fresh session at the same tier and dial, carrying the defect, the original contract, the prior report and the receipt.

## Report mode

`mode` is an optional key on both runners: `implement` (the default, the semantics described above) or `report`. Report mode dispatches the read-only roles — an explorer or an advisor — to the Grok or GPT family without expecting a diff:

- The CLI runs with a read-only tool set; `files` is the read scope and may be empty; `verification` may be empty.
- The CLI is briefed by the report preamble, not the worker preamble.
- An unchanged working tree is the normal outcome and is `complete`; the receipt additionally carries `mode` and `report` (the CLI's final message, which is the lane's answer).
- A working tree that was clean at start and dirty after the run is the error class `unexpected_diff`, never `complete`: a read-only role that wrote is a failure, not a bonus. When `dirty_baseline` is `true`, `unexpected_diff` is not raised; `empty_report` and `complete` are decided as usual, and `changed_files` still records the post-run observation. The read-only tool set is then the only guard.
- A post-run `git status` failure is not `git_status_failed` in report mode. `dirty_baseline` stays whatever the pre-run check recorded (`null` when that check also failed, as on a tree with no git repo). `empty_report` and `complete` are decided as usual. The read-only tool set is the write guard.
- A collected report text that is empty or whitespace-only is the error class `empty_report`, never `complete`: a read-only role that said nothing has not answered. The pending spec is kept. This still applies when git is unavailable.
- Precedence in report mode: `unexpected_diff` (a tree the lane dirtied) first, then `empty_report`, then `complete`. `git_status_failed` is not in this list.
- In Claude Code, the receipt gate applies as usual: a report-mode pending spec without a `complete` receipt blocks the session like any other.

An unknown `mode` value is `spec_invalid`. The pending/receipt flow, the wait protocol, and `resume_session_id` are unchanged.

## Grok deltas (Claude Code only)

`scripts/run-grok.mjs` — same CLI contract (`--spec`, `--cwd`), same preamble, same pending/receipt flow, same receipt gate, same wait protocol, same `mode` values.

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec keys: the five parts plus the required `role`, `tier`, `model` and `effort`, `basis` above `mainstay`, and the optional `mode`, `title`, `idle_timeout_sec`, `timeout_sec`, and `resume_session_id` only.
- `effort` — required, whitelist `low | medium | high | xhigh`; a value outside it is `spec_invalid`. The runner cannot know the CLI's own default, so without an explicit `effort` it could not check the dial; a spec that omits it is rejected as `spec_invalid` before the CLI starts. The receipt records the value the runner submitted to the CLI, never the value the CLI ran with. This is how a grok worker's dial is set without changing lane.
- `model` — required, for the same reason; a spec that omits it is rejected as `spec_invalid` before the CLI starts. When the catalog is readable, `model` is also validated against every entry `grok models` lists — a model not in the catalog is `spec_invalid`. An unreadable catalog is not `grok_unavailable`: the runner logs a diagnostic, skips the catalog check, and the real run decides availability.
- Error classes mirror the codex lane's (`grok_unavailable | grok_failed | …`, plus `no_diff`, `unexpected_diff`, `empty_report`, and `git_status_failed`). The receipt carries the same `role` / `tier` / `basis` / `lane_finished_at` / `model_requested` / `model_used` / `fallback_reason` / `resumed_from` / `end_to_close_ms` / `max_idle_ms` / `idle_timeout_sec` / `timeout_sec` fields (`fallback_reason` is always null: neither runner switches models), and additionally records `usage` and `total_cost_usd` from grok's end event. `grok_session_id` is injected by the runner (`--session-id`), not sniffed from the stream.

## Dispatch, not probes

Never pre-probe a CLI's auth state (a `grok models` login snapshot or the like): the grok CLI refreshes its login only during a real run, and a user-side provider config can bypass auth entirely, so a logged-out snapshot is not evidence that the lane is down. The most a pre-flight may check is installation (`which grok`). Route the spec and let the runner's receipt decide — `*_unavailable` triggers the re-routing rule in [SKILL.md](SKILL.md).
