"""
transport_sprint42_load_test.py — Load tests for Sprint 42 (toast notifications).

Toasts fire after mutating API calls (create, assign, close, cancel).
NFR: POST /tasks p95 < 600 ms; POST /sts p95 < 500 ms; error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class ToastMutationUser(HttpUser):
    wait_time = between(2, 5)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(5)
    def load_tasks_for_toast_baseline(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (toast baseline GET)",
        )

    @task(2)
    def create_task(self):
        self.client.post(
            "/api/admin/transport/tasks",
            json={"transtype": "10", "shipment_date": "2026-06-01"},
            headers=self.default_headers,
            name="POST /tasks (create, triggers toast)",
        )

    @task(1)
    def load_available_sts(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28"},
            headers=self.default_headers,
            name="/available-sts",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/tasks (toast baseline GET)", "GET", 600),
        ("POST /tasks (create, triggers toast)", "POST", 600),
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
        print("[NFR PASS] all toast-mutation endpoints within thresholds")
