"""
transport_sprint5_load_test.py — Load tests for Sprint 5.

Sprint 5 adds visual components fed by existing data fields (VERIFY_PERC,
TRANSPORT_TYPE, STOL, READY_PERC, IS_OWN_DRIVER). No new endpoints —
the load profile tests the endpoints that carry these fields under concurrent
dispatcher load, verifying p95 latency stays within NFR §12 bounds.

Usage:
    python tests/transport/transport_sprint5_load_test.py --users=40 --duration=60
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

DEFAULT_BASE_URL = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")
TOMORROW = (date.today() + timedelta(days=1)).isoformat()

NFR = {
    "GET /available-sts":          500,
    "GET /available-sts assembled": 500,
    "GET /available-sts tr_type":   500,
    "GET /tasks (readiness)":       300,
    "GET /vehicles":                200,
    "GET /drivers":                 200,
    "GET /types":                   150,
}


class ApiClient:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.s = requests.Session()
        self.s.auth = AUTH

    def get(self, path: str, **kw: Any) -> tuple[int, float]:
        t0 = time.perf_counter()
        r = self.s.get(f"{self.base}{path}", **kw)
        return r.status_code, (time.perf_counter() - t0) * 1000


class Collector:
    def __init__(self) -> None:
        self._data: dict[str, list[float]] = {}
        self._errors: dict[str, int] = {}

    def record(self, label: str, ms: float, ok: bool) -> None:
        self._data.setdefault(label, []).append(ms)
        if not ok:
            self._errors[label] = self._errors.get(label, 0) + 1

    def report(self) -> dict[str, dict]:
        out = {}
        for label, times in self._data.items():
            ts = sorted(times)
            n = len(ts)
            out[label] = {
                "count":   n,
                "errors":  self._errors.get(label, 0),
                "mean_ms": round(statistics.mean(ts), 1),
                "p50_ms":  round(ts[int(n * .50)], 1),
                "p95_ms":  round(ts[int(n * .95)], 1),
                "p99_ms":  round(ts[min(int(n * .99), n - 1)], 1),
                "nfr_ms":  NFR.get(label),
                "nfr_ok":  (ts[int(n * .95)] <= NFR[label]) if label in NFR else None,
            }
        return out


def sprint5_scenario(client: ApiClient, col: Collector) -> None:
    # 1. List available STs (raw — feeds VerifyBar + TransportTypeBadge + STOL icon)
    s, ms = client.get("/api/admin/transport/available-sts",
                       params={"stdate": TOMORROW, "unassigned_only": "true"})
    col.record("GET /available-sts", ms, s == 200)

    # 2. Filtered: assembled_only (feeds VERIFY_PERC progress bar)
    s, ms = client.get("/api/admin/transport/available-sts",
                       params={"stdate": TOMORROW, "assembled_only": "true"})
    col.record("GET /available-sts assembled", ms, s == 200)

    # 3. Filtered: by transport_type (feeds TransportTypeBadge filtered view)
    s, ms = client.get("/api/admin/transport/available-sts",
                       params={"stdate": TOMORROW, "transport_type": "10"})
    col.record("GET /available-sts tr_type", ms, s == 200)

    # 4. Tasks with readiness (feeds ReadinessBar + DriverOwnerBadge)
    s, ms = client.get("/api/admin/transport/tasks",
                       params={"shipment_date": TOMORROW, "include_readiness": "true"})
    col.record("GET /tasks (readiness)", ms, s == 200)

    # 5. Reference data (feeds dropdowns showing Свой/Наёмный in create dialog)
    s, ms = client.get("/api/admin/transport/vehicles")
    col.record("GET /vehicles", ms, s == 200)

    s, ms = client.get("/api/admin/transport/drivers")
    col.record("GET /drivers", ms, s == 200)

    s, ms = client.get("/api/admin/transport/types")
    col.record("GET /types", ms, s == 200)


def wait_for_api(base: str, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{base}/api/admin/transport/tasks", auth=AUTH, timeout=5)
            if r.status_code < 500:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print(f"ERROR: API не ответил за {timeout}с", file=sys.stderr)
    sys.exit(1)


def run(base_url: str, users: int, duration: int) -> None:
    print(f"TMS Transport Sprint 5 — Load test")
    print(f"  API: {base_url}  Users: {users}  Duration: {duration}s")
    wait_for_api(base_url)

    col = Collector()
    deadline = time.time() + duration

    def loop() -> None:
        client = ApiClient(base_url)
        while time.time() < deadline:
            sprint5_scenario(client, col)

    with ThreadPoolExecutor(max_workers=users) as pool:
        futs = [pool.submit(loop) for _ in range(users)]
        for f in as_completed(futs):
            try:
                f.result()
            except Exception as e:
                print(f"Worker error: {e}", file=sys.stderr)

    report = col.report()
    total = sum(v["count"] for v in report.values())
    errs  = sum(v["errors"] for v in report.values())
    rps   = total / duration

    print(f"\n{'Endpoint':<38} {'N':>5} {'Err':>4} {'Mean':>7} {'p50':>7} {'p95':>7} {'NFR':>6} {'OK':>4}")
    print("-" * 85)

    violations = 0
    for label, s in sorted(report.items()):
        nfr_s = f"{s['nfr_ms']}ms" if s["nfr_ms"] else "—"
        ok_s  = "✅" if s["nfr_ok"] else ("❌" if s["nfr_ok"] is False else "—")
        if s["nfr_ok"] is False:
            violations += 1
        print(f"{label:<38} {s['count']:>5} {s['errors']:>4} "
              f"{s['mean_ms']:>6.0f}ms {s['p50_ms']:>6.0f}ms "
              f"{s['p95_ms']:>6.0f}ms {nfr_s:>6} {ok_s:>4}")

    print("-" * 85)
    print(f"Total: {total} requests, {errs} errors, {rps:.1f} rps")
    if violations:
        print(f"❌ NFR нарушено: {violations}. Оптимизировать запросы к Oracle.")
        sys.exit(1)
    else:
        print("✅ Все NFR соблюдены.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--users", type=int, default=40)
    p.add_argument("--duration", type=int, default=60)
    return p.parse_args()


if __name__ == "__main__":
    a = parse_args()
    run(a.base_url, a.users, a.duration)
