# Fable Advisor routing profile

This user routing profile was declared on 2026-09-29. It is anchored to `grok-4.7`, `gpt-6-luna`, `gpt-6-sol`, `gpt-6-astra`, `haiku-4-5`, `sonnet-5-5`, `opus-5-5`, `fable-5-1`, and Cursor's `composer-2.5-fast`. Re-evaluate an entry when any model it involves changes generation. `fable-advisor:orchestration` consumes this profile and owns orchestration behaviour, including tier entry and the escalation ladder; this file carries the user's values and the in-cell choosing rules those values depend on. A running session keeps the old profile until it restarts.

## Tiers and choosing inside a cell

- Three columns: `mainstay` carries most everyday work, `crux` takes the hard parts, `rescue` is the backup reached only after `crux` fails or on my declaration. Tiers are split by model; efforts only subdivide a tier.
- `›` separates candidates.
- Candidates are ordered by my preference, not by capability or price. Different model families have different strengths, and picking by need replaces "the later the candidate, the more judgment it needs". Three orders are deliberate:
  - explorer `rescue` puts `opus-5-5` before the weaker `gpt-6-sol`, because in Claude Code the explorer prefers the Claude family;
  - worker `mainstay` puts `grok-4.7` before the cheaper `gpt-6-luna`, because `grok-4.7` gives more capability per unit of price;
  - advisor `mainstay` puts `gpt-6-astra` before the cheaper `opus-5-5`, because I want an opinion from another vendor.
- Take a later candidate when the task falls on its specialty. Specialties are varied; these are examples, not a complete list: simple, high-volume work favours `gpt-6-luna`; a lower price is itself a specialty; frontend leans the claude lane; backend and complex work lean the codex lane; a different vendor's opinion favours a cross-vendor candidate.
- The lane default order is grok lane › codex lane › claude lane. It applies only when several candidates fit equally well, and when a candidate has to be replaced — a whole lane unavailable, one candidate unavailable, or the codex runner failing to start a model all use this order, never the written order.
- Exception, Claude Code only: the explorer uses claude lane › grok lane › codex lane for ties and replacements, and its cells list the Claude candidate first. Claude Code has its own explorer but cannot choose its model; this plugin fills that gap. The reason does not hold in Cursor.
- Example raise path (worker): `grok-4.7[high]` → `gpt-6-sol[xhigh]` → `opus-5-5[xhigh]` → me.

## Model ranking

- Capability: `gpt-6-luna` < `grok-4.7` ≤ `gpt-6-sol` < `sonnet-5-5` < `opus-5-5` ≈ `gpt-6-astra` ≈ `fable-5-1`. Read ≈ as the same level and keep the direction of ≤: `gpt-6-sol` is close to `grok-4.7` but not below it. Moving between models of the same level, across vendors, is not a downgrade.
- Price: `gpt-6-luna` << `grok-4.7` < `gpt-6-sol` ≈ `sonnet-5-5` < `opus-5-5` < `gpt-6-astra` < `fable-5-1`. `grok-4.7` is close to `gpt-6-sol` in capability and cheaper.
- `haiku-4-5` (explorer only, the most basic investigator) and `composer-2.5-fast` are not ranked. A raise from either picks from the `crux` cell by the same need-based rule.
- Speed is not listed: the models show no clear difference.

## Declared assumptions

- Changing model improves results more than raising effort.
- `xhigh` is a clear step up.

Both expire at the next model generation change; re-evaluate the table then.

## Advisor mapping

- Acceptance shape: `mainstay` at its default, `gpt-6-astra[low]`.
- Decision shape: `mainstay` at `medium`.
- A verdict that reports low confidence: `crux`.
- `rescue`: only on my declaration.

## Claude Code candidates

Reach: Grok through the grok runner — omit `model` to follow the CLI default, currently `grok-4.7` (observed 2026-09-27), and set `effort`; GPT through the codex runner (spec `model`, `effort`); Claude through this plugin's agent files with a per-dispatch `model` (dispatch without `name`). The per-dispatch `model` accepts only the aliases `haiku`, `sonnet`, `opus`, `fable`; an alias is a pointer, and the model actually run is the `message.model` in the subagent's record. Agent file per Claude dial:

- explorer: `haiku-4-5` → `explorer-h` with `haiku` (no effort dimension; the file's effort has no effect); `sonnet-5-5[high]` → `explorer-h` with `sonnet`; `opus-5-5[high]` → `explorer-h`, `opus-5-5[xhigh]` → `explorer-xh`, both with `opus`. No explorer file carries `medium`, so `sonnet-5-5[medium]` is also dispatched through `explorer-h` and runs at `high`.
- worker: `opus-5-5[medium]` → `worker-md`, `[high]` → `worker-h`, `[xhigh]` → `worker-xh`, all with `opus`.
- advisor: `[medium]` → `advisor-md`, `[high]` → `advisor-h`, `[xhigh]` → `advisor-xh`, with `opus` or `fable`.

| Role | `mainstay` | `crux` | `rescue` |
|---|---|---|---|
| explorer | haiku-4-5 › gpt-6-luna[high*, xhigh] › grok-4.7[medium*, high] | sonnet-5-5[medium*, high] › gpt-6-luna[max] › grok-4.7[xhigh] | opus-5-5[high*, xhigh] › gpt-6-sol[high*, xhigh] |
| worker | grok-4.7[high*, xhigh] › gpt-6-luna[xhigh*, max] › gpt-6-sol[high] | gpt-6-sol[xhigh*, max] › opus-5-5[medium*, high] › gpt-6-astra[low*, medium] | opus-5-5[xhigh] › gpt-6-astra[high*, xhigh] |
| advisor | gpt-6-astra[low*, medium] › opus-5-5[medium] › fable-5-1[medium] | opus-5-5[high*, xhigh] › gpt-6-astra[high] › fable-5-1[high] | gpt-6-astra[xhigh] › fable-5-1[xhigh] |

## Cursor candidates

Worker and advisor rows are the Claude Code rows. The explorer row follows the lane default order, with `composer-2.5-fast` first in `mainstay`.

Availability is decided by each candidate's actual entrance: GPT candidates through the codex runner via Shell (report mode for explorer and advisor); `grok-4.7`, Claude candidates, and `composer-2.5-fast` through a model-pinned `Task` (an `advisor-*` agent for the advisor, `explore` or `generalPurpose` otherwise). The turn's allowlist constrains only the model-pinned `Task` dispatches. A candidate whose variant is missing there is skipped and the disclosure says so. Slugs are not persisted here.

| Role | `mainstay` | `crux` | `rescue` |
|---|---|---|---|
| explorer | composer-2.5-fast › grok-4.7[medium*, high] › gpt-6-luna[high*, xhigh] › haiku-4-5 | grok-4.7[xhigh] › gpt-6-luna[max] › sonnet-5-5[medium*, high] | gpt-6-sol[high*, xhigh] › opus-5-5[high*, xhigh] |
| worker | grok-4.7[high*, xhigh] › gpt-6-luna[xhigh*, max] › gpt-6-sol[high] | gpt-6-sol[xhigh*, max] › opus-5-5[medium*, high] › gpt-6-astra[low*, medium] | opus-5-5[xhigh] › gpt-6-astra[high*, xhigh] |
| advisor | gpt-6-astra[low*, medium] › opus-5-5[medium] › fable-5-1[medium] | opus-5-5[high*, xhigh] › gpt-6-astra[high] › fable-5-1[high] | gpt-6-astra[xhigh] › fable-5-1[xhigh] |
