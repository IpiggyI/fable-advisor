---
name: orchestration
description: Routing doctrine for the role pool (explorer / worker / advisor at light / standard / senior tiers) and the grok, codex, claude and handoff lanes. USE WHEN acting as architect or orchestrating implementation work or a multi-ticket build, routing tasks to lanes (grok/codex runners in Claude Code, pinned-model dispatches in Cursor), writing a five-part delivery contract, verifying or accepting lane work, consulting the advisor, or managing session cost.
---

# Orchestration — roles, tiers, lanes, posture

The main agent, whatever model runs it, owns requirements, decomposition, delivery contracts, routing, and acceptance. A dispatch is a role at a tier through a lane; posture decides whether the main agent also edits deliverables itself.

## Cost discipline — the prime directive

**Spend judgment where it is scarce.** Judgment is what no contract captures: decomposition, interfaces, reserved constraints, routing, acceptance. A code block longer than an interface signature is a contract not yet delegated. A lane debugs its own defect; the main agent supplies the reproducible failure, and a hypothesis only when the defect's owner is unknown.

**Keep volume out of the main agent's context.** A full-file read here bills twice: re-read every turn, and re-read by the lane. Exploration, searches, and log-grepping go to an explorer; take the map and the conclusions, then read only the lines the contract will quote.

**In the orchestrating posture every deliverable change has a reader other than its author.** The worker writes; the main agent or advisor reads; a self-written, self-accepted change has left the review chain.

## Posture

Posture is the main agent's relation to deliverables. Two postures, differing in exactly one rule:

- **Orchestrating posture**: deliverables change only through a worker; the main agent (the architect, in this posture) writes contracts, dispatches, accepts.
- **Implementing posture**: the main agent may edit deliverables directly.

Every role is dispatchable in both; the decision-type gate binds both; implementing never means "no dispatches".

**Selector.** A user declaration or an upstream instruction wins; with neither, an existing upstream task artifact (issue, spec, task file) means orchestrating, otherwise implementing. Model identity never selects posture.

Posture is relative to a dispatch: a lane is implementing for its own contract and orchestrating toward any subagents it spawns. Depth is not limited.

## The delegation boundary — by artifact class

In the orchestrating posture, whether the architect may edit a file depends on what the file is, never on how small the change looks.

- **Deliverables**: whatever ships, is exercised by tests, or describes behaviour to users. Only through a worker, at any size; a one-line fix is no exception.
- **Coordination artifacts**: task, issue and spec files; decision records; workflow state files; release version fields. Written directly, in either posture.

The repo's path mapping lives in its AGENTS.md or equivalent. An unclear class is a deliverable.

**Same-model dispatch** is a dial of the claude lane: the model is pinned to the session model. It serves one artifact class in the orchestrating posture, the plugin's own doctrine prose (skill and agent text); the class triggers it, not how central the text feels. Cursor: `generalPurpose` with no `model` (inherit). Claude Code: the `worker` agent with per-dispatch `model` set to the session model.

## Roles and tiers

A role is a contract shape (input, permissions, output) and names no model; a tier is a capability level, orthogonal to role.

| Role | Permissions | Returns |
|---|---|---|
| `explorer` | read-only | evidence: `file:line`, symbols, verbatim quotes |
| `worker` | writes inside the contract's Files | a diff plus verification evidence |
| `advisor` | read-only | a verdict under 300 words, in two request shapes: **decision** (before committing: decision, constraints, options) or **acceptance** (after: contract, diff, receipt → criteria met?) |

Tiers: `light`, `standard`, `senior`; any role at any tier. A takeover of a stuck task is a senior worker plus a takeover contract, not another role. The advisor's authority comes from the code it reads, not its tier.

## Lanes

A lane answers how a vendor is reached; roles and tiers answer what is dispatched.

| Lane | Mechanism |
|---|---|
| grok lane | the Grok family through the grok runner (Claude Code) or a pinned dispatch (Cursor) |
| codex lane | the GPT family through the codex runner; model and effort selectable from its whitelist |
| claude lane | Claude subagents (`worker`, `fable-advisor`, the harness explorer); no external CLI. From a Claude main agent disclose: same family (no cross-vendor review), shared Anthropic quota, highest unit price |
| handoff lane | the user carries a spec file to a harness of their own; see [handoff-lane.md](handoff-lane.md) |

The **fill table**, (role, tier) → candidate lanes and dials (a `dial` is model plus effort inside a lane), lives in the user's rules. This doctrine names no models.

### Harness mechanics

A Task/subagent tool with a per-dispatch model means Cursor; running `scripts/run-*.mjs` runners means Claude Code. Before your first dispatch, read the matching file:

- Claude Code (runners, receipts, receipt gate, report mode): [lanes-claude-code.md](lanes-claude-code.md)
- Cursor (pinned dispatches, codex runner through Shell, lifecycle): [lanes-cursor.md](lanes-cursor.md)

[lane-preamble.md](lane-preamble.md) is the executor side of the contract: runners prepend it; a Cursor dispatch opens by pointing the subagent at it. Do not restate it.

## Routing — two stages

**Stage 1 — (role, tier) by judgment dependence.** Role by output: evidence → explorer, a change → worker, a commitment or acceptance → advisor. Tier by how much the outcome depends on judgment the contract cannot capture: little → light or standard (verify anyway); a lot, with costly mistakes → senior, or a race of two fills on one contract. In the orchestrating posture every branch ends in a worker, never in the architect implementing.

**Stage 2 — Pareto inside the cell.** Among that cell's fills in the fill table, trade speed, price, capability, and specialty against the user's declared profile. Specialty is a tie-breaker; it never overturns stage 1. With no declarations, take the cheapest adequate fill, each lane priced at its default dial; dial positions never enter the lane-level comparison, and a lane's cheaper model or lower effort is reached only by user declaration, or when the task is simple and that family is wanted anyway. The handoff lane is a *conditional member*: it joins only after the user's declaration for this task or session.

**Re-routing.** An unavailable or timed-out lane gets the same contract re-routed to another fill in the cell, disclosed. Both CLI lanes down → the claude lane, stating the downgrade (no cross-vendor review). Availability is decided by dispatch, not probes.

**Escalation.** One failed acceptance gets a rework ticket (lane-owned defect; never a hand fix) or a corrected contract (contract gap). When the rework ticket also fails, attribute: capability → a higher-tier worker in a fresh session under a takeover contract (original contract, prior report, receipt); contract gap → a corrected contract on the same lane session. A senior tier may also be a first choice.

## User routing profile

Stage 2 runs on inputs the main agent cannot probe; they enter only as declarations, in two layers.

**Persistent judgments** (the fill table, specialty notes) live in the user's rules, not this repo. Each entry carries a precondition, a voiding condition, a model generation and a date, so a generation swap retires it.

**Volatile state** (quota balance, deadline pressure) is declared verbally when the work starts, holds for that session only, and is never written to disk.

**The handoff declaration.** Per task or per session; it alone makes the handoff lane selectable in stage 2. The main agent may suggest it for large, fully-specified, non-urgent work; a suggestion never routes.

**The low-confidence escape hatch.** Ask the user before routing in exactly two cases, offering at least two options with reasons: declared constraints conflict on the deciding dimension; or the task is high-risk (correctness-critical or hard to reverse) and the profile is silent. Not for a mechanical task, absent declarations (the default), or an unavailable lane (re-route and disclose). Parallel fan-out: ask at most once per batch.

## The delivery contract

Lanes share none of your context. Every dispatch carries five parts:

1. **Objective**: the outcome and its acceptance criteria, not the steps
2. **Files**: the owned scope (paths or directories); new files inside it are allowed
3. **Interfaces**: shared or external contracts the result must match; may be none
4. **Constraints**: the reserved items: what must not change, choices fixed upstream
5. **Verification**: commands whose output is acceptance evidence, including one check that fails when the goal is not met

Everything Constraints leaves open is the lane's decision; "the contract doesn't say how" is not a gap. Steps are not written by default: only when an upstream decision already fixed a sequence, or as targeted direction after a failed rework ticket.

**Contract gap versus implementation choice.** A contract gap (unclear expected behaviour, conflicting requirements, a reserved interface that would have to change, no way to tell what passes) comes back as a report and gets a corrected contract. An unspecified implementation choice (internal function boundaries, an equivalent data structure, test organisation, in-scope error handling) is the lane's, neither reported nor waited on.

**Upstream task artifacts.** When an issue, spec, or task file exists, the contract references its path and inlines only the acceptance criteria, reserved constraints, and verification commands, naming which sections are binding. The main agent neither restates nor re-plans.

**Rework tickets.** A new contract to the same lane, reusing its session: Objective = the defect (requirement violated, reproducible failure, expected behaviour, evidence); Files = the original scope; Verification = the check that failed. No fix inside. Grounds: a violated requirement, a reproducible problem, missing verification, an affected reserved interface; never structural preference.

## Parallelism

Independent contracts (no shared files, no ordering dependency) launch as parallel lanes in a single message; sequential chains and single-file surgery stay serial. For high-stakes work, race two fills on one contract and pick the stronger diff; two non-Anthropic fills buy a *third* perspective for one extra lane's cost.

## Decision-type gate

Consult the advisor at these decision types; the list binds any main agent, at any tier, in either posture:

- committing to an architecture, data migration, API shape, or refactor strategy
- overturning an established plan
- changing a public interface or a cross-module dependency
- relaxing acceptance criteria
- the same problem failing twice
- before declaring a multi-step deliverable done: this one takes the advisor's **acceptance** shape

The others take the **decision** shape: pass the decision, constraints, and options; the advisor reads the code itself. Act on the verdict or surface the disagreement; never silently ignore it. No mechanical enforcement, no per-diff review.

## Verification

Reports are claims, not evidence; the object of review is the contract. Three tiers:

1. **Tier 1 — every lane by default.** Accept on the lane's verification evidence (command, exit code, output tail, spot-checked against the working tree) plus `git diff --stat`. A full unscoped `git diff` never enters the main agent's context.
2. **Tier 2 — specific doubt.** On a specific doubt from the report, stat, or verification output, read a path-scoped `git diff <file>`. When the lane authored the acceptance test, read it: it is part of the claim, not evidence.
3. **Tier 3 — correctness-critical work, and same-family diffs.** The advisor in its acceptance shape (context-clean, read-only, reads the diff plus the receipt) returns a verdict plus flagged hunks; read only those. Prefer a cross-vendor fill for a same-family diff. A verdict is still a claim; the main agent keeps final judgment.

"Should work", "tests should pass", or a report with no command output means not done. A subagent idle without its report is not a blocker: verify the workspace evidence and move on.
