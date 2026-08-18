# Cursor lane family gate

Canonical script: `cursor-hooks/fable-lane-family-gate.py`. Live copies stay **user-level** so the gate fires in every Cursor workspace, not only this repo:

- WSL: `python3 /home/hyy/.cursor/hooks/fable-lane-family-gate.py`
- Windows: `python C:/Users/Shy/.cursor/hooks/fable-lane-family-gate.py`

Register under `preToolUse`, matcher `Task`, timeout 10. Merge `cursor-hooks/hooks.example.json` into an existing `~/.cursor/hooks.json`; do not replace a forked file. WSL and Windows configs are already different. This is not `plugin/hooks/` (Claude Code receipt-gate). See [ADR 0011](../adr/0011-cursor-lane-family-gate-user-level.md).

## Update

1. Edit `cursor-hooks/fable-lane-family-gate.py`. Leave `decide()` / `FAMILY` unchanged unless the family table itself is the task.
2. Copy that file onto both live paths. The archive and both live copies must stay byte-identical.
3. On a new machine only, merge the example `preToolUse` fragment. Do not edit a live `hooks.json` unless the user named that file.
4. Run `python3 cursor-hooks/fable-lane-family-gate.py --self-test` and `python3 tests/test_lane_family_gate.py`.

Done when `--self-test` prints `self-test ok` and the drift test passes against every live copy that exists.
