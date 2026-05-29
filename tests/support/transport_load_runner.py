from __future__ import annotations

import concurrent.futures as cf
import os
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from support.project_config import local_config  # noqa: E402


BASE_URL = local_config().api_base_url
AUTH = ("admin", "admin123")
SEED_DATE = os.environ.get("TMS_TRANSPORT_LOAD_SEED_DATE", "2026-05-24")


@dataclass(frozen=True)
class EndpointCase:
    name: str
    path: str
    target_ms: float = 700
    requests: int = 24
    workers: int = 4
    ok_statuses: tuple[int, ...] = (200,)


def qs(**params: object) -> str:
    return urlencode({key: value for key, value in params.items() if value is not None})


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def request_once(case: EndpointCase) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.get(f"{BASE_URL}{case.path}", auth=AUTH, timeout=20)
        return (time.perf_counter() - started) * 1000, response.status_code, response.text[:160]
    except Exception as exc:  # noqa: BLE001
        return (time.perf_counter() - started) * 1000, 0, repr(exc)


def run_case(case: EndpointCase) -> bool:
    with cf.ThreadPoolExecutor(max_workers=case.workers) as pool:
        results = list(pool.map(lambda _: request_once(case), range(case.requests)))
    latencies = [elapsed for elapsed, _, _ in results]
    failures = [(status, body) for _, status, body in results if status not in case.ok_statuses]
    p95 = percentile(latencies, 95)
    avg = statistics.mean(latencies) if latencies else 0.0
    print(
        f"{case.name}: avg={avg:.1f}ms p95={p95:.1f}ms "
        f"target={case.target_ms:.0f}ms failures={len(failures)}"
    )
    if failures:
        print(f"  first failure: HTTP {failures[0][0]} {failures[0][1]}")
        return False
    if p95 > case.target_ms:
        print(f"  NFR FAIL: p95 {p95:.1f}ms > {case.target_ms:.0f}ms")
        return False
    return True


def discover_task_id(seed_date: str = SEED_DATE) -> int | None:
    response = requests.get(
        f"{BASE_URL}/api/admin/transport/tasks?{qs(shipment_date=seed_date, include_readiness='true')}",
        auth=AUTH,
        timeout=20,
    )
    response.raise_for_status()
    tasks = response.json()
    return int(tasks[0]["ID"]) if tasks else None


def dispatcher_read_cases(
    sprint: int,
    *,
    include_task_sts: bool = False,
    include_available_sts: bool = True,
    include_readiness: bool = True,
    seed_date: str = SEED_DATE,
) -> list[EndpointCase]:
    query = qs(shipment_date=seed_date, include_readiness="true" if include_readiness else None)
    cases = [
        EndpointCase(
            f"Sprint {sprint} GET /tasks",
            f"/api/admin/transport/tasks?{query}",
            700,
            24,
            4,
        )
    ]
    if include_available_sts:
        cases.append(
            EndpointCase(
                f"Sprint {sprint} GET /available-sts",
                f"/api/admin/transport/available-sts?{qs(stdate=seed_date)}",
                650,
                24,
                4,
            )
        )
    if include_task_sts:
        task_id = discover_task_id(seed_date)
        if task_id is not None:
            cases.insert(
                0,
                EndpointCase(
                    f"Sprint {sprint} GET /tasks/{{id}}/sts",
                    f"/api/admin/transport/tasks/{task_id}/sts",
                    450,
                    24,
                    4,
                ),
            )
    return cases


def run_read_gate(
    sprint: int,
    *,
    include_task_sts: bool = False,
    include_available_sts: bool = True,
    include_readiness: bool = True,
    seed_date: str = SEED_DATE,
) -> int:
    cases = dispatcher_read_cases(
        sprint,
        include_task_sts=include_task_sts,
        include_available_sts=include_available_sts,
        include_readiness=include_readiness,
        seed_date=seed_date,
    )
    ok = True
    for case in cases:
        request_once(case)
    for case in cases:
        ok = run_case(case) and ok
    return 0 if ok else 1
