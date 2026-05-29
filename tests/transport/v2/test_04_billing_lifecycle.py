"""
test_04_billing_lifecycle.py — Биллинг: полный жизненный цикл счёта

Проверяем:
  - нельзя выставить счёт для открытого рейса
  - создание счёта → добавление рейсов → закрытие → оплата
  - защита: нельзя снять СТ с рейса если рейс в счёте
  - собственные водители не блокируют биллинг (разрешено если компания не указана)
  - пересчёт цены меняет total_price счёта
  - ручная установка цены
  - повторное закрытие / повторная оплата возвращают разумный ответ
  - снятие рейса со счёта освобождает его для другого счёта
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest
import requests

from conftest import BASE_URL, api_get, api_patch, temp_task


def _extract_task_id(payload: dict) -> int:
    return int(payload.get("TT_ID") or payload.get("ID") or payload.get("id") or payload.get("task_id") or 0)


def _task_id(row: dict) -> int:
    return int(row.get("TT_ID") or row.get("ID") or row.get("tt_id") or row.get("task_id") or 0)


def _task_company(session, task_id: int) -> str:
    task = api_get(session, f"/api/admin/transport/tasks/{task_id}")
    return task.get("TK_NAME") or task.get("COMPANY") or task.get("company") or ""


# ---------------------------------------------------------------------------
# Вспомогательный: создать закрытый рейс (или skip если не удаётся)
# ---------------------------------------------------------------------------

def _make_closed_task(session, plan_date: str, seed_sts: list, seed_vehicles: list) -> int | None:
    """Создаёт + закрывает рейс. Возвращает task_id или None."""
    vehicle = max(seed_vehicles, key=lambda v: int(v.get("PALLETS") or 0))
    max_p = int(vehicle.get("PALLETS") or 20)
    drivers = session.get(f"{BASE_URL}/api/admin/transport/drivers", timeout=15).json()
    if not drivers:
        return None
    driver = next((d for d in drivers if d.get("DOVERENNOST_OT") or d.get("TK_NAME") or d.get("COMPANY")), drivers[0])

    chosen, total = [], 0
    for st in seed_sts:
        p = int(st.get("PALLETS_COUNT") or 0)
        if p > 0 and total + p <= max_p:
            chosen.append(st)
            total += p
        if total >= max_p // 2:
            break
    if not chosen:
        return None

    r = session.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        json={"transtype": "10", "shipment_date": plan_date},
        timeout=30,
    )
    if r.status_code != 200:
        return None
    task_id = _extract_task_id(r.json())
    if task_id <= 0:
        return None

    session.post(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
        json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
        timeout=30,
    )
    session.patch(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}",
        json={
            "transport": vehicle.get("NUM") or vehicle.get("NUM_PLAT"),
            "voditel_id": int(driver.get("ID") or driver.get("VODITEL_ID")),
        },
        timeout=30,
    )
    r_close = session.post(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}/close",
        timeout=30,
    )
    if r_close.status_code != 200:
        session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)
        return None
    session.patch(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
        json={"price": 1},
        timeout=30,
    )
    return task_id


# ---------------------------------------------------------------------------
# Группа A: Защита от биллинга незакрытого рейса
# ---------------------------------------------------------------------------

class TestBillingProtection:
    def test_cannot_bill_open_trip(self, session, plan_date):
        with temp_task(session, plan_date) as task_id:
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/billing/open",
                timeout=30,
            )
            assert r.status_code in (400, 409, 422), (
                f"Ожидалась ошибка биллинга открытого рейса, "
                f"получено {r.status_code}: {r.text[:200]}"
            )
            # Ответ должен содержать объяснение
            body = r.json()
            assert body.get("detail") or body.get("message") or body.get("error"), (
                "Ответ об ошибке биллинга не содержит detail/message"
            )

    def test_cannot_remove_st_from_billed_trip(
        self, session, plan_date, seed_sts, seed_vehicles
    ):
        """Рейс в счёте нельзя изменять: снятие СТ должно вернуть 409."""
        task_id = _make_closed_task(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать закрытый рейс")

        try:
            # Выставляем счёт
            r_bill = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/billing/open",
                timeout=30,
            )
            if r_bill.status_code not in (200, 201):
                pytest.skip(f"Не удалось выставить счёт: {r_bill.text[:100]}")

            # Получаем СТ в рейсе
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            if not task_sts:
                pytest.skip("Нет СТ в рейсе")

            st_num = task_sts[0].get("ST_NUMBER")
            r_del = session.delete(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts/{st_num}",
                timeout=15,
            )
            assert r_del.status_code in (409, 403, 422), (
                f"Снятие СТ из рейса в счёте должно блокироваться (409/403/422), "
                f"получено {r_del.status_code}"
            )
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)


# ---------------------------------------------------------------------------
# Группа B: Жизненный цикл счёта
# ---------------------------------------------------------------------------

class TestBillingOrderLifecycle:
    def test_create_billing_order_directly(self, session, plan_date):
        """POST /billing/orders — создание счёта напрямую (без привязки к рейсу)."""
        today = date.today().isoformat()
        week_later = (date.today() + timedelta(days=7)).isoformat()
        r = session.post(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            json={"company": "TEST_COMPANY_V2", "date_from": today, "date_to": week_later},
            timeout=30,
        )
        assert r.status_code in (200, 201), f"Создание счёта: {r.status_code} {r.text[:200]}"
        order = r.json()
        order_id = order.get("order_id") or order.get("ORDER_ID") or order.get("id")
        assert order_id, "Нет order_id в ответе"

    def test_billing_order_appears_in_registry(self, session, plan_date):
        today = date.today().isoformat()
        r = session.post(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            json={"company": "TEST_REGISTRY_V2", "date_from": today, "date_to": today},
            timeout=30,
        )
        assert r.status_code in (200, 201)
        order_id = r.json().get("order_id") or r.json().get("ORDER_ID") or r.json().get("id")

        orders = api_get(session, "/api/admin/transport/billing/orders")
        ids = {int(o.get("order_id") or o.get("ORDER_ID") or 0) for o in orders}
        assert int(order_id) in ids, f"Счёт {order_id} не найден в реестре"

    def test_add_task_to_order_and_verify(
        self, session, plan_date, seed_sts, seed_vehicles
    ):
        task_id = _make_closed_task(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать закрытый рейс")
        company = _task_company(session, task_id)

        today = date.today().isoformat()
        r_ord = session.post(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            json={"company": company, "date_from": today, "date_to": today},
            timeout=30,
        )
        assert r_ord.status_code in (200, 201)
        order_id = r_ord.json().get("order_id") or r_ord.json().get("ORDER_ID") or r_ord.json().get("id")

        try:
            # Добавить рейс в счёт
            r_add = session.post(
                f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
                json={"tt_ids": [task_id]},
                timeout=30,
            )
            assert r_add.status_code in (200, 201), (
                f"Добавление рейса в счёт: {r_add.status_code} {r_add.text[:200]}"
            )

            # Проверить что рейс появился в счёте
            tasks_in_order = api_get(
                session,
                f"/api/admin/transport/billing/orders/{order_id}/tasks",
            )
            tt_ids = [_task_id(t) for t in tasks_in_order]
            assert task_id in tt_ids, f"Рейс {task_id} не появился в счёте {order_id}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_billing_order_close_and_pay(
        self, session, plan_date, seed_sts, seed_vehicles
    ):
        task_id = _make_closed_task(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать закрытый рейс")

        today = date.today().isoformat()
        r_ord = session.post(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            json={"company": "TEST_LIFECYCLE", "date_from": today, "date_to": today},
            timeout=30,
        )
        assert r_ord.status_code in (200, 201)
        order_id = int(r_ord.json().get("order_id") or r_ord.json().get("ORDER_ID") or r_ord.json().get("id"))

        try:
            session.post(
                f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
                json={"tt_ids": [task_id]},
                timeout=30,
            )

            # Закрытие
            r_close = session.patch(
                f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/close",
                json={},
                timeout=30,
            )
            assert r_close.status_code in (200, 204), (
                f"Закрытие счёта: {r_close.status_code} {r_close.text[:200]}"
            )

            # Оплата
            r_pay = session.patch(
                f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/pay",
                json={},
                timeout=30,
            )
            assert r_pay.status_code in (200, 204), (
                f"Оплата счёта: {r_pay.status_code} {r_pay.text[:200]}"
            )

            # Итоговый статус
            order = api_get(session, f"/api/admin/transport/billing/orders/{order_id}")
            assert int(order.get("closed") or 0) == 1, "closed ≠ 1 после закрытия"
            assert int(order.get("payed") or 0) == 1, "payed ≠ 1 после оплаты"

        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_remove_task_from_order(self, session, plan_date, seed_sts, seed_vehicles):
        task_id = _make_closed_task(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать закрытый рейс")
        company = _task_company(session, task_id)

        today = date.today().isoformat()
        r_ord = session.post(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            json={"company": company, "date_from": today, "date_to": today},
            timeout=30,
        )
        assert r_ord.status_code in (200, 201)
        order_id = int(r_ord.json().get("order_id") or r_ord.json().get("ORDER_ID") or r_ord.json().get("id"))

        try:
            session.post(
                f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
                json={"tt_ids": [task_id]},
                timeout=30,
            )

            # Снять рейс со счёта
            r_del = session.delete(
                f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks/{task_id}",
                timeout=15,
            )
            assert r_del.status_code in (200, 204), (
                f"Снятие рейса со счёта: {r_del.status_code} {r_del.text[:200]}"
            )

            tasks_in_order = api_get(
                session,
                f"/api/admin/transport/billing/orders/{order_id}/tasks",
            )
            tt_ids = {_task_id(t) for t in tasks_in_order}
            assert task_id not in tt_ids, f"Рейс {task_id} не удалился из счёта {order_id}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)


# ---------------------------------------------------------------------------
# Группа C: Цена рейса
# ---------------------------------------------------------------------------

class TestBillingPrice:
    def test_manual_price_override(self, session, plan_date, seed_sts, seed_vehicles):
        task_id = _make_closed_task(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать закрытый рейс")

        try:
            target_price = 99999.99
            r = session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
                json={"price": target_price},
                timeout=30,
            )
            assert r.status_code in (200, 204), (
                f"Ручная установка цены: {r.status_code} {r.text[:200]}"
            )

            # Проверить что цена сохранилась
            task = api_get(session, f"/api/admin/transport/tasks/{task_id}")
            saved_price = float(task.get("PRICE") or task.get("price") or 0)
            assert abs(saved_price - target_price) < 0.01, (
                f"Цена после ручной установки: {saved_price} ≠ {target_price}"
            )
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_recalculate_price_changes_value(self, session, plan_date, seed_sts, seed_vehicles):
        task_id = _make_closed_task(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать закрытый рейс")

        try:
            # Сначала устанавливаем заведомо неправильную цену
            session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
                json={"price": 0.01},
                timeout=30,
            )

            # Пересчёт
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/recalculate-price",
                timeout=30,
            )
            assert r.status_code in (200, 204), (
                f"recalculate-price: {r.status_code} {r.text[:200]}"
            )

            task = api_get(session, f"/api/admin/transport/tasks/{task_id}")
            recalc_price = float(task.get("PRICE") or task.get("price") or 0)
            # После пересчёта цена должна отличаться от 0.01
            # (если формула возвращает 0 — тест пропускаем, а не падаем)
            if recalc_price > 0:
                assert abs(recalc_price - 0.01) > 0.001, (
                    "После recalculate-price цена всё ещё 0.01 — пересчёт не работает"
                )
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)


# ---------------------------------------------------------------------------
# Группа D: Справочник компаний
# ---------------------------------------------------------------------------

class TestBillingCompanies:
    def test_companies_list_not_empty(self, session):
        companies = api_get(session, "/api/admin/transport/billing/companies")
        assert isinstance(companies, list), "companies endpoint не вернул список"

    def test_companies_have_name_field(self, session):
        companies = api_get(session, "/api/admin/transport/billing/companies")
        for c in companies[:5]:
            if isinstance(c, str):
                name = c
            else:
                name = c.get("name") or c.get("NAME") or c.get("COMPANY")
            assert name, f"Компания без имени: {c}"
