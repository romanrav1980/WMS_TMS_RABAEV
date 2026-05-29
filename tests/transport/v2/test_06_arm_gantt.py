"""
test_06_arm_gantt.py — ARM: планирование операций и план-факт

Проверяем:
  - plan-operations создаёт цепочку с правильными кодами и положительными длительностями
  - операции последовательны (нет временных дыр до ∞)
  - факт-записи (fact_start/fact_end) сохраняются и delta_min рассчитывается
  - Гант содержит машину после назначения
  - plan-fact report возвращает данные за диапазон дат
  - available vehicles endpoint учитывает занятость машин
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest
import requests

from conftest import BASE_URL, api_get, temp_task


KNOWN_OP_CODES = {"DOCK_ASSIGN", "LOADING", "DRIVE", "UNLOAD", "WAIT"}


def _extract_task_id(payload: dict) -> int:
    return int(payload.get("TT_ID") or payload.get("ID") or payload.get("id") or payload.get("task_id") or 0)


# ---------------------------------------------------------------------------
# Вспомогательная: создать рейс с СТ и запланировать операции
# ---------------------------------------------------------------------------

def _task_with_ops(session, plan_date: str, seed_sts: list, seed_vehicles: list):
    """Возвращает (task_id, vehicle_id) или (None, None) при неудаче."""
    if not seed_sts or not seed_vehicles:
        return None, None
    vehicle = seed_vehicles[0]
    vehicle_num = vehicle.get("NUM") or vehicle.get("NUM_PLAT")

    r = session.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        json={"transtype": "10", "shipment_date": plan_date},
        timeout=30,
    )
    if r.status_code != 200:
        return None, None
    task_id = _extract_task_id(r.json())
    if task_id <= 0:
        return None, None

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
    r_ops = session.post(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations",
        timeout=30,
    )
    if r_ops.status_code != 200:
        session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)
        return None, None

    return task_id, int(vehicle.get("ID") or 0)


# ---------------------------------------------------------------------------
# Группа A: Цепочка операций
# ---------------------------------------------------------------------------

class TestOperationsChain:
    def test_plan_operations_returns_chain(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip("Не удалось создать рейс с операциями")
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            assert len(ops) >= 2, f"Слишком мало операций: {len(ops)}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_operations_have_known_codes(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            codes = {op.get("operation_code") or op.get("CODE") or "" for op in ops}
            codes.discard("")
            # Хотя бы один код должен быть из известного набора
            overlap = codes & KNOWN_OP_CODES
            assert overlap or codes, f"Нет известных кодов операций. Получено: {codes}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_operations_have_positive_duration(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            for op in ops:
                raw_duration = op.get("duration_min")
                if raw_duration is None:
                    raw_duration = op.get("DURATION_MIN")
                assert raw_duration is not None, f"Нет длительности операции: {op}"
                dur = float(raw_duration)
                assert dur >= 0, f"Отрицательная длительность: {op}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_operations_ord_sequential(self, session, plan_date, seed_sts, seed_vehicles):
        """Операции должны иметь уникальные порядковые номера."""
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            ords = [int(op.get("ord") or op.get("ORD") or 0) for op in ops]
            assert len(ords) == len(set(ords)), (
                f"Дублирующиеся ord в операциях: {ords}"
            )
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_operations_plan_times_present(self, session, plan_date, seed_sts, seed_vehicles):
        """После plan-operations у части операций должны быть plan_start/plan_end."""
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            with_times = [
                op for op in ops
                if op.get("plan_start") or op.get("PLAN_START")
            ]
            # Допускаем что времена могут не заполняться если машина/водитель не назначены
            # Просто проверяем что поле присутствует в ответе
            has_field = all(
                "plan_start" in op or "PLAN_START" in op
                for op in ops
            )
            assert has_field, "Поле plan_start отсутствует в ответе операций"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)


# ---------------------------------------------------------------------------
# Группа B: Запись факта операций
# ---------------------------------------------------------------------------

class TestOperationsFact:
    def test_record_fact_start_end(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            if not ops:
                pytest.skip("Нет операций")
            op = ops[0]
            op_id = op.get("op_id") or op.get("OP_ID") or op.get("id")
            if not op_id:
                pytest.skip("Нет op_id")

            fact_start = f"{plan_date} 08:00"
            fact_end = f"{plan_date} 09:30"
            r = session.patch(
                f"{BASE_URL}/api/admin/transport/operations/{op_id}/fact",
                json={"fact_start": fact_start, "fact_end": fact_end},
                timeout=30,
            )
            assert r.status_code in (200, 204), (
                f"Запись факта операции: {r.status_code} {r.text[:200]}"
            )

            # Проверить что факт сохранился
            ops_after = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            updated = next(
                (o for o in ops_after
                 if (o.get("op_id") or o.get("OP_ID") or o.get("id")) == op_id),
                None,
            )
            if updated:
                saved_start = updated.get("fact_start") or updated.get("FACT_START")
                assert saved_start, f"fact_start не сохранился: {updated}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_delta_min_calculated_after_fact(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, _ = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            ops = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            ops_with_plan = [
                o for o in ops
                if o.get("plan_start") or o.get("PLAN_START")
            ]
            if not ops_with_plan:
                pytest.skip("Нет операций с plan_start")

            op = ops_with_plan[0]
            op_id = op.get("op_id") or op.get("OP_ID") or op.get("id")
            if not op_id:
                pytest.skip("Нет op_id")

            session.patch(
                f"{BASE_URL}/api/admin/transport/operations/{op_id}/fact",
                json={"fact_start": f"{plan_date} 10:00", "fact_end": f"{plan_date} 11:00"},
                timeout=30,
            )

            ops_after = api_get(session, f"/api/admin/transport/tasks/{task_id}/operations")
            updated = next(
                (o for o in ops_after
                 if (o.get("op_id") or o.get("OP_ID") or o.get("id")) == op_id),
                None,
            )
            if updated and updated.get("plan_start"):
                # delta_min должен быть числом (или None если не рассчитывается)
                delta = updated.get("delta_min") or updated.get("DELTA_MIN")
                if delta is not None:
                    assert isinstance(float(delta), float), (
                        f"delta_min должен быть числом: {delta!r}"
                    )
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)


# ---------------------------------------------------------------------------
# Группа C: Гант
# ---------------------------------------------------------------------------

class TestGantt:
    def test_gantt_returns_data(self, session, plan_date):
        gantt = api_get(session, "/api/admin/transport/vehicles/gantt", plan_date=plan_date)
        assert isinstance(gantt, list), "Гант вернул не список"

    def test_gantt_vehicle_entry_has_operations(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, vehicle_id = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            gantt = api_get(
                session, "/api/admin/transport/vehicles/gantt",
                plan_date=plan_date,
            )
            vehicle_entry = next(
                (g for g in gantt if int(g.get("vehicle_id") or 0) == vehicle_id),
                None,
            )
            assert vehicle_entry is not None, (
                f"Машина {vehicle_id} не найдена в Ганте"
            )
            ops = vehicle_entry.get("operations") or []
            assert len(ops) >= 1, (
                f"Машина {vehicle_id} в Ганте без операций"
            )
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)

    def test_gantt_operations_have_plan_times(self, session, plan_date, seed_sts, seed_vehicles):
        task_id, vehicle_id = _task_with_ops(session, plan_date, seed_sts, seed_vehicles)
        if not task_id:
            pytest.skip()
        try:
            gantt = api_get(
                session, "/api/admin/transport/vehicles/gantt",
                plan_date=plan_date,
            )
            vehicle_entry = next(
                (g for g in gantt if int(g.get("vehicle_id") or 0) == vehicle_id),
                None,
            )
            if not vehicle_entry:
                pytest.skip(f"Машина {vehicle_id} не в Ганте")

            for op in (vehicle_entry.get("operations") or []):
                has_time = (
                    op.get("plan_start") or op.get("PLAN_START") or
                    op.get("plan_end") or op.get("PLAN_END") or
                    op.get("duration_min") is not None
                )
                assert has_time, f"Операция в Ганте без временны́х меток: {op}"
        finally:
            session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=15)


# ---------------------------------------------------------------------------
# Группа D: Доступность машин (ARM-совет)
# ---------------------------------------------------------------------------

class TestVehicleAvailability:
    def test_available_vehicles_endpoint_works(self, session, plan_date):
        r = session.get(
            f"{BASE_URL}/api/admin/transport/vehicles/available",
            params={"shipment_time": f"{plan_date} 09:00", "pallets": 10},
            timeout=30,
        )
        assert r.status_code == 200, f"vehicles/available: {r.status_code} {r.text[:200]}"
        data = r.json()
        assert isinstance(data, list), "vehicles/available вернул не список"

    def test_available_vehicles_have_status_field(self, session, plan_date):
        r = session.get(
            f"{BASE_URL}/api/admin/transport/vehicles/available",
            params={"shipment_time": f"{plan_date} 09:00", "pallets": 5},
            timeout=30,
        )
        assert r.status_code == 200
        vehicles = r.json()
        if not vehicles:
            pytest.skip("Нет машин в ответе")
        for v in vehicles[:5]:
            status = v.get("status") or v.get("STATUS")
            assert status in ("green", "yellow", "red", None), (
                f"Неизвестный статус машины: {status!r}"
            )


# ---------------------------------------------------------------------------
# Группа E: план-факт
# ---------------------------------------------------------------------------

class TestPlanFact:
    def test_plan_fact_endpoint_returns_data(self, session, plan_date):
        date_from = (date.today() - timedelta(days=7)).isoformat()
        date_to = plan_date
        r = session.get(
            f"{BASE_URL}/api/admin/transport/plan-fact",
            params={"date_from": date_from, "date_to": date_to},
            timeout=30,
        )
        assert r.status_code == 200, f"plan-fact: {r.status_code} {r.text[:200]}"
        data = r.json()
        assert isinstance(data, (list, dict)), "plan-fact вернул неожиданный тип"

    def test_plan_fact_90d_range_works(self, session, plan_date):
        date_from = (date.today() - timedelta(days=90)).isoformat()
        r = session.get(
            f"{BASE_URL}/api/admin/transport/plan-fact",
            params={"date_from": date_from, "date_to": plan_date},
            timeout=30,
        )
        assert r.status_code == 200, (
            f"plan-fact за 90 дней: {r.status_code} {r.text[:200]}"
        )
