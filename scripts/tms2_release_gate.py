from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
SPRINT_60_95 = [ROOT / "tests" / "transport" / f"test_sprint{i}_functional.py" for i in range(60, 96)]
CORE_TESTS = [
    ROOT / "tests" / "transport" / "test_release_acceptance_docs.py",
    ROOT / "tests" / "transport" / "test_routing_infrastructure.py",
    ROOT / "tests" / "transport" / "test_frontend_virtualization_nfr.py",
]
PHASE3_TESTS = [
    ROOT / "tests" / "transport" / "test_sprint96_functional.py",
    ROOT / "tests" / "transport" / "test_sprint97_98_functional.py",
    ROOT / "tests" / "transport" / "test_sprint99_100_functional.py",
    ROOT / "tests" / "transport" / "test_sprint101_102_functional.py",
]


def run(command: list[str], *, env: dict[str, str] | None = None, cwd: Path = ROOT) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def routing_smoke(skip_live: bool) -> None:
    for file_name in ("docker-compose.osrm.yml", "docker-compose.valhalla.yml"):
        path = ROOT / file_name
        if not path.exists():
            raise SystemExit(f"missing routing compose file: {file_name}")
    if skip_live:
        print("Routing live smoke skipped by flag; compose files are present.")
        return
    probes = [
        "http://127.0.0.1:5000/route/v1/driving/60.5975,56.8389;60.6122,56.8519?overview=false",
        "http://127.0.0.1:8002/status",
    ]
    for url in probes:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Routing probe OK: {url} -> {response.status_code}")


def sprint_load_scripts(sprints: range) -> list[Path]:
    return [ROOT / "tests" / "transport" / f"transport_sprint{i}_load_test.py" for i in sprints]


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-platform TMS-2 release/regression gate.")
    parser.add_argument("--seed-date", default="2026-05-25")
    parser.add_argument("--skip-live-routing", action="store_true")
    parser.add_argument("--include-phase3", action="store_true")
    parser.add_argument("--include-ui-smoke", action="store_true")
    parser.add_argument("--include-load-smoke", action="store_true")
    parser.add_argument("--include-mutating-vrp-apply", action="store_true")
    args = parser.parse_args()

    env = os.environ.copy()
    env["TMS_SPRINT1_STDATE"] = args.seed_date
    env["TMS_SPRINT2_STDATE"] = args.seed_date
    env["TMS_SPRINT3_STDATE"] = args.seed_date
    env["TMS_SPRINT8_DATE"] = args.seed_date
    env["TMS_SPRINT9_DATE"] = args.seed_date
    if args.include_mutating_vrp_apply:
        env["TMS_RUN_MUTATING_VRP_APPLY"] = "1"
    else:
        env.pop("TMS_RUN_MUTATING_VRP_APPLY", None)

    routing_smoke(args.skip_live_routing)

    tests = CORE_TESTS + SPRINT_60_95
    if args.include_phase3:
        tests += PHASE3_TESTS
    run([sys.executable, "-m", "pytest", *(str(path) for path in tests), "-q", "-ra", "--tb=short"], env=env)

    if args.include_load_smoke:
        for script in sprint_load_scripts(range(60, 96)):
            run([sys.executable, str(script)], env=env)

    if args.include_ui_smoke:
        run(["node", str(ROOT / "tests" / "ui" / "transport_sprint60_95_ui_smoke.cjs")], env=env)
        run(["node", str(ROOT / "tests" / "ui" / "transport_table_2000_nfr_smoke.cjs")], env=env)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
