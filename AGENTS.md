# fable-advisor

A Claude Code / Cursor plugin that ships a role pool (explorer / worker / advisor at `mainstay` / `crux` / `rescue` tiers) reached through the grok, codex, claude and handoff lanes; any model can run the main agent, and a posture (orchestrating or implementing) decides whether it edits deliverables itself — see [ADR 0014](docs/adr/0014-role-pool-posture.md). This is a fork of [`DannyMac180/fable-advisor`](https://github.com/DannyMac180/fable-advisor) carrying local hardening commits — see [ADR 0001](docs/adr/0001-upstream-sync-fork.md) before syncing upstream.

## Agent skills

### Issue tracker

Issues and specs live as markdown under `.scratch/<feature-slug>/`, tracked in-repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. `docs/adr/` is the only decision store. See `docs/agents/domain.md`.

### Plugin release & local update

Write the version manual (`docs/manuals/<version>.html`) → version bump (two files) → push to `origin` → per-side `claude plugin` update on WSL and Windows → run the companion installer. See `docs/agents/plugin-release.md`.

### Companion installer

`scripts/install-user-level.py` copies the three canonical user-level files (routing profile, Cursor pin rule, Cursor gate script) from this checkout onto their live paths under each `--home`, deletes the retired rule files, and warns when `~/.cursor/hooks.json` lacks the gate entry; `--check` is what `tests/test_user_level_archive.py` runs. Live copies are never edited by hand. See [ADR 0018](docs/adr/0018-post-5-1-tuning.md).

### Cursor lane family gate

Canonical copies of the user-level Cursor `preToolUse` gate and Task pin rule live under `cursor-hooks/` (not `plugin/hooks/`). See `docs/agents/cursor-lane-gate.md`.

### User routing profile

Canonical profile: `docs/agents/fable-advisor-routing.md` (Chinese backup `docs/agents/fable-advisor-routing.zh.md`, not installed). Live copy: `~/.claude/docs/fable-advisor-routing.md` on both sides. The prompts-repo copy is an optional `--also` snapshot, not an edit source and not checked. The skill still reads whichever path the caller names; this fork's `AGENTS.md` names the live path. See [ADR 0017](docs/adr/0017-routing-profile-edit-source.md).

Edit here, then run the companion installer (`python3 scripts/install-user-level.py --home ~ --home /mnt/c/Users/Shy` on this machine) and `python3 tests/test_user_level_archive.py`. The profile's columns are the three tiers: new work starts in `mainstay`, may start in `crux` when a key difficulty is already identified, and reaches `rescue` only after a capability failure in `crux` or a user declaration (see `CONTEXT.md`). The Cursor Task pin rule stays a separate user-level artifact: canonical `cursor-hooks/fable-lane-pin.mdc`, Chinese backup `cursor-hooks/zh/fable-lane-pin.mdc`.

### Delegation boundary by artifact class

Per [ADR 0013](docs/adr/0013-delivery-contract-not-build-instructions.md) and [ADR 0014](docs/adr/0014-role-pool-posture.md), in the **orchestrating posture** the main agent never edits deliverables, whatever the size — they go through a `worker`; coordination artifacts it writes directly in either posture. In the implementing posture (no upstream task artifact, or the user said so) the main agent may edit deliverables itself. In this repo:

- Deliverables (worker only while orchestrating): `plugin/**`, `tests/**`, `cursor-hooks/**`, `scripts/**`, `README.md`, `docs/zh/**`, `docs/manuals/**`.
- Coordination artifacts (main agent may write): `.scratch/**`, `docs/adr/**`, `CONTEXT.md`, `AGENTS.md`, `docs/agents/**`, `.fable-advisor/**`, and the two version fields named in `docs/agents/plugin-release.md`.

### Chinese mirror of runtime docs

Every `plugin/**/*.md` has a Chinese twin at the same relative path under `docs/zh/` (`docs/zh/skills/orchestration/…`, `docs/zh/agents/…`). A change to a runtime `.md` updates its twin in the same commit. `python3 tests/test_zh_mirror.py` checks the one-to-one existence (not content). The mirror is repo-only and does not ship. The Chinese backup of the Cursor pin rule stays in `cursor-hooks/zh/`; the Chinese backup of the routing profile stays in `docs/agents/fable-advisor-routing.zh.md`. Neither lives under `docs/zh/`.
