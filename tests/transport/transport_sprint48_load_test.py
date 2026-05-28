"""
transport_sprint48_load_test.py — Load tests for Sprint 48 (Today button).

«Сегодня» triggers the same data load as the date step buttons.
NFR: p95 < 700 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events
from datetime import date

_nfr_failures: list[str] = []
TODAY = str(date.today())


class TodayButtonUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(5)
    def load_tasks_today(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": TODAY, "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (today btn reset)",
        )

    @task(3)
    def load_sts_today(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": TODAY},
            headers=self.default_headers,
            name="/available-sts (today btn reset)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/tasks (today btn reset)", "GET", 700),
        ("/available-sts (today btn reset)", "GET", 600),
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
        print("[NFR PASS] today-btn endpoints within NFR thresholds")
