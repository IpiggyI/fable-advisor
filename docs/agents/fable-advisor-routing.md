# Fable Advisor routing profile

This user routing profile was declared on 2026-09-11. It is anchored to Grok 4.6, GPT-6 Astra, GPT-5.6 Luna, Opus 5, and Fable 5.1. Re-evaluate an entry when any model it involves changes generation.

The tables give the user's candidate order and declared reasoning effort. An explicit cell value takes precedence; otherwise use the role defaults: worker medium, explorer medium, and advisor high. `fable-advisor:orchestration` consumes this profile and owns orchestration behavior.

## Claude Code candidates

| Cell | Candidates, best first |
|---|---|
| explorer @ light | grok-4.6[medium] › gpt-5.6-luna[high] › the host's built-in Explore |
| explorer @ standard / senior | the worker candidates for that tier |
| worker @ light | grok-4.6[medium] › gpt-5.6-luna[high]. Use Luna as a worker only on my declaration or when the task is simple and the GPT family is wanted |
| worker @ standard | grok-4.6[xhigh] › claude-opus-5[high] |
| worker @ senior | gpt-6-astra[medium]; use gpt-6-astra[high] for unusually hard work |
| advisor (default senior) | gpt-6-astra[high] › claude-fable-5-1[high] |

## Cursor candidates

Cursor model-family values come from the live allowlist; do not persist a possibly stale slug. Where a cell does not specify an effort, use the role default above.

| Cell | Candidates, best first |
|---|---|
| explorer @ light | grok-4.6[medium] › gpt-5.6-luna[high] › the host's built-in `explore` |
| explorer @ standard / senior | the worker candidates for that tier |
| worker @ light | a live Grok-family slug › gpt-5.6-luna[high]. Use Luna as a worker only on my declaration or when the task is simple and the GPT family is wanted |
| worker @ standard | a live Grok-family slug › a live Opus-family slug |
| worker @ senior | gpt-6-astra[medium]; use gpt-6-astra[high] for unusually hard work |
| advisor (default senior) | a live Fable-family slug › gpt-6-astra[high] |

## Resource preferences

Declared on 2026-09-06:

- Speed, fastest first: grok-4.6 > fable5.1 ≈ astra ≈ opus5 > Luna-max.
- Price, cheapest first: Luna-max < grok-4.6 << opus5 ≤ astra ≤ fable5.1.
- Capability: Luna-max < grok-4.6 ≤ opus5 < astra ≈ fable5.1.
- Specialty: frontend leans the claude lane; backend leans the codex lane. Re-evaluate as counter-examples accumulate.
- Quota headroom and deadline enter only through my oral declaration at kickoff. They are valid for that session and are never persisted. Without a declaration, use the cheapest adequate candidate at its listed dial.
- The handoff lane joins the candidate set only when I declare it per task or session.
