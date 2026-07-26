---
name: orchestration
description: Routing doctrine for the architect-as-orchestrator pattern — how a session running the smartest model delegates implementation to cheaper cross-vendor lanes to minimize cost. USE WHEN delegating implementation work, choosing between the grok-implementer agent and codex runner lanes, writing a spec for a subagent, deciding whether to consult fable-advisor, managing session cost or token spend, or running any multi-task build where the session is the architect.
---

# Orchestration — the architect's routing doctrine

The session is the architect: it owns requirements, architecture, decomposition, specs, routing, and verification. It should almost never type implementation code. Routing an implementation task is two-stage: first narrow to the lanes whose capability is adequate for how much the task depends on judgment the spec can't capture, then choose among that adequate set by Pareto trade-off — speed, price, capability, specialty — against the routing profile the user has declared. Escalation is deliberate, per task, never a fixed binding.

## Cost discipline — the prime directive

The session model is the most expensive lane in the system, on both input and output tokens. The whole economic case for this pattern is keeping its token volume low: spend the flagship on judgment, spend the cheap lanes on volume. Three rules follow.

**Emit judgment, not volume.** The architect's output is decomposition, specs, routing decisions, verdicts on diffs, and short reports. It does not type implementation code, test bodies, boilerplate, or config files. A code block longer than an interface signature or a few illustrative lines is a spec that hasn't been delegated yet — stop and delegate it. Fixing a lane's bug by hand is the same failure in disguise: send a corrected spec back to the cheap lane instead.

**Keep the context lean.** Everything in the architect's context is re-read at architect prices on every turn. Delegate broad exploration, codebase searches, and log-grepping to a cheap read-only agent and keep only the conclusions; read files yourself only when the decision genuinely depends on the exact code. Don't paste long files, full diffs, or verbose command output into the conversation when a path reference or an excerpt will do.

**Reason once, then hand off.** Do the hard thinking — the architecture, the interface design, the debugging hypothesis — in one pass, capture it in the spec, and let the cheap lane carry it from there. Re-deriving decisions across turns burns the premium twice.

What stays with the architect regardless of cost: decomposition, interface design, hypothesis selection when debugging, spec writing, lane routing, and judging verification evidence. Those tokens are what the premium is for — everything else is a candidate for delegation. Pareto selection operates *between* lanes; it never trades away delegation itself, and no declared speed or specialty preference licenses the architect to type the implementation instead.

## The lanes

| Lane | Producer | Invoke | Route here when |
|---|---|---|---|
| Routine | Grok 4.5 | `grok-implementer` agent | The spec fully determines the outcome: boilerplate, wiring, CRUD, mechanical edits, straightforward features. **Default lane.** Requires the [Grok CLI](https://x.ai/cli). |
| Cross-vendor | GPT-5.6 (Sol/Terra/Luna, selectable effort) | `scripts/run-codex.mjs` runner, driven by the architect | Correctness/completeness is critical enough to want a second implementation, or as the alternative family when the grok lane is unavailable. Requires the codex CLI and Node. |
| In-house | Opus (in-house Claude; currently Opus as of 2026-07, chosen while Sonnet's price/capability positioning is poor — re-evaluate if the lane is swapped back to a future Sonnet) | `implementer` agent | Routed here on purpose when the user's profile marks the task as this lane's specialty (e.g. frontend), when a task that carries real complexity but stays small is worth isolating from the architect's context, or when a declared quota or deadline constraint points here; and as the fallback when the grok agent and the codex runner are both unavailable or not installed. Keeps the plugin self-contained — no external CLI. Same flagship tier as the architect (value is context isolation, not a cheaper unit price). Disclose three costs on every route here: same family as the architect, so no cross-vendor review; it shares the main session's Anthropic quota; it is the highest unit price under the user's current ranking. |
| Handoff | Any harness the user picks, driven by the user by hand | Five-part spec + operating guide written to `.fable-advisor/handoff/<slug>.md`, executed manually by the user | Only after an explicit user declaration. Pareto coordinates: price ≈ 0 (arbitrage on a subscription the user already pays for), slowest lane by far (a human round-trip), capability = whatever the user picks at the time, available only while the user is present and has declared it. See "The handoff lane" below. |
| Judgment | Fable 5 | `fable-advisor` agent | Not an implementation lane. See "Commitment boundaries" below. |

**Deciding rule, stage 1 — adequacy.** How much does the outcome depend on judgment the spec can't capture? Little → every lane is adequate and the grok lane is the routine default; you will verify anyway. A lot, and mistakes are costly → the adequate set narrows to the codex lane, a race of both lanes on the same spec with you picking the stronger diff, or keeping that piece with the architect. A routine-lane task that fails its spec once gets a corrected spec; twice, it escalates out of the routine lane — repeated failure is evidence the task was misclassified, so re-run stage 1 rather than resending the spec a third time.

**Stage 2 — Pareto choice inside the adequate set.** Among the lanes stage 1 left standing, trade speed, price, capability, and specialty against the user's declared routing profile (next section). A specialty hit is a tie-breaker between lanes of the same adequacy class — it never promotes a lane that stage 1 ruled out, because a preference must not override a correctness judgment. With no declarations, this degrades to the cheapest adequate lane — the pre-profile default behavior, unchanged. The handoff lane is a *conditional member* of that set: it joins the candidates only once the user has declared it for this task or this session (see "User routing profile" and "The handoff lane" below).

Grok vs codex is not a capability ranking — it's a failure-distribution question. Both are non-Anthropic families, so either lane's output gets genuine cross-vendor review from the Claude architect; racing them buys a *third* independent perspective for one extra lane's cost. Any ranking of the two belongs to the user's profile, not to this doctrine.

If a lane returns `unavailable` or `timeout`, re-route the same spec to the other lane and say so explicitly in your report — never quietly absorb the substitution. If both CLI lanes are unavailable, route to the `implementer` agent (the in-house lane) and state the downgrade plainly — it shares the architect's family, so you lose cross-vendor review; that's the cost of the CLIs being down.

## User routing profile

Stage 2 runs on inputs the architect cannot probe: remaining quota on a CLI, delivery pressure, and the user's own sense of which family is better at what are user-owned facts. They enter routing only as declarations, in two layers.

**Persistent judgments** — specialty tables, lane rankings — live in the user's own rules file, not in this repo: they are one user's experience, not project doctrine. Each entry carries the precondition that justifies it and the condition that voids it, anchored to a model generation and date-stamped, so a generation swap retires the entry instead of quietly steering routing with a stale belief.

**Volatile state** — quota balance, deadline pressure — is declared verbally when the work starts ("grok's quota is nearly out", "this one's a rush"). It holds for that session only and is never written to disk; a persisted quota file is stale the moment it is written. A declaration made this way is an input to stage 2 for the rest of the session.

**The handoff declaration.** The handoff lane is declared the same way — per task or per session ("this one goes to handoff") — but the declaration does more than weight the choice: it is what makes the lane exist as a candidate at all. **The handoff lane never enters stage 2 uninvited — it becomes selectable only after an explicit user declaration; the architect may suggest it for a large, fully-specified, non-urgent task, but a suggestion never routes.** The lane physically depends on the user's own hands, so routing there unasked doesn't produce slow work, it produces stalled work. Small tasks are explicitly not worth suggesting: the human round-trip overhead swamps the saving.

**The low-confidence escape hatch.** Ask the user before routing in exactly two cases, offering at least two options with the reason for each:

1. Declared constraints conflict on the dimension that decides the route — a declared deadline pointing at the fastest lane while the task is correctness-critical and points at codex.
2. The task is high-risk (correctness-critical or hard to reverse) and the profile is silent on the dimension that would decide it.

It does not fire for: a mechanical task the spec fully determines; the mere absence of declarations (that is the documented default, not an ambiguity); or a lane being unavailable (re-route and disclose, per the rule above — the hatch does not duplicate that mechanism). For a parallel fan-out, ask at most once, covering the whole batch's routing plan.

## The spec contract

Implementers share none of your conversation context. Every delegation prompt carries all five parts:

1. **Objective** — what to build or change, one paragraph
2. **Files** — exact paths to create or modify
3. **Interfaces** — signatures, types, or API shapes the code must match
4. **Constraints** — project conventions, things not to touch
5. **Verification** — the command(s) that prove it works

A spec you can't finish writing is a signal the decision isn't made yet — that's architect work, not a reason to hand the ambiguity to a cheaper model.

## Spawning the grok lane — keep the guardrail structural

`grok-implementer` restricts itself to `Bash, Read, Grep, Glob` — no `Write`/`Edit` — on purpose: it structurally removes the direct-edit path to silent self-implementation (arbitrary Bash can still write files, which is why independent verification stays mandatory). That whitelist only holds on the plain subagent path. **Spawn this lane without a `name`.** The plugin also carries this rule as a PreToolUse hook (`hooks/hooks.json`) that denies named CLI-lane spawns at the harness layer, fail-closed when no python runtime exists.

Passing a `name` routes the spawn to an in-process teammate, which ignores the agent's tool whitelist and hands it the full default toolset — `Write`/`Edit` included — so a named lane can quietly write the code itself and report success. Verified on the harness: named → teammate (Write/Edit present); no `name` → `local_agent` (Write/Edit don't exist).

- **grok lane: never pass `name`.** For parallel fan-out use `run_in_background: true` — unnamed background subagents still run concurrently and still keep the whitelist; you just can't message them mid-run, so send a fresh self-contained spec instead of a follow-up.
- **`implementer` (in-house Claude) is exempt** — it has no whitelist and is *meant* to write code directly. Name it freely if you want it addressable.

## The codex lane — a runner, not an agent

The codex lane has no wrapper agent: the architect drives GPT-5.6 Sol directly through the deterministic runner. One flow:

1. Write the five-part spec as JSON to `.fable-advisor/pending/<slug>.json` in the target repo:

```json
{
  "objective": "…", "files": ["…"], "interfaces": "…", "constraints": "…",
  "verification": ["…shell command…"],
  "model": "gpt-5.6-sol", "effort": "high", "service_tier": "fast", "timeout_sec": 600
}
```

(All three tuning fields are optional and fail-loud — an out-of-range value is rejected as `spec_invalid`, never silently coerced:
- `model` — `gpt-5.6-sol` (default, ≈ Opus / flagship), `gpt-5.6-terra` (≈ Sonnet), or `gpt-5.6-luna` (≈ Haiku).
- `effort` — `model_reasoning_effort`: `low | medium | high | xhigh | max`, default `high`.
- `service_tier` — omit for Codex's own default; set `"fast"` only when you want speed over quality.
Unknown top-level keys are rejected. The receipt records the `model`, `effort`, and `service_tier` actually used.)

**Dialing the codex lane — quality-first within the lane.** Choosing *which* lane is still cost-first (grok is the default); the cost win comes from delegating off the architect at all, so a quality bump inside the cheap lanes is affordable. Once a task is worth the codex lane (correctness/completeness critical), bias toward quality within it:

- **Default to `gpt-5.6-sol` at `high`** — the quality baseline.
- **Escalate `effort` to `xhigh` or `max` only for unusually hard tasks** (subtle correctness, tricky concurrency, wide refactors). Both noticeably slow completion — escalate deliberately, not by default.
- **Drop to `terra`/`luna` or a lower effort only when the codex-family task is genuinely simple.** This does not replace grok as the routine default; it's for when you specifically want the OpenAI family on light work.
- **Add `service_tier: "fast"` only when trading quality for speed.**

2. Run the runner. This skill's base directory is `<plugin-root>/skills/orchestration`, so the runner lives two levels up:

```bash
node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"
```

3. Judge the receipt. The runner prints it to stdout and writes it to `.fable-advisor/receipts/<spec_hash>.json`: `error_class` (`complete | spec_invalid | codex_unavailable | preparation_stalled | timeout | codex_failed | verification_failed`), `codex_session_id` (bound to the spawned process's event stream — immune to concurrent-session mix-ups), `changed_files`, and the verification commands' actual exit codes and output tails. Acceptance = `error_class: complete` **and** you read the diff. A missing or non-complete receipt is not done.

The receipt is mechanically enforced: a plugin Stop hook (the **receipt gate**) blocks finishing while any spec under `.fable-advisor/pending/` lacks a `complete` receipt. On `complete` the runner deletes the pending spec itself. If you abandon or re-route a pending task, delete its pending file and say so explicitly — never let the gate be the only one who knows.

Add `.fable-advisor/` to the target repo's `.gitignore` — receipts embed command output. Receipts are keyed by spec hash, so parallel runner invocations with distinct spec files don't collide.

## The handoff lane — user-mediated, no mechanical gate

Every other lane requires this session to be able to invoke the producer. The handoff lane trades that away: the user carries the work to a harness of their own choosing (a fixed subscription whose marginal cost is ≈ 0) and brings the result back. What the architect produces is a file, not a process. The flow:

1. Write `.fable-advisor/handoff/<slug>.md` — the same five-part spec, plus an **operating guide**: which model and mode to run it in, and anything the receiving executor needs to get it right in one pass. The executor has zero context and cannot ask you back, so the file must stand alone.
2. The user runs it, by hand, in their harness. There is no receipt, no report contract, and no timeout you can observe.
3. **Acceptance is the diff.** Read the changed files yourself and re-run the verification commands yourself — do not accept the other harness's summary as evidence. The producing model family is unknown, so treat the output as an untrusted source: the fact that it comes back "done" carries no weight the diff doesn't independently support. A returned report is a convenience, not a requirement.

**The handoff directory is outside the receipt gate's field of view** — the gate only reads `.fable-advisor/pending/`. This is deliberate: a handoff spec lives across the user's absence, so filing it under `pending/` would block session close on work that is by design not finished in this session. The backstop is a soft rule instead of a hook, and it is fail-open: before ending a session, sweep `.fable-advisor/handoff/` and report every open item — never leave a spec under `.fable-advisor/handoff/` unresolved: land it, abandon it (delete the file and say so), or state plainly that it carries over to the next session.

Sweet spot: large-grained, spec fully settled, no time pressure, and the user has said the external quota is there to burn. Outside it, prefer a lane you can invoke yourself.

## Parallelism

Independent specs (no shared files, no ordering dependency) launch as parallel agents in a single message. Sequential chains and single-file surgery stay serial. For high-stakes work, a pick-the-stronger-diff race — `grok-implementer` (unnamed background subagent) and the codex runner (background Bash) on the same spec, architect judges — buys three-vendor confidence for one extra lane's cost.

## Commitment boundaries

Consult `fable-advisor` (read-only, verdict in under 300 words) at the moments that decide whether the next hour is wasted:

- Before committing to an architecture, data migration, API shape, or refactor strategy
- Whenever the same problem has resisted two distinct attempts
- Once before declaring a multi-step deliverable done

Pass it the decision, the constraints, and the options considered. Act on the verdict or surface the disagreement — never silently ignore it. (If the session and the advisor already share a flagship-tier model, the advisor still earns its keep as a context-clean skeptic reading the actual code.)

## Verification

Reports are claims, not evidence. Before accepting any lane's work: read the diff, and re-run the verification command (or spot-check its quoted output against the working tree). "Should work", "tests should pass", or a report with no command output means the task is not done. A lane that reports a spec gap gets a corrected spec, not a "use your judgment".

Codex-lane work is accepted through its receipt: `error_class: complete`, a non-null `codex_session_id`, and verification output you can spot-check against the working tree. The receipt gate (Stop hook) enforces the receipt's existence; you still judge its content — read the diff before accepting.

A subagent that goes idle without delivering its report is not a blocker: verify the workspace evidence directly (diff, verification command, and for the codex lane the newest matching rollout file) and move on — don't stall the pipeline waiting for a resend.

## Subagent lifecycle

A subagent spawned with a `name` ("teammate") persists after finishing so it can be messaged again — which means every named batch you don't clean up lingers as "background work" until the session exits. (The grok lane, spawned unnamed per the rule above, isn't addressable this way — it finishes and returns.) Two rules:

- Serial batches (same file, strict ordering) gain nothing from backgrounding: run them with `run_in_background: false` and consume the report inline.
- When a batch does run in the background, stop its teammate once its work is verified and it has no follow-up role. Don't leave verified lanes idling to session end.
