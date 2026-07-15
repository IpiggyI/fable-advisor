"""PreToolUse hook: block Agent spawns of CLI implementer lanes with a `name`.

Passing `name` routes the spawn to an in-process teammate, which strips the
agent definition's tool whitelist (Write/Edit leak back in), enabling silent
self-implementation. See fable-advisor .memory/tasks/2026-07/07-12-cli-lane-spawn-guardrail.
"""
import json
import sys

GUARDED = ("grok-implementer",)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("{}")
        return
    tool_input = data.get("tool_input") or {}
    subagent = tool_input.get("subagent_type") or ""
    lane = subagent.split(":")[-1]
    if lane in GUARDED and tool_input.get("name"):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"BLOCKED: {subagent} must be spawned WITHOUT a `name`. "
                    "A named spawn becomes an in_process_teammate, which strips the agent's "
                    "tool whitelist (Write/Edit leak back in) and drops its system prompt, "
                    "so the lane can silently self-implement instead of driving its CLI. "
                    "Re-issue the Agent call with the `name` parameter removed; "
                    "use run_in_background: true if you need parallel fan-out."
                ),
            }
        }))
    else:
        print("{}")


if __name__ == "__main__":
    main()
