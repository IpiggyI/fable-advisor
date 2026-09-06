#!/usr/bin/env python3
"""Deny Cursor Task spawns of named lane agents on the wrong model family.

Read stdin as UTF-8 bytes, stripping a leading BOM (`utf-8-sig`). Windows
Python defaults to GBK text. Cursor 3.16.17 has prefixed hook stdin with
UTF-8 BOM, and has split `cursor-grok-4.6-*` slugs so `4.6` is a JSON number
(`"cursor-grok-"4.6"-medium"`). Empty stdin is deny. JSON that still cannot
be parsed is deny with the decoder error, not a BOM message.
Explore/generalPurpose inherit is allowed when tool_input is visible.
fable-advisor inherit is allowed (2026-08-31, Fable 5 quota). Resume
skips the model check.

First-party: Cursor 3.16.17, 2026-08-18 Windows leak — hook ran, logged INPUT
had tool_input.model=inherit, process wrote permission=allow. Replay of those
bytes denies; empty stdin is the matching allow path. subagentStart deny does
not block (2026-08-17).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home() / ".cursor" / "hooks" / "logs" / "fable-lane-family-gate.jsonl"

FAMILY = {
    "fable-advisor": ("fable",),
    "implementer": ("opus",),
}

UNREADABLE_AGENT = (
    "fable-lane-family-gate got no tool_input (empty or unparseable stdin). "
    "Retry once. If it persists, a sibling Windows preToolUse hook is consuming "
    "stdin; this Task-matched gate fail-closes when it cannot see subagent_type."
)
UNREADABLE_USER = (
    "车道门未收到 Task 参数，已拦截。可再试一次；"
    "若反复出现，是 Windows 上多个 Task hook 抢 stdin。"
)
# Cursor 3.16.17 Windows has serialized `cursor-grok-4.6-*` as
# `"cursor-grok-"4.6"-medium"` (the 4.6 token becomes a JSON number).
_SPLIT_VERSION_SLUG = re.compile(
    r'"([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)-"(\d+\.\d+)"((?:-[A-Za-z0-9]+)*)"?'
)


def decide(tool_input: dict) -> tuple[str, str | None, str | None]:
    """Return (permission, agent_message, user_message)."""
    if tool_input.get("resume"):
        return "allow", None, None

    agent = str(tool_input.get("subagent_type") or "")
    tokens = FAMILY.get(agent)
    if not tokens:
        return "allow", None, None

    model = tool_input.get("model")
    inherit = (
        not isinstance(model, str)
        or not model.strip()
        or model.strip().lower() == "inherit"
    )
    # 2026-08-31: fable-advisor inherits the parent (Fable 5 quota).
    # Any explicit pin is deny so a Fable slug cannot sneak through.
    # Restore: delete this block; inherit then falls through to omit-deny.
    if agent == "fable-advisor":
        if inherit:
            return "allow", None, None
        agent_msg = (
            "Cursor Task for fable-advisor must inherit the parent (omit model). "
            "Fable pin paused 2026-08-31 (quota). Retry with no model / inherit."
        )
        user_msg = "fable-advisor 暂用会话默认模型，请省略 model 后重试。不要钉 Fable slug。"
        return "deny", agent_msg, user_msg

    if inherit:
        agent_msg = (
            f"Cursor Task for {agent} omitted model (inherit parent). "
            f"Pin a {tokens[0]}-family slug from this turn's Task allowlist and retry. "
            "Agent frontmatter model: is not honored in Cursor."
        )
        user_msg = f"{agent} 未钉模型，已拦截。请从本次允许清单选 {tokens[0]} 家族 slug 后重试。"
        return "deny", agent_msg, user_msg

    slug = model.strip().lower()
    if not any(token in slug for token in tokens):
        agent_msg = (
            f"Cursor Task for {agent} pinned {model!r}, which is not {tokens[0]}-family. "
            f"Pin a {tokens[0]}-family slug from this turn's Task allowlist and retry."
        )
        user_msg = f"{agent} 钉了错家族模型 {model}，已拦截。"
        return "deny", agent_msg, user_msg

    return "allow", None, None


def extract_tool_input(payload: object) -> dict:
    """Normalize Cursor/CLI stdin shapes. Top-level envelope `model` is the parent."""
    if not isinstance(payload, dict):
        return {}
    for key in ("tool_input", "toolInput", "arguments"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value.strip():
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, dict):
                return parsed
    agent = payload.get("subagent_type") or payload.get("subagentType")
    if not agent and not payload.get("resume"):
        return {}
    out: dict = {}
    if agent:
        out["subagent_type"] = agent
    if payload.get("resume"):
        out["resume"] = payload["resume"]
    envelope = any(
        key in payload
        for key in ("tool_name", "toolName", "hook_event_name", "hookEventName")
    )
    # Flat Task args (no envelope): `model` is the child pin. Envelope top-level
    # `model` is the parent composer — never treat it as the pin.
    if not envelope and "model" in payload:
        out["model"] = payload["model"]
    return out


def _log(record: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _emit(obj: dict) -> int:
    # ASCII JSON so GBK stdout cannot invalidate a deny for Cursor's UTF-8 parser.
    sys.stdout.write(json.dumps(obj, ensure_ascii=True))
    sys.stdout.flush()
    return 0


def _decision_out(
    permission: str, agent_message: str | None, user_message: str | None
) -> dict:
    out: dict = {"permission": permission}
    if user_message:
        out["user_message"] = user_message
    if agent_message:
        out["agent_message"] = agent_message
    return out


def _visible_spawn(tool_input: dict) -> bool:
    return bool(
        tool_input.get("subagent_type")
        or tool_input.get("subagentType")
        or tool_input.get("resume")
    )


def _error_snippet(text: str, pos: int, radius: int = 40) -> str:
    lo = max(0, pos - radius)
    hi = min(len(text), pos + radius)
    return text[lo:hi].replace("\n", "\\n")


def _parse_messages(exc: json.JSONDecodeError) -> tuple[str, str]:
    detail = str(exc)[:160]
    agent = (
        f"fable-lane-family-gate could not parse stdin JSON ({detail}). "
        "This is envelope serialization, not the family check."
    )
    user = f"车道门无法解析 Task 参数：{detail}。不是家族校验失败。"
    return agent, user


def _spawn_from_text(text: str) -> dict:
    """Best-effort child pin when JSON is broken. Do not use envelope `model`."""
    out: dict = {}
    resume = re.search(r'"resume"\s*:\s*"([^"]*)"', text)
    if resume:
        out["resume"] = resume.group(1)
    agent = re.search(r'"subagent_type"\s*:\s*"([^"]+)"', text) or re.search(
        r'"subagentType"\s*:\s*"([^"]+)"', text
    )
    if not agent:
        return out
    out["subagent_type"] = agent.group(1)
    window = text[max(0, agent.start() - 400) : agent.start()]
    found = list(
        re.finditer(r'"model"\s*:\s*(?:"([^"]*)"|([A-Za-z][A-Za-z0-9._-]*))', window)
    )
    if found:
        last = found[-1]
        out["model"] = last.group(1) or last.group(2)
    return out


def _loads_hook_json(
    text: str,
) -> tuple[object | None, str | None, json.JSONDecodeError | None]:
    try:
        return json.loads(text), "json", None
    except json.JSONDecodeError as exc:
        last = exc
    repaired = _SPLIT_VERSION_SLUG.sub(r'"\1-\2\3"', text)
    if repaired != text:
        try:
            return json.loads(repaired), "repaired", None
        except json.JSONDecodeError as exc:
            last = exc
            text = repaired
    spawn = _spawn_from_text(text)
    if _visible_spawn(spawn):
        return {"tool_name": "Task", "tool_input": spawn}, "regex", None
    return None, None, last


def evaluate(raw: bytes, *, log: bool = True) -> dict:
    """Decide from raw stdin bytes. Used by main and self-test."""
    ts = datetime.now(timezone.utc).isoformat()
    raw_len = len(raw)
    record: dict = {"ts": ts, "raw_len": raw_len}

    if not raw.strip():
        out = _decision_out("deny", UNREADABLE_AGENT, UNREADABLE_USER)
        record.update(
            {
                "phase": "unreadable",
                "reason": "empty_stdin",
                "permission": "deny",
            }
        )
        if log:
            _log(record)
        return out

    try:
        text = raw.decode("utf-8-sig", errors="replace")
    except Exception:
        text = raw.decode("utf-8", errors="replace")
    payload, parsed_via, decode_exc = _loads_hook_json(text)
    if payload is None:
        agent_message, user_message = _parse_messages(
            decode_exc or json.JSONDecodeError("unreadable", text, 0)
        )
        out = _decision_out("deny", agent_message, user_message)
        pos = decode_exc.pos if decode_exc is not None else 0
        record.update(
            {
                "phase": "unreadable",
                "reason": "json_decode",
                "error": str(decode_exc)[:200] if decode_exc else "unreadable",
                "error_at": _error_snippet(text, pos),
                "permission": "deny",
            }
        )
        if log:
            _log(record)
        return out

    payload_keys = sorted(payload.keys()) if isinstance(payload, dict) else []
    tool_input = extract_tool_input(payload)
    record.update(
        {
            "phase": "decision",
            "hook_event_name": payload.get("hook_event_name") if isinstance(payload, dict) else None,
            "tool_name": payload.get("tool_name") if isinstance(payload, dict) else None,
            "payload_keys": payload_keys,
            "tool_input_keys": sorted(tool_input.keys()),
            "subagent_type": tool_input.get("subagent_type") or tool_input.get("subagentType"),
            "model": tool_input.get("model") if isinstance(tool_input.get("model"), str) else None,
            "parsed_via": parsed_via,
        }
    )

    if not _visible_spawn(tool_input):
        out = _decision_out("deny", UNREADABLE_AGENT, UNREADABLE_USER)
        record.update({"permission": "deny", "reason": "no_subagent_type"})
        if log:
            _log(record)
        return out

    permission, agent_message, user_message = decide(tool_input)
    record["permission"] = permission
    if log:
        _log(record)
    return _decision_out(permission, agent_message, user_message)


def main() -> int:
    stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(stdout_reconfigure):
        try:
            stdout_reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass
    try:
        raw = sys.stdin.buffer.read()
    except OSError:
        raw = b""
    return _emit(evaluate(raw))


def _self_test() -> int:
    decide_cases = [
        ({"subagent_type": "explore"}, "allow"),
        ({"subagent_type": "generalPurpose"}, "allow"),
        ({"subagent_type": "fable-advisor"}, "allow"),
        ({"subagent_type": "fable-advisor", "model": "inherit"}, "allow"),
        ({"subagent_type": "fable-advisor", "model": "cursor-grok-4.6-xhigh"}, "deny"),
        ({"subagent_type": "fable-advisor", "model": "claude-fable-5-thinking-xhigh"}, "deny"),
        ({"subagent_type": "implementer"}, "deny"),
        ({"subagent_type": "implementer", "model": "claude-opus-5-thinking-high"}, "allow"),
        ({"subagent_type": "fable-advisor", "resume": "abc"}, "allow"),
    ]
    failed = 0
    for tool_input, expected in decide_cases:
        got, _, _ = decide(tool_input)
        if got != expected:
            print(f"FAIL decide {tool_input!r}: got {got} expected {expected}", file=sys.stderr)
            failed += 1

    extract_cases = [
        ({"tool_name": "Task", "tool_input": {"subagent_type": "fable-advisor", "model": "inherit"}}, {"subagent_type", "model"}),
        ({"subagent_type": "fable-advisor", "model": "inherit", "prompt": "x"}, {"subagent_type", "model"}),
        ({"tool_name": "Task", "toolInput": {"subagent_type": "fable-advisor", "model": "inherit"}}, {"subagent_type", "model"}),
        ({"tool_name": "Task", "arguments": {"subagent_type": "fable-advisor", "model": "inherit"}}, {"subagent_type", "model"}),
        ({"tool_name": "Task", "tool_input": json.dumps({"subagent_type": "fable-advisor", "model": "inherit"})}, {"subagent_type", "model"}),
        (
            {
                "tool_name": "Task",
                "hook_event_name": "preToolUse",
                "model": "cursor-grok-4.6-xhigh",
                "tool_input": {"subagent_type": "explore"},
            },
            {"subagent_type"},
        ),
    ]
    for payload, expect_keys in extract_cases:
        got = extract_tool_input(payload)
        if not expect_keys <= set(got):
            print(f"FAIL extract {payload!r}: got {got!r} expected keys {expect_keys}", file=sys.stderr)
            failed += 1
        if "model" in expect_keys and got.get("model") != "inherit":
            print(f"FAIL extract model {payload!r}: got {got!r}", file=sys.stderr)
            failed += 1
        # Envelope top-level model must not become the child pin.
        if payload.get("hook_event_name") == "preToolUse" and got.get("model"):
            print(f"FAIL extract used parent model {got!r}", file=sys.stderr)
            failed += 1

    eval_cases = [
        (b"", "deny"),
        (b"not-json", "deny"),
        (
            json.dumps(
                {
                    "tool_name": "Task",
                    "tool_input": {
                        "subagent_type": "fable-advisor",
                        "model": "inherit",
                        "description": "v4 收口裁决",
                    },
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            "allow",
        ),
        (
            json.dumps({"tool_name": "Task", "tool_input": {"subagent_type": "explore"}}).encode(),
            "allow",
        ),
        (
            json.dumps(
                {
                    "tool_name": "Task",
                    "tool_input": {
                        "subagent_type": "fable-advisor",
                        "model": "claude-fable-5-thinking-xhigh",
                    },
                }
            ).encode(),
            "deny",
        ),
        (
            b"\xef\xbb\xbf"
            + json.dumps(
                {
                    "tool_name": "Task",
                    "tool_input": {
                        "subagent_type": "fable-advisor",
                        "model": "claude-fable-5-thinking-low",
                    },
                }
            ).encode("utf-8"),
            "deny",
        ),
        (
            b"\xef\xbb\xbf"
            + json.dumps(
                {
                    "tool_name": "Task",
                    "tool_input": {
                        "subagent_type": "fable-advisor",
                        "model": "inherit",
                    },
                }
            ).encode("utf-8"),
            "allow",
        ),
        (
            json.dumps({"tool_name": "Task", "tool_input": {"subagent_type": "fable-advisor", "resume": "abc"}}).encode(),
            "allow",
        ),
        (
            b'{"tool_name":"Task","tool_input":{"subagent_type":"fable-advisor","model":"cursor-grok-"4.6"-medium"}}',
            "deny",
        ),
        (
            b'{"tool_name":"Task","tool_input":{"subagent_type":"explore","model":"cursor-grok-"4.6"-medium"}}',
            "allow",
        ),
        (
            b'{"tool_name":"Task","tool_input":{"prompt":"use `cwd` and "quotes"","model":"claude-fable-5-thinking-low","subagent_type":"fable-advisor"}}',
            "deny",
        ),
    ]
    for raw, expected in eval_cases:
        got_out = evaluate(raw, log=False)
        got = got_out.get("permission")
        if got != expected:
            print(f"FAIL evaluate {raw[:60]!r}: got {got} expected {expected}", file=sys.stderr)
            failed += 1
        joined = str(got_out.get("user_message") or "") + str(got_out.get("agent_message") or "")
        if b'4.6"-medium' in raw:
            if "BOM" in joined or "无法解析" in joined:
                print(f"FAIL grok-split used parse copy: {joined!r}", file=sys.stderr)
                failed += 1
        if raw == b"not-json":
            if "BOM" in joined:
                print(f"FAIL not-json still mentions BOM: {joined!r}", file=sys.stderr)
                failed += 1
            if "无法解析" not in joined:
                print(f"FAIL not-json missing parse copy: {joined!r}", file=sys.stderr)
                failed += 1

    if failed:
        return 1
    print("self-test ok", len(decide_cases) + len(extract_cases) + len(eval_cases))
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    raise SystemExit(main())
