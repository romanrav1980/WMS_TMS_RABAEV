"""
transport_sprint49_load_test.py — Load tests for Sprint 49 (dense mode).

Dense mode is purely a CSS class toggle; no API calls.
Load profile validates the available-sts endpoint for large datasets
that benefit most from dense mode.
NFR: p95 < 600 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class DenseModeUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(7)
    def load_available_sts_large(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28", "unassigned_only": "false"},
            headers=self.default_headers,
            name="/available-sts (dense mode, all STs)",
        )

    @task(2)
    def load_tasks(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28"},
            headers=self.default_headers,
            name="/tasks (dense mode context)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    endpoint = "/available-sts (dense mode, all STs)"
    entry = stats.entries.get((endpoint, "GET"))
    if entry is None:
        print("[NFR] WARNING: no stats — skipping")
        return

    p95_ms = entry.get_response_time_percentile(0.95)
    err_rate = entry.fail_ratio * 100

    if p95_ms > 600:
        _nfr_failures.append(f"p95 {p95_ms:.0f}ms > 600ms")
    if err_rate > 1.0:
        _nfr_failures.append(f"err {err_rate:.1f}% > 1%")

    if _nfr_failures:
        print(f"[NFR FAIL] {'; '.join(_nfr_failures)}")
        environment.process_exit_code = 1
    else:
        print(f"[NFR PASS] p95={p95_ms:.0f}ms err={err_rate:.2f}%")
