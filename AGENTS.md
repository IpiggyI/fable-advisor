# fable-advisor

A Claude Code / Cursor plugin that ships a role pool (explorer / worker / advisor at `mainstay` / `crux` / `rescue` tiers) reached through the grok, codex, claude and handoff lanes; any model can run the main agent, and a posture (orchestrating or implementing) decides whether it edits deliverables itself — see [ADR 0014](docs/adr/0014-role-pool-posture.md). This is a fork of [`DannyMac180/fable-advisor`](https://github.com/DannyMac180/fable-advisor) carrying local hardening commits — see [ADR 0001](docs/adr/0001-upstream-sync-fork.md) before syncing upstream.

## Agent skills

### Issue tracker

Issues and specs live as markdown under `.scratch/<feature-slug>/`, tracked in-repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) plus the terminal state `resolved`, recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. `docs/adr/` is the only decision store. See `docs/agents/domain.md`.

### Plugin release & local update

Write the version manual (`docs/manuals/<version>.html`) → version bump (two files) → push to `origin` → per-side `claude plugin` update on WSL and Windows → run the companion installer. See `docs/agents/plugin-release.md`.

### Companion installer

`scripts/install-user-level.py` copies the two canonical user-level files (Cursor pin rule, Cursor gate script) from this checkout onto their live paths under each `--home`, and warns when `~/.cursor/hooks.json` lacks the gate entry; `--check` is what `tests/test_user_level_archive.py` runs. Live copies are never edited by hand. See [ADR 0018](docs/adr/0018-post-5-1-tuning.md).

### Cursor lane family gate

Canonical copies of the user-level Cursor `preToolUse` gate and Task pin rule live under `cursor-hooks/` (not `plugin/hooks/`). See `docs/agents/cursor-lane-gate.md`.

### User routing profile

The profile ships inside the plugin: `plugin/skills/orchestration/routing-profile.md`, with its Chinese translation as the mirror twin `docs/zh/skills/orchestration/routing-profile.md`. The skill reads it directly; there is no live copy, and no instruction outside the plugin names it. See [ADR 0023](docs/adr/0023-routing-profile-in-plugin.md).

Edit that file (a deliverable under `plugin/**`), then release and update both sides (see "Plugin release & local update"). A changed cell is a minor version, and the declaration date in the profile's first paragraph changes with it. The profile's columns are the three tiers (`CONTEXT.md`, "档位"). The Cursor Task pin rule stays a separate user-level artifact: canonical `cursor-hooks/fable-lane-pin.mdc`, Chinese backup `cursor-hooks/zh/fable-lane-pin.mdc`.

### Delegation boundary by artifact class

Per [ADR 0013](docs/adr/0013-delivery-contract-not-build-instructions.md) and [ADR 0014](docs/adr/0014-role-pool-posture.md), in the **orchestrating posture** the main agent never edits deliverables, whatever the size — they go through a `worker`; coordination artifacts it writes directly in either posture. In the implementing posture (no upstream task artifact, or the user said so) the main agent may edit deliverables itself. In this repo:

- Deliverables (worker only while orchestrating): `plugin/**`, `tests/**`, `cursor-hooks/**`, `scripts/**`, `README.md`, `docs/zh/**`, `docs/manuals/**`.
- Coordination artifacts (main agent may write): `.scratch/**`, `docs/adr/**`, `CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, `docs/agents/**`, `docs/upstream-sync/**`, `.agent-discuss/**`, `.fable-advisor/**`, and the two version fields named in `docs/agents/plugin-release.md`.

In the orchestrating posture, the doctrine prose under `plugin/skills/**` (except `routing-profile.md`) and `plugin/agents/**` goes through same-model dispatch. The artifact class triggers it, not how central the text feels. The routing profile records the user's declared values, so a profile edit goes through an ordinary `worker`.

### Chinese mirror of runtime docs

Every `plugin/**/*.md` has a Chinese twin at the same relative path under `docs/zh/` (`docs/zh/skills/orchestration/…`, `docs/zh/agents/…`). A change to a runtime `.md` updates its twin in the same commit. `python3 tests/test_zh_mirror.py` checks the one-to-one existence (not content). The mirror is repo-only and does not ship. The Chinese backup of the Cursor pin rule stays in `cursor-hooks/zh/`; it does not live under `docs/zh/`.
