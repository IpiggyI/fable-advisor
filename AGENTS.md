# fable-advisor

A Claude Code / Cursor plugin that ships a role pool (explorer / worker / advisor at light / standard / senior tiers) reached through the grok, codex, claude and handoff lanes; any model can run the main agent, and a posture (orchestrating or implementing) decides whether it edits deliverables itself — see [ADR 0014](docs/adr/0014-role-pool-posture.md). This is a fork of [`DannyMac180/fable-advisor`](https://github.com/DannyMac180/fable-advisor) carrying local hardening commits — see [ADR 0001](docs/adr/0001-upstream-sync-fork.md) before syncing upstream.

## Agent skills

### Issue tracker

Issues and specs live as markdown under `.scratch/<feature-slug>/`, tracked in-repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. `docs/adr/` is the only decision store. See `docs/agents/domain.md`.

### Plugin release & local update

Version bump (two files) → push to `origin` → per-side `claude plugin` update on WSL and Windows. See `docs/agents/plugin-release.md`.

### Cursor lane family gate

Canonical copies of the user-level Cursor `preToolUse` gate and Task pin rule live under `cursor-hooks/` (not `plugin/hooks/`). See `docs/agents/cursor-lane-gate.md`.

### Delegation boundary by artifact class

Per [ADR 0013](docs/adr/0013-delivery-contract-not-build-instructions.md) and [ADR 0014](docs/adr/0014-role-pool-posture.md), in the **orchestrating posture** the main agent never edits deliverables, whatever the size — they go through a `worker`; coordination artifacts it writes directly in either posture. In the implementing posture (no upstream task artifact, or the user said so) the main agent may edit deliverables itself. In this repo:

- Deliverables (worker only while orchestrating): `plugin/**`, `tests/**`, `cursor-hooks/**`, `README.md`, `docs/zh/**`.
- Coordination artifacts (main agent may write): `.scratch/**`, `docs/adr/**`, `CONTEXT.md`, `AGENTS.md`, `docs/agents/**`, `.fable-advisor/**`, and the two version fields named in `docs/agents/plugin-release.md`.

### Chinese mirror of runtime docs

Every `plugin/**/*.md` has a Chinese twin at the same relative path under `docs/zh/` (`docs/zh/skills/orchestration/…`, `docs/zh/agents/…`). A change to a runtime `.md` updates its twin in the same commit. `python3 tests/test_zh_mirror.py` checks the one-to-one existence (not content). The mirror is repo-only and does not ship.
