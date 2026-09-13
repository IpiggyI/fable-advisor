# The lanes in Cursor — pinned subagents, plus the codex runner through Shell

Read this before dispatching a lane in Cursor. Cursor loads this skill through its Claude-plugin compatibility paths. The grok lane and the claude lane are native: a subagent dispatch pins its own model. The codex lane is not in the Task enum; it is reached by running the codex runner from [lanes-claude-code.md](lanes-claude-code.md) through the Shell tool.

## Task dispatches — grok lane and claude lane

- **Invocation.** The dispatch prompt opens with one line pointing the subagent at `<plugin-root>/skills/orchestration/lane-preamble.md` — nothing prepends it for you here, and the executor-side contract must reach every lane. The five-part contract follows, verbatim.
- **Roles.** A worker is a `generalPurpose` dispatch with an explicit `model`; an explorer is an `explore` (or `generalPurpose`) dispatch with an explicit `model`; the advisor is the named agent `fable-advisor`, pinned explicitly. The family of the pin is the fill table's choice: a Grok-family pin is the grok lane, a Claude-family pin is the claude lane. The tier is the dial the pin names.
- **Pin explicitly, every time.** Agent frontmatter `model:` is not honored for plugin-loaded agents in Cursor, and Task inherits the session model when `model` is omitted — an unpinned dispatch silently becomes whatever the session runs. The user-level lane family gate covers one case: a `fable-advisor` dispatch whose `model` is missing or `inherit`. Which family you pin, and an unpinned `generalPurpose` worker, are yours to catch. Use the slug live in this turn's allowlist; a skill example may name a generation the allowlist lacks.
- **Same-model dispatch.** The one dispatch that carries no `model`: the claude-lane dial for doctrine prose in the orchestrating posture is a `generalPurpose` dispatch with `model` omitted — inheriting the session model is the point, not an omission, and it is not a named-agent dispatch, so the gate does not fire. Say "inherit" in the routing disclosure so it is not mistaken for an unpinned lane.
- **Acceptance.** The report returns in-band as the dispatch result, and a failed or unavailable dispatch fails loudly in-band too. Acceptance runs entirely on the verification tiers in [SKILL.md](SKILL.md); there are no receipts for Task dispatches.
- **Rework.** A rework ticket is a Task `resume` with the prior dispatch's agent id, carrying the rework contract (defect, original scope, failing check) as the new prompt — the lane keeps the context it already built. When the rework ticket also fails, attribute (SKILL.md "Escalation"): a contract gap resumes again under a corrected contract; a capability failure is a fresh dispatch at a higher tier with the takeover contract.
- **Re-routing.** A dispatch that fails because the model is unavailable on the user's plan re-routes to another fill in the same cell, disclosed explicitly — the same rule as the CLI lanes.
- **Effort is pinned to the slug.** An ad-hoc model pin carries a fixed effort tier — the codex lane's `effort` knob does not exist on a bare dispatch. Bracket parameters (`<slug>[effort=high]`) are available only in a custom agent definition file; add one deliberately when a task genuinely needs escalated effort, not by default.
- **Races.** A pick-the-stronger-diff race is two pinned dispatches in a single message — no pending files to keep distinct.
- **Economics.** Each vendor's models draw on their own quota pool in Cursor, so lane prices — and the whole cost discipline — apply as written.

## The codex lane through Shell

The GPT family is reached by running `node "<plugin-root>/scripts/run-codex.mjs" --spec .fable-advisor/pending/<slug>.json --cwd "$(pwd)"` through the Shell tool. The spec, the pending/receipt flow, the wait protocol (block on the Shell process, never a fixed sleep), the receipt fields, `resume_session_id`, and `mode: "report"` for read-only roles are exactly as in [lanes-claude-code.md](lanes-claude-code.md). Two differences:

- **No receipt gate.** Whether Cursor loads plugin Stop hooks is unverified, so this lane is designed as if it does not: nothing blocks the session while a pending spec lacks a `complete` receipt. It fails open, at the same safety level as the handoff lane. The main agent judges the receipt itself — `error_class: complete`, a session id, verification output spot-checked against the tree — and sweeps `.fable-advisor/pending/` before ending the session: land, abandon (delete the file and say so), or state that it carries over.
- **Wait on the Shell tool's clock.** The runner's idle deadline and `timeout_sec` work as documented; the Shell tool's own foreground limit is the outer ceiling, so a long ticket runs in the background and is awaited on the shell id.

## Subagent lifecycle

A subagent spawned with a `name` ("teammate") persists after finishing so it can be messaged again — every named batch you don't clean up lingers as background work until the session exits. Two rules:

- Serial batches (same file, strict ordering) gain nothing from backgrounding: run them with `run_in_background: false` and consume the report inline.
- When a batch does run in the background, stop its teammate only after acceptance — verification passing is not the end, because a rework ticket resumes the same agent. Once the diff is accepted and no follow-up is expected, stop it; don't leave accepted lanes idling to session end.
