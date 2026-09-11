# Fable Advisor — postures, roles, fill table

Replaces the two-mode text (architect tier / advisor-only). Mode is no longer selected by model identity; any model may be the main agent. Doctrine lives in the fable-advisor:orchestration skill; this file carries the user-side inputs only. Dated 2026-09-11; anchored to Grok 4.6 / GPT-6 Astra / GPT-5.6 Luna / Opus 5 / Fable 5.1 — re-evaluate an entry when any model it involves changes generation.

## Posture

Two postures, differing in exactly one rule: whether the main agent edits deliverables itself. Dispatching any role (explorer / worker / advisor) is available in both.

- **Orchestrating**: write delivery contracts, dispatch workers, accept on evidence; never edit deliverables (the repo's `AGENTS.md` maps the classes). Coordination artifacts are written directly.
- **Implementing**: edit deliverables directly; still dispatch explorers, workers, advisors as useful.
- Selector, in order: my declaration this session ("直接改" → implementing; "派活 / 编排" → orchestrating) → an upstream instruction in the prompt → default: an upstream task artifact exists (`.scratch/<feature>/issues/`, spec, Trellis task) → orchestrating; none → implementing.
- Posture is relative to a dispatch: a lane is implementing for its own contract and orchestrating toward subagents it spawns. Depth is not limited.

## Decision-type gates (any main agent, any tier)

Consult the advisor (`fable-advisor`, decision shape) before: an architecture, data migration, API shape, or refactor strategy; overturning an established plan; changing a public interface or cross-module dependency; relaxing acceptance criteria; the same problem failing twice. Before declaring a multi-step deliverable done, use the advisor's acceptance shape (contract + diff + receipt). No other mandatory review points; no per-diff review.

## Fill table — (role, tier) → candidates, best first

Candidates are dials (model[effort]) reached through a lane. The doctrine's stage 1 picks the cell; this table only orders fills inside it.

| Cell | Fills |
|---|---|
| explorer @ light | grok-4.6[medium] via grok lane report mode › gpt-5.6-luna[high] via codex lane report mode › harness built-in Explore |
| explorer @ standard / senior | same as worker fills of that tier, in report mode |
| worker @ light | grok-4.6[medium] › gpt-5.6-luna[high] (Luna as a worker only on my declaration or when the task is simple and the GPT family is wanted) |
| worker @ standard | grok-4.6[xhigh] › claude-opus-5[high] via claude lane (`worker` agent) |
| worker @ senior | gpt-6-astra[medium]; escalate to [high] for unusually hard work. Takeover contract = original contract + prior report + receipt, fresh session |
| advisor (default senior) | gpt-6-astra[high] via codex lane report mode (Claude Code: `/codex:adversarial-review` also fits) › claude-fable-5-1[high] via `fable-advisor` agent. Any tier is allowed; the advisor's authority is the code it reads |

Notes: `gpt-5.6-sol` is outside the codex runner whitelist since 4.0.0 (ADR 0003 addendum); re-add only if it returns to my use set. Effort defaults per role: worker medium, explorer medium, advisor high; a lane's default applies only when the role is silent.

## Pareto inputs (carried from 2026-09-06)

- Speed (fastest first): grok-4.6 > fable5.1 ≈ astra ≈ opus5 > Luna-max.
- Price (cheapest first): Luna-max < grok-4.6 << opus5 ≤ astra ≤ fable5.1.
- Capability: Luna-max < grok-4.6 ≤ opus5 < astra ≈ fable5.1.
- Specialty: frontend leans the claude lane; backend leans the codex lane. Re-evaluate as counter-examples accumulate.
- Volatile state (quota headroom, deadline) enters only by my oral declaration at kickoff, valid for the session, never persisted. No declaration → cheapest adequate fill at its default dial.
- The handoff lane joins the candidate set only when I declare it per task or session.
- Low-confidence escape hatch: per the orchestration skill's "User routing profile" section.

## Retired

- The two-mode selector by model series and the third-party architect allowlist block: gone. Capability gating now runs on decision types, not on model identity.
