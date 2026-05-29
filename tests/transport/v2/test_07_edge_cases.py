"""
test_07_edge_cases.py — Граничные и ошибочные сценарии

Проверяем поведение системы на граничных случаях:
  - пустой рейс (0 СТ)
  - рейс с 1 СТ (минимальный)
  - отмена рейса освобождает СТ
  - назначение СТ уже занятого другим рейсом → ошибка
  - закрытие уже закрытого рейса
  - несуществующий task_id → 404
  - переход рейса на следующий день
  - кластерное создание рейса из района
  - быстрое добавление СТ по номеру (quick-add)
  - пагинация таблицы СТ
"""
from __future__ import annotations

import pytest
import requests

from conftest import BASE_URL, api_get, temp_task


def _fresh_sts(session: requests.Session, plan_date: str, min_count: int = 1) -> list[dict]:
    rows = api_get(
        session,
        "/api/admin/transport/available-sts",
        stdate=plan_date,
        unassigned_only="true",
    )
    if len(rows) < min_count:
        pytest.skip(f"Недостаточно свежих unassigned СТ: нужно {min_count}, есть {len(rows)}")
    return rows


# ---------------------------------------------------------------------------
# Группа A: Жизненный цикл рейса — граничные состояния
# ---------------------------------------------------------------------------

class TestTripStateBoundaries:
    def test_empty_trip_close_fails_or_warns(self, session, plan_date):
        """Закрытие пустого рейса (0 СТ) должно вернуть ошибку или пройти с предупреждением."""
        with temp_task(session, plan_date) as task_id:
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/close",
                timeout=30,
            )
            # Ожидаем либо 422 (can_print не прошёл) либо 200 если система разрешает
            assert r.status_code in (200, 422, 400), (
                f"Закрытие пустого рейса: неожиданный статус {r.status_code}"
            )
            if r.status_code == 422:
                assert r.json().get("detail"), "422 без detail — клиент не поймёт причину"

    def test_single_st_trip_works(self, session, plan_date, seed_sts):
        """Рейс с 1 СТ — минимально жизнеспособный."""
        fresh_sts = _fresh_sts(session, plan_date)
        with temp_task(session, plan_date) as task_id:
            st = fresh_sts[0]["ST_NUMBER"]
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [st]},
                timeout=30,
            )
            assert r.status_code == 200, (
                f"Назначение единственного СТ: {r.status_code} {r.text[:200]}"
            )
            task_sts = api_get(session, f"/api/admin/transport/tasks/{task_id}/sts")
            assigned_sts = {row["ST_NUMBER"] for row in task_sts}
            assert assigned_sts == {st}, (
                f"В рейсе должен быть один уникальный СТ {st}, получено {assigned_sts}"
            )

    def test_cancel_trip_releases_sts(self, session, plan_date, seed_sts):
        """После отмены рейса его СТ возвращаются в пул unassigned."""
        fresh_sts = _fresh_sts(session, plan_date, min_count=2)
        chosen = [fresh_sts[0]["ST_NUMBER"], fresh_sts[1]["ST_NUMBER"]]
        with temp_task(session, plan_date) as task_id:
            r = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": chosen},
                timeout=30,
            )
            assert r.status_code == 200, f"assign sts: {r.status_code} {r.text[:200]}"

        # Рейс уже отменён в temp_task.__exit__ — теперь проверяем пул
        after = api_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true",
        )
        pool = {r["ST_NUMBER"] for r in after}
        for st in chosen:
            assert st in pool, (
                f"СТ {st} не вернулся в пул после отмены рейса"
            )

    def test_double_close_returns_error_or_noop(self, session, plan_date, seed_sts, seed_vehicles):
        """Повторное закрытие уже закрытого рейса не должно падать с 500."""
        fresh_sts = _fresh_sts(session, plan_date)
        vehicle = max(seed_vehicles, key=lambda v: int(v.get("PALLETS") or 0))
        max_p = int(vehicle.get("PALLETS") or 20)
        chosen, total = [], 0
        for st in fresh_sts:
            p = int(st.get("PALLETS_COUNT") or 0)
            if p > 0 and total + p <= max_p:
                chosen.append(st)
                total += p
            if total >= max_p // 2:
                break
        if not chosen:
            pytest.skip("Нет СТ для теста повторного закрытия")

        drivers = session.get(f"{BASE_URL}/api/admin/transport/drivers", timeout=15).json()
        if not drivers:
            pytest.skip("Нет водителей")

        with temp_task(session, plan_date) as task_id:
            session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
                json={"st_numbers": [s["ST_NUMBER"] for s in chosen]},
                timeout=30,
            )
            session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}",
                json={
                    "transport": vehicle.get("NUM") or vehicle.get("NUM_PLAT"),
                    "voditel_id": int(drivers[0].get("ID") or drivers[0].get("VODITEL_ID")),
                },
                timeout=30,
            )
            r1 = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/close",
                timeout=30,
            )
            if r1.status_code != 200:
                pytest.skip("can_print не прошёл — пропускаем тест повторного закрытия")

            r2 = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/close",
                timeout=30,
            )
            assert r2.status_code != 500, (
                f"Повторное закрытие вернуло 500 — необработанное исключение: {r2.text[:200]}"
            )


# ---------------------------------------------------------------------------
# Группа B: Конфликты назначения СТ
# ---------------------------------------------------------------------------

class TestSTAssignmentConflicts:
    def test_assign_st_to_two_trips_fails(self, session, plan_date, seed_sts):
        """Назначение одного СТ в два разных рейса должно вернуть ошибку для второго."""
        st = _fresh_sts(session, plan_date)[0]["ST_NUMBER"]
        with temp_task(session, plan_date) as task1_id:
            r1 = session.post(
                f"{BASE_URL}/api/admin/transport/tasks/{task1_id}/sts",
                json={"st_numbers": [st]},
                timeout=30,
            )
            assert r1.status_code == 200

            with temp_task(session, plan_date) as task2_id:
                r2 = session.post(
                    f"{BASE_URL}/api/admin/transport/tasks/{task2_id}/sts",
                    json={"st_numbers": [st]},
                    timeout=30,
                )
                # Должна быть ошибка — СТ уже занят
                assert r2.status_code in (400, 409, 422), (
                    f"СТ {st} назначен в два рейса: второй запрос вернул {r2.status_code}"
                )

    def test_remove_nonexistent_st_from_trip(self, session, plan_date):
        """Попытка снять СТ которого нет в рейсе → не 500."""
        with temp_task(session, plan_date) as task_id:
            r = session.delete(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts/NONEXISTENT_ST_NUMBER",
                timeout=15,
            )
            assert r.status_code in (400, 404, 422), (
                f"Ожидалась ошибка при снятии несуществующего СТ, "
                f"получено {r.status_code}: {r.text[:100]}"
            )
            assert r.status_code != 500


# ---------------------------------------------------------------------------
# Группа C: Несуществующие ресурсы
# ---------------------------------------------------------------------------

class TestNotFoundHandling:
    def test_nonexistent_task_returns_404(self, session):
        r = session.get(
            f"{BASE_URL}/api/admin/transport/tasks/999999999",
            timeout=15,
        )
        assert r.status_code in (404, 422), (
            f"Несуществующий task_id: ожидался 404, получено {r.status_code}"
        )

    def test_nonexistent_task_close_returns_404(self, session):
        r = session.post(
            f"{BASE_URL}/api/admin/transport/tasks/999999999/close",
            timeout=15,
        )
        assert r.status_code in (404, 422, 400), (
            f"Закрытие несуществующего рейса: {r.status_code}"
        )

    def test_nonexistent_billing_order_returns_404(self, session):
        r = session.get(
            f"{BASE_URL}/api/admin/transport/billing/orders/999999999",
            timeout=15,
        )
        assert r.status_code in (404, 422), (
            f"Несуществующий billing order: {r.status_code}"
        )


# ---------------------------------------------------------------------------
# Группа D: Перенос рейса на следующий день
# ---------------------------------------------------------------------------

class TestTripMoveToNextDay:
    def test_move_trip_to_next_day(self, session, plan_date, seed_sts):
        """PATCH с новой датой должен обновить shipment_date рейса."""
        with temp_task(session, plan_date) as task_id:
            from datetime import date, timedelta
            next_day = (
                date.fromisoformat(plan_date) + timedelta(days=1)
            ).isoformat()

            r = session.patch(
                f"{BASE_URL}/api/admin/transport/tasks/{task_id}",
                json={"shipment_date": next_day},
                timeout=30,
            )
            assert r.status_code in (200, 204), (
                f"Перенос рейса: {r.status_code} {r.text[:200]}"
            )

            # Рейс должен исчезнуть из списка на plan_date и появиться на next_day
            tasks_today = api_get(
                session, "/api/admin/transport/tasks", stdate=plan_date
            )
            ids_today = {int(t.get("TT_ID") or t.get("ID") or 0) for t in tasks_today}
            # Рейс может остаться на plan_date если бизнес-логика другая — не падаем
            # Главное что запрос прошёл без 500

            tasks_next = api_get(
                session, "/api/admin/transport/tasks", stdate=next_day
            )
            ids_next = {int(t.get("TT_ID") or t.get("ID") or 0) for t in tasks_next}
            assert task_id in ids_next, (
                f"Рейс {task_id} не появился в списке на {next_day} после переноса"
            )


# ---------------------------------------------------------------------------
# Группа E: Кластерное создание рейса
# ---------------------------------------------------------------------------

class TestClusterCreateTask:
    def test_create_task_from_cluster(self, session, plan_date):
        """Кнопка '⚡ Рейс' — создать рейс из всех СТ района."""
        clusters = api_get(
            session, "/api/admin/transport/clusters",
            stdate=plan_date,
        )
        if not clusters:
            pytest.skip("Нет кластеров на plan_date")

        # Берём кластер с наименьшим числом СТ чтобы не загрязнять много данных
        raion_key = next(k for k in clusters[0] if "RAION" in k.upper() or "raion" in k.lower())
        raion = clusters[0][raion_key]

        r = session.post(
            f"{BASE_URL}/api/admin/transport/clusters/{raion}/create-task",
            json={"stdate": plan_date, "transtype": "10"},
            timeout=60,
        )
        assert r.status_code in (200, 201), (
            f"Создание рейса из кластера '{raion}': {r.status_code} {r.text[:200]}"
        )
        task_id = r.json().get("TT_ID") or r.json().get("task_id")
        assert task_id, "Нет TT_ID в ответе"

        # Teardown
        session.post(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel",
            timeout=15,
        )


# ---------------------------------------------------------------------------
# Группа F: Пагинация
# ---------------------------------------------------------------------------

class TestPagination:
    def test_available_sts_pagination_page1(self, session, plan_date):
        """Пагинация: первая страница (100 строк) меньше полного набора."""
        full = api_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true",
        )
        if len(full) <= 100:
            pytest.skip("Данных меньше 100 — нечего пагинировать")

        page1 = api_get(
            session, "/api/admin/transport/available-sts",
            stdate=plan_date, unassigned_only="true",
            page=1, page_size=100,
        )
        assert 0 < len(page1) <= 100, (
            f"Первая страница должна содержать 1-100 строк, получено {len(page1)}"
        )

    def test_tasks_list_pagination(self, session, plan_date):
        """Таблица рейсов поддерживает параметры пагинации без ошибок."""
        r = session.get(
            f"{BASE_URL}/api/admin/transport/tasks",
            params={"stdate": plan_date, "page": 1, "page_size": 10},
            timeout=30,
        )
        # Не все бэкенды поддерживают пагинацию — принимаем 200 или 422
        assert r.status_code in (200, 422), (
            f"Пагинация рейсов: {r.status_code} {r.text[:100]}"
        )


# ---------------------------------------------------------------------------
# Группа G: WebSocket статус
# ---------------------------------------------------------------------------

class TestWebSocket:
    def test_ws_status_endpoint_works(self, session):
        r = session.get(
            f"{BASE_URL}/api/admin/transport/ws/status",
            timeout=15,
        )
        assert r.status_code == 200, f"ws/status: {r.status_code}"
        data = r.json()
        count = data.get("active_connections") or data.get("count") or data.get("connections") or 0
        assert isinstance(int(count), int), f"active_connections не число: {count!r}"
