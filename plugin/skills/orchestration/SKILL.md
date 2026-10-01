---
name: orchestration
description: "Roles (explorer / worker / advisor), tiers, lanes and posture for delegated work. Use when orchestration or delegation is requested; before editing a deliverable governed by an issue, spec, or task file without a posture instruction; before wide reading, independently parallelizable reading, or reading whose conclusion alone belongs in the main thread; before dispatching or accepting any subagent or lane; or at any of these decision points: architecture, migration, API or refactor strategy, plan reversal, public-interface or cross-module dependency change, relaxed acceptance, a problem failing twice."
---

# Orchestration — roles, tiers, lanes, posture

The main agent, whatever model runs it, owns requirements, decomposition, delivery contracts, routing, and acceptance. A dispatch is a role at a tier through a lane; posture decides whether the main agent also edits deliverables itself.

## Cost discipline — the prime directive

**Spend judgment where it is scarce.** Judgment is what no contract captures: decomposition, interfaces, reserved constraints, routing, acceptance. A lane debugs its own defect; the main agent supplies the reproducible failure, and a hypothesis only when the defect's owner is unknown.

**Keep volume out of the main agent's context.** Dispatch an explorer when the reading is wide, can run independently in parallel, or only its conclusion belongs in the main thread; a bounded lookup in a known file the main agent reads itself. Code-block length and fitting one tool call are not dispatch criteria.

**In the orchestrating posture every deliverable change has a reader other than its author.** The worker writes; the main agent or advisor reads; a self-written, self-accepted change has left the review chain.

## Posture

Posture is the main agent's relation to deliverables. Two postures, differing in exactly one rule:

- **Orchestrating posture**: deliverables change only through a worker; the main agent (the architect, in this posture) writes contracts, dispatches, accepts.
- **Implementing posture**: the main agent may edit deliverables directly.

Every role is dispatchable in both; implementing never means "no dispatches".

**Selector.** A user declaration or an upstream instruction wins; with neither, an existing upstream task artifact (issue, spec, task file) means orchestrating, otherwise implementing.

Posture is relative to a dispatch: a lane is implementing for its own contract and orchestrating toward any subagents it spawns. Depth is not limited.

## The delegation boundary — by artifact class

In the orchestrating posture, whether the architect may edit a file depends on what the file is, never on how small the change looks.

- **Deliverables**: whatever ships, is exercised by tests, or describes behaviour to users. Only through a worker, at any size; a one-line fix is no exception.
- **Coordination artifacts**: task, issue and spec files; decision records; workflow state files; release version fields. Written directly, in either posture.

The repo's path mapping lives in its AGENTS.md or equivalent. An unclear class is a deliverable.

**Same-model dispatch** is a dial of the claude lane: the model is pinned to the session model. The repo's AGENTS.md names the artifact class it serves. Cursor: `generalPurpose` with no `model` (inherit). Claude Code: a `worker-*` agent with per-dispatch `model` set to the session model.

## Roles and tiers

A role is a contract shape (input, permissions, output) and names no model; a tier is a capability level, orthogonal to role.

| Role | Permissions | Returns |
|---|---|---|
| `explorer` | read-only | evidence: `file:line`, symbols, verbatim quotes |
| `worker` | writes inside the contract's Files | a diff plus verification evidence |
| `advisor` | read-only | a verdict under 300 words, in two request shapes: **decision** (before committing: decision, constraints, options) or **acceptance** (after: contract, diff, receipt → criteria met?) |

Tiers: `mainstay`, `crux`, `rescue`; any role at any tier. Tiers split by model; effort only subdivides a tier. Most work ends in `mainstay`; `rescue` is rare. A raise (ladder R2) runs under a takeover contract: contract shape, not tier. The advisor's authority comes from the code it reads, not its tier.

## Lanes

A lane answers how a vendor is reached; roles and tiers answer what is dispatched.

| Lane | Mechanism |
|---|---|
| grok lane | the Grok family through the grok runner (Claude Code) or a pinned dispatch (Cursor) |
| codex lane | the GPT family through the codex runner; model and effort selectable from its whitelist |
| claude lane | Claude subagents, one agent file per (role, effort): effort comes only from that file, the per-dispatch `model` picks the fill. No external CLI. From a Claude main agent disclose: same family (no cross-vendor review), shared Anthropic quota |
| handoff lane | the user carries a spec file to a harness of their own; see [handoff-lane.md](handoff-lane.md) |

### Harness mechanics

Identify the harness by the host you run in and its tools' parameter structure, never by one tool name or a `model` parameter's presence; read the matching lanes file before the first dispatch:

- Claude Code (runners, receipts, receipt gate, report mode): [lanes-claude-code.md](lanes-claude-code.md)
- Cursor (pinned dispatches, codex runner through Shell, lifecycle): [lanes-cursor.md](lanes-cursor.md)

Two executor-side contracts: [lane-preamble.md](lane-preamble.md) for a worker, [lane-preamble-report.md](lane-preamble-report.md) for an explorer or advisor. Runners prepend the one `mode` names; a Cursor dispatch points at the one its role needs. Restate neither.

## Routing — two stages

**Stage 1 — (role, tier).** Role by output. Tier: new work starts in `mainstay`; an identified key difficulty or mutually constraining conditions may send a first round straight to `crux`, no usage ratio; a first-round `rescue` only by user declaration.

**Stage 2 — choosing inside the cell.** The first candidate is the default, at its `*` dial absent declarations. Pick another when the task falls on a specialty the profile declares for it (price counts). Equal fits and replacements follow the profile's lane order.

**Re-routing.** An unavailable or timed-out candidate (whole lane, single candidate, or codex runner start failure) hands its contract unchanged to another in the cell, in the profile's lane order, disclosed; not a capability failure. Both CLI lanes down → the claude lane, stating any lost cross-vendor review. Availability is decided by dispatch, not probes.

**Escalation — the ladder.** R1: a failed acceptance gets a rework ticket, same session, same dial; a contract gap gets a corrected contract, same lane session. R2: the rework ticket fails too, cause capability → a capability failure: raise to the next tier (`mainstay` → `crux` → `rescue` → user), fresh session, takeover contract (original contract, prior report, receipt). Pick its model by the task, not below the failed model in the profile's ranking unless no other candidate exists; the same model must raise effort; effort names never compare across models. R3: a model is raised at most once, counted by full model id. R4: a major execution problem (repeated tool failures, runaway, a reserved item touched) may skip the rework ticket, counting as a capability failure (next tier). Environment problems and contract gaps are not failures. A task started in `crux` reaches `rescue` after one failure there; a `rescue` failure goes to the user.

## User routing profile

Stage 2 inputs enter only as declarations.

**Persistent judgments.** The **fill table**, (role, tier) → candidate lanes and dials, and specialty notes live in [routing-profile.md](routing-profile.md), the user's routing profile shipped with this skill. Read it before the first model assignment, again when it changes or slides out of context; unreadable → report the gap, assume nothing. A `dial` is written `model[a*, b, c]`: that model's efforts available in the cell, `*` the default, else the first listed; a model without an effort dimension is written bare.

**Volatile state** (quota balance, deadline pressure) is declared verbally at kickoff, holds for that session only, never written to disk.

**The handoff declaration** (per task or session) alone makes the handoff lane selectable in stage 2; the main agent may suggest it for large, fully-specified, non-urgent work; suggesting never routes.

**The low-confidence escape hatch.** Ask the user before routing, with two or more reasoned options, only when declared constraints conflict on the deciding dimension, or the task is high-risk (correctness-critical or hard to reverse) and the profile is silent; once per parallel batch at most.

## The delivery contract

Lanes share none of your context. Every dispatch carries five parts:

1. **Objective**: the outcome and its acceptance criteria, not the steps
2. **Files**: the owned scope (paths or directories); new files inside it are allowed
3. **Interfaces**: shared or external contracts the result must match; may be none
4. **Constraints**: the reserved items: what must not change, choices fixed upstream, and the operations the caller keeps in its own session; these bind the lane, its subagents, and its verification commands
5. **Verification**: for a worker, the checks scoped to *this* contract's change and its callers — at least one that fails when the Objective's named behaviour is not met, never held back, the cheapest that does (an existing test, or a grep for a textual change) before new test code — and no batch check, even one a ticket lists; for an explorer or advisor, the expected evidence or verdict shape, possibly empty

Everything Constraints leaves open is the lane's decision. Steps are not written by default: only when an upstream decision already fixed a sequence, or as targeted direction after a failed rework ticket.

**Contract gap versus implementation choice.** A contract gap (unclear expected behaviour, conflicting requirements, a reserved interface that would have to change, no way to tell what passes) comes back as a report and gets a corrected contract. An unspecified implementation choice (internal function boundaries, an equivalent data structure, test organisation, in-scope error handling) is the lane's, neither reported nor waited on.

**Upstream task artifacts.** When an issue, spec, or task file exists, the contract references its path and inlines only the acceptance criteria, reserved constraints, and the contract's own checks, naming which sections are binding. The main agent neither restates nor re-plans.

**Rework tickets.** A new contract to the same lane, reusing its session: Objective = the defect (requirement violated, reproducible failure, expected behaviour, evidence); Files = the original scope; Verification = the smallest runnable check covering the failing cases and the fix's reach, not the whole suite. No fix inside. Grounds: a violated requirement, a reproducible problem, missing verification, an affected reserved interface; never structural preference.

## Parallelism

Independent contracts (no shared files, no ordering dependency) launch as parallel lanes in a single message; sequential chains and single-file surgery stay serial. Tickets sharing files or an area go to one worker as one contract, with a deciding check and a report line per ticket, unless that outgrows one lane's context or a ticket needs another's verified result or separate authorization. The contract is accepted once, not per ticket; commits split only at authorization or rollback boundaries. For high-stakes work, race two fills on one contract and pick the stronger diff; two fills from families other than the main agent's buy a *third* perspective for one extra lane's cost. Two executors in one working tree overwrite each other; a race isolates each fill's working directory and execution records (see the lanes file).

## Decision-type gate

Consult the advisor at these decision types; the list binds any main agent, at any tier, in either posture:

- committing to an architecture, data migration, API shape, or refactor strategy
- overturning an established plan
- changing a public interface or a cross-module dependency
- relaxing acceptance criteria
- the same problem failing twice

All take the **decision** shape: pass the decision, constraints, and options; the advisor reads the code itself. The **acceptance** shape arrives through Verification's Tier 3, never by step count. Act on the verdict or surface the disagreement; never silently ignore it. No mechanical enforcement, no per-diff review.

## Verification

Reports are claims, not evidence; the object of review is the contract, and accepting one closes that contract, not the task. Three tiers:

1. **Tier 1 — every lane by default.** Accept on the lane's verification evidence (command, exit code, output tail, spot-checked against the working tree) plus `git diff --stat`. A full unscoped `git diff` never enters the main agent's context. A lane's own review or acceptance pass is a claim; reuse its command output instead of re-running it, and spend acceptance on what the lane could not see: other contracts, environments it lacked, batch checks.
2. **Tier 2 — specific doubt.** On a specific doubt from the report, stat, or verification output, read a path-scoped `git diff <file>`. When the lane authored the acceptance test, read it: it is part of the claim, not evidence.
3. **Tier 3 — correctness-critical work, same-family diffs, and the user asking for review.** The advisor in its acceptance shape (context-clean, read-only, reads the diff plus the receipt) returns a verdict plus flagged hunks; read only those. Prefer a cross-vendor fill for a same-family diff. A verdict is still a claim; the main agent keeps final judgment.

**Run each check once.** A contract's check list has one executor — the lane's file names which — and is not run again to close. A costly check wider than one contract's change (full suite, browser or end-to-end suite, full build or package) is a batch check, run once after the batch's last contract lands, or earlier where later work builds on what only it verifies, and again only after a rework of a failure it found. A batch holds as many contracts as one failing run can attribute; a failure reworks the contract traced as its cause. Record batch checks once in the task artifact as passed, failed or pending, with output; failed or pending, a check left unrun by an early stop included, means the task is not done unless the user waives it. The main agent may hand a batch's execution to a lane; the verdict stays its own. Evidence holds as long as the code, inputs and environment behind it hold: a changed role or session is not a reason to re-run.

"Should work", "tests should pass", or an acceptance with no command output behind it means not done.
