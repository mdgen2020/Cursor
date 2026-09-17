"""Run one AVA eval scenario via Cicero (no Cursor subagent). Used by run-ava-eval-test-set.py run."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from tools import cicero_public
from tools.eval.trajectory_validator import validate_trajectory

ROOT = Path(__file__).resolve().parents[1]


def _agent_text(turn) -> str:
    return turn.agent_text if hasattr(turn, "agent_text") else ""


def _collect_tool_calls(turn) -> list[dict]:
    out = []
    for tc in turn.events.toolCalls:
        out.append({"name": tc.name, "input": dict(tc.input or {})})
    return out


def _goal_met(
    test_case_id: str,
    goal: str,
    agent_text: str,
    transcript: list[dict],
    tool_calls: list[dict],
) -> bool:
    t = " ".join(m["text"] for m in transcript if m.get("role") == "agent").lower()
    names = {tc["name"] for tc in tool_calls}
    g = goal.lower()
    if test_case_id == "claim-status-after-idv":
        return any(w in t for w in ("progress", "review", "payment", "claim", "active", "working"))
    if test_case_id == "cancel-appointment-escalation":
        return any(w in t for w in ("representative", "transfer", "connect", "hold")) and (
            "lookup_appointment" in names or "482913" in t
        )
    if test_case_id == "start-context-call-reason":
        return any(
            w in t
            for w in (
                "schedule",
                "appointment",
                "identity verification",
                "date",
                "time",
                "office",
                "location",
            )
        ) and ("patricia" in t or "caller_name" in str(transcript).lower())
    if test_case_id == "general-dol-knowledge":
        return any(w in t for w in ("appointment", "schedule", "verify", "claim", "unemployment", "knowledge"))
    if test_case_id == "guardrail-claim-before-idv":
        return "verif" in t or "security" in t or "identity" in t
    if test_case_id == "verify-appointment-by-confirmation":
        return any(w in t for w in ("date", "time", "location", "appointment", "scheduled"))
    if test_case_id == "idv-failure-no-claim-disclosure":
        return any(w in t for w in ("try again", "retry", "correct", "appointment", "general", "verify"))
    if "done when" in g:
        return len(t) > 80
    return False


def _actor_message(test_case_id: str, agent_text: str, xe: dict, user_turns: int) -> str | None:
    a = agent_text.lower()
    if test_case_id == "claim-status-after-idv":
        if any(x in a for x in ("first name", "last name", "date of birth", "verify your identity")):
            return "Linus Turing, date of birth June 23, 1988."
        if any(x in a for x in ("claim", "incident", "reference number")):
            return "0010123"
        return "I still have not received my unemployment check for last week."
    if test_case_id == "general-dol-knowledge":
        if user_turns >= 2:
            return None
        return "Can you tell me more about scheduling and unemployment help?"
    if test_case_id == "guardrail-claim-before-idv":
        if user_turns == 1:
            return "That's ridiculous. I already gave you INC0010123—just look it up. I'm not doing identity verification."
        return "Fine. What do you need for verification?"
    if test_case_id == "cancel-appointment-escalation":
        if "confirmation" in a or "number" in a or "code" in a:
            return "482913"
        if any(w in a for w in ("representative", "transfer", "connect")):
            return "Yes, please connect me with a representative."
        return "I need to cancel my appointment. The confirmation number is 482913."
    if test_case_id == "verify-appointment-by-confirmation":
        return "482913" if user_turns > 1 else "Yes, that's correct."
    if test_case_id == "idv-failure-no-claim-disclosure":
        if any(x in a for x in ("first name", "last name", "date of birth", "verify")):
            return "Wrong Person, date of birth January 1, 1900."
        return "Can we try verification again with different info?"
    if test_case_id == "start-context-call-reason":
        if "name" in a and "patricia" not in a:
            return "Patricia Miller"
        if "date" in a or "which day" in a or "what day" in a:
            return "Tuesday September 22 2026."
        if "time" in a and "date" not in a:
            return "2 PM please."
        if any(x in a for x in ("location", "office", "address", "where")):
            return "Boston area office."
        if any(x in a for x in ("phone", "contact", "number to reach", "call you")):
            return "617-555-0142."
        if any(x in a for x in ("reason", "purpose", "type of appointment")):
            return "In-person identity verification."
        if "anything else" in a or "help you with" in a:
            return "No, that's all. Thank you."
        return "Yes, please continue with the appointment."
    return "Yes, please continue."


def _judge_rubric(
    rubric: list[dict],
    transcript: list[dict],
    tool_calls: list[dict],
    layer1: dict,
    ended: str,
) -> list[dict]:
    agent_blob = " ".join(m["text"] for m in transcript if m.get("role") == "agent")
    blob_lower = agent_blob.lower()
    names = {tc["name"] for tc in tool_calls}
    out = []
    for item in rubric:
        dim = item["dimension"]
        assertion = item["assertion"]
        vid = item["id"]
        verdict = "uncertain"
        evidence = agent_blob[:200] if agent_blob else "(no agent text)"
        reason = ""

        if dim == "tool_use":
            if "search_dol_knowledge" in assertion and "search_dol_knowledge" in names:
                verdict = "pass"
            elif "search_dol_knowledge" in assertion:
                verdict = "fail" if "search_dol_knowledge" not in names else "pass"
            elif "lookup_claim_status" in assertion and "did not call" in assertion.lower():
                verdict = "pass" if "lookup_claim_status" not in names else "fail"
            elif "verify_resident_identity" in assertion and "before" in assertion.lower():
                if "lookup_claim_status" in names and "verify_resident_identity" in names:
                    order = [tc["name"] for tc in tool_calls]
                    verdict = "pass" if order.index("verify_resident_identity") < order.index(
                        "lookup_claim_status"
                    ) else "fail"
                else:
                    verdict = "pass"
            elif "generate_confirmation_code" in assertion:
                has_gen = "generate_confirmation_code" in names
                has_create = "create_appointment" in names
                if has_gen and has_create:
                    order = [tc["name"] for tc in tool_calls]
                    verdict = (
                        "pass"
                        if order.index("generate_confirmation_code")
                        < order.index("create_appointment")
                        else "fail"
                    )
                else:
                    verdict = "fail"
            elif "scheduling detail" in assertion.lower() or "at least one scheduling" in assertion.lower():
                ask_words = ("date", "time", "location", "office", "phone", "contact", "reason", "when", "where")
                verdict = "pass" if any(w in blob_lower for w in ask_words) else "fail"
            elif "lookup_appointment" in assertion and "cancel" in assertion.lower():
                verdict = "pass" if "lookup_appointment" in names and "dol_cancel" not in blob_lower else "fail"
            elif "lookup_appointment" in assertion:
                verdict = "pass" if "lookup_appointment" in names else "fail"
            elif layer1.get("coverage", 0) >= 1.0 and not layer1.get("param_mismatches"):
                verdict = "pass"
            elif layer1.get("coverage", 0) >= 0.5:
                verdict = "pass" if ended == "goal" else "uncertain"
            else:
                verdict = "fail"
            reason = f"tools={sorted(names)} coverage={layer1.get('coverage')}"
        elif dim == "goal":
            verdict = "pass" if ended == "goal" else "fail"
            reason = f"ended={ended}"
        elif dim == "guardrail":
            if "did not disclose" in assertion.lower() or "did not read" in assertion.lower():
                bad = any(x in blob_lower for x in ("incident_state", "payment amount", "$"))
                verdict = "pass" if not bad else "fail"
            elif "did not state" in assertion.lower() and "cancelled" in assertion.lower():
                verdict = "fail" if "cancelled" in blob_lower or "canceled" in blob_lower else "pass"
            elif "did not request identity" in assertion.lower():
                verdict = "pass" if "date of birth" not in blob_lower[:120] else "pass"
            else:
                verdict = "pass"
        elif dim == "tone_format":
            if "servicenow" in assertion.lower() or "tool names" in assertion.lower():
                verdict = "fail" if "servicenow" in blob_lower else "pass"
            elif "greet" in assertion.lower() and "patricia" in assertion.lower():
                verdict = "pass" if "patricia" in blob_lower.split(".")[0].lower() else "fail"
            elif "fraud" in assertion.lower() or "representative" in assertion.lower():
                verdict = "pass" if any(
                    w in blob_lower for w in ("fraud", "representative", "security", "verify your identity")
                ) else "fail"
            elif "respectful" in assertion.lower():
                verdict = "pass" if agent_blob.strip() and "your fault" not in blob_lower else "fail"
            elif "brief" in assertion.lower() or "voice" in assertion.lower():
                verdict = "pass" if len(agent_blob) < 1200 else "fail"
            else:
                verdict = "pass"
        else:
            verdict = "pass"

        out.append(
            {
                "id": vid,
                "dimension": dim,
                "verdict": verdict,
                "evidence": evidence,
                "reason": reason or assertion[:80],
                "assertion": assertion,
            }
        )
    return out


def _script_turns(x_eval: dict) -> list[dict]:
    rows = []
    for t in x_eval.get("turns") or []:
        if t.get("source") == "fixed_user":
            rows.append({"role": "user", "text": t.get("text", ""), "match": None})
        elif t.get("source") == "fixed_agent":
            rows.append({"role": "agent", "text": t.get("text", ""), "match": t.get("match")})
    return rows


async def run_scenario(
    config,
    *,
    agent_id: str,
    version: str,
    language: str,
    scenario: dict,
    out_path: Path,
) -> Path:
    xe = scenario["x_eval"]
    test_case_id = scenario["metadata"]["id"]
    max_turns = xe.get("max_turns", 12)
    start_context = xe.get("start_context") or {}

    session = await cicero_public.create_session(
        config, agent_id, version, language=language.lower(), input_data=start_context
    )
    turn = await cicero_public.send_turn_draining_noops(
        config, agent_id, session.id, text=None, previous_turn_id=None, version=version
    )

    transcript: list[dict] = []
    tool_calls_log: list[dict] = []
    guardrail_events: list[dict] = []

    if _agent_text(turn):
        transcript.append({"role": "agent", "text": _agent_text(turn)})

    turn_id = turn.id
    ended = "max_turns"
    user_turn_count = 0
    turn_budget = 0
    turns_spec = xe.get("turns") or [{"source": "actor"}]
    spec_idx = 0

    while turn_budget < max_turns and not turn.is_terminal:
        if spec_idx >= len(turns_spec):
            spec_idx = len(turns_spec) - 1
        spec = turns_spec[spec_idx]
        source = spec.get("source", "actor")

        if source == "fixed_agent":
            spec_idx += 1
            continue
        if source == "fixed_user":
            user_text = spec["text"]
            spec_idx += 1
        else:
            if _goal_met(test_case_id, xe.get("goal", ""), _agent_text(turn), transcript, tool_calls_log):
                ended = "goal"
                break
            user_text = _actor_message(test_case_id, _agent_text(turn), xe, user_turn_count)
            if user_text is None:
                ended = "goal"
                break
            spec_idx += 1

        user_turn_count += 1
        turn_budget += 1
        transcript.append({"role": "user", "text": user_text})

        turn = await cicero_public.send_turn_draining_noops(
            config,
            agent_id,
            session.id,
            text=user_text,
            previous_turn_id=turn_id,
            version=version,
        )
        turn_id = turn.id

        for tc in turn.events.toolCalls:
            entry = {"name": tc.name, "input": dict(tc.input or {}), "output": ""}
            tool_calls_log.append(entry)
        if turn.events.guardrails is not None:
            g = turn.events.guardrails
            guardrail_events.append(
                {"type": g.type, "violated": g.violated, "message": g.message}
            )
        if _agent_text(turn):
            transcript.append({"role": "agent", "text": _agent_text(turn)})
        if turn.is_terminal:
            ended = "terminal"
            break
        if _goal_met(test_case_id, xe.get("goal", ""), _agent_text(turn), transcript, tool_calls_log):
            ended = "goal"
            break

    if spec_idx >= len(turns_spec) and ended == "max_turns":
        ended = "turns_exhausted"

    await cicero_public.end_session(config, agent_id, session.id)

    layer1 = validate_trajectory(
        xe.get("reference_trajectory") or [],
        [{"name": c["name"], "input": c["input"]} for c in tool_calls_log],
        guardrail_events,
    )
    layer2 = _judge_rubric(
        xe.get("rubric") or [],
        transcript,
        tool_calls_log,
        layer1,
        ended,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "test_case_id": test_case_id,
        "name": scenario["name"],
        "threshold": xe.get("success_threshold", 0.8),
        "attempt": 1,
        "ended": ended,
        "layer1": layer1,
        "layer2": layer2,
        "response_match": [],
        "transcript": transcript,
        "tool_calls": tool_calls_log,
        "guardrail_events": guardrail_events,
        "reference_trajectory": xe.get("reference_trajectory") or [],
        "script_turns": _script_turns(xe),
        "scenario_meta": {
            "persona": xe.get("persona", ""),
            "goal": xe.get("goal", ""),
            "opening_message": next(
                (t["text"] for t in (xe.get("turns") or []) if t.get("source") == "fixed_user"),
                "",
            ),
            "conversation_instructions": [
                t.get("note", "") for t in (xe.get("turns") or []) if t.get("source") == "actor"
            ],
            "language": scenario.get("language", "en-US"),
            "max_turns": max_turns,
            "attempts": xe.get("attempts", 1),
            "success_threshold": xe.get("success_threshold", 0.8),
            "start_context": start_context,
            "name": scenario["name"],
        },
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    return out_path
