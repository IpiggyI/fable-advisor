---
name: orchestration
description: Routing doctrine for the architect-as-orchestrator pattern. USE WHEN acting as architect on implementation work or a multi-ticket build, routing tasks to lanes (grok/codex runners in Claude Code, pinned-model dispatches in Cursor), writing a five-part spec or delivery contract, verifying or accepting lane work, consulting fable-advisor, or managing session cost.
---

# Orchestration — the architect's routing doctrine

The session is the architect: it owns requirements, decomposition, delivery contracts, routing, and acceptance; lanes own implementation inside those contracts. Routing runs in two stages, adequacy then Pareto; escalation is deliberate, per task, never a fixed binding.

## Cost discipline — the prime directive

The session model is the most expensive lane; the economic case is keeping its token volume low: the flagship for judgment, the lanes for volume.

**Emit judgment, not volume.** The architect's output is decomposition, contracts, routing decisions, verdicts on diffs, and short reports, never implementation code. A code block longer than an interface signature is a contract not yet delegated; a lane's bug fixed by hand is the same failure: send a rework ticket.

**Keep the context lean.** Everything in the architect's context is re-read at architect prices every turn, and the lane re-reads the named files itself, so a full-file read here bills twice. Delegate exploration, searches, and log-grepping to a cheap read-only scout; keep only the conclusions. Get the map (exports, signatures, line numbers) from the scout, then personally read only the lines the contract will quote.

**Decide what is reserved, not how it is built.** Reserved to the architect regardless of cost: decomposition, interface design, the constraints a lane must not cross, routing, and judging acceptance evidence, captured once in the contract. How the lane meets them is the lane's call; pre-deciding it spends the premium on work the lane already covers. A lane-owned defect is debugged by the lane; the architect supplies the reproducible failure and picks a hypothesis only when the defect's owner is unknown, which is decomposition.

## The delegation boundary — by artifact class

Whether the architect may edit a file depends on what the file is, never on how small the change looks.

- **Deliverables**: whatever ships with the product, is exercised by tests, or describes behaviour to its users. Changed only through a lane, at any size; a one-line fix is not an exception.
- **Coordination artifacts**: task, issue and spec files; decision records; workflow state files; release version fields. The architect writes these directly.

The repo's path mapping lives in its agent instructions (AGENTS.md or equivalent). An unclear class is a deliverable.

**Same-model dispatch** is a dial of the in-house lane, not a fifth lane: the model is pinned to the session model instead of the default alias. It serves one artifact class, doctrine prose shipped with the plugin (its own skill and agent text), for consistency with the architect's judgment; the class triggers it, not how central the text feels. In Cursor: `generalPurpose` with no `model` (inherit). In Claude Code it runs as the Opus in-house lane, disclosed.

## The lanes

Lane semantics are harness-independent; only the invocation differs.

| Lane | Producer | Route here when |
|---|---|---|
| Routine | Grok, at the grok CLI's catalog default (currently grok-4.6, 2026-09) | The contract fully determines the outcome: boilerplate, wiring, CRUD, mechanical edits. **Default lane.** |
| Cross-vendor | GPT family, from the codex lane's current catalog (model and effort selectable) | Correctness or completeness warrants a second implementation, or the grok lane is unavailable. |
| In-house | Claude via the `opus` alias | On purpose: a profile-marked specialty, a small-but-complex task worth isolating from the architect's context, a declared quota or deadline constraint, same-model dispatch of doctrine prose; also the fallback when both CLI runners are unavailable. Disclose three costs per route: same family (no cross-vendor review), shared Anthropic quota, highest unit price. |
| Handoff | Any harness, driven by the user by hand | Only after an explicit user declaration; see [handoff-lane.md](handoff-lane.md). |
| Judgment | Fable series (`fable-advisor` agent) | Not an implementation lane; see "Commitment boundaries". |

**Stage 1 — adequacy.** How much does the outcome depend on judgment the contract can't capture? Little → every lane is adequate and grok is the default; you verify anyway. A lot, with costly mistakes → the codex lane, a race of both lanes on one contract, or the in-house lane; every branch ends in a lane, never in the architect implementing. One failed acceptance gets a rework ticket or, for a contract gap, a corrected contract; two means misclassification: re-run stage 1 in a fresh session rather than resend a third time. Targeted direction is allowed then, not as the opening move.

**Stage 2 — Pareto choice inside the adequate set.** Trade speed, price, capability, and specialty against the user's declared routing profile. A specialty hit is a tie-breaker inside an adequacy class; it never promotes a lane stage 1 ruled out. With no declarations, this degrades to the cheapest adequate lane, each lane priced at its default dial; dial positions inside a lane never enter the lane-level comparison. A lane's cheaper model or lower effort is reached only by user declaration, or when the task is simple and that family is wanted anyway. The handoff lane is a *conditional member*: it joins only once the user has declared it for this task or session.

Grok vs codex is not a capability ranking; it's a failure-distribution question: both are non-Anthropic families, so either gets cross-vendor review from the Claude architect, and racing them buys a *third* perspective for one extra lane's cost. Ranking the two belongs to the user's profile, not this doctrine.

**Re-routing.** A lane that comes back unavailable or times out gets the same contract re-routed to the other cross-vendor lane, disclosed explicitly. If both CLI lanes are down, route in-house and state the downgrade: you lose cross-vendor review. Availability is decided by dispatch, not probes.

### Harness mechanics

A Task/subagent tool with a per-dispatch model means Cursor; running `scripts/run-*.mjs` runners means Claude Code. Before your first dispatch, read the matching file:

- Claude Code (runners, waiting, receipts, receipt gate, session reuse, dispatch-not-probes): [lanes-claude-code.md](lanes-claude-code.md)
- Cursor (pinned-model dispatches, no receipts, `resume`, subagent lifecycle): [lanes-cursor.md](lanes-cursor.md)

The executor side of the contract is [lane-preamble.md](lane-preamble.md): runners prepend it to every lane prompt; a Cursor dispatch opens by pointing the subagent at it. Do not restate it in a contract.

## User routing profile

Stage 2 runs on inputs the architect cannot probe: quota headroom, delivery pressure, the user's sense of which family is better at what. They enter routing only as declarations, in two layers.

**Persistent judgments** (specialty tables, lane rankings) live in the user's own rules file, not this repo: one user's experience, not project doctrine. Each entry carries its precondition and voiding condition, anchored to a model generation and date-stamped, so a generation swap retires it.

**Volatile state** (quota balance, deadline pressure) is declared verbally when the work starts, holds for that session only, and is never written to disk.

**The handoff declaration.** Declared the same way, per task or per session; the declaration is what makes the handoff lane selectable in stage 2. The architect may suggest it for a large, fully-specified, non-urgent task, but a suggestion never routes: unasked, it produces stalled work.

**The low-confidence escape hatch.** Ask the user before routing in exactly two cases, offering at least two options with reasons: declared constraints conflict on the deciding dimension; or the task is high-risk (correctness-critical or hard to reverse) and the profile is silent on it. It does not fire for a mechanical task, the mere absence of declarations (the documented default), or an unavailable lane (re-route and disclose). For a parallel fan-out, ask at most once per batch.

## The delivery contract

Lanes share none of your conversation context. Every dispatch carries all five parts:

1. **Objective**: the outcome and its acceptance criteria, not the steps
2. **Files**: the owned scope, the paths or directories the lane may touch; new files inside it are allowed
3. **Interfaces**: shared or external contracts the result must match; may be none
4. **Constraints**: the reserved items: what must not change, choices fixed upstream
5. **Verification**: commands whose output is acceptance evidence, including one check that fails when the goal is not met

Everything Constraints leaves open is the lane's decision; "the contract doesn't say how" is not a gap. Steps are not required and not written by default: a sequence belongs in the contract only when an upstream decision already fixed it, or as targeted direction after two failed attempts.

**Contract gap versus implementation choice.** A contract gap (unclear expected behaviour, conflicting requirements, a reserved interface that would have to change, no way to tell what passes) comes back as a report and gets a corrected contract. An unspecified implementation choice (internal function boundaries, an equivalent data structure, test organisation, in-scope error handling) is the lane's, neither reported nor waited on. A lane-owned defect found at acceptance gets a rework ticket, never a hand fix.

**Upstream task artifacts.** When an issue, spec, or task file exists, the contract references its path and inlines only the acceptance criteria, reserved constraints, and verification commands, naming which sections are binding. The architect neither restates nor re-plans.

**Rework tickets.** A new contract to the same lane, reusing its session: Objective = the defect (requirement violated, reproducible failure, expected behaviour, evidence); Files = the original scope; Verification = the check that failed. No fix inside. Grounds: a violated requirement, a reproducible problem, missing verification, an affected reserved interface; never structural preference.

## Parallelism

Independent contracts (no shared files, no ordering dependency) launch as parallel lanes in a single message; sequential chains and single-file surgery stay serial. For high-stakes work, race both cross-vendor lanes on one contract and pick the stronger diff.

## Commitment boundaries

Consult `fable-advisor` (read-only, verdict in under 300 words) at the moments that decide whether the next hour is wasted:

- Before committing to an architecture, data migration, API shape, or refactor strategy
- Whenever the same problem has resisted two distinct attempts
- Once before declaring a multi-step deliverable done

Pass it the decision, the constraints, and the options considered. Act on the verdict or surface the disagreement; never silently ignore it.

## Verification

Reports are claims, not evidence; the object of review is the contract. Three tiers:

1. **Tier 1 — every lane by default.** Accept on the lane's verification evidence (command, exit code, output tail, spot-checked against the working tree) plus `git diff --stat`. A full unscoped `git diff` never enters the architect's context.
2. **Tier 2 — specific doubt.** When the report, stat, or verification output raises a specific doubt, read a path-scoped `git diff <file>` for the suspect files. When the lane authored the acceptance test, read that test file: a test the lane wrote is part of the claim, not evidence for it.
3. **Tier 3 — correctness-critical and in-house work.** Delegate whole-diff review to a context-clean reviewer subagent that returns a verdict plus flagged hunks; read only the flagged hunks yourself. Prefer a cross-vendor reviewer for in-house diffs; it restores the review that lane lacks. A reviewer verdict is still a claim; the architect keeps final judgment.

"Should work", "tests should pass", or a report with no command output means not done. A reported contract gap gets a corrected contract; a lane-owned defect gets a rework ticket. A subagent that goes idle without its report is not a blocker: verify the workspace evidence directly and move on.
