# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

This is a **single-context** repo: one `CONTEXT.md` and one `docs/adr/` at the root. There is no `CONTEXT-MAP.md` and no per-context ADR directory.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — the glossary.
- **`docs/adr/`** — read the ADRs that touch the area you're about to work in.

If either doesn't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-upstream-sync-fork.md
│   └── 0002-codex-lane-dewrapper-receipt-gate.md
├── agents/
├── hooks/
├── scripts/
└── skills/
```

## ADR location — one store only

`docs/adr/` is the **only** decision store, and it is tracked in git.

Decisions previously lived in `.memory/decisions/` (the `mem` skill's surface, gitignored). That directory was migrated to `docs/adr/` on 2026-07-25 and no longer exists — see [ADR 0004](../adr/0004-adr-store-in-repo.md). If you find a reference to `.memory/decisions/` anywhere, it is stale; the decision it points at is in `docs/adr/` under the same slug.

`.memory/tasks/` is unaffected and still holds the retrospective task archive.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0002 (receipt gate as the acceptance mechanism) — but worth reopening because…_
