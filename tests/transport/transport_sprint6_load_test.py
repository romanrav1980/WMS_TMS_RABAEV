"""
transport_sprint6_load_test.py — Load tests for Sprint 6.

Sprint 6 adds GET /sts/{st_number}/pallets — a read-only endpoint that joins
RRL_SBORKA_PALLETS and RRL_SBORKA_PALLET_ROWS.  The load profile simulates
dispatchers browsing pallet details for STs already loaded via available-sts.

NFR §12: GET /sts/{st}/pallets p95 ≤ 200ms (same bound as other ST endpoints).

Usage:
    python tests/transport/transport_sprint6_load_test.py --users=40 --duration=60
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")
TOMORROW = "2026-05-25"

NFR = {
    "GET /available-sts":         500,
    "GET /sts/{st}/pallets":      200,
    "GET /tasks":                 300,
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


_sample_sts: list[str] = []


def _fetch_sample_sts(base: str) -> None:
    global _sample_sts
    try:
        r = requests.get(
            f"{base}/api/admin/transport/available-sts",
            params={"stdate": TOMORROW, "unassigned_only": "false"},
            auth=AUTH, timeout=15,
        )
        rows = r.json() if r.status_code == 200 else []
        _sample_sts = [row["ST_NUMBER"] for row in rows[:20]]
    except Exception:
        _sample_sts = []


def sprint6_scenario(client: ApiClient, col: Collector, idx: int) -> None:
    # 1. List available STs (simulates dispatcher opening the tab)
    s, ms = client.get("/api/admin/transport/available-sts",
                       params={"stdate": TOMORROW, "unassigned_only": "false"})
    col.record("GET /available-sts", ms, s == 200)

    # 2. Fetch pallets for one of the pre-fetched STs
    if _sample_sts:
        st = _sample_sts[idx % len(_sample_sts)]
        s, ms = client.get(f"/api/admin/transport/sts/{requests.utils.quote(st, safe='')}/pallets")
        col.record("GET /sts/{st}/pallets", ms, s == 200)

    # 3. Task list (background refresh typical in dispatch view)
    s, ms = client.get("/api/admin/transport/tasks",
                       params={"shipment_date": TOMORROW, "include_readiness": "true"})
    col.record("GET /tasks", ms, s == 200)


def wait_for_api(base: str, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(
                f"{base}/api/admin/transport/tasks",
                auth=AUTH,
                params={"shipment_date": TOMORROW},
                timeout=5,
            )
            if r.status_code < 500:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print(f"ERROR: API не ответил за {timeout}с", file=sys.stderr)
    sys.exit(1)


def run(base_url: str, users: int, duration: int) -> None:
    print(f"TMS Transport Sprint 6 — Load test")
    print(f"  API: {base_url}  Users: {users}  Duration: {duration}s")
    wait_for_api(base_url)
    _fetch_sample_sts(base_url)
    print(f"  Sample STs: {len(_sample_sts)}")

    col = Collector()
    deadline = time.time() + duration
    counter = [0]

    def loop() -> None:
        client = ApiClient(base_url)
        while time.time() < deadline:
            idx = counter[0]
            counter[0] += 1
            sprint6_scenario(client, col, idx)

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
        ok_s  = "OK" if s["nfr_ok"] else ("FAIL" if s["nfr_ok"] is False else "-")
        if s["nfr_ok"] is False:
            violations += 1
        print(f"{label:<38} {s['count']:>5} {s['errors']:>4} "
              f"{s['mean_ms']:>6.0f}ms {s['p50_ms']:>6.0f}ms "
              f"{s['p95_ms']:>6.0f}ms {nfr_s:>6} {ok_s:>4}")

    print("-" * 85)
    print(f"Total: {total} requests, {errs} errors, {rps:.1f} rps")
    if violations:
        print(f"NFR FAILED: {violations}. Add/check IDX_SP_ST_NUMBER.")
        sys.exit(1)
    else:
        print("All NFR checks passed.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--users", type=int, default=40)
    p.add_argument("--duration", type=int, default=60)
    return p.parse_args()


if __name__ == "__main__":
    a = parse_args()
    run(a.base_url, a.users, a.duration)
