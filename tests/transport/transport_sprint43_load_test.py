"""
transport_sprint43_load_test.py — Load tests for Sprint 43 (sortable trips table).

Sorting is client-side; the load profile matches the tasks GET endpoint.
NFR: p95 < 700 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class SortableTableUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(7)
    def load_tasks_for_sort(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (sortable table source)",
        )

    @task(2)
    def load_tasks_date_range(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-01", "date_to": "2026-05-31", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (sort, large date range)",
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
    endpoint = "/tasks (sortable table source)"
    entry = stats.entries.get((endpoint, "GET"))
    if entry is None:
        print("[NFR] WARNING: no stats for sort endpoint — skipping")
        return

    p95_ms = entry.get_response_time_percentile(0.95)
    err_rate = entry.fail_ratio * 100

    if p95_ms > 700:
        _nfr_failures.append(f"p95 {p95_ms:.0f}ms > 700ms")
    if err_rate > 1.0:
        _nfr_failures.append(f"err {err_rate:.1f}% > 1%")

    if _nfr_failures:
        print(f"[NFR FAIL] {'; '.join(_nfr_failures)}")
        environment.process_exit_code = 1
    else:
        print(f"[NFR PASS] p95={p95_ms:.0f}ms err={err_rate:.2f}%")
