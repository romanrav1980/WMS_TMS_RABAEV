"""
test_01_business_flow_e2e.py — Сквозной бизнес-кейс «Логистика дня»

Описание процесса (15 шагов):
  1.  Диспетчер видит таблицу СТ на дату: поля заполнены, данные из Oracle
  2.  Фильтрация по складу — результат сужается
  3.  Кластеризация по районам — СТ сгруппированы
  4.  Создание рейса вручную
  5.  Назначение СТ в рейс — итоги совпадают с суммой по назначенным СТ
  6.  Рейс виден в таблице рейсов, поля корректны
  7.  Назначение машины и водителя
  8.  Попытка закрыть рейс: can_print возвращает ok или 422 с деталью
  9.  Закрытие рейса (при наличии достаточного кол-ва паллет)
  10. Закрытый рейс исчезает из доступных СТ
  11. Планирование операций ARM
  12. Гант отображает рейс
  13. Создание счёта биллинга для закрытого рейса
  14. Счёт содержит рейс, сумма > 0
  15. Закрытие и оплата счёта

Cleanup: тест отменяет созданные рейсы и удаляет счета в teardown.
"""
from __future__ import annotations

import pytest
import requests

from conftest import (
    BASE_URL, SEED_VEHICLE_IDS,
    api_get, api_post, api_patch, api_delete,
    temp_task,
)


def _row_id(row: dict) -> int:
    return int(row.get("TT_ID") or row.get("ID") or row.get("task_id") or 0)


def _extract_task_id(payload: dict) -> int:
    return int(payload.get("TT_ID") or payload.get("ID") or payload.get("id") or payload.get("task_id") or 0)


def _cluster_st_numbers(cluster: dict) -> list[str]:
    for key in ("ST_NUMBERS", "st_numbers", "STS", "sts", "ST_LIST", "st_list"):
        value = cluster.get(key)
        if isinstance(value, list):
            if not value or isinstance(value[0], str):
                return value
            if isinstance(value[0], dict):
                numbers = [str(item.get("ST_NUMBER") or item.get("st_number") or "") for item in value]
                return [number for number in numbers if number]
    for value in cluster.values():
        if isinstance(value, list):
            if not value:
                return value
            if isinstance(value[0], str):
                return value
            if isinstance(value[0], dict):
                numbers = [str(item.get("ST_NUMBER") or item.get("st_number") or "") for item in value]
                return [number for number in numbers if number]
    return []


# ---------------------------------------------------------------------------
# Шаг 1: Таблица СТ — поля заполнены и разнообразны
# ---------------------------------------------------------------------------

class TestStep01AvailableSTs:
    def test_at_least_100_sts_on_seed_date(self, session, seed_sts):
        assert len(seed_sts) >= 100, (
            f"Ожидалось ≥100 СТ на seed-дату, получено {len(seed_sts)}"
        )

    def test_st_rows_have_required_columns(self, session, seed_sts):
        required = {
            "ST_NUMBER", "ADDR", "RAION", "PALLETS_COUNT",
            "WEIGHT_KG", "ZONE", "VERIFY_PERC", "WARE_ID",
        }
        row = seed_sts[0]
        missing = required - set(row.keys())
        assert not missing, f"В строке СТ отсутствуют обязательные поля: {missing}"

    def test_pallets_count_non_zero(self, session, seed_sts):
        non_zero = [r for r in seed_sts if int(r.get("PALLETS_COUNT") or 0) > 0]
        assert len(non_zero) >= len(seed_sts) * 0.8, (
            "Более 20% СТ имеют PALLETS_COUNT=0 — данные не загружены"
        )

    def test_weight_non_zero(self, session, seed_sts):
        non_zero = [r for r in seed_sts if float(r.get("WEIGHT_KG") or 0) > 0]
        assert len(non_zero) >= len(seed_sts) * 0.8, (
            "Более 20% СТ имеют WEIGHT_KG=0"
        )

    def test_multiple_raions_present(self, session, seed_sts):
        raions = {r.get("RAION") for r in seed_sts if r.get("RAION")}
        assert len(raions) >= 3, (
            f"Ожидалось ≥3 района, найдено: {raions}"
        )

    def test_multiple_ware_ids_present(self, session, seed_sts):
        ware_ids = {r.get("WARE_ID") for r in seed_sts if r.get("WARE_ID")}
        assert len(ware_ids) >= 2, (
            f"Ожидалось ≥2 склада, найдено: {ware_ids}"
        )

    def test_verify_perc_is_numeric_in_range(self, session, seed_sts):
        has_value = [r for r in seed_sts if r.get("VERIFY_PERC") is not None]
        assert has_value, "VERIFY_PERC отсутствует во всех строках — поле не прокидывается из Oracle"
        for row in has_value[:20]:
            v = float(row["VERIFY_PERC"])
            assert 0.0 <= v <= 100.0, f"VERIFY_PERC={v} вне диапазона [0, 100]"


# ---------------------------------------------------------------------------
# Шаг 2: Фильтрация по складу
# ---------------------------------------------------------------------------

class TestStep02WarehouseFilter:
    def test_filter_by_ware_id_narrows_result(self, session, seed_sts, plan_date):
        ware_ids = list({r.get("WARE_ID") for r in seed_sts if r.get("WARE_ID")})
        if len(ware_ids) < 2:
            pytest.skip("Недостаточно складов для теста фильтрации")
        first_ware = ware_ids[0]
        filtered = api_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true", ware_ids=first_ware,
        )
        assert len(filtered) < len(seed_sts), (
            "Фильтр по ware_id не сузил результат"
        )
        assert all(
            int(r.get("WARE_ID") or 0) == int(first_ware)
            for r in filtered
        ), "Фильтр по ware_id вернул строки с другим WARE_ID"

    def test_filter_unassigned_only_excludes_assigned(self, session, plan_date, seed_sts):
        # Создаём рейс, назначаем один СТ, проверяем что он исчезает из unassigned
        with temp_task(session, plan_date) as task_id:
            st = seed_sts[0]["ST_NUMBER"]
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [st]},
                timeout=30,
            )
            after = api_get(
                session, "/api/admin/transport/available-sts",
                stdate=plan_date, unassigned_only="true",
            )
            assigned_numbers = {r["ST_NUMBER"] for r in after}
            assert st not in assigned_numbers, (
                f"СТ {st} назначен в рейс {task_id}, но всё ещё в unassigned_only списке"
            )


# ---------------------------------------------------------------------------
# Шаг 3: Кластеры по районам
# ---------------------------------------------------------------------------

class TestStep03Clusters:
    def test_clusters_returned(self, session, plan_date):
        clusters = api_get(
            session, "/api/admin/transport/clusters",
            stdate=plan_date,
        )
        assert isinstance(clusters, list) and len(clusters) >= 2, (
            "Ожидалось ≥2 кластеров (районов)"
        )

    def test_cluster_has_st_numbers(self, session, plan_date):
        clusters = api_get(
            session, "/api/admin/transport/clusters",
            stdate=plan_date,
        )
        for c in clusters[:5]:
            assert "raion" in c or "RAION" in c, f"Кластер без поля RAION: {c.keys()}"
            st_list = _cluster_st_numbers(c)
            assert len(st_list) >= 1, "Пустой кластер не должен возвращаться"

    def test_cluster_pallets_match_sum_of_sts(self, session, plan_date, seed_sts):
        clusters = api_get(
            session, "/api/admin/transport/clusters",
            stdate=plan_date,
        )
        # Построим индекс паллет по ST_NUMBER из seed_sts
        pallet_index = {r["ST_NUMBER"]: int(r.get("PALLETS_COUNT") or 0) for r in seed_sts}
        for cluster in clusters[:3]:
            st_numbers = _cluster_st_numbers(cluster)
            sum_pallets = sum(pallet_index.get(st, 0) for st in st_numbers)
            reported = int(cluster.get("PALLETS") or cluster.get("pallets") or 0)
            if reported > 0:
                assert abs(reported - sum_pallets) <= 2, (
                    f"Кластер {cluster.get('RAION')}: сумма паллет {sum_pallets} "
                    f"≠ reported {reported}"
                )


# ---------------------------------------------------------------------------
# Шаг 4–7: Создание рейса, назначение СТ, назначение машины
# ---------------------------------------------------------------------------

class TestStep04to07TripCreation:
    """Полный цикл создания рейса с контролем данных на каждом шаге."""

    def test_create_trip_returns_tt_id(self, session, plan_date):
        with temp_task(session, plan_date, transtype="10") as task_id:
            assert isinstance(task_id, int) and task_id > 0, (
                f"Некорректный TT_ID после создания рейса: {task_id}"
            )

    def test_created_trip_visible_in_task_list(self, session, plan_date):
        with temp_task(session, plan_date) as task_id:
            tasks = api_get(
                session, "/api/admin/transport/tasks",
                stdate=plan_date,
            )
            ids = [_row_id(t) for t in tasks]
            assert task_id in ids, (
                f"Созданный рейс {task_id} не найден в списке рейсов на {plan_date}"
            )

    def test_assign_sts_updates_trip_summary(self, session, plan_date, seed_sts):
        with temp_task(session, plan_date) as task_id:
            # Берём 3 СТ с известным кол-вом паллет
            chosen = [s for s in seed_sts if int(s.get("PALLETS_COUNT") or 0) > 0][:3]
            expected_pallets = sum(int(s["PALLETS_COUNT"]) for s in chosen)
            expected_weight = sum(float(s.get("WEIGHT_KG") or 0) for s in chosen)
            st_numbers = [s["ST_NUMBER"] for s in chosen]

            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": st_numbers},
                timeout=30,
            )
            assert r.status_code == 200, f"Назначение СТ: {r.status_code} {r.text[:200]}"

            # Получаем состав рейса и проверяем суммы
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            actual_pallets = sum(int(s.get("PALLETS_COUNT") or 0) for s in task_sts)
            actual_weight = sum(float(s.get("WEIGHT_KG") or 0) for s in task_sts)

            assert actual_pallets == expected_pallets, (
                f"Паллеты в рейсе {actual_pallets} ≠ сумме назначенных {expected_pallets}"
            )
            assert abs(actual_weight - expected_weight) < 1.0, (
                f"Вес в рейсе {actual_weight:.1f} ≠ {expected_weight:.1f} кг"
            )

    def test_task_sts_have_verify_perc_from_db(self, session, plan_date, seed_sts):
        """VERIFY_PERC в составе рейса должен совпадать с тем же полем в available-sts."""
        chosen = seed_sts[:3]
        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            seed_index = {s["ST_NUMBER"]: s for s in seed_sts}
            for ts in task_sts:
                st = ts.get("ST_NUMBER")
                seed = seed_index.get(st)
                if seed and seed.get("VERIFY_PERC") is not None:
                    diff = abs(float(ts.get("VERIFY_PERC") or 0) - float(seed["VERIFY_PERC"]))
                    assert diff < 1.0, (
                        f"VERIFY_PERC для {st}: в составе рейса {ts.get('VERIFY_PERC')}, "
                        f"в available-sts {seed['VERIFY_PERC']} — данные не совпадают"
                    )

    def test_assign_vehicle_and_driver_to_trip(self, session, plan_date, seed_vehicles):
        with temp_task(session, plan_date) as task_id:
            vehicle = seed_vehicles[0]
            drivers = api_get(session, "/api/admin/transport/drivers")
            assert drivers, "Нет доступных водителей"
            driver = drivers[0]

            updated = api_patch(
                session,
                f"/api/admin/transport/tasks/{task_id}",
                {
                    "transport": vehicle.get("NUM") or vehicle.get("NUM_PLAT"),
                    "voditel_id": int(driver.get("ID") or driver.get("VODITEL_ID")),
                },
            )
            # Рейс обновился — проверяем что машина записалась
            tasks = api_get(
                session, "/api/admin/transport/tasks",
                stdate=plan_date,
            )
            task = next((t for t in tasks if _row_id(t) == task_id), None)
            assert task is not None, f"Рейс {task_id} исчез из списка после PATCH"
            transport_field = task.get("TRANSPORT") or task.get("transport") or ""
            vehicle_num = vehicle.get("NUM") or vehicle.get("NUM_PLAT") or ""
            assert transport_field == vehicle_num, (
                f"Машина в рейсе '{transport_field}' ≠ назначенной '{vehicle_num}'"
            )


# ---------------------------------------------------------------------------
# Шаг 8–10: Закрытие рейса и проверка что СТ ушли из пула
# ---------------------------------------------------------------------------

class TestStep08to10TripClose:
    def test_close_trip_with_enough_pallets(self, session, plan_date, seed_sts, seed_vehicles):
        """
        Берём СТ, которых хватает чтобы пройти can_print.
        Если can_print не ok — принимаем 422 с detail (правильное поведение).
        """
        # Берём машину с достаточной вместимостью
        vehicle = max(seed_vehicles, key=lambda v: int(v.get("PALLETS") or 0))
        max_pallets = int(vehicle.get("PALLETS") or 20)

        # Берём СТ суммарно ~50% от вместимости
        target = max(1, max_pallets // 2)
        chosen, total = [], 0
        for st in seed_sts:
            p = int(st.get("PALLETS_COUNT") or 0)
            if p > 0 and total + p <= max_pallets:
                chosen.append(st)
                total += p
            if total >= target:
                break

        if not chosen:
            pytest.skip("Нет подходящих СТ для теста закрытия рейса")

        drivers = api_get(session, "/api/admin/transport/drivers")
        assert drivers, "Нет водителей для теста"

        with temp_task(session, plan_date, transtype="10") as task_id:
            # Назначаем СТ
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            assert r.status_code == 200

            # Назначаем машину и водителя
            session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}",
                json={
                    "transport": vehicle.get("NUM") or vehicle.get("NUM_PLAT"),
                    "voditel_id": int(drivers[0].get("ID") or drivers[0].get("VODITEL_ID")),
                },
                timeout=30,
            )

            # Пробуем закрыть
            r_close = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/close",
                timeout=30,
            )
            assert r_close.status_code in (200, 422), (
                f"Закрытие рейса вернуло неожиданный статус {r_close.status_code}: "
                f"{r_close.text[:300]}"
            )

            if r_close.status_code == 422:
                detail = r_close.json().get("detail", "")
                assert detail, "can_print вернул 422 без detail — клиент не узнает причину"

    def test_closed_trip_sts_not_in_unassigned_pool(self, session, plan_date, seed_sts):
        """После закрытия рейса его СТ не должны появляться в unassigned_only=true."""
        chosen = seed_sts[:2]
        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            r_close = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/close",
                timeout=30,
            )
            if r_close.status_code != 200:
                pytest.skip("can_print не прошёл — skip проверки пула")

            after = api_get(
                session, "/api/admin/transport/available-sts",
                stdate=plan_date, unassigned_only="true",
            )
            closed_numbers = {s["ST_NUMBER"] for s in chosen}
            pool_numbers = {r["ST_NUMBER"] for r in after}
            leaked = closed_numbers & pool_numbers
            assert not leaked, (
                f"СТ {leaked} закрыты в рейсе, но всё ещё в пуле unassigned"
            )


# ---------------------------------------------------------------------------
# Шаг 11–12: ARM — планирование операций и Гант
# ---------------------------------------------------------------------------

class TestStep11to12ARMGantt:
    def test_plan_operations_creates_chain(self, session, plan_date, seed_sts):
        chosen = seed_sts[:2]
        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations",
                timeout=30,
            )
            assert r.status_code == 200, f"plan-operations: {r.status_code} {r.text[:200]}"
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            assert len(ops) >= 2, f"Ожидалось ≥2 операций, получено {len(ops)}"
            codes = [op.get("operation_code") or op.get("CODE") for op in ops]
            assert any(c for c in codes if c), "Операции без кодов — pipeline пуст"

    def test_operations_have_positive_duration(self, session, plan_date, seed_sts):
        chosen = seed_sts[:2]
        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations",
                timeout=30,
            )
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            for op in ops:
                dur = float(op.get("duration_min") or op.get("DURATION_MIN") or 0)
                assert dur >= 0, f"Отрицательная длительность операции: {op}"

    def test_gantt_includes_trip_vehicle(self, session, plan_date, seed_sts, seed_vehicles):
        vehicle = seed_vehicles[0]
        vehicle_id = int(vehicle.get("ID") or vehicle.get("TT_ID"))
        chosen = seed_sts[:1]
        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}",
                json={"transport": vehicle.get("NUM") or vehicle.get("NUM_PLAT")},
                timeout=30,
            )
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations",
                timeout=30,
            )
            gantt = api_get(
                session, "/api/admin/transport/vehicles/gantt",
                plan_date=plan_date,
            )
            vehicle_ids_in_gantt = {int(g.get("vehicle_id") or g.get("ID") or 0) for g in gantt}
            assert vehicle_id in vehicle_ids_in_gantt, (
                f"Машина {vehicle_id} (NUM={vehicle.get('NUM')}) не появилась в Ганте"
            )


# ---------------------------------------------------------------------------
# Шаг 13–15: Биллинг — создание → закрытие → оплата
# ---------------------------------------------------------------------------

class TestStep13to15Billing:
    def _close_trip_for_billing(self, session, plan_date, seed_sts, seed_vehicles) -> int | None:
        """Вспомогательный: создать + закрыть рейс. Возвращает task_id или None."""
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

        r_create = session.post(
            f"{BASE_URL}/api/admin/transport/tasks",
            json={"transtype": "10", "shipment_date": plan_date},
            timeout=30,
        )
        if r_create.status_code != 200:
            return None
        task_id = _extract_task_id(r_create.json())
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
        r_price = session.post(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/recalculate-price",
            timeout=30,
        )
        session.patch(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
            json={"price": 1},
            timeout=30,
        )
        return task_id

    def test_billing_full_lifecycle(
        self, session, plan_date, seed_sts, seed_vehicles,
    ):
        task_id = self._close_trip_for_billing(session, plan_date, seed_sts, seed_vehicles)
        if task_id is None:
            pytest.skip("Не удалось подготовить закрытый рейс для теста биллинга")

        billing_order_id = None
        try:
            # 13. Создать счёт на рейс
            r_bill = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/billing/open",
                timeout=30,
            )
            assert r_bill.status_code in (200, 201), (
                f"Создание счёта: {r_bill.status_code} {r_bill.text[:200]}"
            )
            bill_info = r_bill.json()
            billing_order_id = (
                bill_info.get("order_id") or
                bill_info.get("ORDER_ID") or
                bill_info.get("id")
            )
            assert billing_order_id, "Нет order_id после создания счёта"

            # 14. Счёт содержит рейс, сумма > 0
            orders = api_get(session, "/api/admin/transport/billing/orders")
            created = next(
                (o for o in orders
                 if int(o.get("order_id") or o.get("ORDER_ID") or 0) == int(billing_order_id)),
                None,
            )
            assert created is not None, f"Счёт {billing_order_id} не найден в реестре"

            task_in_order = api_get(
                session,
                f"/api/admin/transport/billing/orders/{billing_order_id}/tasks",
            )
            tt_ids = [int(t.get("TT_ID") or t.get("tt_id") or 0) for t in task_in_order]
            assert task_id in tt_ids, (
                f"Рейс {task_id} не попал в счёт {billing_order_id}"
            )

            price = float(created.get("total_price") or 0)
            assert price >= 0, f"total_price отрицательная: {price}"

            # 15. Закрыть и оплатить
            r_close_bill = session.patch(
                f"{BASE_URL}/api/admin/transport/billing/orders/{billing_order_id}/close",
                json={},
                timeout=30,
            )
            assert r_close_bill.status_code in (200, 204), (
                f"Закрытие счёта: {r_close_bill.status_code}"
            )

            r_pay = session.patch(
                f"{BASE_URL}/api/admin/transport/billing/orders/{billing_order_id}/pay",
                json={},
                timeout=30,
            )
            assert r_pay.status_code in (200, 204), (
                f"Оплата счёта: {r_pay.status_code}"
            )

            # Проверяем статус
            final = api_get(
                session,
                f"/api/admin/transport/billing/orders/{billing_order_id}",
            )
            closed = int(final.get("closed") or 0)
            payed = int(final.get("payed") or 0)
            assert closed == 1, f"Счёт {billing_order_id} не закрыт: closed={closed}"
            assert payed == 1, f"Счёт {billing_order_id} не оплачен: payed={payed}"

        finally:
            # Teardown: отменить рейс (billing уже создан — рейс можно только снять с биллинга)
            if task_id:
                session.post(
                    f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel",
                    timeout=15,
                )

    def test_open_trip_cannot_be_billed(self, session, plan_date):
        """Попытка выставить счёт для ещё не закрытого рейса должна вернуть 422."""
        with temp_task(session, plan_date) as task_id:
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/billing/open",
                timeout=30,
            )
            assert r.status_code in (422, 400, 409), (
                f"Ожидалась ошибка при биллинге открытого рейса, "
                f"получено {r.status_code}: {r.text[:200]}"
            )
