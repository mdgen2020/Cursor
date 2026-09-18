#!/usr/bin/env python3
"""Patch NY DOL Architect flows and write .i3 import files."""
from __future__ import annotations

import base64
import copy
import json
import uuid
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs/demo/architect-exports"

# --- i3 codec ---


def load_i3(path: Path) -> dict:
    raw = path.read_text().strip()
    s = base64.b64decode(raw).decode("utf-8")
    while not s.startswith("{"):
        s2 = unquote(s)
        if s2 == s:
            break
        s = s2
    return json.loads(s)


def save_i3(data: dict, path: Path) -> None:
    j = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    enc = quote(j, safe="")
    path.write_text(base64.b64encode(enc.encode("utf-8")).decode("ascii"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


# --- expression helpers ---


def ref_value(name: str, var_id: str, type_: str = "str", *, mode: int = 0) -> dict:
    return {
        "config": {"ref": {"pos": 1, "text": name, "type": type_, "val": var_id}},
        "text": name,
        "type": type_,
        "uiMetaData": {"mode": mode},
        "metaData": {
            "references": [{"id": var_id, "type": type_, "isSysRef": False, "name": name}]
        },
        "version": 2,
    }


def lit_value(text: str) -> dict:
    return {
        "config": {"lit": {"pos": 1, "text": text, "type": "str"}},
        "text": text,
        "type": "str",
        "uiMetaData": {"mode": 1},
        "metaData": {},
        "version": 2,
    }


def empty_str_value() -> dict:
    return {
        "config": {"emp": {"pos": 1, "text": "", "type": "str"}},
        "text": "",
        "type": "str",
        "uiMetaData": {"mode": 3},
        "metaData": {},
        "version": 2,
    }


def string_variable(name: str, var_id: str) -> dict:
    return {
        "id": var_id,
        "isCollection": False,
        "isInternal": False,
        "isOutput": False,
        "isInput": False,
        "isSecure": False,
        "version": "1.0",
        "__type": "StringVariable",
        "name": name,
        "initialValue": empty_str_value(),
    }


def update_data_copy_inc_to_script(tracking_id: int) -> dict:
    return {
        "nextAction": None,  # filled by caller
        "trackingId": tracking_id,
        "id": str(uuid.uuid4()),
        "name": "Update Data — INCtoScript",
        "uiMetaData": {"collapsed": False},
        "__type": "UpdateVariableAction",
        "variables": [
            {
                "expression": ref_value("Flow.incnumber", IDS_BOT["Flow.incnumber"]),
                "variable": ref_value("Flow.INCtoScript", IDS_BOT["Flow.INCtoScript"], mode=2),
            }
        ],
    }


IDS_BOT = {
    "Flow.incnumber": "fb083d49-b84d-4ce2-9c45-663f4862c4e9",
    "Flow.INCtoScript": "e9e1ccd9-c857-468a-b110-1401f3b51143",
    "Flow.incident_state": "47e013c4-86a0-48fd-8caf-954b179de386",
    "Flow.short_des": "240dd750-c2d3-4b60-a658-596da917f866",
    "Slot.Name": "455c4375-a3a3-48fe-a852-88352350a791",
}

AVA_DOL = {
    "agentId": "ebc26f01-f4c4-43ca-873e-15580c12c8f4",
    "name": "DOL_Front_Door_miked",
    "version": "5.0",
}

LEGACY_TASK_ID = "fa34ebb4-3201-4320-a54a-641d1891a965"
LEGACY_TASK_NAME = "legacy dol bot"
INITIAL_GREETING_STATE_ID = "b560bff7-4e13-4980-bf59-2eb74442b781"
INITIAL_GREETING_COMMUNICATE_ID = "9c282de1-8cf3-49d3-ae68-c9a8a5a82631"
INITIAL_GREETING_CALL_TASK_ID = "c3ac7605-02fe-450c-9c10-88c23267a051"
INITIAL_GREETING_EXIT_ID = "837542a7-02fa-4ab5-ad80-33a1925a16fe"

IDS_MSG = {
    "Flow.incfrombot": "bb8c4967-4bbd-4cbb-99b0-ac546dfd6576",
    "Flow.FirstName": "2dc69804-8226-4965-bfde-fcc52d48c021",
    "Flow.LastName": "fef7346f-be1c-4932-be22-fa11c0d0a6a4",
    "Flow.INCScript": "409718dd-f8a4-486a-91a1-af19e50414b7",
    "Flow.IBVivrselection": "492cdd3c-5665-4554-acb9-457af6c472eb",
}

IDS_MSG["Flow.IncState"] = str(uuid.uuid4())
IDS_MSG["Flow.ClaimShort"] = str(uuid.uuid4())

# Script input referenceIds (from msg flow uiMetaData scripts)
SCRIPT_REFS = {
    "customer_selection": "a69ab769-a1e4-41e5-ac73-4df05811c0dc",
    "claim_number": "d0d96d71-c210-433d-9a6b-c08ef675a59f",
    "claim_descript": "c7792c43-0d9a-4799-b66f-26062870b304",
    "IncState": "cc7cfc91-bf81-4632-98f4-5f303f57701a",
    "acct_status": "985a7045-ca79-470e-a2ec-d1775a47eada",
    "customer_name": "c4ef097a-59b0-4a8b-ac47-4652d9240476",
    "agent_summary": "2d3d1da5-dc72-4f28-9191-d1ec3f9e959c",
    "banner_text": "76987136-e7fd-4a73-a59a-3b7de436c2d7",
    "banner_color": "806f0080-ee2f-4cfb-91f4-8f4aaf3075ee",
}


def patch_bot(bot: dict) -> None:
    bot["description"] = (bot.get("description") or "") + " | patched INC outputs + INCtoScript update (sc12)"
    for v in bot.get("variables", []):
        if v.get("name") in ("Flow.incident_state", "Flow.short_des", "Flow.priority"):
            v["isOutput"] = True

    task = next(i for i in bot["flowSequenceItemList"] if i.get("name") == "Status Request")
    data_action_id = "90e7a103-5578-47b4-b692-5c9d36fcee35"
    end_task_id = "52a2e460-bf05-460d-ab63-26bb1baf5b94"
    upd = update_data_copy_inc_to_script(tracking_id=bot.get("nextTrackingNumber", 300))
    bot["nextTrackingNumber"] = bot.get("nextTrackingNumber", 300) + 1
    upd["nextAction"] = end_task_id
    for a in task["actionList"]:
        if a.get("id") == data_action_id:
            a["nextAction"] = upd["id"]
    task["actionList"].append(upd)


def rename_legacy_starting_task(bot: dict) -> None:
    for item in bot.get("flowSequenceItemList", []):
        if item.get("id") == LEGACY_TASK_ID:
            item["name"] = LEGACY_TASK_NAME
    tasks = bot.get("uiMetaData", {}).get("task") or []
    for task in tasks:
        if task.get("id") == LEGACY_TASK_ID:
            task["name"] = LEGACY_TASK_NAME
    settings = bot.get("botFlowSettings") or {}
    if settings.get("knowledgeFollowupTaskName") == "Starting Task":
        settings["knowledgeFollowupTaskName"] = LEGACY_TASK_NAME
    ks = bot.get("knowledgeSettings") or {}
    if ks.get("knowledgeFollowupTaskName") == "Starting Task":
        ks["knowledgeFollowupTaskName"] = LEGACY_TASK_NAME
    for item in bot.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            if action.get("taskReference") == LEGACY_TASK_ID or action.get("taskName") == "Starting Task":
                action["taskName"] = LEGACY_TASK_NAME


def ava_output(name: str, flow_var: str, var_id: str) -> dict:
    return {"name": name, "value": ref_value(flow_var, var_id, mode=2)}


def call_agentic_virtual_agent_action(*, action_id: str, tracking_id: int, next_action: str, exit_id: str) -> dict:
    agent_id = AVA_DOL["agentId"]
    version = AVA_DOL["version"]
    return {
        "uiMetaData": {"collapsed": False},
        "id": action_id,
        "name": "Call Agentic Virtual Agent",
        "__type": "CallAgenticVirtualAgentAction",
        "agenticVirtualAgentVersionId": f"{agent_id}~{version}",
        "agenticVirtualAgentId": agent_id,
        "agenticVirtualAgentName": AVA_DOL["name"],
        "agenticVirtualAgentVersion": version,
        "inputs": [],
        "outputs": [
            ava_output("claim_lookup.0.number", "Flow.incnumber", IDS_BOT["Flow.incnumber"]),
            ava_output(
                "claim_lookup.0.incident_state",
                "Flow.incident_state",
                IDS_BOT["Flow.incident_state"],
            ),
            ava_output(
                "appointment_lookup.entities.contact_name.0",
                "Slot.Name",
                IDS_BOT["Slot.Name"],
            ),
        ],
        "errorBindings": [],
        "voiceProcessingPrompt": {
            "config": {"emp": {"pos": 1, "text": "", "type": "com"}},
            "text": "",
            "type": "com",
            "uiMetaData": {"mode": 3},
            "metaData": {},
            "version": 2,
            "outOfService": True,
        },
        "exitReason": {
            "config": {"emp": {"pos": 1, "text": "", "type": "str"}},
            "text": "",
            "type": "str",
            "uiMetaData": {"mode": 3},
            "metaData": {},
            "version": 2,
        },
        "paths": [
            {
                "label": "Success",
                "outputId": "__SUCCESS__",
                "isCategory": False,
                "uiMetaData": {"collapsed": False},
            },
            {
                "nextActionId": exit_id,
                "label": "Failure",
                "outputId": "__FAILURE__",
                "isCategory": False,
                "uiMetaData": {"collapsed": False},
            },
            {
                "nextActionId": exit_id,
                "label": "Timeout",
                "outputId": "__TIMEOUT__",
                "isCategory": False,
                "uiMetaData": {"collapsed": False},
            },
        ],
        "nextAction": next_action,
        "trackingId": tracking_id,
    }


def patch_bot_ava(bot: dict) -> None:
    suffix = " | AVA DOL_Front_Door_miked on Initial Greeting (sc12)"
    if suffix.strip("| ") not in (bot.get("description") or ""):
        bot["description"] = (bot.get("description") or "") + suffix

    rename_legacy_starting_task(bot)

    settings = bot.setdefault("botFlowSettings", {})
    settings["agenticVirtualAgentEnabled"] = True
    settings["virtualAgentEnabled"] = True

    state = next(
        i for i in bot["flowSequenceItemList"] if i.get("id") == INITIAL_GREETING_STATE_ID
    )
    for existing in state.get("actionList") or []:
        if existing.get("__type") == "CallAgenticVirtualAgentAction":
            return

    ava_id = str(uuid.uuid4())
    update_id = str(uuid.uuid4())
    tracking = bot.get("nextTrackingNumber", 300)
    bot["nextTrackingNumber"] = tracking + 2

    update_inc = update_data_copy_inc_to_script(tracking_id=tracking)
    update_inc["id"] = update_id
    update_inc["nextAction"] = INITIAL_GREETING_EXIT_ID

    ava = call_agentic_virtual_agent_action(
        action_id=ava_id,
        tracking_id=tracking + 1,
        next_action=update_id,
        exit_id=INITIAL_GREETING_EXIT_ID,
    )

    actions = state.get("actionList") or []
    for action in actions:
        if action.get("id") == INITIAL_GREETING_COMMUNICATE_ID:
            action["nextAction"] = ava_id
    state["actionList"] = [
        a for a in actions if a.get("id") != INITIAL_GREETING_CALL_TASK_ID
    ]
    state["actionList"].extend([ava, update_inc])


def patch_msg_outputs(call_action: dict) -> None:
    outputs = call_action.setdefault("outputs", [])
    existing = {o.get("name") for o in outputs}

    def add_output(bot_param: str, parent_name: str, parent_id: str) -> None:
        if bot_param in existing:
            for o in outputs:
                if o.get("name") == bot_param:
                    o["value"] = ref_value(parent_name, parent_id, mode=2)
            return
        outputs.append(
            {"name": bot_param, "value": ref_value(parent_name, parent_id, mode=2)}
        )

    add_output("Flow.incident_state", "Flow.IncState", IDS_MSG["Flow.IncState"])
    add_output("Flow.short_des", "Flow.ClaimShort", IDS_MSG["Flow.ClaimShort"])
    add_output("Flow.INCtoScript", "Flow.INCScript", IDS_MSG["Flow.INCScript"])


def patch_screen_pop_inputs(inputs: list) -> None:
    mapping = {
        "customer_selection": ref_value("Flow.IBVivrselection", IDS_MSG["Flow.IBVivrselection"]),
        "claim_number": ref_value("Flow.incfrombot", IDS_MSG["Flow.incfrombot"]),
        "claim_descript": ref_value("Flow.ClaimShort", IDS_MSG["Flow.ClaimShort"]),
        "IncState": ref_value("Flow.IncState", IDS_MSG["Flow.IncState"]),
        "acct_status": ref_value("Flow.IncState", IDS_MSG["Flow.IncState"]),
        "customer_name": ref_value("Flow.FirstName", IDS_MSG["Flow.FirstName"]),
        "agent_summary": lit_value(
            "NYS DOL Messenger handoff — review claim number, status, and description with the resident."
        ),
        "banner_text": ref_value("Flow.ClaimShort", IDS_MSG["Flow.ClaimShort"]),
        "banner_color": lit_value("#00447C"),
    }
    by_name = {i["name"]: i for i in inputs}
    for name, val in mapping.items():
        ref_id = SCRIPT_REFS.get(name)
        if name in by_name:
            by_name[name]["value"] = copy.deepcopy(val)
            if ref_id:
                by_name[name]["referenceId"] = ref_id


def patch_msg(msg: dict) -> None:
    msg["description"] = (msg.get("description") or "") + " | patched bot outputs + screen pop DOL fields (sc12)"
    names = {v["name"] for v in msg.get("variables", [])}
    if "Flow.IncState" not in names:
        msg["variables"].append(string_variable("Flow.IncState", IDS_MSG["Flow.IncState"]))
    if "Flow.ClaimShort" not in names:
        msg["variables"].append(string_variable("Flow.ClaimShort", IDS_MSG["Flow.ClaimShort"]))

    for item in msg.get("flowSequenceItemList", []):
        for action in item.get("actionList") or []:
            if action.get("__type") == "CallDigitalBotFlowAction" and action.get("flowName") == "Dig_bot_nydol":
                patch_msg_outputs(action)
            if action.get("__type") == "ScreenPopAction" and action.get("screenPopName") == "miked_script_2026":
                patch_screen_pop_inputs(action.get("inputs") or [])


def main() -> None:
    bot_v15 = OUT_DIR / "Dig_bot_nydol_v15-0.json"
    bot_v14 = OUT_DIR / "Dig_bot_nydol_v14-0.json"
    msg_src = OUT_DIR / "msg_dig_nydol_miked_v9-0.json"

    if bot_v15.is_file():
        bot = load_json(bot_v15)
    elif bot_v14.is_file():
        bot = load_json(bot_v14)
        patch_bot(bot)
    else:
        bot = load_i3(
            Path(
                "/Users/michael.debiase/Library/CloudStorage/OneDrive-GenesysTelecommunicationsLaboratories,Inc/Desktop/NY_Techshow_sept2026/Dig_bot_nydol_v14-0.i3DigitalBotFlow"
            )
        )
        patch_bot(bot)

    patch_bot_ava(bot)
    msg = load_json(msg_src)
    patch_msg(msg)

    bot_out = OUT_DIR / "Dig_bot_nydol_v16-0.i3DigitalBotFlow"
    msg_out = OUT_DIR / "msg_dig_nydol_miked_v10-0.i3InboundMessage"
    save_i3(bot, bot_out)
    save_i3(msg, msg_out)

    (OUT_DIR / "Dig_bot_nydol_v16-0.json").write_text(json.dumps(bot, indent=2) + "\n")
    (OUT_DIR / "msg_dig_nydol_miked_v10-0.json").write_text(json.dumps(msg, indent=2) + "\n")

    print("Wrote:", bot_out)
    print("Wrote:", msg_out)
    print("AVA:", AVA_DOL["name"], AVA_DOL["version"])
    print("Legacy task renamed to:", LEGACY_TASK_NAME)


if __name__ == "__main__":
    main()
