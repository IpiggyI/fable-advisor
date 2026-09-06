# fable-advisor

A Claude Code plugin implementing the architect pattern: the session runs a flagship-tier model as a full-time architect and routes implementation to cheaper cross-vendor lanes. This is a fork of [`DannyMac180/fable-advisor`](https://github.com/DannyMac180/fable-advisor) carrying local hardening commits — see [ADR 0001](docs/adr/0001-upstream-sync-fork.md) before syncing upstream.

## Agent skills

### Issue tracker

Issues and specs live as markdown under `.scratch/<feature-slug>/`, tracked in-repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, unchanged (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. `docs/adr/` is the only decision store. See `docs/agents/domain.md`.

### Plugin release & local update

Version bump (two files) → push to `origin` → per-side `claude plugin` update on WSL and Windows. See `docs/agents/plugin-release.md`.

### Cursor lane family gate

Canonical copies of the user-level Cursor `preToolUse` gate and Task pin rule live under `cursor-hooks/` (not `plugin/hooks/`). See `docs/agents/cursor-lane-gate.md`.
