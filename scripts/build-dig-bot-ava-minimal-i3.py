#!/usr/bin/env python3
"""Build a minimal publishable Dig_bot_nydol virtual-agent flow from an org export."""
from __future__ import annotations

import base64
import copy
import json
import sys
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs/demo/architect-exports"

DEFAULT_SRC = Path(
    "/Users/michael.debiase/Library/CloudStorage/OneDrive-GenesysTelecommunicationsLaboratories,Inc/Desktop/NY_Techshow_sept2026/sc12stuff/Dig_bot_nydol_v16-0.i3DigitalBotFlow"
)

EXIT_ID = "837542a7-02fa-4ab5-ad80-33a1925a16fe"
GREETING_STATE_ID = "b560bff7-4e13-4980-bf59-2eb74442b781"


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


def empty_str_value() -> dict:
    return {
        "config": {"emp": {"pos": 1, "text": "", "type": "str"}},
        "text": "",
        "type": "str",
        "uiMetaData": {"mode": 3},
        "metaData": {},
        "version": 2,
    }


def slim_flow(src: dict) -> dict:
    flow = copy.deepcopy(src)
    greeting = next(
        i for i in flow["flowSequenceItemList"] if i.get("id") == GREETING_STATE_ID
    )
    flow["flowSequenceItemList"] = [greeting]
    flow["initialSequence"] = GREETING_STATE_ID

    flow["description"] = (
        "NYS DOL Messenger — minimal virtual agent flow: greeting → DOL_Front_Door_miked → exit (sc12)"
    )
    flow["nextTrackingNumber"] = max(flow.get("nextTrackingNumber", 300), 260)

    # Drop legacy knowledge follow-up task (points at removed "legacy dol bot" task).
    ks = flow.get("knowledgeSettings") or {}
    ks.pop("knowledgeFollowupTaskId", None)
    ks.pop("knowledgeFollowupTaskName", None)
    ks.pop("knowledgeBaseId", None)
    ks.pop("knowledgeBaseName", None)
    flow["knowledgeSettings"] = ks

    ui = flow.setdefault("uiMetaData", {})
    ui["task"] = []
    manifest = ui.get("manifest") or flow.get("manifest") or {}
    for key in (
        "knowledgeBaseDocument",
        "dataAction",
        "knowledgeBase",
        "actionServiceActions",
    ):
        if isinstance(manifest, dict) and key in manifest:
            manifest[key] = []
    if "bridgeServerActions" in ui:
        ui["bridgeServerActions"] = []
    if "knowledgeBases" in ui:
        ui["knowledgeBases"] = []

    actions = {a["id"]: a for a in greeting.get("actionList") or []}
    ava = next(
        a for a in greeting["actionList"] if a.get("__type") == "CallAgenticVirtualAgentAction"
    )
    communicate = actions.get("9c282de1-8cf3-49d3-ae68-c9a8a5a82631")

    # Remove Update Data and any Call Task; AVA → Exit (matches working EOHHS VA bot pattern).
    greeting["actionList"] = [
        a
        for a in greeting["actionList"]
        if a.get("__type")
        in ("ExitBotFlowAction", "CommunicateAction", "CallAgenticVirtualAgentAction")
    ]

    ava = next(
        a for a in greeting["actionList"] if a.get("__type") == "CallAgenticVirtualAgentAction"
    )
    ava["nextAction"] = EXIT_ID
    for path in ava.get("paths") or []:
        path["nextActionId"] = EXIT_ID

    # Outputs: only map claim fields; leave all other AVA outputs explicitly empty (mode 3).
    claim_targets = {
        "claim_lookup.0.number": "Flow.incnumber",
        "claim_lookup.0.incident_state": "Flow.incident_state",
    }
    var_by_name = {v["name"]: v["id"] for v in flow.get("variables", []) if v.get("name")}
    new_outputs = []
    for out in ava.get("outputs") or []:
        name = out.get("name")
        if name in claim_targets:
            target = claim_targets[name]
            vid = var_by_name.get(target)
            if vid:
                out = copy.deepcopy(out)
                out["value"] = {
                    "config": {
                        "ref": {"pos": 1, "text": target, "type": "str", "val": vid}
                    },
                    "text": target,
                    "type": "str",
                    "uiMetaData": {"mode": 2},
                    "metaData": {
                        "references": [
                            {
                                "id": vid,
                                "type": "str",
                                "isSysRef": False,
                                "name": target,
                            }
                        ]
                    },
                    "version": 2,
                }
            new_outputs.append(out)
        else:
            new_outputs.append({"name": name, "value": empty_str_value()})
    ava["outputs"] = new_outputs

    if communicate:
        communicate["nextAction"] = ava["id"]

    settings = flow.setdefault("botFlowSettings", {})
    settings["virtualAgentEnabled"] = True
    settings["agenticVirtualAgentEnabled"] = True

    return flow


def main() -> None:
    src_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src_path.is_file():
        raise SystemExit(f"Source not found: {src_path}")

    src = load_i3(src_path)
    (OUT_DIR / "Dig_bot_nydol_user_export.json").write_text(json.dumps(src, indent=2) + "\n")

    slim = slim_flow(src)
    json_out = OUT_DIR / "Dig_bot_nydol_v17_ava_minimal.json"
    i3_out = OUT_DIR / "Dig_bot_nydol_v17_ava_minimal.i3DigitalBotFlow"

    json_out.write_text(json.dumps(slim, indent=2) + "\n")
    save_i3(slim, i3_out)

    print("Source:", src_path)
    print("Wrote:", i3_out)
    print("Wrote:", json_out)
    print("States:", [i.get("name") for i in slim["flowSequenceItemList"]])
    ava = next(
        a
        for item in slim["flowSequenceItemList"]
        for a in item["actionList"]
        if a.get("__type") == "CallAgenticVirtualAgentAction"
    )
    mapped = [o["name"] for o in ava["outputs"] if o["value"]["uiMetaData"]["mode"] == 2]
    print("AVA mapped outputs:", mapped)


if __name__ == "__main__":
    main()
