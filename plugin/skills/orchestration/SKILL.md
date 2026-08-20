---
name: orchestration
description: Routing doctrine for the architect-as-orchestrator pattern. USE WHEN acting as architect on implementation work or a multi-ticket build, routing tasks to lanes (grok/codex runners in Claude Code, pinned-model dispatches in Cursor), writing a five-part spec, verifying or accepting lane work, consulting fable-advisor, or managing session cost.
---

# Orchestration — the architect's routing doctrine

The session is the architect: it owns requirements, architecture, decomposition, specs, routing, and verification — and it should almost never type implementation code. Routing runs in two stages, adequacy then Pareto (under "The lanes" below); escalation is deliberate, per task, never a fixed binding.

## Cost discipline — the prime directive

The session model is the most expensive lane in the system, on both input and output tokens. The whole economic case for this pattern is keeping its token volume low: spend the flagship on judgment, spend the cheap lanes on volume. Three rules follow.

**Emit judgment, not volume.** The architect's output is decomposition, specs, routing decisions, verdicts on diffs, and short reports — not implementation code, test bodies, boilerplate, or config files. A code block longer than an interface signature or a few illustrative lines is a spec that hasn't been delegated yet — stop and delegate it. Fixing a lane's bug by hand is the same failure in disguise: send a corrected spec back to the cheap lane instead.

**Keep the context lean.** Everything in the architect's context is re-read at architect prices on every turn — and the receiving lane re-reads the named files in its own context as its first step, so a full-file read here bills the same content twice. Delegate broad exploration, codebase searches, and log-grepping to a cheap read-only scout and keep only the conclusions. To write a spec, get the map — exports, signatures, line numbers — from the scout, then personally read only the lines the spec will quote in its Interfaces or Constraints. A path reference or an excerpt beats pasting long files, full diffs, or verbose command output.

**Reason once, then hand off.** Do the hard thinking — the architecture, the interface design, the debugging hypothesis — in one pass, capture it in the spec, and let the cheap lane carry it from there. Re-deriving decisions across turns burns the premium twice.

What stays with the architect regardless of cost: decomposition, interface design, hypothesis selection when debugging, spec writing, lane routing, and judging verification evidence. Those tokens are what the premium is for — everything else is a candidate for delegation. Pareto selection operates *between* lanes; it never trades away delegation itself, and no declared speed or specialty preference licenses the architect to type the implementation instead.

## The lanes

Lane semantics are harness-independent; only the invocation differs — see "Harness mechanics" below.

| Lane | Producer | Route here when |
|---|---|---|
| Routine | Grok (catalog-selected, currently grok-4.6) | The spec fully determines the outcome: boilerplate, wiring, CRUD, mechanical edits, straightforward features. **Default lane.** |
| Cross-vendor | GPT-5.6 (Sol/Terra/Luna, selectable effort) | Correctness/completeness is critical enough to want a second implementation, or as the alternative family when the grok lane is unavailable. |
| In-house | Opus (in-house Claude; chosen 2026-07 while Sonnet's price/capability positioning is poor — re-evaluate if the lane is swapped back to a future Sonnet) | Routed on purpose: a profile-marked specialty (e.g. frontend), a small-but-complex task worth isolating from the architect's context, or a declared quota or deadline constraint; also the fallback when both CLI runners are unavailable. Same flagship tier as the architect — the value is context isolation, not a cheaper unit price. Disclose three costs on every route: same family as the architect (no cross-vendor review), shares the main session's Anthropic quota, highest unit price under the user's current ranking. |
| Handoff | Any harness the user picks, driven by the user by hand | Only after an explicit user declaration — mechanics and acceptance in [handoff-lane.md](handoff-lane.md). Price ≈ 0 (subscription arbitrage), slowest by far (a human round-trip), capability = whatever the user picks, available only while the user is present. |
| Judgment | Fable 5 (`fable-advisor` agent) | Not an implementation lane. See "Commitment boundaries" below. |

**Stage 1 — adequacy.** How much does the outcome depend on judgment the spec can't capture? Little → every lane is adequate and the grok lane is the routine default; you will verify anyway. A lot, and mistakes are costly → the adequate set narrows to the codex lane, a race of both lanes on the same spec with you picking the stronger diff, or keeping that piece with the architect. A routine-lane task that fails its spec once gets a corrected spec; twice, it escalates — repeated failure means the task was misclassified, so re-run stage 1 rather than resend a third time.

**Stage 2 — Pareto choice inside the adequate set.** Among the lanes stage 1 left standing, trade speed, price, capability, and specialty against the user's declared routing profile (next section). A specialty hit is a tie-breaker between lanes of the same adequacy class — it never promotes a lane that stage 1 ruled out, because a preference must not override a correctness judgment. With no declarations, this degrades to the cheapest adequate lane. The handoff lane is a *conditional member* of that set: it joins the candidates only once the user has declared it for this task or this session.

Grok vs codex is not a capability ranking — it's a failure-distribution question. Both are non-Anthropic families, so either lane's output gets genuine cross-vendor review from the Claude architect; racing them buys a *third* independent perspective for one extra lane's cost. Ranking the two belongs to the user's profile, not this doctrine.

**Re-routing.** A lane that comes back unavailable or times out gets the same spec re-routed to the other cross-vendor lane, disclosed explicitly — never quietly absorb the substitution. If both CLI lanes are down, route to the in-house lane and state the downgrade plainly: it shares the architect's family, so you lose cross-vendor review. Availability is decided by dispatch, not probes — route the spec and let the result decide.

### Harness mechanics

Which harness am I in? If delegation happens through a Task/subagent tool that accepts a per-dispatch model, you are in Cursor; if you delegate by running `scripts/run-*.mjs` runners, you are in Claude Code. Before your first dispatch, read the matching mechanics file — it is short and load-bearing:

- Claude Code — runners, receipts, the receipt gate, dispatch-not-probes: [lanes-claude-code.md](lanes-claude-code.md)
- Cursor — pinned-model dispatches, no receipts, subagent lifecycle: [lanes-cursor.md](lanes-cursor.md)

## User routing profile

Stage 2 runs on inputs the architect cannot probe — quota headroom, delivery pressure, the user's own sense of which family is better at what. They enter routing only as declarations, in two layers.

**Persistent judgments** — specialty tables, lane rankings — live in the user's own rules file, not in this repo: they are one user's experience, not project doctrine. Each entry carries the precondition that justifies it and the condition that voids it, anchored to a model generation and date-stamped, so a generation swap retires the entry instead of quietly steering routing with a stale belief.

**Volatile state** — quota balance, deadline pressure — is declared verbally when the work starts ("grok's quota is nearly out", "this one's a rush"). It holds for that session only and is never written to disk — a persisted quota file is stale the moment written.

**The handoff declaration.** Declared the same way, per task or per session ("this one goes to handoff"). **The handoff lane never enters stage 2 uninvited — it becomes selectable only after an explicit user declaration; the architect may suggest it for a large, fully-specified, non-urgent task, but a suggestion never routes.** The lane physically depends on the user's own hands, so routing there unasked doesn't produce slow work, it produces stalled work.

**The low-confidence escape hatch.** Ask the user before routing in exactly two cases, offering at least two options with the reason for each:

1. Declared constraints conflict on the dimension that decides the route.
2. The task is high-risk (correctness-critical or hard to reverse) and the profile is silent on the dimension that would decide it.

It does not fire for a mechanical task the spec fully determines, the mere absence of declarations (that is the documented default), or a lane being unavailable (re-route and disclose, per the rule above). For a parallel fan-out, ask at most once for the whole batch.

## The spec contract

Implementers share none of your conversation context. Every delegation prompt carries all five parts:

1. **Objective** — what to build or change, one paragraph
2. **Files** — exact paths to create or modify
3. **Interfaces** — signatures, types, or API shapes the code must match
4. **Constraints** — project conventions, things not to touch
5. **Verification** — the command(s) that prove it works

A spec you can't finish writing is a signal the decision isn't made yet — that's architect work, not a reason to hand the ambiguity to a cheaper model.

## Parallelism

Independent specs (no shared files, no ordering dependency) launch as parallel lanes in a single message; sequential chains and single-file surgery stay serial. For high-stakes work, race both cross-vendor lanes on the same spec and pick the stronger diff — three-vendor confidence for one extra lane's cost.

## Commitment boundaries

Consult `fable-advisor` (read-only, verdict in under 300 words) at the moments that decide whether the next hour is wasted:

- Before committing to an architecture, data migration, API shape, or refactor strategy
- Whenever the same problem has resisted two distinct attempts
- Once before declaring a multi-step deliverable done

Pass it the decision, the constraints, and the options considered. Act on the verdict or surface the disagreement — never silently ignore it. (If the session and the advisor already share a flagship-tier model, the advisor still earns its keep as a context-clean skeptic reading the actual code.)

## Verification

Reports are claims, not evidence. Accept lane work through a three-tier protocol:

1. **Tier 1 — every lane by default.** Accept on the lane's verification evidence — command, exit code, and output tail, spot-checked against the working tree — plus `git diff --stat`. A full unscoped `git diff` never enters the architect's context.
2. **Tier 2 — specific doubt.** When the report, the stat, or the verification output raises a specific doubt, read a path-scoped `git diff <file>` for the suspect files only.
3. **Tier 3 — correctness-critical and in-house work.** For correctness-critical tasks and for every in-house-lane diff, delegate whole-diff review to a context-clean reviewer subagent that returns a verdict plus flagged hunks, then personally read only the flagged hunks. Prefer a cross-vendor reviewer for in-house diffs — it restores the cross-vendor review that lane otherwise lacks. A reviewer verdict is still a claim, so the architect keeps final judgment and may spot-check beyond the flags.

"Should work", "tests should pass", or a report with no command output means the task is not done. A lane that reports a spec gap gets a corrected spec, not a "use your judgment". A subagent that goes idle without delivering its report is not a blocker: verify the workspace evidence directly (diff and verification command) and move on. CLI receipt acceptance and handoff's diff-only acceptance live in their own files.
