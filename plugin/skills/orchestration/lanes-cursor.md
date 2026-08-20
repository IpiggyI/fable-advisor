# The lanes in Cursor — pinned subagents, no runners

Read this before dispatching a lane in Cursor. Cursor loads this skill through its Claude-plugin compatibility paths and exposes every lane's model natively: a subagent dispatch pins its own model. The runner apparatus in [lanes-claude-code.md](lanes-claude-code.md) is Claude Code machinery — skip it entirely: no pending files, no receipts, no receipt gate.

- **Invocation.** Write the same five-part spec, verbatim, as the subagent's prompt, and pin the lane's model explicitly on every dispatch: Grok 4.6 for the routine lane, GPT-5.6 Sol for the cross-vendor lane, an Opus pin for the in-house lane, and a Fable pin (e.g. `claude-fable-5-thinking-high`) when dispatching `fable-advisor` for judgment. Agent frontmatter `model:` is not honored for plugin-loaded agents in Cursor — a bare named-agent dispatch silently inherits the session model, so an unpinned dispatch from a non-flagship session quietly downgrades the lane (verified 2026-08-12).
- **Acceptance.** The report returns in-band as the dispatch result, and a failed or unavailable dispatch fails loudly in-band too. Acceptance runs entirely on the verification tiers in [SKILL.md](SKILL.md) — they were always the real judge; the receipt gate only ever policed out-of-band CLI runs, and Cursor has none.
- **Re-routing.** A dispatch that fails because the model is unavailable on the user's plan re-routes to the other cross-vendor lane, disclosed explicitly — the same rule as the CLI lanes. The dispatch-not-probes rule has no object here: there is no CLI auth state to be tempted to probe.
- **Effort is pinned to the slug.** An ad-hoc model pin carries a fixed effort tier — the codex lane's `effort` knob does not exist on a bare dispatch. Bracket parameters (`gpt-5.6-sol[effort=high]`) are available only in a custom agent definition file; add one deliberately when a task genuinely needs escalated effort, not by default.
- **Races.** A pick-the-stronger-diff race is two pinned dispatches in a single message — no pending files to keep distinct.
- **Economics unchanged.** Each vendor's models draw on their own quota pool in Cursor, so the price gradient between lanes — and the whole cost discipline — applies as written.

## Subagent lifecycle

A subagent spawned with a `name` ("teammate") persists after finishing so it can be messaged again — every named batch you don't clean up lingers as background work until the session exits. Two rules:

- Serial batches (same file, strict ordering) gain nothing from backgrounding: run them with `run_in_background: false` and consume the report inline.
- When a batch does run in the background, stop its teammate once its work is verified and it has no follow-up role. Don't leave verified lanes idling to session end.
