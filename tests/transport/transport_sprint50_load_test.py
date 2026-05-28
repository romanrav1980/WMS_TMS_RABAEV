"""
transport_sprint50_load_test.py — Load tests for Sprint 50 (ready-ST highlight).

The highlight reads VERIFY_PERC from already-loaded AvailableSt objects.
Load profile validates available-sts with verify data.
NFR: p95 < 600 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class ReadyHighlightUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(6)
    def load_available_sts_with_verify(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28", "assembled_only": "true"},
            headers=self.default_headers,
            name="/available-sts (assembled, ready-highlight)",
        )

    @task(3)
    def load_available_sts_all(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28"},
            headers=self.default_headers,
            name="/available-sts (all, ready-highlight)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/available-sts (assembled, ready-highlight)", "GET", 600),
        ("/available-sts (all, ready-highlight)", "GET", 600),
    ]
    for name, method, threshold_ms in checks:
        entry = stats.entries.get((name, method))
        if entry is None:
            continue
        p95_ms = entry.get_response_time_percentile(0.95)
        err_rate = entry.fail_ratio * 100
        if p95_ms > threshold_ms:
            _nfr_failures.append(f"{name} p95 {p95_ms:.0f}ms > {threshold_ms}ms")
        if err_rate > 1.0:
            _nfr_failures.append(f"{name} err {err_rate:.1f}% > 1%")

    if _nfr_failures:
        print(f"[NFR FAIL] {'; '.join(_nfr_failures)}")
        environment.process_exit_code = 1
    else:
        print("[NFR PASS] ready-highlight endpoints within NFR thresholds")
