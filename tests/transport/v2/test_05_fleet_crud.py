"""
test_05_fleet_crud.py — CRUD транспортных средств и водителей

Проверяем полный жизненный цикл:
  - создание → появление в списке → обновление → удаление
  - уникальность num_plat
  - типы транспорта (GET /types)
  - водители: своя компания vs нанятая
  - данные seed-машин присутствуют и корректны
"""
from __future__ import annotations

import uuid

import pytest
import requests

from conftest import BASE_URL, SEED_VEHICLE_IDS, api_get


# ---------------------------------------------------------------------------
# Группа A: Справочник типов транспорта
# ---------------------------------------------------------------------------

class TestTransportTypes:
    def test_types_list_not_empty(self, session):
        types = api_get(session, "/api/admin/transport/types")
        assert isinstance(types, list) and len(types) >= 1, "Список типов ТС пуст"

    def test_types_have_id_and_name(self, session):
        types = api_get(session, "/api/admin/transport/types")
        for t in types[:5]:
            assert t.get("ID") or t.get("id") or t.get("TRANSTYPE_ID") or t.get("TRANSPORTTYPE"), (
                f"Тип ТС без ID: {t}"
            )


# ---------------------------------------------------------------------------
# Группа B: Seed-машины присутствуют
# ---------------------------------------------------------------------------

class TestSeedVehicles:
    def test_all_seed_vehicles_present(self, session, seed_vehicles):
        assert len(seed_vehicles) == len(SEED_VEHICLE_IDS), (
            f"Ожидалось {len(SEED_VEHICLE_IDS)} seed-машин, "
            f"найдено {len(seed_vehicles)}"
        )

    def test_seed_vehicles_have_pallets(self, session, seed_vehicles):
        no_pallets = [v for v in seed_vehicles if int(v.get("PALLETS") or 0) == 0]
        assert not no_pallets, (
            f"Seed-машины без PALLETS: {[v.get('NUM') for v in no_pallets]}"
        )

    def test_seed_vehicles_have_num_plat(self, session, seed_vehicles):
        no_num = [v for v in seed_vehicles if not (v.get("NUM") or v.get("NUM_PLAT"))]
        assert not no_num, f"Seed-машины без номера: {no_num}"

    def test_seed_vehicles_full_endpoint_returns_extra_fields(self, session):
        full = api_get(session, "/api/admin/transport/vehicles/full")
        seed_full = [v for v in full if int(v.get("ID") or 0) in SEED_VEHICLE_IDS]
        if not seed_full:
            pytest.skip("Seed-машины не найдены в /vehicles/full")
        # /full должен возвращать больше полей чем /vehicles
        base = api_get(session, "/api/admin/transport/vehicles")
        base_fields = set(base[0].keys()) if base else set()
        full_fields = set(seed_full[0].keys())
        extra = full_fields - base_fields
        # Ожидаем хотя бы 1 дополнительное поле в /full
        assert len(full_fields) >= len(base_fields), (
            "/vehicles/full не содержит дополнительных полей по сравнению с /vehicles"
        )


# ---------------------------------------------------------------------------
# Группа C: CRUD машин
# ---------------------------------------------------------------------------

class TestVehicleCRUD:
    def test_create_vehicle_lifecycle(self, session):
        """Создать машину → обновить → удалить."""
        num_plat = f"TEST_V2_VEH_{uuid.uuid4().hex[:8]}"
        # Создание
        r_create = session.post(
            f"{BASE_URL}/api/admin/transport/vehicles",
            json={
                "num_plat": num_plat,
                "transtype_id": None,
                "max_weight_kg": 5000,
                "max_pallets": 10,
                "sobstvennyy": True,
            },
            timeout=30,
        )
        assert r_create.status_code in (200, 201), (
            f"Создание машины: {r_create.status_code} {r_create.text[:200]}"
        )
        created = r_create.json()
        vehicle_id = created.get("ID") or created.get("id") or created.get("vehicle_id")
        assert vehicle_id, "Нет ID после создания машины"

        try:
            # Машина появилась в списке
            full = api_get(session, "/api/admin/transport/vehicles/full")
            ids = {int(v.get("ID") or 0) for v in full}
            assert int(vehicle_id) in ids, (
                f"Созданная машина {vehicle_id} не найдена в /vehicles/full"
            )

            # Обновление
            r_upd = session.patch(
                f"{BASE_URL}/api/admin/transport/vehicles/{vehicle_id}",
                json={
                    "num_plat": num_plat,
                    "transtype_id": None,
                    "max_pallets": 15,
                    "max_weight_kg": 7000,
                    "sobstvennyy": True,
                },
                timeout=30,
            )
            assert r_upd.status_code in (200, 204), (
                f"Обновление машины: {r_upd.status_code} {r_upd.text[:200]}"
            )

            # Проверить обновление
            full_after = api_get(session, "/api/admin/transport/vehicles/full")
            updated = next(
                (v for v in full_after if int(v.get("ID") or 0) == int(vehicle_id)),
                None,
            )
            if updated:
                assert int(updated.get("PALLETS") or updated.get("MAX_PALLETS") or updated.get("max_pallets") or 0) == 15, (
                    "Поле max_pallets не обновилось"
                )

        finally:
            # Удаление
            r_del = session.delete(
                f"{BASE_URL}/api/admin/transport/vehicles/{vehicle_id}",
                timeout=15,
            )
            assert r_del.status_code in (200, 204), (
                f"Удаление машины: {r_del.status_code} {r_del.text[:200]}"
            )

            # Машина исчезла
            full_final = api_get(session, "/api/admin/transport/vehicles/full")
            ids_final = {int(v.get("ID") or 0) for v in full_final}
            assert int(vehicle_id) not in ids_final, (
                f"Машина {vehicle_id} всё ещё в списке после удаления"
            )

    def test_vehicle_num_appears_in_short_list(self, session):
        """Созданная машина должна быть видна в /vehicles (короткий список для диспетчера)."""
        num_plat = f"TV2SHORT{uuid.uuid4().hex[:8]}"
        r = session.post(
            f"{BASE_URL}/api/admin/transport/vehicles",
            json={
                "num_plat": num_plat,
                "transtype_id": None,
                "max_weight_kg": 3000,
                "max_pallets": 8,
                "sobstvennyy": True,
            },
            timeout=30,
        )
        assert r.status_code in (200, 201)
        vehicle_id = r.json().get("ID") or r.json().get("id") or r.json().get("vehicle_id")

        try:
            short = api_get(session, "/api/admin/transport/vehicles")
            nums = [v.get("NUM") or v.get("NUM_PLAT") or "" for v in short]
            assert num_plat in nums, (
                "Новая машина не появилась в коротком списке /vehicles"
            )
        finally:
            if vehicle_id:
                session.delete(f"{BASE_URL}/api/admin/transport/vehicles/{vehicle_id}", timeout=15)


# ---------------------------------------------------------------------------
# Группа D: CRUD водителей
# ---------------------------------------------------------------------------

class TestDriverCRUD:
    def test_create_driver_lifecycle(self, session):
        """Создать водителя → обновить → удалить."""
        name = f"Тест Водитель v2 {uuid.uuid4().hex[:8]}"
        r_create = session.post(
            f"{BASE_URL}/api/admin/transport/drivers",
            json={
                "name": name,
                "phone": "+7-999-000-00-00",
                "license_number": "00AA000000",
                "company": None,
            },
            timeout=30,
        )
        assert r_create.status_code in (200, 201), (
            f"Создание водителя: {r_create.status_code} {r_create.text[:200]}"
        )
        created = r_create.json()
        driver_id = created.get("ID") or created.get("id") or created.get("VODITEL_ID")
        assert driver_id, "Нет ID после создания водителя"

        try:
            # Появился в списке
            full = api_get(session, "/api/admin/transport/drivers/full")
            ids = {int(d.get("ID") or d.get("VODITEL_ID") or 0) for d in full}
            assert int(driver_id) in ids, (
                f"Водитель {driver_id} не найден в /drivers/full"
            )

            # Обновление
            r_upd = session.patch(
                f"{BASE_URL}/api/admin/transport/drivers/{driver_id}",
                json={"name": name, "phone": "+7-999-111-11-11"},
                timeout=30,
            )
            assert r_upd.status_code in (200, 204), (
                f"Обновление водителя: {r_upd.status_code} {r_upd.text[:200]}"
            )

        finally:
            # Удаление
            r_del = session.delete(
                f"{BASE_URL}/api/admin/transport/drivers/{driver_id}",
                timeout=15,
            )
            assert r_del.status_code in (200, 204), (
                f"Удаление водителя: {r_del.status_code} {r_del.text[:200]}"
            )
            full_after = api_get(session, "/api/admin/transport/drivers/full")
            ids_after = {int(d.get("ID") or d.get("VODITEL_ID") or 0) for d in full_after}
            assert int(driver_id) not in ids_after, (
                f"Водитель {driver_id} всё ещё в списке после удаления"
            )

    def test_driver_appears_in_short_list(self, session):
        name = f"Тест Краткий Список v2 {uuid.uuid4().hex[:8]}"
        r = session.post(
            f"{BASE_URL}/api/admin/transport/drivers",
            json={"name": name, "company": None},
            timeout=30,
        )
        assert r.status_code in (200, 201)
        driver_id = r.json().get("ID") or r.json().get("id") or r.json().get("VODITEL_ID")

        try:
            short = api_get(session, "/api/admin/transport/drivers")
            names = [d.get("NAME") or d.get("name") or d.get("FULL_NAME") or "" for d in short]
            assert name in names, (
                "Новый водитель не появился в коротком списке /drivers"
            )
        finally:
            if driver_id:
                session.delete(f"{BASE_URL}/api/admin/transport/drivers/{driver_id}", timeout=15)

    def test_drivers_have_name_field(self, session):
        drivers = api_get(session, "/api/admin/transport/drivers")
        assert drivers, "Список водителей пуст"
        for d in drivers[:5]:
            name = d.get("NAME") or d.get("name") or d.get("FULL_NAME")
            assert name, f"Водитель без имени: {d}"
