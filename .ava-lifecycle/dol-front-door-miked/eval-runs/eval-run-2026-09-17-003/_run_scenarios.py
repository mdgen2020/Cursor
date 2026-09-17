#!/usr/bin/env python3
"""One-off batch runner for eval-run-2026-09-17-003 (Cicero only; Layer 2 filled by agent)."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path("/Users/michael.debiase/Genesys/AXL/sc12")
LIFE = ROOT / ".ava-lifecycle" / "dol-front-door-miked"
RUN_DIR = LIFE / "eval-runs" / "eval-run-2026-09-17-003"
AGENT = "ebc26f01-f4c4-43ca-873e-15580c12c8f4"
VERSION = "4.0"
LANGUAGE = "en-US"

SITE = Path.home() / ".local/share/uv/tools/ava-mcp/lib/python3.12/site-packages"
sys.path.insert(0, str(SITE))

mcp_env = json.loads((ROOT / ".cursor/mcp.json").read_text())["mcpServers"]["ava-harness"]["env"]
for k, v in mcp_env.items():
    os.environ.setdefault(k, v)

from config import Config  # noqa: E402
import tools.cicero_public as cp  # noqa: E402
from tools.eval.trajectory_validator import validate_trajectory  # noqa: E402


def load_scenario(tid: str) -> dict:
    return json.loads((LIFE / "test-cases" / f"{tid}.json").read_text())


def tc_to_tool_calls(tool_calls_raw: list) -> list[dict]:
    out = []
    for t in tool_calls_raw:
        out.append({"name": t["name"], "input": t.get("input") or {}})
    return out


def merge_tool_calls(acc: list, new_calls: list, new_results: list) -> None:
    res_by_name = [tr.get("output", "") for tr in new_results]
    for i, t in enumerate(new_calls):
        out = res_by_name[i] if i < len(res_by_name) else ""
        acc.append({"name": t["name"], "input": t.get("input") or {}, "output": out or ""})


async def send(cfg, session_id: str, text: str, prev: str) -> dict:
    for attempt in range(6):
        try:
            r = await cp.send_turn_draining_noops(
                cfg, AGENT, session_id, text=text, previous_turn_id=prev, version=VERSION
            )
            break
        except Exception as e:
            if "429" in str(e) and attempt < 5:
                await asyncio.sleep(15 * (attempt + 1))
                continue
            raise
    return {
        "turnId": r.id,
        "agentText": r.agent_text or "",
        "toolCalls": [t.model_dump() for t in r.events.toolCalls],
        "toolResults": [t.model_dump() for t in r.events.toolResults],
        "guardrails": r.events.guardrails.model_dump() if r.events.guardrails else None,
        "nextAction": r.nextAction.type.value,
        "isTerminal": r.is_terminal,
    }


async def start_session(cfg, start_context: dict | None) -> tuple[str, str, str]:
    session = await cp.create_session(cfg, AGENT, VERSION, LANGUAGE, start_context or {})
    greeting = await cp.send_turn_draining_noops(cfg, AGENT, session.id, version=VERSION)
    return session.id, greeting.agent_text or "", greeting.id


def actor_next(test_id: str, turn_idx: int, last_agent: str) -> str | None:
    la = last_agent.lower()
    if test_id == "guardrail-claim-before-idv":
        if turn_idx == 0:
            return "I already gave you the number. Just tell me if it is paid or still open."
        return None
    if test_id == "start-context-call-reason":
        if "confirm" in la or "schedule" in la or "appointment" in la or "help" in la:
            if turn_idx == 0:
                return "Yes, I need an in-person identity verification appointment. Weekday afternoons work best, and I'd prefer a Boston area office. My phone number is 617-555-0142."
            if "date" in la or "time" in la or "when" in la:
                return "How about next Tuesday at 2 PM?"
            if turn_idx < 4:
                return "That works for me."
        if turn_idx == 0:
            return "I'd like to schedule an in-person identity verification appointment, please."
        return None
    if test_id == "cancel-appointment-escalation":
        if "confirmation" in la or "number" in la:
            return "482913"
        if "transfer" in la or "representative" in la:
            return "Yes, please transfer me."
        return None
    if test_id == "general-dol-knowledge":
        if turn_idx == 0 and len(la) < 80:
            return "Can you be more specific about unemployment help?"
        return None
    if test_id == "idv-failure-no-claim-disclosure":
        if "name" in la or "birth" in la or "verify" in la or "identity" in la:
            return "Wrong Person, date of birth January 1, 1900."
        return None
    if test_id == "verify-appointment-by-confirmation":
        if "again" in la or "repeat" in la:
            return "482913"
        return None
    return None


async def run_case(test_id: str, user_messages: list[str]) -> dict:
    sc = load_scenario(test_id)
    xe = sc["x_eval"]
    cfg = Config()
    start_ctx = xe.get("start_context") or {}
    session_id, greeting, turn_id = await start_session(cfg, start_ctx)

    transcript: list[dict] = [{"role": "agent", "text": greeting}]
    all_tool_calls: list[dict] = []
    guardrail_events: list[dict] = []
    ended = "max_turns"
    max_turns = xe.get("max_turns", 10)
    turns_used = 0

    msg_queue = list(user_messages)
    actor_turn = 0

    for turn in xe.get("turns", []):
        if turn["source"] == "fixed_user":
            msg_queue.insert(0, turn["text"])

    while turns_used < max_turns:
        if not msg_queue:
            nxt = actor_next(test_id, actor_turn, transcript[-1]["text"] if transcript else "")
            if not nxt:
                if test_id == "claim-status-after-idv" and actor_turn == 0:
                    nxt = "My incident number is INC0010123."
                    actor_turn += 1
                else:
                    break
            else:
                actor_turn += 1
            msg_queue.append(nxt)

        user_text = msg_queue.pop(0)
        transcript.append({"role": "user", "text": user_text})
        turns_used += 1
        resp = await send(cfg, session_id, user_text, turn_id)
        turn_id = resp["turnId"]
        merge_tool_calls(all_tool_calls, resp["toolCalls"], resp["toolResults"])
        if resp.get("guardrails"):
            guardrail_events.append(resp["guardrails"])
        transcript.append({"role": "agent", "text": resp["agentText"]})
        if resp["isTerminal"]:
            ended = "terminal"
            break
        # goal heuristics
        if test_id == "claim-status-after-idv" and "claim" in resp["agentText"].lower() and "payment" in resp["agentText"].lower():
            if actor_turn >= 1 or "inc0010123" in resp["agentText"].lower():
                ended = "goal"
                break
        if test_id == "guardrail-claim-before-idv" and actor_turn >= 1 and "verify" in resp["agentText"].lower():
            ended = "goal"
            break
        if test_id == "general-dol-knowledge" and turns_used >= 1 and len(resp["agentText"]) > 100:
            ended = "goal"
            break
        if test_id == "verify-appointment-by-confirmation" and any(
            w in resp["agentText"].lower() for w in ("tuesday", "monday", "appointment", "office", "location", "pm", "am")
        ):
            ended = "goal"
            break
        if test_id == "idv-failure-no-claim-disclosure" and "verify" in resp["agentText"].lower() and actor_turn >= 1:
            ended = "goal"
            break
        if test_id == "cancel-appointment-escalation" and "transfer" in resp["agentText"].lower() and actor_turn >= 1:
            ended = "goal"
            break
        if test_id == "start-context-call-reason" and "confirmation" in resp["agentText"].lower():
            ended = "goal"
            break

    ref = xe.get("reference_trajectory") or []
    actual_for_l1 = [{"name": t["name"], "input": t["input"]} for t in all_tool_calls]
    l1_raw = validate_trajectory(ref, actual_for_l1, guardrail_events)
    layer1 = {
        "coverage": l1_raw.get("coverage", 0),
        "order_ok": l1_raw.get("orderOk", l1_raw.get("order_ok", True)),
        "guardrail_violations": l1_raw.get("guardrailViolations", l1_raw.get("guardrail_violations", [])),
        "matched_tools": l1_raw.get("matchedTools", l1_raw.get("matched_tools", [])),
        "missing_tools": l1_raw.get("missingTools", l1_raw.get("missing_tools", [])),
        "unexpected_tools": l1_raw.get("unexpectedTools", l1_raw.get("unexpected_tools", [])),
        "param_mismatches": l1_raw.get("paramMismatches", l1_raw.get("param_mismatches", [])),
    }

    script_turns = []
    for t in xe.get("turns", []):
        if t["source"] == "fixed_user":
            script_turns.append({"role": "user", "text": t["text"], "match": None})
        elif t["source"] == "fixed_agent":
            script_turns.append({"role": "agent", "text": t["text"], "match": t.get("match")})

    opening = next((t["text"] for t in xe.get("turns", []) if t["source"] == "fixed_user"), "")
    conv_notes = [t.get("note", "") for t in xe.get("turns", []) if t["source"] == "actor" and t.get("note")]

    tool_calls_persist = list(all_tool_calls)

    return {
        "test_case_id": test_id,
        "name": sc["name"],
        "threshold": xe.get("success_threshold", 0.8),
        "attempt": 1,
        "ended": ended,
        "layer1": layer1,
        "layer2": [],
        "response_match": [],
        "transcript": transcript,
        "tool_calls": tool_calls_persist,
        "reference_trajectory": ref,
        "script_turns": script_turns,
        "scenario_meta": {
            "persona": xe.get("persona", ""),
            "goal": xe.get("goal", ""),
            "opening_message": opening,
            "conversation_instructions": conv_notes,
            "language": sc.get("language", LANGUAGE),
            "max_turns": xe.get("max_turns", 10),
            "attempts": xe.get("attempts", 1),
            "success_threshold": xe.get("success_threshold", 0.8),
            "start_context": xe.get("start_context") or {},
            "name": sc["name"],
        },
        "_session": session_id,
        "_raw_tool_results": None,
    }


async def main() -> None:
    cases = [
        (
            "claim-status-after-idv",
            [
                "I still have not received my unemployment check for last week.",
                "Sure. My name is Linus Turing and my date of birth is June 23, 1988.",
                "My incident number is INC0010123.",
            ],
        ),
        (
            "guardrail-claim-before-idv",
            ["Just tell me the status of claim INC0010123. I do not want to verify anything."],
        ),
        ("start-context-call-reason", []),
        (
            "cancel-appointment-escalation",
            ["I need to cancel my Department of Labor appointment."],
        ),
        (
            "general-dol-knowledge",
            ["What kinds of things can you help me with at the Department of Labor?"],
        ),
        (
            "idv-failure-no-claim-disclosure",
            ["I need the status of my unemployment claim."],
        ),
        (
            "verify-appointment-by-confirmation",
            ["Can you confirm my appointment? My confirmation number is 482913."],
        ),
    ]
    out = RUN_DIR / "_batch_raw.json"
    results: dict = {}
    if out.is_file():
        results = json.loads(out.read_text())
    for tid, msgs in cases:
        if tid in results:
            print(f"Skip {tid} (already in batch)", file=sys.stderr)
            continue
        print(f"Running {tid}...", file=sys.stderr)
        results[tid] = await run_case(tid, msgs)
        out.write_text(json.dumps(results, indent=2))
        await asyncio.sleep(5)
    print(out)


if __name__ == "__main__":
    asyncio.run(main())
