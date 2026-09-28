#!/usr/bin/env python3
"""Build greenfield NYS DOL Messenger flows (new names, no Dig_bot_nydol)."""
from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/demo/architect-exports"

BOT_NAME = "miked_dol_VAbotflow"
INBOUND_NAME = "miked_dol_inbound_message"
AVA_AGENT_ID = "ebc26f01-f4c4-43ca-873e-15580c12c8f4"
AVA_VERSION = "12.0"
EXTERNAL_CONTACT_ACTION_ID = "custom_-_816547b6-db32-410d-8aae-9f6824846583"
HYDRATE_CONTACT_ACTION_ID = "a7b4c2d1-6e5f-4a8b-9c0d-1e2f3a4b5c6d"
INC_SCRIPT_UPDATE_ACTION_ID = "b8c5d3e2-7f6a-5b9c-0d1e-2f3a4b5c6d7e"
USER_DIG_BOT = OUT / "Dig_bot_nydol_user_export.json"
INBOUND_CALL_BOT_ACTION_ID = "f6b4d239-02e9-4b28-afa2-5ecac6208b09"


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


def string_var(
    name: str,
    var_id: str,
    *,
    is_input: bool = False,
    is_output: bool = True,
) -> dict:
    return {
        "id": var_id,
        "isCollection": False,
        "isInternal": False,
        "isOutput": is_output,
        "isInput": is_input,
        "isSecure": False,
        "version": "1.0",
        "__type": "StringVariable",
        "name": name,
        "initialValue": {
            "config": {"emp": {"pos": 1, "text": "", "type": "str"}},
            "text": "",
            "type": "str",
            "uiMetaData": {"mode": 3},
            "metaData": {},
            "version": 2,
        },
    }


DIG_MINIMAL = OUT / "Dig_bot_nydol_v17_ava_minimal.json"
EOHHS_I3 = OUT / "miked_eohhs_VAbotflow_v2-0.i3BotFlow"
MSG_DIG = OUT / "msg_dig_nydol_miked_v10-0.json"
REF_INBOUND_TRANSFER_ID = "7619f8f1-9c21-4eff-a313-7d835852c702"


VAR_IDS = {
    "Flow.incnumber": "fb083d49-b84d-4ce2-9c45-663f4862c4e9",
    "Flow.incident_state": "47e013c4-86a0-48fd-8caf-954b179de386",
    "Flow.INCtoScript": "e9e1ccd9-c857-468a-b110-1401f3b51143",
    "Slot.Name": "455c4375-a3a3-48fe-a852-88352350a791",
    "Slot.email": "26cd616c-d086-4858-9594-8fac5105dfd4",
    "Slot.LastName": "5aed3689-d480-4021-8648-3115d46a9077",
    "Flow.lastname": "46d74d92-c0ae-43a3-897d-442903ca66bf",
    "Flow.firstname": "82868a5a-bfe8-4184-89e4-89b343b8919c",
    "Flow.address1": "a11bb249-bc20-4a29-b0fe-fcf1a13e9d9a",
    "Flow.state": "1cb66580-d7fe-4097-8be9-00183abdde9a",
    "Flow.zip": "8dc6258e-df8e-4ce6-a262-8ed9a9969b7c",
    "Flow.city": "352187bb-3fff-42d1-b3b9-b126e477807d",
}


CLAIM_OUTPUT_VAR_IDS = frozenset(
    {
        VAR_IDS["Flow.incnumber"],
        VAR_IDS["Flow.incident_state"],
        VAR_IDS["Flow.INCtoScript"],
    }
)


def handoff_vars_from_dig_bot() -> list[dict]:
    """Output-only claim variables from Dig_bot reference (isInput false)."""
    ref = load_json(DIG_MINIMAL)
    out = []
    for v in ref["variables"]:
        if v["id"] in CLAIM_OUTPUT_VAR_IDS:
            out.append(copy.deepcopy(v))
    if len(out) != len(CLAIM_OUTPUT_VAR_IDS):
        raise SystemExit(
            f"Expected {len(CLAIM_OUTPUT_VAR_IDS)} claim output vars from Dig_bot export, got {len(out)}"
        )
    return out


def dig_bot_variables_by_name(names: set[str]) -> list[dict]:
    ref = load_json(DIG_MINIMAL)
    out = []
    for v in ref["variables"]:
        if v["name"] in names:
            out.append(copy.deepcopy(v))
    missing = names - {v["name"] for v in out}
    if missing:
        raise SystemExit(f"Missing bot variables in Dig_bot export: {sorted(missing)}")
    return out


def _ava_output_binding(ava_out: str, bot_var: str, var_id: str, *, coll: bool) -> dict:
    vtype = "str_coll" if coll else "str"
    return {
        "name": ava_out,
        "value": {
            "config": {
                "ref": {
                    "pos": 1,
                    "text": bot_var,
                    "type": vtype,
                    "val": var_id,
                }
            },
            "text": bot_var,
            "type": vtype,
            "uiMetaData": {"mode": 2},
            "metaData": {
                "references": [
                    {
                        "id": var_id,
                        "type": vtype,
                        "isSysRef": False,
                        "name": bot_var,
                    }
                ]
            },
            "version": 2,
        },
    }


def dig_bot_call_ava_outputs() -> list[dict]:
    """Call AVA output bindings (claim handoff + contact profile agent outputs)."""
    ref = load_json(OUT / "Dig_bot_nydol_v17_ava_minimal.json")
    ava = next(
        a
        for item in ref["flowSequenceItemList"]
        for a in item["actionList"]
        if a.get("__type") == "CallAgenticVirtualAgentAction"
    )
    outs = copy.deepcopy(ava.get("outputs") or [])
    extra = [
        ("handoff.contact_email", "Slot.email", VAR_IDS["Slot.email"], False),
        ("handoff.resident_name", "Slot.Name", VAR_IDS["Slot.Name"], False),
        ("handoff.contact_last_name", "Slot.LastName", VAR_IDS["Slot.LastName"], False),
    ]
    names = {o.get("name") for o in outs}
    for ava_out, bot_var, var_id, coll in extra:
        if ava_out in names:
            continue
        outs.append(_ava_output_binding(ava_out, bot_var, var_id, coll=coll))
    return outs


def strip_empty_sequence_items(obj: object) -> None:
    """EOHHS Transfer actions ship preTransferAudio.sequenceItems: [] — Architect flags as broken."""
    if isinstance(obj, dict):
        if obj.get("sequenceItems") == []:
            obj.pop("sequenceItems", None)
        for v in obj.values():
            strip_empty_sequence_items(v)
    elif isinstance(obj, list):
        for item in obj:
            strip_empty_sequence_items(item)


def empty_comm_out_of_service() -> dict:
    """Valid empty communication expression for Messenger Transfer to ACD (Architect rejects mode-0 blank)."""
    return {
        "config": {
            "emp": {
                "pos": 1,
                "text": "",
                "type": "com",
            }
        },
        "text": "",
        "type": "com",
        "uiMetaData": {"mode": 3},
        "metaData": {},
        "version": 2,
        "outOfService": True,
    }


def sanitize_transfer_audio_block(audio: dict) -> dict:
    """Remove broken defaultAudio sequenceItems (Architect: builder sequences in error)."""
    block = copy.deepcopy(audio)
    default = block.get("defaultAudio")
    if isinstance(default, dict):
        ui = default.get("uiMetaData")
        if isinstance(ui, dict) and "sequenceItems" in ui:
            ui.pop("sequenceItems", None)
            if not ui:
                default.pop("uiMetaData", None)
        default["outOfService"] = True
    return block


def normalize_transfer_pre_transfer_blocks(state: dict) -> None:
    """Messenger-safe Transfer to ACD: no pre/fail prompts; valid empty comm expressions."""
    ref = load_json(MSG_DIG)
    ref_transfer = None
    for item in ref.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            if action.get("id") == REF_INBOUND_TRANSFER_ID:
                ref_transfer = action
                break
        if ref_transfer:
            break
    if not ref_transfer:
        raise SystemExit(f"Reference transfer {REF_INBOUND_TRANSFER_ID} not found in {MSG_DIG.name}")

    pre_audio = sanitize_transfer_audio_block(ref_transfer["preTransferAudio"])
    fail_audio = sanitize_transfer_audio_block(ref_transfer["failureTransferAudio"])
    empty_comm = empty_comm_out_of_service()
    for action in state.get("actionList") or []:
        if action.get("__type") != "TransferPureMatchAction":
            continue
        action["preTransferAudio"] = copy.deepcopy(pre_audio)
        action["preTransferCommunication"] = copy.deepcopy(empty_comm)
        action["failureTransferAudio"] = copy.deepcopy(fail_audio)
        action["failureTransferCommunication"] = copy.deepcopy(empty_comm)


def _find_external_contact_data_action() -> dict:
    ref = load_json(USER_DIG_BOT)
    for item in ref.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            if action.get("actionId") == EXTERNAL_CONTACT_ACTION_ID:
                return copy.deepcopy(action)
    raise SystemExit(f"External contact Data Action not found in {USER_DIG_BOT.name}")


def external_contact_hydrate_action(*, next_action_id: str) -> dict:
    """Re-run contact lookup so collection vars match inbound / script (AVA outputs are scalars)."""
    action = _find_external_contact_data_action()
    action["id"] = HYDRATE_CONTACT_ACTION_ID
    action["name"] = "Hydrate external contact for handoff"
    action["nextAction"] = next_action_id
    for path in action.get("paths") or []:
        path["nextActionId"] = next_action_id
    return action


def inc_script_update_action(*, next_action_id: str) -> dict:
    """Flow.INCtoScript is output-only on inbound — copy claim number before exit."""
    return {
        "nextAction": next_action_id,
        "trackingId": 201,
        "id": INC_SCRIPT_UPDATE_ACTION_ID,
        "name": "Update Data — INCtoScript",
        "uiMetaData": {"collapsed": False},
        "__type": "UpdateVariableAction",
        "variables": [
            {
                "expression": {
                    "config": {
                        "ref": {
                            "pos": 1,
                            "text": "Flow.incnumber",
                            "type": "str",
                            "val": VAR_IDS["Flow.incnumber"],
                        }
                    },
                    "text": "Flow.incnumber",
                    "type": "str",
                    "uiMetaData": {"mode": 0},
                    "metaData": {
                        "references": [
                            {
                                "id": VAR_IDS["Flow.incnumber"],
                                "type": "str",
                                "isSysRef": False,
                                "name": "Flow.incnumber",
                            }
                        ]
                    },
                    "version": 2,
                },
                "variable": {
                    "config": {
                        "ref": {
                            "pos": 1,
                            "text": "Flow.INCtoScript",
                            "type": "str",
                            "val": VAR_IDS["Flow.INCtoScript"],
                        }
                    },
                    "text": "Flow.INCtoScript",
                    "type": "str",
                    "uiMetaData": {"mode": 2},
                    "metaData": {
                        "references": [
                            {
                                "id": VAR_IDS["Flow.INCtoScript"],
                                "type": "str",
                                "isSysRef": False,
                                "name": "Flow.INCtoScript",
                            }
                        ]
                    },
                    "version": 2,
                },
            }
        ],
    }


def eohhs_ava_canvas_state() -> tuple[dict, dict, dict, dict]:
    """Default Bot canvas: AVA → hydrate contact → INC script copy → Exit."""
    eohhs = load_i3(EOHHS_I3)
    init = eohhs["initialSequence"]
    state = copy.deepcopy(next(x for x in eohhs["flowSequenceItemList"] if x["id"] == init))
    state["name"] = "Default Bot"
    allowed = {
        "ExitBotFlowAction",
        "CallAgenticVirtualAgentAction",
        "TransferPureMatchAction",
        "DataAction",
        "UpdateVariableAction",
    }
    state["actionList"] = [
        copy.deepcopy(a) for a in state["actionList"] if a.get("__type") in allowed
    ]
    for action in state["actionList"]:
        strip_empty_sequence_items(action)
    normalize_transfer_pre_transfer_blocks(state)

    ava = next(a for a in state["actionList"] if a["__type"] == "CallAgenticVirtualAgentAction")
    exit_a = next(a for a in state["actionList"] if a["__type"] == "ExitBotFlowAction")
    inc_update = inc_script_update_action(next_action_id=exit_a["id"])
    hydrate = external_contact_hydrate_action(next_action_id=inc_update["id"])
    ava["agenticVirtualAgentId"] = AVA_AGENT_ID
    ava["agenticVirtualAgentName"] = "DOL_Front_Door_miked"
    ava["agenticVirtualAgentVersion"] = AVA_VERSION
    ava["agenticVirtualAgentVersionId"] = f"{AVA_AGENT_ID}~{AVA_VERSION}"
    ava["inputs"] = []
    ava["outputs"] = dig_bot_call_ava_outputs()
    ava["nextAction"] = hydrate["id"]
    for path in ava.get("paths") or []:
        if path.get("outputId") == "__SUCCESS__":
            path["nextActionId"] = hydrate["id"]
    state["actionList"].extend([hydrate, inc_update])
    state["startAction"] = ava["id"]
    return state, ava, hydrate, inc_update


def build_bot_v2() -> dict:
    """Dig_bot minimal settings + EOHHS AVA/Transfer canvas (Messenger-safe, no broken builders)."""
    flow = copy.deepcopy(load_json(DIG_MINIMAL))
    flow["name"] = BOT_NAME
    flow["type"] = "digitalbot"
    flow["description"] = (
        f"Greenfield NYS DOL Messenger VA bot — DOL_Front_Door_miked {AVA_VERSION} → "
        "AVA → hydrate external contact → Exit; Transfer to ACD on AVA Failure/Timeout (sc12)"
    )

    state, ava, hydrate, _inc_update = eohhs_ava_canvas_state()
    flow["initialSequence"] = state["id"]
    flow["flowSequenceItemList"] = [state]

    contact_vars = {
        "Flow.address1",
        "Flow.address2",
        "Flow.state",
        "Flow.zip",
        "Flow.city",
        "Flow.firstname",
        "Flow.lastname",
    }
    flow["variables"] = handoff_vars_from_dig_bot() + [
        string_var("Slot.Name", VAR_IDS["Slot.Name"], is_input=True, is_output=True),
        string_var("Slot.email", VAR_IDS["Slot.email"], is_input=True, is_output=True),
        string_var("Slot.LastName", VAR_IDS["Slot.LastName"], is_input=True, is_output=True),
    ] + dig_bot_variables_by_name(contact_vars)

    settings = flow.setdefault("botFlowSettings", {})
    settings["virtualAgentEnabled"] = True
    settings["agenticVirtualAgentEnabled"] = True

    ui = flow.setdefault("uiMetaData", {})
    ui["agenticVirtualAgents"] = [
        {
            "status": "Published",
            "id": AVA_AGENT_ID,
            "name": "DOL_Front_Door_miked",
        }
    ]
    ui["agenticVirtualAgentsVersions"] = [
        {
            "status": "TestReady",
            "id": f"{AVA_AGENT_ID}~{AVA_VERSION}",
            "version": AVA_VERSION,
            "inputs": [],
            "outputs": [],
        }
    ]

    manifest = flow.setdefault("manifest", {})
    manifest["dataAction"] = [
        {
            "name": "External Contact by eMail - MikeD - Full",
            "id": EXTERNAL_CONTACT_ACTION_ID,
            "context": [
                {
                    "actionName": hydrate["name"],
                    "id": hydrate["id"],
                    "name": hydrate["name"],
                }
            ],
        }
    ]
    manifest["agenticVirtualAgent"] = [
        {
            "name": "DOL_Front_Door_miked",
            "id": AVA_AGENT_ID,
            "context": [
                {
                    "actionName": "Call Agentic Virtual Agent",
                    "id": ava["id"],
                    "name": "Call Agentic Virtual Agent",
                }
            ],
        }
    ]
    manifest["agenticVirtualAgentVersion"] = [
        {
            "name": AVA_VERSION,
            "id": f"{AVA_AGENT_ID}~{AVA_VERSION}",
            "context": [
                {
                    "actionName": "Call Agentic Virtual Agent",
                    "id": ava["id"],
                    "name": "Call Agentic Virtual Agent",
                }
            ],
        }
    ]
    manifest["queue"] = [
        {
            "name": "Support_MikeD",
            "id": "dc15ad2c-7917-413f-9a00-4f52df4d4602",
            "context": [
                {
                    "actionName": "Transfer to ACD",
                    "id": "c8a4e112-4720-434c-a5b9-b16d8bee7cda",
                    "name": "Transfer to ACD",
                },
                {
                    "actionName": "Transfer to ACD",
                    "id": "636c0bbe-4404-4417-b0f3-707f434171da",
                    "name": "Transfer to ACD",
                },
            ],
        }
    ]

    strip_empty_sequence_items(flow)
    return flow


OLD_DIG_BOT_ID = "d9c7a0f5-2a7c-490e-a626-379261b4f8b7"
OLD_DIG_BOT_NAME = "Dig_bot_nydol"


def read_bot_flow_id() -> str:
    path = OUT / "miked_dol_VAbotflow.flow-id"
    if path.is_file():
        line = path.read_text().strip().splitlines()[0].strip()
        if line and not line.startswith("#") and "00000000" not in line:
            return line
    import os

    env = os.environ.get("MIKED_DOL_VABOTFLOW_ID", "").strip()
    if env:
        return env
    raise SystemExit(
        "Set published bot flow UUID:\n"
        f"  echo '<uuid>' > {path}\n"
        "  or MIKED_DOL_VABOTFLOW_ID=<uuid> python3 scripts/build-nydol-greenfield-flows.py --inbound-only\n"
        f"See {OUT / 'miked_dol_VAbotflow.flow-id.example'}"
    )


def build_inbound(bot_flow_id: str) -> dict:
    flow = copy.deepcopy(load_json(OUT / "msg_dig_nydol_miked_v10-0.json"))
    flow["name"] = INBOUND_NAME
    flow["description"] = (
        "Greenfield NYS DOL Messenger inbound — IBV 132 → miked_dol_VAbotflow → "
        "contact merge → DOL transfer → miked_script_2026 (sc12)"
    )

    call_action_id = "f6b4d239-02e9-4b28-afa2-5ecac6208b09"

    manifest = flow.setdefault("manifest", {})
    manifest["digitalBotFlow"] = [
        {
            "name": BOT_NAME,
            "id": bot_flow_id,
            "version": "published",
            "context": [
                {
                    "actionName": "Call Digital Bot Flow",
                    "id": call_action_id,
                    "name": "Call Digital Bot Flow",
                }
            ],
        }
    ]

    for item in flow.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            if action.get("__type") != "CallDigitalBotFlowAction":
                continue
            if action.get("id") != call_action_id:
                continue
            action["flowName"] = BOT_NAME
            action["flowId"] = bot_flow_id
            action["flowLatestVersion"] = True
            action["flowDebugPublished"] = False
            action["flowOutOfService"] = False

    # Remove any stale Dig_bot manifest ids if present elsewhere in tree
    raw = json.dumps(flow)
    raw = raw.replace(OLD_DIG_BOT_NAME, BOT_NAME)
    raw = raw.replace(OLD_DIG_BOT_ID, bot_flow_id)
    flow = json.loads(raw)

    return flow


import sys


def main() -> None:
    inbound_only = "--inbound-only" in sys.argv
    bot_only = "--bot-only" in sys.argv

    if not inbound_only:
        bot = build_bot_v2()
        bot_json = OUT / f"{BOT_NAME}_v2-0.json"
        bot_i3 = OUT / f"{BOT_NAME}_v2-0.i3DigitalBotFlow"
        bot_json.write_text(json.dumps(bot, indent=2) + "\n")
        save_i3(bot, bot_i3)
        print("Wrote:", bot_i3)

    if not bot_only:
        bot_flow_id = read_bot_flow_id()
        inbound = build_inbound(bot_flow_id)
        in_json = OUT / f"{INBOUND_NAME}_v1-0.json"
        in_i3 = OUT / f"{INBOUND_NAME}_v1-0.i3InboundMessage"
        in_json.write_text(json.dumps(inbound, indent=2) + "\n")
        save_i3(inbound, in_i3)
        print("Wrote:", in_i3, "bot flowId", bot_flow_id)
        print("Call Digital Bot outputs:", len(
            next(
                a
                for item in inbound["flowSequenceItemList"]
                for a in item["actionList"]
                if a.get("id") == "f6b4d239-02e9-4b28-afa2-5ecac6208b09"
            ).get("outputs", [])
        ))


if __name__ == "__main__":
    main()
