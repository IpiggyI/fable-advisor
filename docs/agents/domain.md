# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

This is a **single-context** repo: one `CONTEXT.md` and one `docs/adr/` at the root. There is no `CONTEXT-MAP.md` and no per-context ADR directory.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — the glossary.
- **`docs/adr/`** — read the ADRs that touch the area you're about to work in.

## ADR location — one store only

`docs/adr/` is the **only** decision store, and it is tracked in git.

The `mem` skill's default decision surface, `.memory/decisions/`, is not used in this repo: record a decision as an ADR under `docs/adr/` instead — see [ADR 0004](../adr/0004-adr-store-in-repo.md).

`.memory/tasks/` holds the retrospective task archive.

When a new ADR revises, supersedes, or withdraws a decision of an earlier ADR, the same change appends a back-pointer to the earlier ADR's Status line, inside its parentheses, for example `决策 2 已被 [ADR 0023](./0023-routing-profile-in-plugin.md) 取代`. A reader who opens only the earlier ADR then learns that part of it no longer holds.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0002 (receipt gate as the acceptance mechanism) — but worth reopening because…_
