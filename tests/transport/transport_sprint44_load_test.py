"""
transport_sprint44_load_test.py — Load tests for Sprint 44 (Escape key handler).

Escape is a pure client-side event handler with no API calls.
Load profile validates the pages that Escape interactions touch.
NFR: p95 < 600 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class EscapeHandlerUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(5)
    def load_tasks(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (escape ctx)",
        )

    @task(3)
    def load_available_sts(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28"},
            headers=self.default_headers,
            name="/available-sts (escape ctx)",
        )

    @task(1)
    def load_clusters(self):
        self.client.get(
            "/api/admin/transport/clusters",
            params={"stdate": "2026-05-28"},
            headers=self.default_headers,
            name="/clusters (escape ctx)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/tasks (escape ctx)", "GET", 600),
        ("/available-sts (escape ctx)", "GET", 500),
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
        print("[NFR PASS] Escape handler pages within NFR thresholds")
