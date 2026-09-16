# Fable Advisor routing profile

This user routing profile was declared on 2026-09-16 and replaces the 2026-09-11 profile. It is anchored to Grok 4.6, GPT-6 Astra, GPT-5.6 Sol, GPT-5.6 Luna, Opus 5, Sonnet 5, Haiku 4.5, Fable 5.1, and Cursor's Composer 2.5. Re-evaluate an entry when any model it involves changes generation. `fable-advisor:orchestration` consumes this profile and owns orchestration behaviour; this file carries only the user's values.

## First-round pool and the senior gate

- The `light` and `standard` columns are one **first-round pool**. Choose between them by the skill's stage 1 judgment; there is no precondition for either, and a first-round dispatch may take any dial in the pool, including the most expensive one, when the task warrants it. With no reason to do otherwise, take the cheapest adequate candidate at its `*` dial.
- The `senior` column is gated: it is reached only through the skill's escalation ladder (two capability-attributed failures inside the pool) or my declaration. Its dials are, on purpose, different models from the pool.
- Dial notation: `model[a*, b, c]` lists the efforts of that model available in that cell; all are first-round options and `*` is the default. A model with no effort dimension is written bare.
- Candidate order inside a cell is the lane default order: grok lane › codex lane › claude lane. Specialty only breaks ties: frontend leans the claude lane, backend leans the codex lane. Complex work leans the codex lane.
- Escalation follows the skill's ladder R1–R4. The same model is raised at most once, so the typical path is `grok-4.6[medium]` → `grok-4.6[xhigh]` → `gpt-6-astra[medium]`.

## Claude Code candidates

Reach: Grok through the grok runner (spec `effort`); GPT through the codex runner (spec `model`, `effort`); Claude through this plugin's agent files with a per-dispatch `model` (dispatch without `name`). Agent file per effort: explorer `explorer-h` / `explorer-xh`; worker `worker-md` / `worker-h` / `worker-xh`; advisor `advisor-l` / `advisor-md` / `advisor-h` / `advisor-xh`. Haiku has no effort dimension: dispatch it through `explorer-h` and the effort declaration has no effect.

| Role | light | standard | senior (gated) |
|---|---|---|---|
| explorer | grok-4.6[medium] › gpt-5.6-luna[high] › haiku-4-5 | grok-4.6[xhigh] › gpt-5.6-luna[max] › sonnet-5[high*, xhigh] | gpt-5.6-sol[high*, xhigh] › opus-5[high*, xhigh] |
| worker | grok-4.6[medium*, high] › gpt-5.6-luna[xhigh] › sonnet-5[high] | grok-4.6[xhigh] › gpt-5.6-sol[high*, xhigh] › gpt-6-astra[low] › opus-5[high*, xhigh] | gpt-6-astra[medium*, high] |
| advisor | gpt-6-astra[low] › fable-5-1[low] | gpt-6-astra[medium] › fable-5-1[medium] | gpt-6-astra[high*, xhigh] › fable-5-1[high*, xhigh] |

Advisor defaults: the decision shape uses the `standard` cell; the acceptance shape uses the `light` cell. The advisor goes `senior` only when its verdict reports low confidence or I declare it. Luna as a worker: only on my declaration or when the task is simple and the GPT family is wanted.

## Cursor candidates

Reach: GPT rows through the codex runner via Shell (report mode for explorer and advisor); Grok `medium` / `high` through the grok runner via Shell, Grok `xhigh` through a Task pinned to the live Grok slug; Claude rows through a Task pinned to the live slug of that family (an `advisor-*` agent for the advisor, `explore` or `generalPurpose` otherwise); Composer through `explore` pinned to its slug (cursor lane). Slugs come from the turn's allowlist and are not persisted here: a pinned slug's effort is its suffix, so a cell lists only the variants the allowlist carries, and a candidate whose variant is absent is skipped and the disclosure says so. On 2026-09-16 the allowlist carried Grok 4.6 xhigh, Opus 5 high, Fable 5.1 xhigh, and Composer 2.5 fast; Sonnet and Haiku had no slug.

| Role | light | standard | senior (gated) |
|---|---|---|---|
| explorer | composer-2.5-fast › grok-4.6[medium] › gpt-5.6-luna[high] | grok-4.6[xhigh] › gpt-5.6-luna[max] | gpt-5.6-sol[high*, xhigh] › opus-5[high] |
| worker | grok-4.6[medium*, high] › gpt-5.6-luna[xhigh] | grok-4.6[xhigh] › gpt-5.6-sol[high*, xhigh] › gpt-6-astra[low] › opus-5[high] | gpt-6-astra[medium*, high] |
| advisor | gpt-6-astra[low] | gpt-6-astra[medium] | gpt-6-astra[high*, xhigh] › fable-5-1[xhigh] |

Fable appears only in the senior cell because the allowlist carries only its xhigh variant; the standard advisor in Cursor is therefore Astra through the codex runner. Same-model dispatch (doctrine prose in the orchestrating posture) stays a `generalPurpose` dispatch with `model` omitted, outside this table.

## Resource preferences

Declared on 2026-09-06:

- Speed, fastest first: grok-4.6 > fable5.1 ≈ astra ≈ opus5 > Luna-max.
- Price, cheapest first: Luna-max < grok-4.6 << opus5 ≤ astra ≤ fable5.1.
- Capability: Luna-max < grok-4.6 ≤ opus5 < astra ≈ fable5.1.
- Specialty: frontend leans the claude lane; backend leans the codex lane. Re-evaluate as counter-examples accumulate.
- Quota headroom and deadline enter only through my oral declaration at kickoff. They are valid for that session and are never persisted. Without a declaration, use the cheapest adequate candidate at its listed dial.
- The handoff lane joins the candidate set only when I declare it per task or session.

Declared on 2026-09-16:

- The capability gap between models is larger than the gap between efforts of one model. Basis, one test set: opus-5[high] 73%±2%, opus-5[medium] 69%±1%, sonnet-5[high] 48%±5%, sonnet-5[medium] 40%±3%. This is why a raise changes model after one effort step and why the senior column changes model outright.

## Adjusting this profile

1. Edit the cell here. This file is the only edit source; the Chinese file beside it is a translation and is not installed.
2. Run the companion installer from the checkout to refresh the live copies, on this machine `python3 scripts/install-user-level.py --home ~ --home /mnt/c/Users/Shy`; `--check` reports drift without writing.
3. Nothing else changes: the skill re-reads the profile when it changes, and no doctrine or plugin edit is needed for a value change. Update the declaration date in the first paragraph when a table changes.
