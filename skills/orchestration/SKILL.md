---
name: orchestration
description: Routing doctrine for the architect-as-orchestrator pattern — how a session running the smartest model delegates implementation to cheaper cross-vendor lanes to minimize cost. USE WHEN delegating implementation work, choosing between grok-implementer/codex-implementer lanes, writing a spec for a subagent, deciding whether to consult fable-advisor, managing session cost or token spend, or running any multi-task build where the session is the architect.
---

# Orchestration — the architect's routing doctrine

The session is the architect: it owns requirements, architecture, decomposition, specs, routing, and verification. It should almost never type implementation code. Every implementation task gets routed to the cheapest lane that is adequate for it — escalation is deliberate, per task, never a fixed binding.

## Cost discipline — the prime directive

The session model is the most expensive lane in the system, on both input and output tokens. The whole economic case for this pattern is keeping its token volume low: spend Fable on judgment, spend Sonnet on volume. Three rules follow.

**Emit judgment, not volume.** The architect's output is decomposition, specs, routing decisions, verdicts on diffs, and short reports. It does not type implementation code, test bodies, boilerplate, or config files. A code block longer than an interface signature or a few illustrative lines is a spec that hasn't been delegated yet — stop and delegate it. Fixing a lane's bug by hand is the same failure in disguise: send a corrected spec back to the cheap lane instead.

**Keep the context lean.** Everything in the architect's context is re-read at architect prices on every turn. Delegate broad exploration, codebase searches, and log-grepping to a cheap read-only agent and keep only the conclusions; read files yourself only when the decision genuinely depends on the exact code. Don't paste long files, full diffs, or verbose command output into the conversation when a path reference or an excerpt will do.

**Reason once, then hand off.** Do the hard thinking — the architecture, the interface design, the debugging hypothesis — in one pass, capture it in the spec, and let the cheap lane carry it from there. Re-deriving decisions across turns burns the premium twice.

What stays with the architect regardless of cost: decomposition, interface design, hypothesis selection when debugging, spec writing, lane routing, and judging verification evidence. Those tokens are what the premium is for — everything else is a candidate for delegation.

## The lanes

| Lane | Producer | Invoke | Route here when |
|---|---|---|---|
| Routine | Grok 4.5 | `grok-implementer` agent | The spec fully determines the outcome: boilerplate, wiring, CRUD, mechanical edits, straightforward features. **Default lane.** Requires the [Grok CLI](https://x.ai/cli). |
| Cross-vendor | GPT-5.6 Sol (high reasoning) | `codex-implementer` agent | Correctness/completeness is critical enough to want a second implementation, or as the alternative family when the grok lane is unavailable. Requires the codex CLI. |
| Fallback | Sonnet / Opus (in-house Claude) | `implementer` agent | Both CLI lanes are unavailable or not installed. Keeps the plugin self-contained — no external CLI. Same family as the architect, so no cross-vendor review; use `model="opus"` for high-stakes work reached this way. |
| Judgment | Fable 5 | `fable-advisor` agent | Not an implementation lane. See "Commitment boundaries" below. |

Deciding rule: how much does the outcome depend on judgment the spec can't capture? Little → the default grok lane; you will verify anyway. A lot, and mistakes are costly → race both lanes on the same spec and pick the stronger diff, or keep that piece with the architect.

Grok vs codex is not a capability ranking — it's a failure-distribution question. Both are non-Anthropic families, so either lane's output gets genuine cross-vendor review from the Claude architect; racing them buys a *third* independent perspective for one extra lane's cost.

If a lane returns `unavailable` or `timeout`, re-route the same spec to the other lane and say so explicitly in your report — never quietly absorb the substitution. If both CLI lanes are unavailable, route to the `implementer` agent (the in-house Claude fallback) and state the downgrade plainly — it shares the architect's family, so you lose cross-vendor review; that's the cost of the CLIs being down.

## The spec contract

Implementers share none of your conversation context. Every delegation prompt carries all five parts:

1. **Objective** — what to build or change, one paragraph
2. **Files** — exact paths to create or modify
3. **Interfaces** — signatures, types, or API shapes the code must match
4. **Constraints** — project conventions, things not to touch
5. **Verification** — the command(s) that prove it works

A spec you can't finish writing is a signal the decision isn't made yet — that's architect work, not a reason to hand the ambiguity to a cheaper model.

## Spawning the CLI lanes — keep the guardrail structural

`codex-implementer` and `grok-implementer` restrict themselves to `Bash, Read, Grep, Glob` — no `Write`/`Edit` — on purpose: it structurally removes the direct-edit path to silent self-implementation (arbitrary Bash can still write files, which is why the SESSION-evidence backstop below stays mandatory). That whitelist only holds on the plain subagent path. **Spawn these two lanes without a `name`.** The plugin also carries this rule as a PreToolUse hook (`hooks/hooks.json`) that denies named CLI-lane spawns at the harness layer, fail-closed when no python runtime exists.

Passing a `name` routes the spawn to an in-process teammate, which ignores the agent's tool whitelist and hands it the full default toolset — `Write`/`Edit` included — so a named codex/grok lane can quietly write the code itself and report success. Verified on the harness: named → teammate (Write/Edit present); no `name` → `local_agent` (Write/Edit don't exist).

- **CLI lanes: never pass `name`.** For parallel fan-out use `run_in_background: true` — unnamed background subagents still run concurrently and still keep the whitelist; you just can't message them mid-run, so send a fresh self-contained spec instead of a follow-up.
- **`implementer` (in-house Claude) is exempt** — it has no whitelist and is *meant* to write code directly. Name it freely if you want it addressable.

This is the primary defense; the SESSION-evidence check under Verification is the backstop.

## Parallelism

Independent specs (no shared files, no ordering dependency) launch as parallel agents in a single message. Sequential chains and single-file surgery stay serial. For high-stakes work, a pick-the-stronger-diff race — `grok-implementer` and `codex-implementer` on the same spec, architect judges — buys three-vendor confidence for one extra lane's cost.

## Commitment boundaries

Consult `fable-advisor` (read-only, verdict in under 300 words) at the moments that decide whether the next hour is wasted:

- Before committing to an architecture, data migration, API shape, or refactor strategy
- Whenever the same problem has resisted two distinct attempts
- Once before declaring a multi-step deliverable done

Pass it the decision, the constraints, and the options considered. Act on the verdict or surface the disagreement — never silently ignore it. (If the session itself already runs on Fable, the advisor still earns its keep as a context-clean skeptic reading the actual code.)

## Verification

Reports are claims, not evidence. Before accepting any lane's work: read the diff, and re-run the verification command (or spot-check its quoted output against the working tree). "Should work", "tests should pass", or a report with no command output means the task is not done. A lane that reports a spec gap gets a corrected spec, not a "use your judgment".

Codex-lane work gets one backstop check — **channel authenticity** — for a lane that slipped through spawned wrong. The wrapper agent has been observed writing the code itself instead of driving codex (spawned as a named teammate, which strips its tool whitelist — see the spawning rule above). Its report must carry a SESSION line (codex session id + rollout file path); verify the cited file exists under `~/.codex/sessions/` and its `cwd` points at this repo before accepting the diff. No SESSION line, or a session pointing elsewhere, means impersonation: reject the report and re-dispatch with the channel requirement restated.

A subagent that goes idle without delivering its report is not a blocker: verify the workspace evidence directly (diff, verification command, and for the codex lane the newest matching rollout file) and move on — don't stall the pipeline waiting for a resend.

## Subagent lifecycle

A subagent spawned with a `name` ("teammate") persists after finishing so it can be messaged again — which means every named batch you don't clean up lingers as "background work" until the session exits. (The CLI lanes, spawned unnamed per the rule above, aren't addressable this way — they finish and return.) Two rules:

- Serial batches (same file, strict ordering) gain nothing from backgrounding: run them with `run_in_background: false` and consume the report inline.
- When a batch does run in the background, stop its teammate once its work is verified and it has no follow-up role. Don't leave verified lanes idling to session end.
