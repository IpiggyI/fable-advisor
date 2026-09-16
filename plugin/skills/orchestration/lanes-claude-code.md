# The CLI lanes in Claude Code — the runners

Read this before dispatching a lane in Claude Code. The main agent drives both CLI producers directly through deterministic runners, with no subagent startup cost. The grok lane requires the [Grok CLI](https://x.ai/cli); the codex lane requires the codex CLI and Node. The claude lane is a plain subagent dispatch, no runner. It keeps the plugin self-contained when both CLIs are missing. Its role pool ships as one agent file per (role, effort), addressed as `fable-advisor:<name>`, with the effort abbreviated in the name (`l`, `md`, `h`, `xh`): `explorer-h`, `explorer-xh`, `worker-md`, `worker-h`, `worker-xh`, `advisor-l`, `advisor-md`, `advisor-h`, `advisor-xh`. The frontmatter `effort:` keeps the full word; only the file name and `name:` are abbreviated. Because effort has no per-dispatch parameter and the model does, the dial is split: the file fixes the effort, the per-dispatch `model` picks the fill. So `explorer-*` and `worker-*` carry no `model:` key at all — a dispatch that omits `model` falls back to the session model rather than the tier the fill table named. `advisor-*` set `model: fable`. Pinning a worker's `model` to the session model is same-model dispatch. The harness's built-in Explore agent remains a light-explorer fill, but it takes no effort of its own — given no explicit `model` it runs on the session model (capped at Opus on the Claude API), so an unpinned Explore costs session price. Claude-lane reports return inside the Task result; a background dispatch's report is read from that task's output file.

Agent files load only when the session starts. A file added or renamed mid-session cannot be dispatched — the call fails with `Agent type '<name>' not found` — so a change to this pool takes effect only after the session is restarted.

Effort on the claude lane is not a per-dispatch parameter. The `Agent` tool's arguments are `description`, `prompt`, `subagent_type`, `model` and `isolation`, plus `name` in a session started with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; there is no `effort` argument. A dial can therefore reach a dispatch only two ways: the agent definition's frontmatter `effort:` (`low | medium | high | xhigh | max`; which levels exist depends on the model), or the CLI's `--effort` at startup, which sets the whole session.

**Passing `name` or not is the one switch that decides the dispatch kind, and it decides whether frontmatter effort works at all.** Omit `name` and the dispatch is a background subagent: frontmatter `effort:` takes effect. Pass `name` and it is a named teammate: frontmatter `effort:` is ignored and the dial falls back to that model's level in `~/.claude/settings.json`, silently — nothing in the dispatch says the declared value was dropped. Measured on the same session, same agents, both paths — under the pre-retirement file names `worker` and `fable-advisor`, which no longer exist, so this pair is not reproducible by name today: `worker` (then declaring `medium`) ran xhigh as a teammate and medium in the background; `fable-advisor` (declaring `high`) with `model: sonnet` ran medium as a teammate and high in the background. Dispatch this role pool without `name`, or its whole point is gone.

All four levels this pool uses are measured working on the background path: `low` with fable, `medium` with opus, `high` with opus and with sonnet, `xhigh` with sonnet. The mechanism is therefore verified for every value, but the entrances are not equal: through a **plugin-level** agent file only `medium` and `high` have actually been run, and plugin-level `low` and `xhigh` are extrapolated from project-level agent files, which is a different load path. Probe those two through this pool once the session has restarted. The overrides run both ways — opus's configured level is xhigh and both a declared `high` and a declared `medium` won over it; sonnet's is medium and a declared `xhigh` won over it — so these are real overrides, not a declaration that happened to match a default.

An agent definition with **no** `effort:` follows the configured level of the model it actually runs on, not the session's effort; the two coincide only when the subagent's model equals the session's. `claude-haiku-4-5` has no effort dimension at all — its records carry no such field.

The observation point is `~/.claude/projects/<project>/<session>/subagents/agent-*.jsonl`, where every assistant record carries the `model` and `effort` actually in force. `/tasks` is not an observation point for this: it lists named teammates only, with member name and status, showing neither model nor effort, and it does not list background subagents at all.

Model resolution order: a per-dispatch `model` wins, then the agent file's `model:`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main session's model.

**Fable as the advisor bills to usage credits, and the account has to have them enabled.** Three things are established. The host says so itself: `/advisor fable` answered "Fable 5.1 as the advisor bills to usage credits, which need to be set up for your account. Run /model fable to review and enable, then set it as the advisor."; `/model fable` then answered "Set model to `Fable 5.1` … Draws from usage credits", after which `/advisor fable` succeeded and `~/.claude/settings.json` gained an `advisorModel: "fable"` key. Since enabling, three of three requests ran wholly on `claude-fable-5-1` with no `model_changed` marker. Before enabling, only one of nine requests stayed on it for a whole run; the rest either started on `claude-fable-5-1` and switched to `claude-sonnet-5` once tool results came back, or were `claude-sonnet-5` from the first turn.

**What is not established is whether that gate is the cause of the downgrades.** It is at most a correlation: the gate is not a deterministic per-dispatch pre-check, because one pre-enablement dispatch ran wholly on fable — its first record timestamped eighteen minutes before credits were switched on — and another ran its opening segment on fable before switching away. Treat the cause as unproven, and do not substitute a guessed mechanism for it.

Two unknowns therefore stay open. First, that opening-segment-then-switch pattern has no explanation. Second, every post-enablement sample is a background subagent: the named-teammate path has no sample at all since credits were enabled, and the one pre-enablement teammate run that was sonnet from the first turn cannot be carried over, so whether fable is reachable as a teammate is untested.

The general rule survives the fix: a model is a request, not an execution guarantee, so cite it in the receipt wording of ADR 0015 — submitted, not observed. What bounds an advisor's answer is therefore that its authority is the code it reads, not the model it runs on, never an assumption about which model served it.

Same flow for both CLI lanes; the codex walkthrough is canonical, the grok deltas follow it. Both runners serve the worker role by default and the read-only roles in report mode (see "Report mode" below).

## 0. The preamble reaches every lane

Both runners read `<plugin-root>/skills/orchestration/lane-preamble.md` (resolved relative to their own directory, `<plugin-root>/scripts/`) and prepend it verbatim to the lane prompt, ahead of the five parts. A missing preamble makes the runner exit non-zero before spawning anything — the executor-side contract is never silently dropped.

## 1. Write the spec

Start from a clean working tree — `git status --porcelain` empty. The runner detects the lane's changes with `git status`, so pre-existing dirt makes an empty run look like work (see `no_diff` below).

Write the five-part spec as JSON to `.fable-advisor/pending/<slug>.json` in the target repo:

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-6-astra", "effort": "medium", "service_tier": "fast", "idle_timeout_sec": 600
}
```

The tuning fields are optional and fail-loud — an out-of-range value or unknown top-level key is rejected as `spec_invalid`, never silently coerced. The receipt records the values the runner submitted to the CLI.

- `model` — `gpt-6-astra` (default) or `gpt-5.6-luna`; the codex catalog is a static whitelist, so a retired name is `spec_invalid`.
- `effort` — `model_reasoning_effort`: `low | medium | high | xhigh | max`. The default follows the model: astra → `medium`, luna → `max`. Which dial a task gets is the fill table's call.
- `service_tier` — omit for Codex's own default; `"fast"` is Codex's speed mode: about 1.5× faster at about 2.5× the ChatGPT credit consumption, with no loss of intelligence. It does not apply on API-key billing.
- `idle_timeout_sec` — the silence deadline (default 600 s): how long after the *last* event a stalled CLI child is killed. A lane that keeps emitting events runs as long as it takes; only silence is cut, and that path skips verification, so a lane cut here loses its verification evidence entirely.
- `timeout_sec` — an optional absolute cap on the whole run; no default, so omitting it leaves the run uncapped.
- `resume_session_id` — a prior codex session id; see "Rework tickets" below.
- `mode` — `implement` (default) or `report`; see "Report mode" below.

**Fallback.** If astra fails before a session is established (`preparation_stalled`, or `codex_failed` with no session id yet), the runner retries once on luna at luna's default effort; the receipt shows `model_requested: gpt-6-astra`, `model_used: gpt-5.6-luna`, and a non-null `fallback_reason`. Once a session exists there is no fallback — a half-finished run is not redone on another model. A direct luna request never falls back. When accepting a fallen-back run, restate the downgrade in your own words; the receipt discloses, you acknowledge.

## 2. Run the runner

This skill's base directory is `<plugin-root>/skills/orchestration`, so the runners live two levels up:

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

## 3. Wait for the runner

The lane is done when the **runner process exits** — not when the event stream shows an `end` event, and not when a sleep runs out. Two ways to wait, no third:

- Run the runner in the foreground and let Bash return on exit.
- If it was backgrounded, `Read` the output file the background Bash call reported, and re-read it until the completion evidence below appears. `TaskOutput` is officially deprecated in favour of that `Read`; deprecated is not the same as unavailable today, but the wait is written against `Read`.

Completion evidence is the pending file disappearing or the receipt appearing under `.fable-advisor/receipts/`. Never `sleep N` and then `ls .fable-advisor/pending/` as a wait — a fixed sleep keeps burning the full interval after the runner has already exited. For parallel lanes, block on each background task in turn, or run the runners in the foreground in one message.

Three independent clocks run over a dispatch, and each one can end it:

- **The runner's idle deadline** (`idle_timeout_sec`, default 600 s) kills the CLI child once the event stream has been silent that long, skips verification, and leaves an `idle_timeout` receipt. An explicit `timeout_sec` adds an absolute cap on top, with a `timeout` receipt; without it the runner imposes no total limit.
- **The harness Bash tool's `timeout`** (default 600000 ms, maximum 3600000 ms) kills the foreground call. The runner never gets to write anything, so there is no receipt at all and the pending spec stays behind. Since the runner caps nothing by default, this is the real ceiling on a foreground dispatch: a ticket expected to run long needs an explicit larger Bash `timeout`.
- **The background read** kills nothing and has no deadline of its own: a `Read` of the task's output file returns whatever has been written so far, with the lane possibly still running, so one read is not a wait — re-read until the completion evidence appears, and judge that evidence (pending file gone, receipt present), not the length of the output. This is the only path with no upper bound; a single foreground call can never exceed 60 minutes.

Letting the runner finish is always cheaper than killing it. The CLI child is spawned detached, in its own process group, so it survives a signal aimed at the runner's process group. The runner traps SIGTERM and SIGINT, kills the child tree and writes an `interrupted` receipt — but a SIGKILL of the runner still leaves the CLI running and editing the repo, with no receipt at all.

## 4. Judge the receipt

The runner prints the receipt to stdout and writes it to `.fable-advisor/receipts/<spec_hash>.json`:

- `error_class` — `complete | spec_invalid | codex_unavailable | preparation_stalled | idle_timeout | timeout | interrupted | codex_failed | verification_failed | no_diff | unexpected_diff | empty_report | git_status_failed`.
- `codex_session_id` — bound to the spawned process's event stream, immune to concurrent-session mix-ups; on a resumed run it equals the resumed id.
- `model_requested`, `model_used`, `fallback_reason` (null when none), `resumed_from` (null when none), `end_to_close_ms` (terminal event to process close; null when the terminal event was not seen — a diagnostic, not a gate), `max_idle_ms` (the longest gap between consecutive events on the CLI's stream, measured from child spawn to the last event; null when no event was observed — a diagnostic, not a gate: after an `idle_timeout` it says whether the idle deadline was too tight, on a clean run how much headroom was left), `idle_timeout_sec` and `timeout_sec` (the values actually in force; `timeout_sec` null when the run was uncapped). Three layers, not two: `model_requested` is the value the spec asked for; `model_used` and `effort` are the values the runner submitted to the CLI (after a fallback, the retry's values); the runner does not read the CLI's run events for the configuration it actually executed, so that stays unknown — when you cite a receipt's model or effort, write "submitted, not observed".
- `changed_files`, plus the verification commands' actual exit codes and output tails.

`no_diff` means `files` was non-empty and nothing changed in implement mode; the pending file stays. On an ordinary spec that is a silent no-op — investigate. On a rework ticket it is the expected answer when the lane finds the defect does not reproduce: read the report, delete the pending file, and say so. `git_status_failed` means the runner could not determine what changed; it is not `complete`.

`idle_timeout` and `timeout` mean a clock cut the lane, not that its work is wrong — and because both paths skip verification, the receipt carries no verification evidence to judge. The cut session's data is intact on disk, so the clean recovery is a rework ticket carrying that receipt's session id in `resume_session_id`: the lane resumes and finishes its own verification. Hand-verifying a cut lane's working tree yourself is not the recovery path.

CLI-lane acceptance = `error_class: complete`, a non-null session id, verification output you can spot-check against the working tree, **and** the diff passes the tiered acceptance in [SKILL.md](SKILL.md). A missing or non-complete receipt is not done. Tier 3 is the advisor's acceptance shape; which fill answers it is the fill table's row for the advisor.

The receipt is mechanically enforced: a plugin Stop hook (the **receipt gate**) blocks finishing while any spec under `.fable-advisor/pending/` lacks a `complete` receipt. On `complete` the runner deletes the pending spec itself. If you abandon or re-route a pending task, delete its pending file and say so explicitly — never let the gate be the only one who knows. The gate enforces the receipt's existence; you still judge its content.

Add `.fable-advisor/` to the target repo's `.gitignore` — receipts embed command output. Receipts are keyed by spec hash, so parallel runner invocations with distinct spec files don't collide on the receipt — but two executors in one working tree overwrite each other's edits, and distinct pending file names are not isolation. A pick-the-stronger-diff race needs one isolated working directory per contestant (`git worktree add`), each holding its own pending spec and receiving its own receipt, with the runner's `--cwd` pointing at that worktree.

## Rework tickets

A rework ticket is a new five-part pending file that carries `resume_session_id` — the `codex_session_id` (or `grok_session_id`) from the run being reworked. The runner invokes `codex exec resume <id>` (grok: `--resume <id>`), so the lane keeps the context it already paid for; the receipt records `resumed_from` and its session id equals the resumed one. Objective = the defect, Files = the original scope, Verification = the check that failed — no fix inside (shape in [SKILL.md](SKILL.md)). When the rework ticket also fails, attribution decides (SKILL.md "Escalation"): a contract gap keeps `resume_session_id` under a corrected contract; a capability failure goes to a higher-tier worker in a fresh session — omit `resume_session_id` and give the takeover contract the original contract, the prior lane's report, and its receipt.

## Report mode

`mode` is an optional key on both runners: `implement` (the default, the semantics described above) or `report`. Report mode dispatches the read-only roles — an explorer or an advisor — to the Grok or GPT family without expecting a diff:

- The CLI runs with a read-only tool set; `files` is the read scope and may be empty; `verification` may be empty.
- An unchanged working tree is the normal outcome and is `complete`; the receipt additionally carries `mode` and `report` (the CLI's final message, which is the lane's answer).
- A changed working tree is the error class `unexpected_diff`, never `complete`: a read-only role that wrote is a failure, not a bonus.
- A clean working tree whose collected report text is empty or whitespace-only is the error class `empty_report`, never `complete`: a read-only role that said nothing has not answered. The pending spec is kept.
- Precedence in report mode: `unexpected_diff` (dirty tree) first, then `empty_report`, then `complete`.
- The receipt gate applies as usual: a report-mode pending spec without a `complete` receipt blocks the session like any other.

An unknown `mode` value is `spec_invalid`. The pending/receipt flow, the wait protocol, and `resume_session_id` are unchanged.

## Grok deltas

`scripts/run-grok.mjs` — same CLI contract (`--spec`, `--cwd`), same preamble, same pending/receipt flow, same receipt gate, same wait protocol, same `mode` values.

```bash
node "<plugin-root>/scripts/run-grok.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

- Spec keys: the five parts plus optional `model`, `effort`, `mode`, `idle_timeout_sec`, `timeout_sec`, and `resume_session_id` only.
- `effort` — optional, whitelist `low | medium | high | xhigh`; a value outside it is `spec_invalid`. Omitted sends no effort flag, so the CLI's own default applies; the receipt records the value the runner submitted to the CLI (null when omitted), never the value the CLI ran with. This is how a grok worker's tier is dialled without changing lane.
- `model` — omit by default: unset sends no `-m` flag, so the CLI runs its own default and tracks the live catalog (currently grok-4.6, 2026-09) with zero spec edits on a generation swap. Set it only to deliberately pick a non-default catalog entry surfaced by `grok models`. When the catalog is readable, `model` is validated against every listed entry — a model not in the catalog is `spec_invalid`. An unreadable catalog is not `grok_unavailable`: the runner logs a diagnostic, skips validation, and the real run decides availability.
- Error classes mirror the codex lane's (`grok_unavailable | grok_failed | …`, plus `no_diff`, `unexpected_diff`, `empty_report`, and `git_status_failed`). The receipt carries the same `model_requested` / `model_used` / `fallback_reason` / `resumed_from` / `end_to_close_ms` / `max_idle_ms` / `idle_timeout_sec` / `timeout_sec` fields (`fallback_reason` stays null — no model fallback is defined for the grok lane), and additionally records `usage` and `total_cost_usd` from grok's end event. `grok_session_id` is injected by the runner (`--session-id`), not sniffed from the stream.

## Dispatch, not probes

Never pre-probe a CLI's auth state (a `grok models` login snapshot or the like): the grok CLI refreshes its login only during a real run, and a user-side provider config can bypass auth entirely, so a logged-out snapshot is not evidence that the lane is down. The most a pre-flight may check is installation (`which grok`). Route the spec and let the runner's receipt decide — `*_unavailable` triggers the re-routing rule in [SKILL.md](SKILL.md).
