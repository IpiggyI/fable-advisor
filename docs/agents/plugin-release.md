# Plugin release & local update

How a change in this repo reaches the installed plugin on this machine (WSL + Windows). The installed marketplaces on **both** sides point at GitHub (`IpiggyI/fable-advisor`), not at this working tree — an unpushed commit never reaches the plugin.

## 1. Bump the version — two files, not one

- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Both must move together. The marketplace version drives update discovery; leaving it stale means `claude plugin update` sees nothing new (this drift actually happened: marketplace sat at 3.7.0 while plugin.json said 3.8.0). Minor bump for semantic changes, per the ADR precedents.

## 2. Commit and push

```bash
git add -A && git commit && git push origin main
```

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

## 5. Restart and spot-check

Both CLIs report "Restart to apply changes" — running Claude Code / Cursor sessions keep the old version until restarted. Cursor consumes the same installed plugin through its Claude-plugin compatibility paths (see ADR 0010), so one update serves both harnesses per side.

Optional spot-check that the new content actually landed:

```bash
ls ~/.claude/plugins/cache/fable-advisor/fable-advisor/   # new version dir present
grep -c "The lanes in Cursor" ~/.claude/plugins/cache/fable-advisor/fable-advisor/<version>/skills/orchestration/SKILL.md
```

(Adapt the grep to whatever the release changed.)
