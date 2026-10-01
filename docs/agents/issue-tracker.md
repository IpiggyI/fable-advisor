# Issue tracker: Local Markdown

Issues and specs (you may know a spec as a PRD) for this repo live as markdown files in `.scratch/`. The directory is tracked in git — it is deliberately **not** in `.gitignore`, unlike `.memory/` and `.fable-advisor/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading
- Batch checks are recorded once per feature, under a `## Batch checks` heading in its spec or closing ticket

## Batch checks

A delivery contract carries only the checks scoped to its own change; a costly check wider than one contract's change (full suite, browser or end-to-end suite, full build or package) is a batch check (`CONTEXT.md`, "批次验收"). A batch check has no mechanical keeper — the receipt gate does not see it and no runner records it — so the task artifact is where it lives.

Name each batch check once under `## Batch checks` in the feature's spec or closing ticket when the batch is planned, and record its result there when it runs: passed, failed or pending, with its output or the path to it. A feature with a failed or pending batch check, one left unrun by an early stop included, is not done unless the user waives it.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Relationship to `.memory/`

`.memory/` is the `mem` skill's surface — a gitignored, machine-local record of completed work (`.memory/tasks/<month>/<slug>/` holding `task.json`, `prd.md`, `what.md`, `investigation.md`). It is **not** the issue tracker: it is untracked, so a fresh clone has none of it, and it records work retrospectively rather than queueing it.

Keep the two separate: `.scratch/` queues work, `.memory/tasks/` archives it.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
