# Cursor lane family gate

Canonical copies of user-level Cursor live artifacts live under `cursor-hooks/` (not `plugin/hooks/`, not this repo's `.cursor/`). The same class as [ADR 0011](../adr/0011-cursor-lane-family-gate-user-level.md): archive in-repo, live stays user-level so it applies in every Cursor workspace, byte-identical drift detection. This is not Claude Code's receipt-gate.

## preToolUse script

Canonical script: `cursor-hooks/fable-lane-family-gate.py`.

- WSL: `python3 /home/hyy/.cursor/hooks/fable-lane-family-gate.py`
- Windows: `python C:/Users/Shy/.cursor/hooks/fable-lane-family-gate.py`

Register under `preToolUse`, matcher `Task`, timeout 10. Merge `cursor-hooks/hooks.example.json` into an existing `~/.cursor/hooks.json`; do not replace a forked file. WSL and Windows configs are already different.

### Update

1. Edit `cursor-hooks/fable-lane-family-gate.py`. Leave `decide()` / `FAMILY` unchanged unless the family table itself is the task.
2. Copy that file onto both live paths. The archive and both live copies must stay byte-identical.
3. On a new machine only, merge the example `preToolUse` fragment. Do not edit a live `hooks.json` unless the user named that file.
4. Run `python3 cursor-hooks/fable-lane-family-gate.py --self-test` and `python3 tests/test_lane_family_gate.py`.

Done when `--self-test` prints `self-test ok` and the drift test passes against every live copy that exists.

## Task pin rule

Canonical rule: `cursor-hooks/fable-lane-pin.mdc`. Cursor loads it as an `alwaysApply` user rule, not from this repo.

- WSL: `/home/hyy/.cursor/rules/fable-lane-pin.mdc`
- Windows: `C:/Users/Shy/.cursor/rules/fable-lane-pin.mdc`

### Update

1. Edit `cursor-hooks/fable-lane-pin.mdc`.
2. Copy that file onto both live paths. The archive and both live copies must stay byte-identical.
3. Run `python3 tests/test_lane_family_gate.py`.

Done when the drift test passes against every live copy that exists.
