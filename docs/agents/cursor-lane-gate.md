# Cursor lane family gate

Canonical copies of user-level Cursor live artifacts live under `cursor-hooks/` (not `plugin/hooks/`, not this repo's `.cursor/`). The same class as [ADR 0011](../adr/0011-cursor-lane-family-gate-user-level.md): archive in-repo, live stays user-level so it applies in every Cursor workspace, byte-identical drift detection. This is not Claude Code's receipt-gate.

The gate exists to stop a named-agent `Task` dispatch from silently inheriting the session model. It does not match vendor families.

## preToolUse script

Canonical script: `cursor-hooks/fable-lane-family-gate.py`.

- WSL: `python3 /home/hyy/.cursor/hooks/fable-lane-family-gate.py`
- Windows: `python C:/Users/Shy/.cursor/hooks/fable-lane-family-gate.py`

Register under `preToolUse`, matcher `Task`, timeout 10. Merge `cursor-hooks/hooks.example.json` into an existing `~/.cursor/hooks.json`; do not replace a forked file. WSL and Windows configs are already different.

### Behaviour

I/O is unchanged: UTF-8 stdin payload in, JSON `permission` (`allow` / `deny`) out, exit 0. Only the decision rule changed.

- `subagent_type` is `fable-advisor` and `model` is missing, empty, or `inherit` → deny. The deny text says an explicit, non-inherit `model` is required.
- `fable-advisor` with any other explicit `model` string → allow (any vendor slug).
- Any other `subagent_type` (`generalPurpose`, `explore`, and the rest) → allow regardless of `model`.
- `resume` set → allow (skips the pin check).

Do not extend the hook to `generalPurpose`. There is no marker that distinguishes a worker dispatch from an ordinary scout.

### Update

1. Edit `cursor-hooks/fable-lane-family-gate.py`. Change `decide()` only when the pin rule itself is the task: named agent `fable-advisor` needs an explicit, non-inherit `model`; every other `subagent_type` is allowed regardless of `model`; resume skips the pin check.
2. Copy that file onto both live paths. The archive and both live copies must stay byte-identical.
3. On a new machine only, merge the example `preToolUse` fragment. Do not edit a live `hooks.json` unless the user named that file.
4. Run `python3 cursor-hooks/fable-lane-family-gate.py --self-test` and `python3 tests/test_lane_family_gate.py`.

Done when `--self-test` prints `self-test ok` and the drift test passes against every live copy that exists.

## Task pin rule

Canonical rule: `cursor-hooks/fable-lane-pin.mdc`. Cursor loads it as an `alwaysApply` user rule, not from this repo.

- WSL: `/home/hyy/.cursor/rules/fable-lane-pin.mdc`
- Windows: `C:/Users/Shy/.cursor/rules/fable-lane-pin.mdc`

`fable-advisor` dispatches must carry an explicit, non-inherit `model`. Worker lanes are `generalPurpose` (or `explore` for read-only scouting) plus an explicit `model`; omitting `model` is a same-model dispatch, not a vendor lane. Plugin frontmatter `model:` is ignored. Use the live allowlist slug.

### Update

1. Edit `cursor-hooks/fable-lane-pin.mdc`.
2. Copy that file onto both live paths. The archive and both live copies must stay byte-identical.
3. Run `python3 tests/test_lane_family_gate.py`.

Done when the drift test passes against every live copy that exists.
