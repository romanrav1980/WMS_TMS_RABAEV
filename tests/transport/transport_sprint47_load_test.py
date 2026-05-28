"""
transport_sprint47_load_test.py — Load tests for Sprint 47 (localStorage persistence).

localStorage reads happen at page init and writes happen on state change.
Both are synchronous browser-side operations (no network). Load profile
validates the initial data load that fires after state is restored.
NFR: p95 < 700 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []

RESTORED_DATE = "2026-05-28"


class LocalStorageRestoreUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(4)
    def load_tasks_restored_date(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": RESTORED_DATE, "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (localStorage restore)",
        )

    @task(3)
    def load_available_sts_restored_date(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": RESTORED_DATE},
            headers=self.default_headers,
            name="/available-sts (localStorage restore)",
        )

    @task(1)
    def load_clusters_restored(self):
        self.client.get(
            "/api/admin/transport/clusters",
            params={"stdate": RESTORED_DATE},
            headers=self.default_headers,
            name="/clusters (localStorage restore, clusters mode)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/tasks (localStorage restore)", "GET", 700),
        ("/available-sts (localStorage restore)", "GET", 600),
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
        print("[NFR PASS] localStorage restore load within NFR thresholds")
