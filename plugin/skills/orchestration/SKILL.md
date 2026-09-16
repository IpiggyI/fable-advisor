---
name: orchestration
description: Roles (explorer / worker / advisor), tiers, lanes and posture for delegated work. Use when deciding how to carry out a deliverable change, dispatching or accepting any subagent or CLI lane, or consulting the advisor.
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

**Selector.** A user declaration or an upstream instruction wins; with neither, an existing upstream task artifact (issue, spec, task file) means orchestrating, otherwise implementing. Model identity never selects posture.

Posture is relative to a dispatch: a lane is implementing for its own contract and orchestrating toward any subagents it spawns. Depth is not limited. Claude Code caps subagent nesting at three layers below the main session.

## The delegation boundary — by artifact class

In the orchestrating posture, whether the architect may edit a file depends on what the file is, never on how small the change looks.

- **Deliverables**: whatever ships, is exercised by tests, or describes behaviour to users. Only through a worker, at any size; a one-line fix is no exception.
- **Coordination artifacts**: task, issue and spec files; decision records; workflow state files; release version fields. Written directly, in either posture.

The repo's path mapping lives in its AGENTS.md or equivalent. An unclear class is a deliverable.

**Same-model dispatch** is a dial of the claude lane: the model is pinned to the session model. It serves one artifact class in the orchestrating posture, the plugin's own doctrine prose (skill and agent text); the class triggers it, not how central the text feels. Cursor: `generalPurpose` with no `model` (inherit). Claude Code: a `worker-*` agent with per-dispatch `model` set to the session model.

## Roles and tiers

A role is a contract shape (input, permissions, output) and names no model; a tier is a capability level, orthogonal to role.

| Role | Permissions | Returns |
|---|---|---|
| `explorer` | read-only | evidence: `file:line`, symbols, verbatim quotes |
| `worker` | writes inside the contract's Files | a diff plus verification evidence |
| `advisor` | read-only | a verdict under 300 words, in two request shapes: **decision** (before committing: decision, constraints, options) or **acceptance** (after: contract, diff, receipt → criteria met?) |

Tiers: `light`, `standard`, `senior`; any role at any tier. A takeover of a stuck task is a senior worker under a takeover contract. The advisor's authority comes from the code it reads, not its tier.

## Lanes

A lane answers how a vendor is reached; roles and tiers answer what is dispatched.

| Lane | Mechanism |
|---|---|
| grok lane | the Grok family through the grok runner (Claude Code) or a pinned dispatch (Cursor) |
| codex lane | the GPT family through the codex runner; model and effort selectable from its whitelist |
| claude lane | Claude subagents, one agent file per (role, effort): effort comes only from that file, the per-dispatch `model` picks the fill. Unpinned, Explore runs the session model (Opus-capped on the Claude API) with no effort dial. No external CLI. From a Claude main agent disclose: same family (no cross-vendor review), shared Anthropic quota |
| handoff lane | the user carries a spec file to a harness of their own; see [handoff-lane.md](handoff-lane.md) |

### Harness mechanics

Identify the harness by the host you run in and its tools' parameter structure, never by one tool name or the presence of a `model` parameter; the main agent then reads the matching lanes file before its first dispatch:

- Claude Code (runners, receipts, receipt gate, report mode): [lanes-claude-code.md](lanes-claude-code.md)
- Cursor (pinned dispatches, codex runner through Shell, lifecycle): [lanes-cursor.md](lanes-cursor.md)

[lane-preamble.md](lane-preamble.md) is the executor side of the contract: runners prepend it; a Cursor dispatch opens by pointing the subagent at it. Do not restate it.

## Routing — two stages

**Stage 1 — (role, tier) by judgment dependence.** Role by output: evidence → explorer, a change → worker, a commitment or acceptance → advisor. Tier by how much the outcome depends on judgment the contract cannot capture: little → light or standard (verify anyway); a lot, with costly mistakes → senior, or a race of two fills on one contract.

**Stage 2 — Pareto inside the cell.** Among that cell's fills in the fill table, trade speed, price, capability, and specialty against the user's declared profile. Specialty is a tie-breaker; it never overturns stage 1. With no declarations, take the cheapest adequate fill, each lane priced at its default dial; dial positions never enter the lane-level comparison.

**Re-routing.** An unavailable or timed-out lane gets the same contract re-routed to another fill in the cell, disclosed. Both CLI lanes down → the claude lane, stating any loss of cross-vendor review. Availability is decided by dispatch, not probes.

**Escalation.** One failed acceptance gets a rework ticket (lane-owned defect; never a hand fix) or a corrected contract (contract gap). When the rework ticket also fails, attribute: capability → a higher-tier worker in a fresh session under a takeover contract (original contract, prior report, receipt); contract gap → a corrected contract on the same lane session.

## User routing profile

Stage 2 inputs enter only as declarations, in two layers.

**Persistent judgments.** The **fill table**, (role, tier) → candidate lanes and dials, and specialty notes live in the user routing profile the caller's instructions name, not this repo. Read it before the first model assignment; re-read it when it changes or has slid out of context; if none is named or it cannot be read, report the gap and assume nothing. A `dial` is written `model[first-round options | escalation-only]`, `*` marks the default; options after `|` are reached by a worker only through escalation after a failed rework ticket, and by any role only on user declaration.

**Volatile state** (quota balance, deadline pressure) is declared verbally when the work starts, holds for that session only, and is never written to disk.

**The handoff declaration.** Per task or per session; it alone makes the handoff lane selectable in stage 2. The main agent may suggest it for large, fully-specified, non-urgent work; a suggestion never routes.

**The low-confidence escape hatch.** Ask the user before routing in exactly two cases, offering at least two options with reasons: declared constraints conflict on the deciding dimension; or the task is high-risk (correctness-critical or hard to reverse) and the profile is silent. Not for a mechanical task, absent declarations (the default), or an unavailable lane (re-route and disclose). Parallel fan-out: ask at most once per batch.

## The delivery contract

Lanes share none of your context. Every dispatch carries five parts:

1. **Objective**: the outcome and its acceptance criteria, not the steps
2. **Files**: the owned scope (paths or directories); new files inside it are allowed
3. **Interfaces**: shared or external contracts the result must match; may be none
4. **Constraints**: the reserved items: what must not change, choices fixed upstream, and the operations the caller keeps in its own session; these bind the lane, its subagents, and its verification commands
5. **Verification**: for a worker, commands whose output is acceptance evidence, including at least one check that fails when the goal is not met; for an explorer or advisor, the expected evidence or verdict shape, possibly empty

Everything Constraints leaves open is the lane's decision. Steps are not written by default: only when an upstream decision already fixed a sequence, or as targeted direction after a failed rework ticket.

**Contract gap versus implementation choice.** A contract gap (unclear expected behaviour, conflicting requirements, a reserved interface that would have to change, no way to tell what passes) comes back as a report and gets a corrected contract. An unspecified implementation choice (internal function boundaries, an equivalent data structure, test organisation, in-scope error handling) is the lane's, neither reported nor waited on.

**Upstream task artifacts.** When an issue, spec, or task file exists, the contract references its path and inlines only the acceptance criteria, reserved constraints, and verification commands, naming which sections are binding. The main agent neither restates nor re-plans.

**Rework tickets.** A new contract to the same lane, reusing its session: Objective = the defect (requirement violated, reproducible failure, expected behaviour, evidence); Files = the original scope; Verification = the check that failed. No fix inside. Grounds: a violated requirement, a reproducible problem, missing verification, an affected reserved interface; never structural preference.

## Parallelism

Independent contracts (no shared files, no ordering dependency) launch as parallel lanes in a single message; sequential chains and single-file surgery stay serial. For high-stakes work, race two fills on one contract and pick the stronger diff; two fills from families other than the main agent's buy a *third* perspective for one extra lane's cost. Two executors in one working tree overwrite each other; a race isolates each fill's working directory and execution records (see the lanes file).

## Decision-type gate

Consult the advisor at these decision types; the list binds any main agent, at any tier, in either posture:

- committing to an architecture, data migration, API shape, or refactor strategy
- overturning an established plan
- changing a public interface or a cross-module dependency
- relaxing acceptance criteria
- the same problem failing twice

All take the **decision** shape: pass the decision, constraints, and options; the advisor reads the code itself. The **acceptance** shape arrives through Verification's Tier 3, never by step count. Act on the verdict or surface the disagreement; never silently ignore it. No mechanical enforcement, no per-diff review.

## Verification

Reports are claims, not evidence; the object of review is the contract. Three tiers:

1. **Tier 1 — every lane by default.** Accept on the lane's verification evidence (command, exit code, output tail, spot-checked against the working tree) plus `git diff --stat`. A full unscoped `git diff` never enters the main agent's context.
2. **Tier 2 — specific doubt.** On a specific doubt from the report, stat, or verification output, read a path-scoped `git diff <file>`. When the lane authored the acceptance test, read it: it is part of the claim, not evidence.
3. **Tier 3 — correctness-critical work, same-family diffs, and the user asking for review.** The advisor in its acceptance shape (context-clean, read-only, reads the diff plus the receipt) returns a verdict plus flagged hunks; read only those. Prefer a cross-vendor fill for a same-family diff. A verdict is still a claim; the main agent keeps final judgment.

"Should work", "tests should pass", or a report with no command output means not done.
