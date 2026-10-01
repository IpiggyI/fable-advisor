# Plugin release & local update

How a change in this repo reaches the installed plugin on this machine (WSL + Windows). The installed marketplaces on **both** sides point at GitHub (`IpiggyI/fable-advisor`), not at this working tree — an unpushed commit never reaches the plugin.

## 0. Write the version manual

Write `docs/manuals/<version>.html` before bumping any version field. The version manual is a self-contained Chinese HTML with two parts: a full description of this version's behaviour, and every change since the previous version (what changed, why, ADR and ticket). A release does not proceed without it. From 5.2.0 onward each release has one file in `docs/manuals/`.

## 1. Bump the version — two files, not one

- `plugin/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Both must move together. The marketplace version drives update discovery; leaving it stale means `claude plugin update` sees nothing new. Major for a breaking runner or doctrine change, minor for a backward-compatible semantic change, patch for text-only fixes.

Only `plugin/` ships: `marketplace.json` sets `"source": "./plugin"`, and Claude Code copies that directory wholesale into the versioned cache (it does not honor `.pluginignore` or `export-ignore`). `source` stays `./plugin`.

## 1b. Sync the Chinese mirror

Every `plugin/**/*.md` touched by the release has a twin at the same relative path under `docs/zh/` (see `AGENTS.md`, "Chinese mirror of runtime docs"). Update the twins in the same commit and run `python3 tests/test_zh_mirror.py` and `python3 tests/test_shipped_wording.py`.

## 2. Commit and push

Stage the release files by name, review the staged diff, then commit and push:

```bash
git add plugin/ docs/zh/ .claude-plugin/marketplace.json <other files of this release>
git diff --cached --stat
git commit && git push origin main
```

Not `git add -A`: `.scratch/` is tracked and `outputs/` is not ignored, so `-A` sweeps in-flight tickets and local artifacts into the release commit.

Commit style: English imperative summary naming the change, the ADR, and the bump — see `git log --oneline` for precedent.

## 3. Update the WSL side

```bash
claude plugin marketplace update fable-advisor
claude plugin update fable-advisor@fable-advisor
```

## 4. Update the Windows side (from WSL)

CMD refuses a WSL UNC path as its working directory — change to a Windows drive first:

```bash
cd /mnt/c && cmd.exe /c "claude plugin marketplace update fable-advisor && claude plugin update fable-advisor@fable-advisor"
```

## 5. Run the companion installer

From the checkout:

```bash
python3 scripts/install-user-level.py --home ~ --home /mnt/c/Users/Shy
```

`--check` is what the drift test runs.

## 6. Restart and spot-check

Both CLIs report "Restart to apply changes" — running Claude Code / Cursor sessions keep the old version until restarted. Cursor consumes the same installed plugin through its Claude-plugin compatibility paths (see ADR 0010), so one update serves both harnesses per side.

Optional spot-check that the new content actually landed — a version directory existing does not prove its content:

```bash
ls ~/.claude/plugins/cache/fable-advisor/fable-advisor/   # new version dir present
grep -c "<a phrase this release added>" ~/.claude/plugins/cache/fable-advisor/fable-advisor/<version>/skills/orchestration/SKILL.md
```
