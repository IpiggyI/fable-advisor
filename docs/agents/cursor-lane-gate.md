# Cursor lane family gate

Canonical copies of user-level Cursor live artifacts live under `cursor-hooks/` (not `plugin/hooks/`, not this repo's `.cursor/`). The same class as [ADR 0011](../adr/0011-cursor-lane-family-gate-user-level.md): archive in-repo, live stays user-level so it applies in every Cursor workspace, byte-identical drift detection. This is not Claude Code's receipt-gate.

The gate exists to stop a named-agent `Task` dispatch from silently inheriting the session model; that is the only check it makes.

## preToolUse script

Canonical script: `cursor-hooks/fable-lane-family-gate.py`.

- WSL: `python3 /home/hyy/.cursor/hooks/fable-lane-family-gate.py`
- Windows: `python C:/Users/Shy/.cursor/hooks/fable-lane-family-gate.py`

Register under `preToolUse`, matcher `Task`, timeout 10. Merge `cursor-hooks/hooks.example.json` into an existing `~/.cursor/hooks.json`; do not replace a forked file. WSL and Windows configs are already different.

The rule, in one place: a `Task` whose `subagent_type` starts with `advisor-` needs an explicit, non-inherit `model`; any other `subagent_type` passes regardless of `model`; `resume` skips the check. The match is the prefix, not a fixed name, so a new advisor dial is guarded as soon as its file lands — ADR 0016's decision 8 moved the trigger here from the retired bare name `fable-advisor`. The `subagent_type` is stripped and lowercased before the prefix test, the way `model` already was: a permission decision normalizes its input first, so ` advisor-h` and `Advisor-h` deny too. Normalization stops at whitespace and case; an interior zero-width or full-width character would still slip past, and closing that needs evidence of what Cursor accepts as a `subagent_type`. I/O is UTF-8 stdin payload in, JSON `permission` (`allow` / `deny`) out, exit 0. Do not extend the hook to `generalPurpose`: nothing marks a worker dispatch apart from an ordinary scout. The full case list is the script's `--self-test`.

### Update

1. Edit `cursor-hooks/fable-lane-family-gate.py`; change `decide()` only when the rule itself is the task.
2. Copy that file onto both live paths. The archive and both live copies must stay byte-identical.
3. On a new machine only, merge the example `preToolUse` fragment. Do not edit a live `hooks.json` unless the user named that file.
4. Run `python3 cursor-hooks/fable-lane-family-gate.py --self-test` and `python3 tests/test_lane_family_gate.py`.

Done when `--self-test` prints `self-test ok` and the drift test passes against every live copy that exists.

## Task pin rule

Canonical rule: `cursor-hooks/fable-lane-pin.mdc`. Cursor loads it as an `alwaysApply` user rule, not from this repo. The Chinese backup is `cursor-hooks/zh/fable-lane-pin.mdc` and is not installed. The copy in the prompts repo (`/mnt/d/Development/Local/prompts/current-prompts/rules/fable-lane-pin.cursor.mdc`) is a deployment snapshot; edit here.

- WSL: `/home/hyy/.cursor/rules/fable-lane-pin.mdc`
- Windows: `C:/Users/Shy/.cursor/rules/fable-lane-pin.mdc`

### Update

1. Edit `cursor-hooks/fable-lane-pin.mdc`.
2. Copy that file onto both live paths and the prompts-repo snapshot. Archive and copies must stay byte-identical.
3. Run `python3 tests/test_user_level_archive.py`.

Done when the drift test passes against every copy that exists.
