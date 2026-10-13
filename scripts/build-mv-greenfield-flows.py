#!/usr/bin/env python3
"""Build greenfield Massachusetts RMV voice Architect flows (miked_mv_VAbotflow + inbound)."""
from __future__ import annotations

import base64
import copy
import json
import sys
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/demo/architect-exports"

BOT_NAME = "miked_mv_VAbotflow"
INBOUND_NAME = "miked direct to queue"
MV_AVA_AGENT_ID = "0490c8a0-4830-4c57-981b-0623f5a5a466"
MV_AVA_VERSION = "7.0"
SUPPORT_QUEUE_ID = "dc15ad2c-7917-413f-9a00-4f52df4d4602"
SUPPORT_QUEUE_NAME = "Support_MikeD"
SCRIPT_NAME = "miked_script_2026"
SCRIPT_ID = "09d11916-8ffd-4feb-9e6b-9568aaf8bfe3"
EXTERNAL_CONTACT_ACTION_ID = "custom_-_816547b6-db32-410d-8aae-9f6824846583"

EOHHS_I3 = OUT / "miked_eohhs_VAbotflow_v2-0_org-archive.i3BotFlow"
INBOUND_V3 = OUT / "miked direct to queue_v3-0.json"
WELCOME_TTS = "Welcome to the Massachusetts Registry of Motor Vehicles"


def save_i3(data: dict, path: Path) -> None:
    j = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    enc = quote(j, safe="")
    path.write_text(base64.b64encode(enc.encode("utf-8")).decode("ascii"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_i3(path: Path) -> dict:
    raw = path.read_text().strip()
    s = base64.b64decode(raw).decode("utf-8")
    while not s.startswith("{"):
        s2 = unquote(s)
        if s2 == s:
            break
        s = s2
    return json.loads(s)


def strip_empty_sequence_items(obj: object) -> None:
    if isinstance(obj, dict):
        if obj.get("sequenceItems") == []:
            obj.pop("sequenceItems", None)
        for v in obj.values():
            strip_empty_sequence_items(v)
    elif isinstance(obj, list):
        for item in obj:
            strip_empty_sequence_items(item)


def empty_str_input(name: str) -> dict:
    return {
        "name": name,
        "value": {
            "config": {"emp": {"pos": 1, "text": "", "type": "str"}},
            "text": "",
            "type": "str",
            "uiMetaData": {"mode": 3},
            "metaData": {},
            "version": 2,
        },
    }


def lit_str_input(name: str, literal: str) -> dict:
    return {
        "name": name,
        "value": {
            "config": {"lit": {"pos": 1, "text": literal, "type": "str"}},
            "text": literal,
            "type": "str",
            "uiMetaData": {"mode": 1},
            "metaData": {},
            "version": 2,
        },
    }


def mv_ava_start_context_inputs() -> list[dict]:
    """InputData fields for miked_mv_front_door (bind first_name in Architect if known)."""
    return [
        empty_str_input("first_name"),
        lit_str_input("state_code", "MA"),
        empty_str_input("conversation_id"),
        lit_str_input("interaction_channel", "voice"),
    ]


def patch_ava_action(action: dict) -> None:
    action["agenticVirtualAgentId"] = MV_AVA_AGENT_ID
    action["agenticVirtualAgentName"] = "miked_mv_front_door"
    action["agenticVirtualAgentVersion"] = MV_AVA_VERSION
    action["agenticVirtualAgentVersionId"] = f"{MV_AVA_AGENT_ID}~{MV_AVA_VERSION}"
    action["inputs"] = mv_ava_start_context_inputs()
    action["outputs"] = []


def build_mv_bot() -> dict:
    flow = load_i3(EOHHS_I3)
    flow["name"] = BOT_NAME
    flow["description"] = (
        f"Massachusetts RMV voice VA bot — miked_mv_front_door {MV_AVA_VERSION} → "
        "Call AVA; Transfer to ACD on Failure, Timeout, and agent escalation (sc12)"
    )

    for item in flow.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            strip_empty_sequence_items(action)
            if action.get("__type") == "CallAgenticVirtualAgentAction":
                patch_ava_action(action)
            if action.get("__type") == "TransferPureMatchAction":
                for q in action.get("queues") or []:
                    q["text"] = SUPPORT_QUEUE_NAME
                    if "config" in q and "lit" in q["config"]:
                        q["config"]["lit"]["text"] = SUPPORT_QUEUE_NAME
                        q["config"]["lit"]["val"] = SUPPORT_QUEUE_ID

    eh = flow.setdefault("errorHandling", {})
    eh["enableAgentEscalation"] = {
        "config": {"lit": {"pos": 1, "text": "true", "type": "bln"}},
        "text": "true",
        "type": "bln",
        "uiMetaData": {"mode": 1},
        "metaData": {},
        "version": 2,
    }
    # Exit (not Transfer) so post-AVA actions run MV handoff task with screen pop.
    eh["agentEscalationHandlingType"] = "Exit"

    settings = flow.setdefault("botFlowSettings", {})
    settings["virtualAgentEnabled"] = True
    settings["agenticVirtualAgentEnabled"] = True

    ui = flow.setdefault("uiMetaData", {})
    ui["agenticVirtualAgents"] = [
        {
            "status": "Published",
            "id": MV_AVA_AGENT_ID,
            "name": "miked_mv_front_door",
        }
    ]
    ui["agenticVirtualAgentsVersions"] = [
        {
            "status": "TestReady",
            "id": f"{MV_AVA_AGENT_ID}~{MV_AVA_VERSION}",
            "version": MV_AVA_VERSION,
            "inputs": [],
            "outputs": [],
        }
    ]

    ava_action = next(
        a
        for item in flow["flowSequenceItemList"]
        for a in item["actionList"]
        if a.get("__type") == "CallAgenticVirtualAgentAction"
    )
    manifest = flow.setdefault("manifest", {})
    manifest["agenticVirtualAgent"] = [
        {
            "name": "miked_mv_front_door",
            "id": MV_AVA_AGENT_ID,
            "context": [
                {
                    "actionName": "Call Agentic Virtual Agent",
                    "id": ava_action["id"],
                    "name": "Call Agentic Virtual Agent",
                }
            ],
        }
    ]
    manifest["agenticVirtualAgentVersion"] = [
        {
            "name": MV_AVA_VERSION,
            "id": f"{MV_AVA_AGENT_ID}~{MV_AVA_VERSION}",
            "context": [
                {
                    "actionName": "Call Agentic Virtual Agent",
                    "id": ava_action["id"],
                    "name": "Call Agentic Virtual Agent",
                }
            ],
        }
    ]
    manifest["queue"] = [
        {
            "name": SUPPORT_QUEUE_NAME,
            "id": SUPPORT_QUEUE_ID,
            "context": [
                {
                    "actionName": "Transfer to ACD",
                    "id": t["id"],
                    "name": "Transfer to ACD",
                }
                for item in flow["flowSequenceItemList"]
                for t in item.get("actionList") or []
                if t.get("__type") == "TransferPureMatchAction"
            ],
        }
    ]
    manifest["dataAction"] = [
        {
            "name": "External Contact by eMail - MikeD - Full",
            "id": EXTERNAL_CONTACT_ACTION_ID,
            "context": [],
        }
    ]
    manifest["agentScript"] = [
        {
            "name": SCRIPT_NAME,
            "id": SCRIPT_ID,
            "context": [],
        }
    ]

    strip_empty_sequence_items(flow)
    return flow


def read_bot_flow_id() -> str:
    path = OUT / f"{BOT_NAME}.flow-id"
    if path.is_file():
        line = path.read_text().strip().splitlines()[0].strip()
        if line and not line.startswith("#") and "00000000" not in line:
            return line
    import os

    env = os.environ.get("MIKED_MV_VABOTFLOW_ID", "").strip()
    if env:
        return env
    return "00000000-0000-4000-8000-000000000001"


def replace_welcome_tts(obj: object, old: str, new: str) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "text" and isinstance(v, str) and old in v:
                obj[k] = v.replace(old, new)
            else:
                replace_welcome_tts(v, old, new)
        if "parameter" in obj and obj.get("parameter") == old:
            obj["parameter"] = new
    elif isinstance(obj, list):
        for item in obj:
            replace_welcome_tts(item, old, new)


def build_inbound_v5(bot_flow_id: str) -> dict:
    flow = copy.deepcopy(load_json(INBOUND_V3))
    flow["description"] = (
        "781 RMV demo — welcome → miked_mv_VAbotflow → disconnect or queue transfer via bot"
    )

    old_welcome = "Welcome to the Massachusetts E O H H S demonstration line."
    replace_welcome_tts(flow, old_welcome, WELCOME_TTS)

    call_bot_id = "62d4c53d-c8e2-4070-8c16-884969306e1c"
    for item in flow.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            if action.get("__type") != "CallBotFlowAction":
                continue
            if action.get("id") != call_bot_id and action.get("name") == "Call Bot Flow":
                pass
            action["flowName"] = BOT_NAME
            action["flowId"] = bot_flow_id
            action["flowLatestVersion"] = True
            action["flowDebugPublished"] = False
            action["flowOutOfService"] = bot_flow_id.startswith("00000000")

    raw = json.dumps(flow)
    raw = raw.replace("miked_eohhs_VAbotflow", BOT_NAME)
    raw = raw.replace("0ddb5a61-7d13-4d92-bf72-02ef2b70c07c", bot_flow_id)
    flow = json.loads(raw)

    manifest = flow.setdefault("manifest", {})
    manifest["botFlow"] = [
        {
            "name": BOT_NAME,
            "id": bot_flow_id,
            "version": "published",
            "context": [
                {
                    "actionName": "Call Bot Flow",
                    "id": call_bot_id,
                    "name": "Call Bot Flow",
                }
            ],
        }
    ]
    return flow


def main() -> None:
    inbound_only = "--inbound-only" in sys.argv
    bot_only = "--bot-only" in sys.argv

    if not inbound_only:
        bot = build_mv_bot()
        bot_json = OUT / f"{BOT_NAME}_v1-0.json"
        bot_i3 = OUT / f"{BOT_NAME}_v1-0.i3BotFlow"
        bot_json.write_text(json.dumps(bot, indent=2) + "\n")
        save_i3(bot, bot_i3)
        print("Wrote:", bot_i3)
        print("Wrote:", bot_json)

    if not bot_only:
        bot_flow_id = read_bot_flow_id()
        inbound = build_inbound_v5(bot_flow_id)
        in_json = OUT / "miked direct to queue_v5-mv-0.json"
        in_i3 = OUT / "miked direct to queue_v5-mv-0.i3InboundFlow"
        in_json.write_text(json.dumps(inbound, indent=2) + "\n")
        save_i3(inbound, in_i3)
        print("Wrote:", in_i3, "bot flowId", bot_flow_id)
        if bot_flow_id.startswith("00000000"):
            print(
                "NOTE: Placeholder bot flow ID — after first bot publish, run:\n"
                f"  echo '<uuid>' > {OUT / f'{BOT_NAME}.flow-id'}\n"
                "  python3 scripts/build-mv-greenfield-flows.py --inbound-only"
            )


if __name__ == "__main__":
    main()
