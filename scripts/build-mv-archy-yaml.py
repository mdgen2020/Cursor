#!/usr/bin/env python3
"""Emit Archy YAML for MV voice wiring (source of truth for archy create/update/publish).

Also refreshes legacy .i3 exports via build-mv-greenfield-flows.py.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YAML_DIR = ROOT / "docs/demo/architect-exports/archy-yaml"
BOT_YAML = YAML_DIR / "miked_mv_VAbotflow_v1.yaml"
INBOUND_YAML = YAML_DIR / "miked_direct_to_queue_v5_mv.yaml"


def main() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/build-mv-greenfield-flows.py")],
        check=True,
    )
    print("Archy YAML (maintained for MCP / archy create):")
    print(" ", BOT_YAML)
    print(" ", INBOUND_YAML)
    print("\nValidate:")
    print(f"  archy validateYaml --file '{BOT_YAML}'")
    print(f"  archy validateYaml --file '{INBOUND_YAML}'")
    print("\nDeploy (bot first, then inbound update on existing flow name):")
    print(f"  archy create --file '{BOT_YAML}'")
    print(f"  archy publish --file '{BOT_YAML}'")
    print(f"  archy update --file '{INBOUND_YAML}'")
    print(f"  archy publish --file '{INBOUND_YAML}'")


if __name__ == "__main__":
    main()
