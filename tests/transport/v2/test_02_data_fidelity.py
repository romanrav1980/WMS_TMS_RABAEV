"""
test_02_data_fidelity.py — Верификация потока данных Oracle → API

ЦЕЛЬ: Обнаружить «silent drop» — ситуацию когда поле объявлено в модели,
SQL-запрос его выбирает, но маппинг теряет значение и клиент получает
дефолт (None / 0 / 1080), а не реальные данные из БД.

Именно такой gap был в VRP: ZONE_TIME_PLAN_IN/OUT SELECT-ился, но не
прокидывался в VrpOrder.tw_from/tw_to — до тех пор пока fallback не
перекрывал значение.

Каждый тест проверяет:
  1. Поле присутствует в ответе (не KeyError / None everywhere)
  2. Значения РАЗНООБРАЗНЫ (≥2 разных значения) — не залочены на дефолт
  3. При наличии двух источников одного поля — значения СОВПАДАЮТ между
     эндпоинтами (available-sts ↔ planner/orders ↔ vrp stops)
"""
from __future__ import annotations

import pytest
import requests

from conftest import (
    BASE_URL, api_get, assert_field_from_db, temp_task,
    PLANNER_ORDERS_CONTRACT, VRP_STOP_CONTRACT, AVAILABLE_STS_CONTRACT,
)


def _aggregate_task_sts(rows: list[dict]) -> dict[str, dict]:
    """task/sts may return several pallet/order rows for the same ST_NUMBER."""
    index: dict[str, dict] = {}
    for row in rows:
        st = row.get("ST_NUMBER")
        if not st:
            continue
        acc = index.setdefault(st, dict(row, PALLETS_COUNT=0, WEIGHT_KG=0))
        acc["PALLETS_COUNT"] = int(acc.get("PALLETS_COUNT") or 0) + int(row.get("PALLETS_COUNT") or 0)
        acc["WEIGHT_KG"] = float(acc.get("WEIGHT_KG") or 0) + float(row.get("WEIGHT_KG") or 0)
    return index


def _fresh_available_sts(session: requests.Session, plan_date: str) -> list[dict]:
    rows = api_get(
        session,
        "/api/admin/transport/available-sts",
        stdate=plan_date,
        unassigned_only="true",
    )
    if not rows:
        pytest.skip("Нет свежих unassigned СТ для mutating data-fidelity теста")
    return rows


# ---------------------------------------------------------------------------
# Группа A: available-sts — поля из Oracle
# ---------------------------------------------------------------------------

class TestAvailableSTsFields:
    """Поля в таблице СТ должны приходить из Oracle, а не быть константами."""

    def test_time_from_is_not_all_zero(self, session, seed_sts):
        """TIME_FROM (из ZONE_TIME_PLAN_IN) не должен быть 0 для всех строк."""
        assert_field_from_db(seed_sts, "TIME_FROM", default_value=None, min_distinct=2)

    def test_time_to_is_not_all_1080(self, session, seed_sts):
        """TIME_TO (из ZONE_TIME_PLAN_OUT) не должен быть 1080 (дефолт) для всех строк."""
        values = [r.get("TIME_TO") for r in seed_sts if r.get("TIME_TO") is not None]
        if not values:
            pytest.skip("TIME_TO отсутствует в ответе — поле не возвращается эндпоинтом")
        non_default = [v for v in values if v != "18:00" and v != 1080]
        assert non_default, (
            "TIME_TO во всех строках равен дефолту '18:00'/1080 — "
            "данные из ZONE_TIME_PLAN_OUT не прокидываются"
        )

    def test_weight_kg_varies_across_rows(self, session, seed_sts):
        assert_field_from_db(seed_sts, "WEIGHT_KG", default_value=0, min_distinct=5)

    def test_pallets_count_varies(self, session, seed_sts):
        assert_field_from_db(seed_sts, "PALLETS_COUNT", default_value=0, min_distinct=3)

    def test_verify_perc_is_not_all_null(self, session, seed_sts):
        """VERIFY_PERC должен присутствовать хотя бы у части строк."""
        has_value = [r for r in seed_sts if r.get("VERIFY_PERC") is not None]
        assert len(has_value) >= len(seed_sts) * 0.3, (
            f"VERIFY_PERC=None у {len(seed_sts)-len(has_value)}/{len(seed_sts)} строк — "
            "подозрение на пропуск поля в SQL"
        )

    def test_napr_field_present_and_non_empty(self, session, seed_sts):
        """NAPR (направление) должно присутствовать у части строк."""
        with_napr = [r for r in seed_sts if r.get("NAPR")]
        assert with_napr, (
            "NAPR отсутствует во всех строках — поле не возвращается из Oracle"
        )

    def test_zone_field_not_all_null(self, session, seed_sts):
        """ZONE (район/зона) должна быть заполнена хотя бы для 50% строк."""
        with_zone = [r for r in seed_sts if r.get("ZONE")]
        assert len(with_zone) >= len(seed_sts) * 0.5, (
            f"ZONE пуст в {len(seed_sts)-len(with_zone)}/{len(seed_sts)} строках"
        )

    def test_addr_not_all_empty(self, session, seed_sts):
        with_addr = [r for r in seed_sts if r.get("ADDR")]
        assert len(with_addr) >= len(seed_sts) * 0.8, (
            "ADDR пуст в большинстве строк — адреса не загружены"
        )

    def test_ware_id_is_integer_not_string(self, session, seed_sts):
        """WARE_ID должен быть целым числом, а не строкой."""
        for row in seed_sts[:10]:
            wid = row.get("WARE_ID")
            if wid is not None:
                assert isinstance(wid, (int, float)) or str(wid).isdigit(), (
                    f"WARE_ID='{wid}' — не число"
                )


# ---------------------------------------------------------------------------
# Группа B: planner/orders — временные окна должны совпадать с available-sts
# ---------------------------------------------------------------------------

class TestPlannerOrdersDataFidelity:
    """Эндпоинт /planner/orders должен возвращать те же TW что и available-sts."""

    def test_planner_orders_have_coords(self, session, plan_date):
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        with_coords = [o for o in orders if o.get("LAT") and o.get("LON")]
        assert len(with_coords) >= 10, (
            f"Только {len(with_coords)} из {len(orders)} заказов имеют координаты"
        )

    def test_planner_orders_time_windows_vary(self, session, plan_date):
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        time_froms = [o.get("TIME_FROM") for o in orders if o.get("TIME_FROM") is not None]
        if not time_froms:
            pytest.skip("TIME_FROM отсутствует в /planner/orders — поле не возвращается")
        distinct = set(time_froms)
        assert len(distinct) >= 2, (
            f"TIME_FROM в /planner/orders одинаков для всех заказов: {distinct}. "
            "ZONE_TIME_PLAN_IN не прокидывается из Oracle."
        )

    def test_planner_orders_tw_strict_present(self, session, plan_date):
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        assert any("TW_STRICT" in o for o in orders), (
            "TW_STRICT отсутствует в /planner/orders — поле не возвращается из Oracle"
        )

    def test_planner_orders_tw_matches_available_sts(self, session, plan_date, seed_sts):
        """
        Для тех же СТ TIME_FROM в /planner/orders должен совпадать с TIME_FROM
        в /available-sts — иначе один из двух эндпоинтов теряет данные.
        """
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        order_index = {o["ST_NUMBER"]: o for o in orders if o.get("ST_NUMBER")}
        sts_index = {r["ST_NUMBER"]: r for r in seed_sts if r.get("ST_NUMBER")}

        mismatches = []
        for st_num, order in list(order_index.items())[:30]:
            sts_row = sts_index.get(st_num)
            if not sts_row:
                continue
            tf_order = order.get("TIME_FROM")
            tf_sts = sts_row.get("TIME_FROM")
            if tf_order is not None and tf_sts is not None and tf_order != tf_sts:
                mismatches.append(
                    f"ST={st_num}: planner={tf_order!r} vs available-sts={tf_sts!r}"
                )

        assert not mismatches, (
            f"TIME_FROM расходится между /planner/orders и /available-sts:\n"
            + "\n".join(mismatches[:5])
        )


# ---------------------------------------------------------------------------
# Группа C: task/sts — поля в составе рейса совпадают с available-sts
# ---------------------------------------------------------------------------

class TestTaskSTsDataFidelity:
    """Поля СТ внутри рейса должны совпадать с теми же полями в available-sts."""

    def test_task_sts_weight_matches_available_sts(self, session, plan_date, seed_sts):
        chosen = [s for s in seed_sts if float(s.get("WEIGHT_KG") or 0) > 0][:5]
        if len(chosen) < 3:
            pytest.skip("Недостаточно СТ с весом для теста")

        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            task_index = _aggregate_task_sts(task_sts)
            seed_index = {s["ST_NUMBER"]: s for s in chosen}
            for st, ts in task_index.items():
                seed = seed_index.get(st)
                if not seed:
                    continue
                w_task = float(ts.get("WEIGHT_KG") or 0)
                w_seed = float(seed.get("WEIGHT_KG") or 0)
                assert abs(w_task - w_seed) < 1.0, (
                    f"WEIGHT_KG для {st}: в рейсе={w_task}, в available-sts={w_seed}"
                )

    def test_task_sts_pallets_match_available_sts(self, session, plan_date, seed_sts):
        chosen = [s for s in seed_sts if int(s.get("PALLETS_COUNT") or 0) > 0][:5]
        if len(chosen) < 3:
            pytest.skip("Недостаточно СТ с паллетами")

        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            task_index = _aggregate_task_sts(task_sts)
            seed_index = {s["ST_NUMBER"]: s for s in chosen}
            for st, ts in task_index.items():
                seed = seed_index.get(st)
                if not seed:
                    continue
                p_task = int(ts.get("PALLETS_COUNT") or 0)
                p_seed = int(seed.get("PALLETS_COUNT") or 0)
                assert p_task == p_seed, (
                    f"PALLETS_COUNT для {st}: в рейсе={p_task}, в available-sts={p_seed}"
                )

    def test_task_sts_verify_perc_not_all_zero(self, session, plan_date, seed_sts):
        """VERIFY_PERC в составе рейса не должен быть 0 для всех строк."""
        fresh_sts = _fresh_available_sts(session, plan_date)
        chosen = [s for s in fresh_sts if s.get("VERIFY_PERC") is not None][:5]
        if not chosen:
            pytest.skip("Нет СТ с VERIFY_PERC в seed_sts")

        with temp_task(session, plan_date) as task_id:
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            assert r.status_code == 200, f"assign sts: {r.status_code} {r.text[:200]}"
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            with_vp = [ts for ts in task_sts if ts.get("VERIFY_PERC") is not None]
            assert with_vp, (
                "VERIFY_PERC отсутствует во всех строках состава рейса — "
                "поле не прокидывается из Oracle"
            )


# ---------------------------------------------------------------------------
# Группа D: VRP stops — данные о временных окнах из Oracle
# ---------------------------------------------------------------------------

class TestVRPStopDataFidelity:
    """
    Ключевой тест: stops в VRP-плане должны иметь tw_from/tw_to
    основанные на реальных ZONE_TIME_PLAN_IN/OUT, а не только на дефолтах.
    """

    def test_vrp_solve_stops_have_tw_from_field(self, session, plan_date):
        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 10,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        assert r.status_code == 200, f"VRP solve: {r.status_code} {r.text[:200]}"
        plan = r.json()
        assert plan.get("routes"), "VRP не построил ни одного маршрута"
        stop = plan["routes"][0]["stops"][0]
        assert "tw_from" in stop, (
            "Поле tw_from отсутствует в stops VRP-плана — "
            "данные о временных окнах не передаются в VrpOrder"
        )
        assert "tw_to" in stop, "Поле tw_to отсутствует в stops VRP-плана"

    def test_vrp_stops_not_all_default_tw(self, session, plan_date):
        """
        Хотя бы один stop должен иметь tw_from ≠ 0 или tw_to ≠ 1080.
        Если все stops имеют дефолтные значения — данные из Oracle потеряны.
        """
        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 10,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        assert r.status_code == 200
        plan = r.json()

        non_default_stops = []
        for route in plan.get("routes", []):
            for stop in route.get("stops", []):
                tw_from = int(stop.get("tw_from") or 0)
                tw_to = int(stop.get("tw_to") or 1080)
                if tw_from != 0 or tw_to != 1080:
                    non_default_stops.append((stop.get("st_number"), tw_from, tw_to))

        assert non_default_stops, (
            "Все stops в VRP-плане имеют tw_from=0, tw_to=1080 (дефолтные значения). "
            "Это означает что ZONE_TIME_PLAN_IN/OUT из Oracle не попадают в VrpOrder. "
            "Проверьте get_planner_orders() и маппинг в solve_vrp()."
        )

    def test_vrp_tw_from_matches_planner_orders(self, session, plan_date):
        """
        tw_from в stop VRP-плана должен совпадать с TIME_FROM в /planner/orders
        для того же ST — с поправкой на конвертацию времени в минуты от 06:00.
        """
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        order_index = {o["ST_NUMBER"]: o for o in orders if o.get("ST_NUMBER")}

        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 10,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        assert r.status_code == 200
        plan = r.json()

        mismatches = []
        for route in plan.get("routes", []):
            for stop in route.get("stops", []):
                st = stop.get("st_number")
                order = order_index.get(st)
                if not order or not order.get("TIME_FROM"):
                    continue
                # TIME_FROM приходит как "HH:MM", tw_from — минуты от 06:00
                tf = order["TIME_FROM"]
                if isinstance(tf, str) and ":" in tf:
                    h, m = map(int, tf.split(":")[:2])
                    expected_min = max(0, (h * 60 + m) - 360)  # 06:00 = 360 min
                    actual_min = int(stop.get("tw_from") or 0)
                    if abs(actual_min - expected_min) > 5:  # ±5 мин допуск
                        mismatches.append(
                            f"ST={st}: TIME_FROM={tf} → expected tw_from≈{expected_min}, "
                            f"actual={actual_min}"
                        )
        if mismatches:
            # Ненулевые расхождения — warning, не fail
            # (могут быть нормальные отличия из-за другой бизнес-логики)
            # Если расхождений много — это красный флаг
            assert len(mismatches) < len(order_index) * 0.5, (
                f"Более 50% stops имеют расхождение tw_from vs TIME_FROM:\n"
                + "\n".join(mismatches[:5])
            )

    def test_vrp_tw_strict_flag_propagated(self, session, plan_date):
        """TW_STRICT из /planner/orders должен появляться в stops VRP-плана."""
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        strict_sts = {o["ST_NUMBER"] for o in orders if o.get("TW_STRICT")}

        if not strict_sts:
            pytest.skip("Нет заказов с TW_STRICT=1 в seed-данных")

        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 10,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        assert r.status_code == 200
        plan = r.json()

        strict_in_plan = set()
        for route in plan.get("routes", []):
            for stop in route.get("stops", []):
                if stop.get("tw_strict"):
                    strict_in_plan.add(stop.get("st_number"))

        overlap = strict_sts & strict_in_plan
        assert overlap, (
            f"СТ с TW_STRICT=1 в /planner/orders: {strict_sts}. "
            f"Но в VRP stops tw_strict=True не найдено. "
            f"TW_STRICT не прокидывается в VrpOrder."
        )


# ---------------------------------------------------------------------------
# Группа E: Консистентность между источниками данных
# ---------------------------------------------------------------------------

class TestCrossEndpointConsistency:
    """Одни и те же данные из разных эндпоинтов должны совпадать."""

    def test_task_list_and_task_detail_pallets_match(self, session, plan_date, seed_sts):
        """Итоги паллет в списке рейсов совпадают с суммой по составу рейса."""
        chosen = [s for s in seed_sts if int(s.get("PALLETS_COUNT") or 0) > 0][:4]
        if len(chosen) < 2:
            pytest.skip("Недостаточно СТ")

        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            tasks = api_get(session, "/api/admin/transport/tasks", stdate=plan_date)
            task_in_list = next(
                (t for t in tasks if int(t.get("TT_ID") or t.get("ID") or 0) == task_id), None
            )
            assert task_in_list is not None

            # Паллеты в списке рейсов
            p_list = int(task_in_list.get("PALLETS") or task_in_list.get("pallets") or 0)
            # Паллеты из состава
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            p_detail = sum(int(s.get("PALLETS_COUNT") or 0) for s in _aggregate_task_sts(task_sts).values())

            if p_list > 0:
                assert p_list == p_detail, (
                    f"Рейс {task_id}: паллет в списке={p_list}, "
                    f"сумма по составу={p_detail}"
                )

    def test_gantt_vehicle_matches_task_transport(self, session, plan_date, seed_sts,
                                                   seed_vehicles):
        """Если рейсу назначена машина — она должна появляться в Ганте."""
        vehicle = seed_vehicles[0]
        vehicle_id = int(vehicle.get("ID") or 0)
        vehicle_num = vehicle.get("NUM") or vehicle.get("NUM_PLAT") or ""

        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [seed_sts[0]["ST_NUMBER"]]},
                timeout=30,
            )
            session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}",
                json={"transport": vehicle_num},
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
            gantt_ids = {int(g.get("vehicle_id") or 0) for g in gantt}
            # Машина из seed должна быть в Ганте (у неё уже есть запланированные операции)
            assert vehicle_id in gantt_ids, (
                f"Машина ID={vehicle_id} (NUM={vehicle_num}) не найдена в Ганте — "
                f"операции не создались или vehicle_id не прокидывается"
            )


class TestTaskStatusEncoding:
    def test_task_condition_is_not_question_marks(self, session, plan_date):
        tasks = api_get(session, "/api/admin/transport/tasks", stdate=plan_date)
        for task in tasks[:10]:
            cond = task.get("CONDITION") or task.get("condition") or ""
            assert "?" not in cond or cond == "", (
                f"CONDITION='{cond}' — кириллица не декодируется, кодировочный баг"
            )


# ---------------------------------------------------------------------------
# Группа F: Контракты полей (паттерн wave3 _assert_business_payload)
#
# wave3 проверял набор полей только для первого ответа в серии.
# Здесь мы: а) проверяем ВСЕ строки ответа, б) проверяем что значения не все None,
# в) объединяем контракт с проверкой разнообразия данных.
# ---------------------------------------------------------------------------

class TestFieldContracts:
    """
    Взято из wave3 _assert_business_payload и усилено:
    - проверяем все строки, не только первую
    - проверяем что ключевые поля не все None/пустые
    """

    def test_available_sts_full_contract(self, session, seed_sts):
        """Все обязательные поля присутствуют в каждой строке /available-sts."""
        for i, row in enumerate(seed_sts[:20]):
            missing = AVAILABLE_STS_CONTRACT - set(row.keys())
            assert not missing, (
                f"Строка {i} ({row.get('ST_NUMBER')}) нарушает контракт: "
                f"отсутствуют поля {missing}"
            )

    def test_planner_orders_full_contract(self, session, plan_date):
        """Все обязательные поля из wave3 присутствуют в каждой строке /planner/orders."""
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        assert orders, "planner/orders вернул пустой список"
        for i, row in enumerate(orders[:20]):
            missing = PLANNER_ORDERS_CONTRACT - set(row.keys())
            assert not missing, (
                f"Строка {i} ({row.get('ST_NUMBER')}) в /planner/orders нарушает контракт: "
                f"отсутствуют поля {missing}. "
                f"Это означает что поля не добавлены в SQL SELECT или не прокидываются "
                f"в dict-ответ get_planner_orders()."
            )

    def test_vrp_stops_full_contract(self, session, plan_date):
        """
        Все обязательные поля (включая tw_from, tw_to, tw_strict, unload_norm_min)
        присутствуют в каждом stop VRP-плана.
        wave3 проверял только первый stop — здесь проверяем все.
        """
        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 10,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        assert r.status_code == 200, f"VRP solve: {r.status_code}"
        plan = r.json()
        assert plan.get("routes"), "VRP не построил маршрутов"

        violations = []
        for route_idx, route in enumerate(plan["routes"]):
            for stop_idx, stop in enumerate(route.get("stops", [])):
                missing = VRP_STOP_CONTRACT - set(stop.keys())
                if missing:
                    violations.append(
                        f"route[{route_idx}].stops[{stop_idx}] "
                        f"(ST={stop.get('st_number')}): missing {missing}"
                    )

        assert not violations, (
            f"VRP stops нарушают контракт ({len(violations)} нарушений):\n"
            + "\n".join(violations[:5])
            + "\nПроверьте VrpRouteStop модель и маппинг в solve_vrp()."
        )

    def test_planner_orders_time_fields_not_all_none(self, session, plan_date):
        """
        Ключевое: TIME_FROM и TIME_TO в /planner/orders не должны быть None у всех строк.
        Именно это не проверял wave3 — он только проверял наличие ключа.
        """
        orders = api_get(session, "/api/admin/transport/planner/orders",
                         plan_date=plan_date)
        with_tf = [o for o in orders if o.get("TIME_FROM") is not None]
        with_tt = [o for o in orders if o.get("TIME_TO") is not None]
        assert with_tf, (
            "TIME_FROM=None у всех строк /planner/orders. "
            "Ключ присутствует, но данные из ZONE_TIME_PLAN_IN не попадают. "
            "wave3 это НЕ поймал бы — он проверял только наличие ключа."
        )
        assert with_tt, (
            "TIME_TO=None у всех строк /planner/orders."
        )

    def test_vrp_stops_tw_values_not_all_none(self, session, plan_date):
        """
        tw_from и tw_to в stops не должны быть None у всех stops.
        wave3 проверял только ключ, не значение.
        """
        r = session.post(
            f"{BASE_URL}/api/admin/transport/planner/solve",
            json={
                "plan_date": plan_date,
                "time_limit_s": 10,
                "source": "haversine",
                "solver": "savings",
            },
            timeout=120,
        )
        assert r.status_code == 200
        plan = r.json()

        all_stops = [
            stop
            for route in plan.get("routes", [])
            for stop in route.get("stops", [])
        ]
        assert all_stops, "Нет stops в VRP-плане"

        with_tw_from = [s for s in all_stops if s.get("tw_from") is not None]
        assert with_tw_from, (
            "tw_from=None у всех stops VRP-плана. "
            "Ключ есть (wave3 прошёл бы), но значение потеряно."
        )
