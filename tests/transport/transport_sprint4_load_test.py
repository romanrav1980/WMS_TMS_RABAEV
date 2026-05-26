"""
transport_sprint4_load_test.py — Load tests for Sprint 4 transport dispatch endpoints.

Simulates 30 concurrent dispatchers performing read-heavy operations
(list tasks, list STs, get task STs) mixed with write operations
(patch task attributes, assign/unassign ST).

Targets from ТЗ §12 NFR:
  GET  /tasks             < 300 ms p95
  GET  /available-sts     < 500 ms p95
  GET  /tasks/{id}/sts    < 200 ms p95
  PATCH /tasks/{id}       < 400 ms p95

Usage:
    pip install requests
    python tests/transport/transport_sprint4_load_test.py --users=30 --duration=60
    python tests/transport/transport_sprint4_load_test.py --users=50 --duration=120 --base-url=http://prod:8088
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()

# NFR thresholds (ms) from ТЗ §12
NFR: dict[str, int] = {
    "GET /tasks":              300,
    "GET /available-sts":      500,
    "GET /tasks/{id}/sts":     200,
    "PATCH /tasks/{id}":       400,
    "POST /tasks":             600,
    "POST /tasks/{id}/cancel": 400,
}


# ---------------------------------------------------------------------------
# ApiClient
# ---------------------------------------------------------------------------

class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = AUTH
        self.session.headers["Content-Type"] = "application/json"

    def get(self, path: str, **kw: Any) -> tuple[int, float]:
        t0 = time.perf_counter()
        r = self.session.get(f"{self.base}{path}", **kw)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return r.status_code, elapsed_ms

    def post(self, path: str, body: Any = None) -> tuple[int, float, dict]:
        t0 = time.perf_counter()
        r = self.session.post(f"{self.base}{path}",
                              data=json.dumps(body) if body else None)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        data = {}
        try:
            data = r.json()
        except Exception:
            pass
        return r.status_code, elapsed_ms, data

    def patch(self, path: str, body: Any) -> tuple[int, float]:
        t0 = time.perf_counter()
        r = self.session.patch(f"{self.base}{path}", data=json.dumps(body))
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return r.status_code, elapsed_ms

    def delete(self, path: str) -> tuple[int, float]:
        t0 = time.perf_counter()
        r = self.session.delete(f"{self.base}{path}")
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return r.status_code, elapsed_ms


# ---------------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------------

class Collector:
    def __init__(self) -> None:
        self._data: dict[str, list[float]] = {}
        self._errors: dict[str, int] = {}

    def record(self, label: str, ms: float, ok: bool) -> None:
        self._data.setdefault(label, []).append(ms)
        if not ok:
            self._errors[label] = self._errors.get(label, 0) + 1

    def report(self) -> dict[str, dict[str, Any]]:
        out = {}
        for label, times in self._data.items():
            times_sorted = sorted(times)
            n = len(times_sorted)
            p50 = times_sorted[int(n * 0.50)]
            p95 = times_sorted[int(n * 0.95)]
            p99 = times_sorted[min(int(n * 0.99), n - 1)]
            nfr = NFR.get(label)
            out[label] = {
                "count":   n,
                "errors":  self._errors.get(label, 0),
                "mean_ms": round(statistics.mean(times), 1),
                "p50_ms":  round(p50, 1),
                "p95_ms":  round(p95, 1),
                "p99_ms":  round(p99, 1),
                "nfr_ms":  nfr,
                "nfr_ok":  (p95 <= nfr) if nfr else None,
            }
        return out


# ---------------------------------------------------------------------------
# Worker scenario: mixed read + write
# ---------------------------------------------------------------------------

def dispatcher_scenario(client: ApiClient, col: Collector, task_id: int | None,
                        available_st: str | None, iteration: int) -> None:
    """Simulates one dispatcher interaction cycle."""

    # 1. List tasks
    status, ms = client.get("/api/admin/transport/tasks",
                            params={"shipment_date": TOMORROW, "include_readiness": "true"})
    col.record("GET /tasks", ms, status == 200)

    # 2. List available STs
    status, ms = client.get("/api/admin/transport/available-sts",
                            params={"stdate": TOMORROW, "unassigned_only": "true"})
    col.record("GET /available-sts", ms, status == 200)

    if task_id is None:
        return

    # 3. Get task STs (composition panel)
    status, ms = client.get(f"/api/admin/transport/tasks/{task_id}/sts")
    col.record("GET /tasks/{id}/sts", ms, status == 200)

    # 4. Patch primechanie (simulate dispatcher typing note)
    status, ms = client.patch(f"/api/admin/transport/tasks/{task_id}",
                              {"primechanie": f"Load test iter {iteration}"})
    col.record("PATCH /tasks/{id}", ms, status == 200)

    # 5. Patch transtype (Sprint 4 new field)
    transtype = "10" if iteration % 2 == 0 else "15"
    status, ms = client.patch(f"/api/admin/transport/tasks/{task_id}",
                              {"transtype": transtype})
    col.record("PATCH /tasks/{id}", ms, status == 200)

    # 6. Patch shipment_date (Sprint 4 new field)
    new_date = (date.today() + timedelta(days=2)).isoformat()
    status, ms = client.patch(f"/api/admin/transport/tasks/{task_id}",
                              {"shipment_date": new_date})
    col.record("PATCH /tasks/{id}", ms, status == 200)


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------

def wait_for_api(base_url: str, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{base_url}/api/admin/transport/tasks",
                             auth=AUTH, timeout=5)
            if r.status_code < 500:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print(f"ERROR: API не ответил за {timeout}с на {base_url}", file=sys.stderr)
    sys.exit(1)


def create_test_task(base_url: str) -> int | None:
    try:
        r = requests.post(f"{base_url}/api/admin/transport/tasks",
                          auth=AUTH,
                          headers={"Content-Type": "application/json"},
                          json={"transtype": "10", "shipment_date": TOMORROW},
                          timeout=10)
        if r.status_code == 200:
            return r.json()["task_id"]
    except Exception as e:
        print(f"WARN: не удалось создать тест-рейс: {e}", file=sys.stderr)
    return None


def cleanup_test_task(base_url: str, task_id: int) -> None:
    try:
        requests.post(f"{base_url}/api/admin/transport/tasks/{task_id}/cancel",
                      auth=AUTH, timeout=10)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def run_load(base_url: str, users: int, duration: int) -> None:
    print(f"TMS Transport Sprint 4 — Load test")
    print(f"  API:      {base_url}")
    print(f"  Users:    {users}")
    print(f"  Duration: {duration}s")
    print()

    wait_for_api(base_url)
    task_id = create_test_task(base_url)
    if task_id:
        print(f"  Тест-рейс: #{task_id}")
    else:
        print("  WARN: без тест-рейса — только GET-сценарии")

    col = Collector()
    deadline = time.time() + duration
    iteration = 0

    def worker_loop() -> None:
        nonlocal iteration
        client = ApiClient(base_url)
        while time.time() < deadline:
            it = iteration
            iteration += 1
            dispatcher_scenario(client, col, task_id, None, it)

    with ThreadPoolExecutor(max_workers=users) as pool:
        futures = [pool.submit(worker_loop) for _ in range(users)]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"Worker error: {e}", file=sys.stderr)

    if task_id:
        cleanup_test_task(base_url, task_id)

    # Report
    report = col.report()
    total_req = sum(v["count"] for v in report.values())
    total_err = sum(v["errors"] for v in report.values())
    rps = total_req / duration

    print(f"\n{'Endpoint':<35} {'N':>5} {'Err':>4} {'Mean':>7} {'p50':>7} {'p95':>7} {'p99':>7} {'NFR':>6} {'OK':>4}")
    print("-" * 90)

    nfr_violations = 0
    for label, s in sorted(report.items()):
        nfr_str = f"{s['nfr_ms']}ms" if s["nfr_ms"] else "—"
        ok_str = "✅" if s["nfr_ok"] else ("❌" if s["nfr_ok"] is False else "—")
        if s["nfr_ok"] is False:
            nfr_violations += 1
        print(f"{label:<35} {s['count']:>5} {s['errors']:>4} "
              f"{s['mean_ms']:>6.0f}ms {s['p50_ms']:>6.0f}ms "
              f"{s['p95_ms']:>6.0f}ms {s['p99_ms']:>6.0f}ms "
              f"{nfr_str:>6} {ok_str:>4}")

    print("-" * 90)
    print(f"Total: {total_req} requests, {total_err} errors, {rps:.1f} rps")
    print()
    if nfr_violations:
        print(f"❌ NFR нарушено: {nfr_violations} эндпоинт(а). Требуется оптимизация.")
        sys.exit(1)
    else:
        print("✅ Все NFR соблюдены.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Transport Sprint 4 load test")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--users", type=int, default=30)
    p.add_argument("--duration", type=int, default=60, help="Длительность теста, сек")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_load(args.base_url, args.users, args.duration)
