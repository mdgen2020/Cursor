#!/Users/michael.debiase/.local/share/uv/tools/ava-mcp/bin/python3
"""Prepare, score, and open AVA evaluation runs from local test sets.

Scenario conversations (Cicero actor + rubric judge) are run by the Cursor
ava-scenario-runner subagent or the ava-evaluate skill. This script handles:

  dry-run    — projected Cicero call count
  prepare    — next eval-run-YYYY-MM-DD-NNN directory + manifest
  score      — generate scorecard from persisted attempt-*.json files
  open       — open scorecard.html in the default browser (macOS)

Examples:

  # DOL front door (defaults)
  ./scripts/run-dol-front-door-eval.sh dry-run

  ./scripts/run-ava-eval-test-set.py prepare \\
    --slug dol-front-door-miked \\
    --test-set dol-front-door-miked-suite

  # After Cursor/agent finishes all scenario-runners:
  ./scripts/run-ava-eval-test-set.py score \\
    --slug dol-front-door-miked \\
    --run-id eval-run-2026-09-17-002

  ./scripts/run-ava-eval-test-set.py open \\
    --slug dol-front-door-miked \\
    --run-id eval-run-2026-09-17-002
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AVA_MCP_SITE = Path.home() / ".local/share/uv/tools/ava-mcp/lib/python3.12/site-packages"
if AVA_MCP_SITE.is_dir():
    sys.path.insert(0, str(AVA_MCP_SITE))
sys.path.insert(0, str(ROOT / "scripts"))

from config import Config  # noqa: E402
from tools.eval import scorecard as scorecard_mod  # noqa: E402
from ava_eval_cicero_runner import run_scenario  # noqa: E402


def load_genesys_env() -> None:
    if os.environ.get("GENESYS_CLIENT_ID") and os.environ.get("GENESYS_CLIENT_SECRET"):
        return
    mcp_path = ROOT / ".cursor/mcp.json"
    if not mcp_path.is_file():
        return
    env = json.loads(mcp_path.read_text()).get("mcpServers", {}).get("ava-harness", {}).get("env", {})
    for key in ("GENESYS_CLIENT_ID", "GENESYS_CLIENT_SECRET", "AVA_HABITAT"):
        if key in env and not os.environ.get(key):
            os.environ[key] = env[key]


def lifecycle_dir(slug: str) -> Path:
    return ROOT / ".ava-lifecycle" / slug


def read_sage_agent(slug: str) -> dict:
    path = lifecycle_dir(slug) / "sage-agent.json"
    if not path.is_file():
        raise SystemExit(f"Missing {path} — run ava-build first.")
    return json.loads(path.read_text())


def read_test_set(slug: str, test_set_id: str) -> dict:
    path = lifecycle_dir(slug) / "test-sets" / f"{test_set_id}.json"
    if not path.is_file():
        raise SystemExit(f"Missing test set: {path}")
    return json.loads(path.read_text())


def load_scenario(slug: str, test_case_id: str) -> dict:
    path = lifecycle_dir(slug) / "test-cases" / f"{test_case_id}.json"
    if not path.is_file():
        raise SystemExit(f"Missing scenario: {path}")
    return json.loads(path.read_text())


def projected_cicero_calls(slug: str, test_set: dict) -> tuple[int, list[str]]:
    total = 0
    ids: list[str] = []
    for ref in test_set["test_cases"]:
        tid = ref["test_case_id"]
        ids.append(tid)
        sc = load_scenario(slug, tid)
        xe = sc["x_eval"]
        attempts = xe.get("attempts", 1)
        max_turns = xe.get("max_turns", 10)
        total += attempts * (max_turns + 2)
    return total, ids


def next_run_id(slug: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    runs_root = lifecycle_dir(slug) / "eval-runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    prefix = f"eval-run-{today}-"
    existing = sorted(p.name for p in runs_root.iterdir() if p.is_dir() and p.name.startswith(prefix))
    seq = 1
    for name in existing:
        try:
            n = int(name.split("-")[-1])
            seq = max(seq, n + 1)
        except ValueError:
            continue
    return f"{prefix}{seq:03d}"


def cmd_dry_run(args: argparse.Namespace) -> None:
    test_set = read_test_set(args.slug, args.test_set)
    total, ids = projected_cicero_calls(args.slug, test_set)
    sage = read_sage_agent(args.slug)
    version = args.version or sage.get("version") or sage.get("_meta", {}).get("gc_version")
    print(f"AVA: {sage.get('agent_name', args.slug)}")
    print(f"agent_id: {sage['_meta']['agent_id']}  version: {version}")
    print(f"test_set: {args.test_set}  scenarios: {len(ids)}")
    print(f"projected_cicero_calls: {total}")
    for tid in ids:
        print(f"  - {tid}")


def cmd_prepare(args: argparse.Namespace) -> None:
    test_set = read_test_set(args.slug, args.test_set)
    sage = read_sage_agent(args.slug)
    run_id = args.run_id or next_run_id(args.slug)
    run_dir = lifecycle_dir(args.slug) / "eval-runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    version = args.version or sage.get("version") or sage.get("_meta", {}).get("gc_version")
    _, case_ids = projected_cicero_calls(args.slug, test_set)
    manifest = {
        "run_id": run_id,
        "slug": args.slug,
        "test_set_id": args.test_set,
        "agent_id": sage["_meta"]["agent_id"],
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "test_case_ids": case_ids,
        "eval_run_dir": str(run_dir),
        "instructions": (
            "Run ava-scenario-runner once per test_case_id in Cursor (ava-evaluate skill), "
            "then: run-ava-eval-test-set.py score --slug ... --run-id ..."
        ),
    }
    (run_dir / "run-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    print(f"\nRun directory: {run_dir}")


async def cmd_score(args: argparse.Namespace) -> None:
    load_genesys_env()
    sage = read_sage_agent(args.slug)
    run_id = args.run_id
    if not run_id:
        raise SystemExit("--run-id is required for score")
    run_dir = lifecycle_dir(args.slug) / "eval-runs" / run_id
    if not run_dir.is_dir():
        raise SystemExit(f"Run directory not found: {run_dir}")
    version = args.version or sage.get("version") or sage.get("_meta", {}).get("gc_version")
    agent_id = sage["_meta"]["agent_id"]
    config = Config()
    result = await scorecard_mod.generate_scorecard(config, str(run_dir), agent_id, version)
    print(json.dumps(result, indent=2))


def cmd_open(args: argparse.Namespace) -> None:
    run_id = args.run_id
    if not run_id:
        raise SystemExit("--run-id is required for open")
    html = lifecycle_dir(args.slug) / "eval-runs" / run_id / "scorecard.html"
    if not html.is_file():
        raise SystemExit(f"No scorecard yet: {html}\nRun score first after scenario-runners finish.")
    if sys.platform == "darwin":
        subprocess.run(["open", str(html)], check=False)
    else:
        print(html)
    print(f"Opened: {html}")


def cmd_cursor_prompt(args: argparse.Namespace) -> None:
    """Print a prompt you can paste into Cursor Agent to run all scenarios."""
    test_set = read_test_set(args.slug, args.test_set)
    sage = read_sage_agent(args.slug)
    run_id = args.run_id or next_run_id(args.slug)
    version = args.version or sage.get("version") or sage.get("_meta", {}).get("gc_version")
    cases = [r["test_case_id"] for r in test_set["test_cases"]]
    lines = [
        f"Run full AVA evaluation for {args.slug}.",
        f"Test set: {args.test_set}",
        f"Run ID: {run_id}",
        f"Version: {version}",
        f"Repository: {ROOT}",
        "",
        "For each test_case_id, launch ava-scenario-runner with the scenario JSON under:",
        f"  {lifecycle_dir(args.slug) / 'test-cases'}/<id>.json",
        f"Persist attempts under:",
        f"  {lifecycle_dir(args.slug) / 'eval-runs' / run_id}/<id>/",
        "",
        "Test cases:",
        *[f"  - {c}" for c in cases],
        "",
        "When all finish, call generate_scorecard once, then summarize scorecard.md.",
    ]
    print("\n".join(lines))


async def cmd_run(args: argparse.Namespace) -> None:
    load_genesys_env()
    sage = read_sage_agent(args.slug)
    test_set = read_test_set(args.slug, args.test_set)
    run_id = args.run_id or next_run_id(args.slug)
    run_dir = lifecycle_dir(args.slug) / "eval-runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    version = args.version or sage.get("version") or sage.get("_meta", {}).get("gc_version")
    agent_id = sage["_meta"]["agent_id"]
    only = set(args.only.split(",")) if args.only else None
    config = Config()

    for ref in test_set["test_cases"]:
        tid = ref["test_case_id"]
        if only and tid not in only:
            continue
        scenario = load_scenario(args.slug, tid)
        out = run_dir / tid / "attempt-1.json"
        print(f"Running {tid} -> {out} ...", flush=True)
        await run_scenario(
            config,
            agent_id=agent_id,
            version=version,
            language=scenario.get("language", "en-US"),
            scenario=scenario,
            out_path=out,
        )
        print(f"  done ended={json.loads(out.read_text())['ended']}", flush=True)
        await asyncio.sleep(5)

    print(f"\nRun complete: {run_dir}")
    if args.score_after:
        result = await scorecard_mod.generate_scorecard(config, str(run_dir), agent_id, version)
        print(json.dumps(result["summary"], indent=2))
        print(result["htmlPath"])


def main() -> None:
    parser = argparse.ArgumentParser(description="AVA local test-set evaluation helper")
    parser.add_argument("--slug", default="dol-front-door-miked")
    parser.add_argument("--test-set", default="dol-front-door-miked-suite")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--version", default=None, help="Override AVA version (default: sage-agent.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("dry-run", help="Project Cicero call count").set_defaults(func=cmd_dry_run)
    sub.add_parser("prepare", help="Create eval run dir + manifest").set_defaults(func=cmd_prepare)
    p_score = sub.add_parser("score", help="Generate scorecard from attempt files")
    p_score.add_argument("--run-id", required=True)
    p_score.set_defaults(func=lambda a: asyncio.run(cmd_score(a)))
    p_open = sub.add_parser("open", help="Open scorecard.html")
    p_open.add_argument("--run-id", required=True)
    p_open.set_defaults(func=cmd_open)
    sub.add_parser("cursor-prompt", help="Print Cursor agent prompt for full eval").set_defaults(
        func=cmd_cursor_prompt
    )
    p_run = sub.add_parser("run", help="Run all scenarios via Cicero (terminal, no subagent)")
    p_run.add_argument("--run-id", default=None)
    p_run.add_argument("--only", default=None, help="Comma-separated test_case_ids")
    p_run.add_argument("--score-after", action="store_true", help="Generate scorecard when done")
    p_run.set_defaults(func=lambda a: asyncio.run(cmd_run(a)))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
