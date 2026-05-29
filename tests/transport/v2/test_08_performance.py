"""
test_08_performance.py — SLA и производительность запросов Oracle

Методология v2 (улучшение над v1):
  - v1: проверяет p95 среди N параллельных запросов → тестирует throughput
  - v2: дополнительно проверяет single-request latency → тестирует Oracle query time

Для каждого ключевого эндпоинта:
  1. THROUGHPUT: N параллельных запросов, p95 в пределах SLA
  2. ORACLE BASELINE: один последовательный запрос, измеряем время
     (если > порог — в выводе появляется WARN с рекомендацией индекса/хинта)

SLA пороги (ms):
  available_sts:   500   (тяжёлый JOIN, критичен)
  list_tasks:      300
  planner_orders:  300
  clusters:        200
  plan_metrics:    500
  billing_orders:  400
  plan_fact_90d:  2000   (агрегация за 90 дней)
  gantt:           500
"""
from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import requests

from conftest import (
    BASE_URL, AUTH, SLA,
    PLANNER_ORDERS_CONTRACT, VRP_STOP_CONTRACT, AVAILABLE_STS_CONTRACT,
    timed_get, timed_post,
)


# ---------------------------------------------------------------------------
# Вспомогательные
# ---------------------------------------------------------------------------

def _check_contract(body: str, contract: frozenset[str] | None,
                    errors: list[str], path: str) -> None:
    """
    Проверяет payload каждого ответа под нагрузкой — паттерн из wave3.
    Ловит ситуации когда поля пропадают под конкуренцией (pool exhaustion,
    connection reuse, partial response).
    """
    if not contract:
        return
    import json as _json
    try:
        data = _json.loads(body)
    except Exception:
        errors.append(f"JSON parse error: {body[:100]}")
        return
    # Для списков проверяем первую строку; для dict — саму структуру
    row = data[0] if isinstance(data, list) and data else data
    if isinstance(row, dict):
        missing = contract - set(row.keys())
        if missing:
            errors.append(f"{path} contract violation under load: missing {missing}")


def _parallel_get(session: requests.Session, path: str,
                  params: dict, n: int, workers: int,
                  contract: frozenset[str] | None = None) -> dict:
    """
    Запускает N параллельных GET, возвращает статистику (ms).
    contract: если передан — каждый ответ проверяется на наличие полей
    (паттерн из wave3 _assert_business_payload).
    """
    durations: list[float] = []
    errors: list[str] = []

    def _call():
        t0 = time.perf_counter()
        r = session.get(f"{BASE_URL}{path}", params=params, timeout=60)
        ms = (time.perf_counter() - t0) * 1000
        if r.status_code != 200:
            errors.append(f"HTTP {r.status_code}: {r.text[:80]}")
        elif contract:
            _check_contract(r.text, contract, errors, path)
        return ms

    with ThreadPoolExecutor(max_workers=workers) as pool:
        durations = list(pool.map(lambda _: _call(), range(n)))

    p95 = statistics.quantiles(durations, n=100)[94] if len(durations) >= 20 else max(durations)
    return {
        "n": n,
        "errors": len(errors),
        "mean_ms": round(statistics.mean(durations), 1),
        "p95_ms": round(p95, 1),
        "max_ms": round(max(durations), 1),
    }


def _assert_sla(result: dict, sla_ms: int, name: str) -> None:
    assert not result["errors"], f"{name}: {result['errors']} ошибок из {result['n']} запросов"
    assert result["p95_ms"] <= sla_ms, (
        f"{name}: p95={result['p95_ms']:.0f}ms превышает SLA {sla_ms}ms. "
        f"mean={result['mean_ms']:.0f}ms, max={result['max_ms']:.0f}ms. "
        f"→ Проверьте EXPLAIN PLAN запроса, добавьте индекс или HINT."
    )


# ---------------------------------------------------------------------------
# Группа A: Таблица доступных СТ (самый тяжёлый запрос)
# ---------------------------------------------------------------------------

class TestAvailableSTsPerformance:
    def test_single_request_baseline(self, session, plan_date):
        """Один запрос — базовый Oracle latency без накладных расходов параллелизма."""
        _, ms = timed_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true",
        )
        sla = SLA["available_sts"]
        if ms > sla * 2:
            pytest.fail(
                f"available-sts single request: {ms:.0f}ms >> SLA {sla}ms. "
                f"Требуется оптимизация SQL (EXPLAIN PLAN, индексы на ST_DATE, TRANSTASK_ID)."
            )
        elif ms > sla:
            # Предупреждение — не падаем, но фиксируем
            pytest.warns(UserWarning, match="SLA")

    def test_throughput_p95_with_contract(self, session, plan_date):
        """
        Паттерн wave3: каждый из N параллельных ответов проверяется на наличие
        всех обязательных полей (в т.ч. VERIFY_PERC, TIME_FROM, TIME_TO).
        Ловит пропадание полей под конкурентной нагрузкой.
        """
        result = _parallel_get(
            session,
            "/api/admin/transport/available-sts",
            {"stdate": plan_date, "unassigned_only": "true"},
            n=20, workers=5,
            contract=AVAILABLE_STS_CONTRACT,
        )
        _assert_sla(result, SLA["available_sts"], "available-sts throughput+contract")

    def test_filtered_by_ware_is_faster_than_unfiltered(self, session, plan_date):
        """Запрос с фильтром по складу должен быть не медленнее полного запроса."""
        _, ms_full = timed_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true",
        )
        _, ms_filtered = timed_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true", ware_ids=9201,
        )
        # Фильтрованный запрос должен быть ≤ полному + 20% допуск
        assert ms_filtered <= ms_full * 1.2 + 100, (
            f"Фильтрованный запрос ({ms_filtered:.0f}ms) медленнее полного ({ms_full:.0f}ms). "
            f"Возможно нет индекса на WARE_ID или server-side filter не работает."
        )


# ---------------------------------------------------------------------------
# Группа B: Список рейсов
# ---------------------------------------------------------------------------

class TestTaskListPerformance:
    def test_single_request_baseline(self, session, plan_date):
        _, ms = timed_get(
            session, "/api/admin/transport/tasks",
            stdate=plan_date,
        )
        sla = SLA["list_tasks"]
        assert ms <= sla * 3, (
            f"list_tasks single request: {ms:.0f}ms >> SLA {sla}ms"
        )

    def test_throughput_p95(self, session, plan_date):
        result = _parallel_get(
            session, "/api/admin/transport/tasks",
            {"stdate": plan_date},
            n=30, workers=5,
        )
        _assert_sla(result, SLA["list_tasks"], "list_tasks throughput")


# ---------------------------------------------------------------------------
# Группа C: Планировщик / карта
# ---------------------------------------------------------------------------

class TestPlannerPerformance:
    def test_planner_orders_baseline(self, session, plan_date):
        _, ms = timed_get(
            session, "/api/admin/transport/planner/orders",
            plan_date=plan_date,
        )
        sla = SLA["planner_orders"]
        assert ms <= sla * 3, (
            f"planner/orders: {ms:.0f}ms >> SLA {sla}ms"
        )

    def test_planner_orders_throughput_with_contract(self, session, plan_date):
        """
        Паттерн wave3: все поля контракта (включая TIME_FROM/TIME_TO, VERIFY_PERC)
        должны присутствовать в каждом из параллельных ответов.
        """
        result = _parallel_get(
            session, "/api/admin/transport/planner/orders",
            {"plan_date": plan_date},
            n=20, workers=4,
            contract=PLANNER_ORDERS_CONTRACT,
        )
        _assert_sla(result, SLA["planner_orders"], "planner/orders throughput+contract")

    def test_clusters_throughput(self, session, plan_date):
        result = _parallel_get(
            session, "/api/admin/transport/clusters",
            {"stdate": plan_date},
            n=30, workers=6,
        )
        _assert_sla(result, SLA["clusters"], "clusters throughput")

    def test_plan_metrics_throughput(self, session, plan_date):
        result = _parallel_get(
            session, "/api/admin/transport/planner/metrics",
            {"plan_date": plan_date},
            n=30, workers=5,
        )
        _assert_sla(result, SLA["plan_metrics"], "plan_metrics throughput")


# ---------------------------------------------------------------------------
# Группа D: VRP solve — SLA на полной задаче
# ---------------------------------------------------------------------------

class TestVRPSolvePerformance:
    def test_vrp_solve_within_time_limit(self, session, plan_date):
        """VRP solve с time_limit_s=15 должен завершиться за ≤20 сек полного RTT."""
        t0 = time.perf_counter()
        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 15,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200, f"VRP solve: {r.status_code}"
        assert elapsed_ms <= 20_000, (
            f"VRP solve RTT={elapsed_ms:.0f}ms > 20s при time_limit=15s. "
            f"Возможно узкое место в get_planner_orders() или matrix rebuild."
        )
        # Проверяем что solve_time_ms отражает реальное время
        plan = r.json()
        solve_ms = int(plan.get("solve_time_ms") or 0)
        if solve_ms > 0:
            assert solve_ms <= elapsed_ms + 1000, (
                f"solve_time_ms={solve_ms} > полного RTT {elapsed_ms:.0f}ms — некорректный замер"
            )

    def test_distance_matrix_rebuild_under_60s(self, session):
        """Перестройка матрицы расстояний (haversine) за <60 сек."""
        t0 = time.perf_counter()
        r = session.post(
            f"{BASE_URL}/api/admin/transport/distance-matrix/rebuild",
            params={"source": "haversine"},
            timeout=120,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200, f"Matrix rebuild: {r.status_code} {r.text[:200]}"
        assert elapsed_ms <= 60_000, (
            f"Matrix rebuild: {elapsed_ms:.0f}ms > 60s. "
            f"Адресов в БД может быть слишком много или запрос не оптимален."
        )


# ---------------------------------------------------------------------------
# Группа E: Биллинг
# ---------------------------------------------------------------------------

class TestBillingPerformance:
    def test_billing_orders_throughput(self, session):
        result = _parallel_get(
            session, "/api/admin/transport/billing/orders",
            {},
            n=20, workers=4,
        )
        _assert_sla(result, SLA["billing_orders"], "billing_orders throughput")


# ---------------------------------------------------------------------------
# Группа F: план-факт за 90 дней
# ---------------------------------------------------------------------------

class TestPlanFactPerformance:
    def test_plan_fact_90d_within_sla(self, session, plan_date):
        from datetime import date, timedelta
        date_from = (date.fromisoformat(plan_date) - timedelta(days=90)).isoformat()
        _, ms = timed_get(
            session, "/api/admin/transport/plan-fact",
            date_from=date_from, date_to=plan_date,
        )
        sla = SLA["plan_fact_90d"]
        assert ms <= sla, (
            f"plan-fact 90д: {ms:.0f}ms > SLA {sla}ms. "
            f"Добавьте индекс на TRANSPORT_TASK(STDATE) или ограничьте выборку."
        )


# ---------------------------------------------------------------------------
# Группа G: Гант
# ---------------------------------------------------------------------------

class TestGanttPerformance:
    def test_gantt_within_sla(self, session, plan_date):
        _, ms = timed_get(
            session, "/api/admin/transport/vehicles/gantt",
            plan_date=plan_date,
        )
        sla = SLA["gantt"]
        assert ms <= sla * 2, (
            f"gantt: {ms:.0f}ms > SLA {sla}ms. "
            f"Проверьте JOIN RRL_TT_OPERATIONS с TRANSPORT_TASK."
        )

    def test_gantt_throughput(self, session, plan_date):
        result = _parallel_get(
            session, "/api/admin/transport/vehicles/gantt",
            {"plan_date": plan_date},
            n=15, workers=3,
        )
        _assert_sla(result, SLA["gantt"], "gantt throughput")


# ---------------------------------------------------------------------------
# Группа H: Routing status (лёгкий)
# ---------------------------------------------------------------------------

class TestRoutingStatusPerformance:
    def test_routing_status_fast(self):
        with requests.Session() as fresh:
            fresh.auth = AUTH
            fresh.headers.update({"Content-Type": "application/json"})
            data, ms = timed_get(fresh, "/api/admin/transport/routing/status")
        assert data.get("active_provider") or data.get("provider"), (
            f"routing/status не вернул активный provider: {data}"
        )
        assert ms <= 200, f"routing/status: {ms:.0f}ms > 200ms — запрос слишком медленный"
