"""
conftest.py — shared fixtures и helpers для TMS-2 v2 test suite.

Ключевые принципы v2:
  - каждый тест проверяет ДАННЫЕ, не только HTTP 200
  - seed-константы задают конкретные ожидаемые значения
  - тесты, создающие данные, убирают их за собой через yield-фикстуры
  - plan_date определяется динамически: первая дата, для которой есть seed-СТ
"""
from __future__ import annotations

import os
import time
from contextlib import contextmanager
from datetime import date, timedelta
from typing import Generator

import pytest
import requests

# ---------------------------------------------------------------------------
# Конфигурация из окружения
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")
_raw_auth = os.environ.get("TMS_AUTH", "admin:admin123").split(":", 1)
AUTH: tuple[str, str] = (_raw_auth[0], _raw_auth[1])

# Seed-данные: ID машин, складов, водителей из миграции 047_dobrotseny
SEED_VEHICLE_IDS: set[int] = set(range(9201, 9216))   # 15 машин
SEED_WARE_IDS: list[int] = [9201, 9202, 9203]         # 3 склада

# SLA пороги (ms) для performance-тестов
SLA = {
    "available_sts":      500,
    "list_tasks":         300,
    "planner_orders":     300,
    "clusters":           200,
    "plan_metrics":       500,
    "billing_orders":     400,
    "plan_fact_90d":     2000,
    "gantt":              500,
}

# ---------------------------------------------------------------------------
# Базовые фикстуры
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session() -> requests.Session:
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def plan_date(session: requests.Session) -> str:
    """Возвращает первую дату из следующих 7 дней, для которой есть ≥10 seed-СТ."""
    explicit = os.environ.get("TMS_PLAN_DATE") or os.environ.get("TMS_SEED_DATE")
    if explicit:
        r = session.get(
            f"{BASE_URL}/api/admin/transport/available-sts",
            params={"stdate": explicit, "unassigned_only": "true"},
            timeout=30,
        )
        if r.status_code == 200 and len(r.json()) >= 10:
            return explicit
        pytest.skip(f"Нет seed-СТ на явно заданную дату {explicit}")

    for delta in range(0, 8):
        d = (date.today() + timedelta(days=delta)).isoformat()
        r = session.get(
            f"{BASE_URL}/api/admin/transport/available-sts",
            params={"stdate": d, "unassigned_only": "true"},
            timeout=30,
        )
        if r.status_code == 200 and len(r.json()) >= 10:
            return d
    pytest.skip("Нет seed-СТ в ближайшие 7 дней — сначала примените миграцию 046/047")


@pytest.fixture(scope="session")
def seed_sts(session: requests.Session, plan_date: str) -> list[dict]:
    """Возвращает список всех доступных (нераспределённых) СТ на plan_date."""
    r = session.get(
        f"{BASE_URL}/api/admin/transport/available-sts",
        params={"stdate": plan_date, "unassigned_only": "true"},
        timeout=30,
    )
    assert r.status_code == 200
    sts = r.json()
    assert len(sts) >= 10, "Слишком мало seed-СТ для тестирования"
    return sts


@pytest.fixture(scope="session")
def seed_vehicles(session: requests.Session) -> list[dict]:
    """Возвращает список seed-машин (ID 9201–9215)."""
    r = session.get(f"{BASE_URL}/api/admin/transport/vehicles", timeout=15)
    assert r.status_code == 200
    return [v for v in r.json() if int(v.get("ID") or 0) in SEED_VEHICLE_IDS]


# ---------------------------------------------------------------------------
# Контрактные наборы полей (из wave3 _assert_business_payload + дополнения)
# Используются и в data-fidelity тестах, и в performance-тестах под нагрузкой.
# ---------------------------------------------------------------------------

# Поля которые ОБЯЗАНЫ присутствовать в каждой строке /planner/orders
PLANNER_ORDERS_CONTRACT: frozenset[str] = frozenset({
    "ST_NUMBER", "LAT", "LON",
    "PALLETS_COUNT", "WEIGHT_KG", "WARE_ID",
    "TRANSPORT_TYPE",
    "TIME_FROM", "TIME_TO",      # из ZONE_TIME_PLAN_IN/OUT — тот самый gap
    "UNLOAD_NORM_MIN",
    "VERIFY_PERC",
    "TW_STRICT",
})

# Поля которые ОБЯЗАНЫ присутствовать в каждом stops-объекте VRP-плана
VRP_STOP_CONTRACT: frozenset[str] = frozenset({
    "st_number", "lat", "lon",
    "pallets", "weight_kg", "ware_id",
    "tw_from", "tw_to",          # минуты от 06:00 — из ZONE_TIME_PLAN_IN/OUT
    "tw_strict",
    "unload_norm_min",
})

# Поля которые ОБЯЗАНЫ присутствовать в каждой строке /available-sts
AVAILABLE_STS_CONTRACT: frozenset[str] = frozenset({
    "ST_NUMBER", "ADDR", "RAION",
    "PALLETS_COUNT", "WEIGHT_KG", "WARE_ID",
    "VERIFY_PERC",
})

# ---------------------------------------------------------------------------
# Helpers: HTTP wrappers с коротким описанием ошибки
# ---------------------------------------------------------------------------

def api_get(session: requests.Session, path: str, **params) -> dict | list:
    r = session.get(f"{BASE_URL}{path}", params=params or None, timeout=30)
    assert r.status_code == 200, f"GET {path} → {r.status_code}: {r.text[:300]}"
    return r.json()


def api_post(session: requests.Session, path: str, body: dict | None = None,
             expected: int = 200) -> dict | list:
    r = session.post(f"{BASE_URL}{path}", json=body or {}, timeout=60)
    assert r.status_code == expected, f"POST {path} → {r.status_code}: {r.text[:300]}"
    return r.json()


def api_patch(session: requests.Session, path: str, body: dict,
              expected: int = 200) -> dict | list:
    r = session.patch(f"{BASE_URL}{path}", json=body, timeout=30)
    assert r.status_code == expected, f"PATCH {path} → {r.status_code}: {r.text[:300]}"
    return r.json()


def api_delete(session: requests.Session, path: str,
               expected: int = 200) -> int:
    r = session.delete(f"{BASE_URL}{path}", timeout=30)
    assert r.status_code == expected, f"DELETE {path} → {r.status_code}: {r.text[:300]}"
    return r.status_code


# ---------------------------------------------------------------------------
# Helpers: создание/удаление тестовых рейсов
# ---------------------------------------------------------------------------

@contextmanager
def temp_task(session: requests.Session, plan_date: str,
              transtype: str = "10") -> Generator[int, None, None]:
    """Создаёт рейс, передаёт его ID в блок with, затем отменяет."""
    body = {"transtype": transtype, "shipment_date": plan_date}
    r = session.post(f"{BASE_URL}/api/admin/transport/tasks", json=body, timeout=30)
    assert r.status_code == 200, f"Не удалось создать тестовый рейс: {r.text[:300]}"
    payload = r.json()
    task_id = int(payload.get("TT_ID") or payload.get("ID") or payload.get("id") or payload.get("task_id") or 0)
    assert task_id > 0, f"Создание рейса не вернуло TT_ID/ID: {payload!r}"
    try:
        yield task_id
    finally:
        # Попытка отмены — игнорируем ошибку если уже закрыт/отменён
        session.post(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel",
            timeout=15,
        )


# ---------------------------------------------------------------------------
# Helpers: измерение времени запроса
# ---------------------------------------------------------------------------

def timed_get(session: requests.Session, path: str, **params) -> tuple[dict | list, float]:
    """Возвращает (response_json, elapsed_ms)."""
    t0 = time.perf_counter()
    r = session.get(f"{BASE_URL}{path}", params=params or None, timeout=60)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert r.status_code == 200, f"GET {path} → {r.status_code}: {r.text[:200]}"
    return r.json(), elapsed_ms


def timed_post(session: requests.Session, path: str,
               body: dict | None = None, timeout: int = 120) -> tuple[dict | list, float]:
    """Возвращает (response_json, elapsed_ms)."""
    t0 = time.perf_counter()
    r = session.post(f"{BASE_URL}{path}", json=body or {}, timeout=timeout)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert r.status_code == 200, f"POST {path} → {r.status_code}: {r.text[:200]}"
    return r.json(), elapsed_ms


# ---------------------------------------------------------------------------
# Helpers: проверка данных
# ---------------------------------------------------------------------------

def assert_field_from_db(rows: list[dict], field: str, default_value,
                         min_distinct: int = 2, sample_size: int | None = None) -> None:
    """
    Проверяет, что поле field в rows НЕ является константой default_value для всех строк.
    Это детектирует «silent drop» — когда поле объявлено в модели, но всегда приходит как дефолт.

    min_distinct — минимальное число различных значений (кроме None).
    """
    subset = rows[:sample_size] if sample_size else rows
    values = [r.get(field) for r in subset if r.get(field) is not None]
    assert values, f"Поле '{field}' отсутствует или всегда None во всех {len(subset)} строках"

    non_default = [v for v in values if v != default_value]
    distinct = set(values)
    assert len(distinct) >= min_distinct, (
        f"Поле '{field}' имеет только {len(distinct)} различных значений {distinct!r}. "
        f"Подозрение: данные из БД не доходят, вместо них — дефолт {default_value!r}."
    )
    assert non_default, (
        f"Поле '{field}' всегда равно дефолту {default_value!r} — "
        f"данные из Oracle не прокидываются."
    )
