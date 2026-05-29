"""
Wave 3: Business Factor Trace.

These tests are the third testing wave for TMS-2.  They do not only check that
the planner endpoints answer 200; they prove that the business factors used by
daily dispatch planning are wired end-to-end:

Oracle/source SQL -> planner order contract -> VrpOrder -> solver response.
"""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import os
from pathlib import Path
from typing import Any

import pytest
import requests


ROOT = Path(__file__).resolve().parents[2]
BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")
AUTH = tuple(os.environ.get("TMS_AUTH", "admin:admin123").split(":", 1))
PLAN_DATE = os.environ.get("TMS_WAVE3_PLAN_DATE", "2026-05-24")

SEED_VEHICLE_IDS = set(range(9201, 9216))
DISPATCH_SLOTS = ("06:00", "10:00", "14:00", "18:00")
AVAILABLE_STS_CONTRACT = {
    "ST_NUMBER",
    "ADDR",
    "RAION",
    "PALLETS_COUNT",
    "WEIGHT_KG",
    "WARE_ID",
    "VERIFY_PERC",
}
PLANNER_ORDERS_CONTRACT = {
    "ST_NUMBER",
    "LAT",
    "LON",
    "PALLETS_COUNT",
    "WEIGHT_KG",
    "WARE_ID",
    "TRANSPORT_TYPE",
    "TIME_FROM",
    "TIME_TO",
    "UNLOAD_NORM_MIN",
    "VERIFY_PERC",
    "TW_STRICT",
}
VRP_STOP_CONTRACT = {
    "st_number",
    "lat",
    "lon",
    "pallets",
    "weight_kg",
    "ware_id",
    "tw_from",
    "tw_to",
    "tw_strict",
    "unload_norm_min",
}


BUSINESS_FACTORS = {
    "coordinates": {
        "sql": ("A.SHIROTA AS LAT", "A.DOLGOTA AS LON"),
        "order_fields": ("LAT", "LON"),
        "vrp_mapping": ("lat=", "lon="),
        "stop_fields": ("lat", "lon"),
    },
    "pallet_capacity": {
        "sql": ("PALLETS_COUNT",),
        "order_fields": ("PALLETS_COUNT",),
        "vrp_mapping": ("pallets=",),
        "stop_fields": ("pallets",),
    },
    "weight_load": {
        "sql": ("WEIGHT_KG",),
        "order_fields": ("WEIGHT_KG",),
        "vrp_mapping": ("weight_kg=",),
        "stop_fields": ("weight_kg",),
    },
    "warehouse": {
        "sql": ("P.WARE_ID",),
        "order_fields": ("WARE_ID",),
        "vrp_mapping": ("ware_id=",),
        "stop_fields": ("ware_id",),
    },
    "transport_type": {
        "sql": ("TRANSPORT_TYPE",),
        "order_fields": ("TRANSPORT_TYPE",),
        "vrp_mapping": ("transport_type=",),
        "route_fields": ("vehicle_type",),
    },
    "store_time_windows": {
        "sql": ("ZONE_TIME_PLAN_IN", "ZONE_TIME_PLAN_OUT"),
        "order_fields": ("TIME_FROM", "TIME_TO"),
        "vrp_mapping": ("tw_from=", "tw_to="),
        "stop_fields": ("tw_from", "tw_to"),
    },
    "strict_time_window_flag": {
        "sql": ("TW_STRICT",),
        "order_fields": ("TW_STRICT",),
        "vrp_mapping": ("tw_strict=",),
        "stop_fields": ("tw_strict",),
    },
    "unload_norm": {
        "sql": ("UNLOAD_NORM_MIN",),
        "order_fields": ("UNLOAD_NORM_MIN",),
        "vrp_mapping": ("unload_norm_min=",),
        "stop_fields": ("unload_norm_min",),
    },
    "readiness": {
        "sql": ("VERIFY_PERC",),
        "order_fields": ("VERIFY_PERC",),
    },
}


def _session() -> requests.Session:
    session = requests.Session()
    session.auth = AUTH
    session.headers.update({"Content-Type": "application/json"})
    return session


def _get_json(session: requests.Session, path: str, **params):
    response = session.get(f"{BASE_URL}{path}", params=params, timeout=60)
    assert response.status_code == 200, f"{path} failed: {response.status_code} {response.text}"
    return response.json()


def _values(rows: list[dict[str, Any]], field: str) -> list[Any]:
    return [row.get(field) for row in rows if row.get(field) is not None]


def _assert_field_has_real_values(
    rows: list[dict[str, Any]],
    field: str,
    *,
    default: Any | None = None,
    min_distinct: int = 2,
    why: str,
) -> None:
    values = _values(rows, field)
    assert values, f"{field}: all values are None/missing. {why}"
    distinct = {str(value) for value in values}
    assert len(distinct) >= min_distinct, (
        f"{field}: only {len(distinct)} distinct value(s) {sorted(distinct)[:5]}. "
        f"Possible silent drop/default lock. {why}"
    )
    if default is not None:
        assert any(value != default for value in values), (
            f"{field}: every value equals default {default!r}. {why}"
        )


def _minutes_from_shift_start(value: Any, shift_start_hour: int = 6) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value)
    if "T" in text:
        text = text.split("T", 1)[1]
    elif " " in text:
        text = text.rsplit(" ", 1)[-1]
    if ":" not in text:
        return None
    try:
        hour, minute = (int(part) for part in text.split(":", 2)[:2])
    except ValueError:
        return None
    return max(0, hour * 60 + minute - shift_start_hour * 60)


def _extract_task_id(payload: Any) -> int | None:
    if isinstance(payload, int):
        return payload
    if not isinstance(payload, dict):
        return None
    for key in ("TT_ID", "task_id", "id", "ID"):
        value = payload.get(key)
        if value is not None:
            return int(value)
    return None


@contextmanager
def _temp_task(session: requests.Session, plan_date: str):
    response = session.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        json={"transtype": "10", "shipment_date": plan_date},
        timeout=30,
    )
    assert response.status_code == 200, f"Create temp task failed: {response.status_code} {response.text}"
    task_id = _extract_task_id(response.json())
    assert task_id is not None, (
        f"Create temp task returned no task id. Expected TT_ID/task_id/id/ID, got: {response.text}"
    )
    try:
        yield task_id
    finally:
        session.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel", timeout=30)


def _solve(session: requests.Session, *, transport_type: str | None = None) -> dict:
    payload = {
        "plan_date": PLAN_DATE,
        "time_limit_s": 15,
        "source": "auto",
        "solver": "savings",
    }
    if transport_type:
        payload["transport_type"] = transport_type
    response = session.post(
        f"{BASE_URL}/api/admin/transport/planner/solve",
        json=payload,
        timeout=120,
    )
    assert response.status_code == 200, f"Planner solve failed: {response.status_code} {response.text}"
    return response.json()


def test_wave3_static_contract_traces_business_factors_through_planner_code():
    service_src = (ROOT / "api/wms_api_server/app/services/transport_service.py").read_text(encoding="utf-8")
    solver_src = (ROOT / "api/wms_api_server/app/services/vrp_solver.py").read_text(encoding="utf-8")
    schemas_src = (ROOT / "api/wms_api_server/app/schemas.py").read_text(encoding="utf-8")

    for factor, contract in BUSINESS_FACTORS.items():
        for marker in contract.get("sql", ()):
            assert marker in service_src, f"{factor}: SQL source marker is not selected: {marker}"
        for field in contract.get("order_fields", ()):
            assert field in service_src, f"{factor}: planner order field is absent: {field}"
        for marker in contract.get("vrp_mapping", ()):
            assert marker in service_src, f"{factor}: solve_vrp does not map into VrpOrder: {marker}"
        for field in contract.get("stop_fields", ()):
            assert field in schemas_src, f"{factor}: solver response stop field is absent: {field}"
        for field in contract.get("route_fields", ()):
            assert field in schemas_src, f"{factor}: solver response route field is absent: {field}"

    for marker in (
        "if route.total_pallets + order.pallets > route.vehicle.max_pallets",
        "if (route.total_kg + order.weight_kg) / 1000 > route.vehicle.max_tons",
        "time_dim.SetCumulVarSoftLowerBound",
        "time_dim.SetCumulVarSoftUpperBound",
        "time_cb",
    ):
        assert marker in solver_src, f"VRP solver does not show factor participation: {marker}"


def test_wave3_planner_orders_expose_non_default_business_factors_on_seed():
    session = _session()
    orders = _get_json(session, "/api/admin/transport/planner/orders", date=PLAN_DATE)
    assert len(orders) >= 300, f"Expected full daily order set, got {len(orders)}"

    required = {
        field
        for contract in BUSINESS_FACTORS.values()
        for field in contract.get("order_fields", ())
    }
    for row in orders[:30]:
        missing = required - set(row)
        assert not missing, f"Planner order misses business fields: {missing}"

    assert any(row.get("LAT") and row.get("LON") for row in orders), "No geocoded orders in daily set"
    assert sum(int(row.get("PALLETS_COUNT") or 0) for row in orders) > 0
    assert sum(float(row.get("WEIGHT_KG") or 0) for row in orders) > 0
    assert any(row.get("TIME_FROM") or row.get("TIME_TO") for row in orders) or any(
        row.get("UNLOAD_NORM_MIN") for row in orders
    )
    assert any(row.get("VERIFY_PERC") is not None for row in orders)


def test_wave3_available_sts_values_are_real_not_default_locked():
    session = _session()
    rows = _get_json(
        session,
        "/api/admin/transport/available-sts",
        stdate=PLAN_DATE,
        unassigned_only="true",
    )
    if not rows:
        pytest.skip("No seed STs for Wave 3 data-fidelity check")

    for idx, row in enumerate(rows[:30]):
        missing = AVAILABLE_STS_CONTRACT - set(row)
        assert not missing, f"available-sts row {idx} misses fields {missing}; check list_available_sts SELECT"

    _assert_field_has_real_values(
        rows,
        "PALLETS_COUNT",
        default=0,
        min_distinct=2,
        why="Check RRL_SBORKA_PALLETS aggregation and PALLETS_COUNT mapping.",
    )
    _assert_field_has_real_values(
        rows,
        "WEIGHT_KG",
        default=0,
        min_distinct=5,
        why="Check RRL_SBORKA_PALLET_ROWS join and WEIGHT_KG mapping.",
    )
    _assert_field_has_real_values(
        rows,
        "WARE_ID",
        min_distinct=2,
        why="Check WARE_ID filter/source mapping; seed should contain several warehouses.",
    )
    verify_values = _values(rows, "VERIFY_PERC")
    assert len(verify_values) >= len(rows) * 0.3, (
        "VERIFY_PERC is missing for most available ST rows; check SQL expression and API dict mapping."
    )


def test_wave3_planner_orders_match_available_sts_for_same_business_facts():
    session = _session()
    available = _get_json(
        session,
        "/api/admin/transport/available-sts",
        stdate=PLAN_DATE,
        unassigned_only="true",
    )
    orders = _get_json(session, "/api/admin/transport/planner/orders", date=PLAN_DATE)
    if not available or not orders:
        pytest.skip("No seed rows for cross-endpoint data fidelity")

    available_by_st = {str(row["ST_NUMBER"]): row for row in available if row.get("ST_NUMBER")}
    orders_by_st = {str(row["ST_NUMBER"]): row for row in orders if row.get("ST_NUMBER")}
    common = sorted(set(available_by_st) & set(orders_by_st))
    assert common, "No common ST_NUMBER between available-sts and planner/orders"

    mismatches: list[str] = []
    for st_number in common[:50]:
        st_row = available_by_st[st_number]
        order_row = orders_by_st[st_number]
        for field in ("PALLETS_COUNT", "WEIGHT_KG", "WARE_ID", "VERIFY_PERC"):
            left = st_row.get(field)
            right = order_row.get(field)
            if left is None or right is None:
                continue
            if field in ("WEIGHT_KG", "VERIFY_PERC"):
                if abs(float(left) - float(right)) > 1.0:
                    mismatches.append(f"{st_number}.{field}: available={left!r}, planner={right!r}")
            elif str(left) != str(right):
                mismatches.append(f"{st_number}.{field}: available={left!r}, planner={right!r}")
        if st_row.get("TIME_FROM") is not None and order_row.get("TIME_FROM") is not None:
            if str(st_row["TIME_FROM"]) != str(order_row["TIME_FROM"]):
                mismatches.append(
                    f"{st_number}.TIME_FROM: available={st_row['TIME_FROM']!r}, planner={order_row['TIME_FROM']!r}"
                )

    assert not mismatches, (
        "The same ST has different business facts across endpoints. "
        "Check list_available_sts/get_planner_orders SELECT aliases and mappings:\n"
        + "\n".join(mismatches[:10])
    )


def test_wave3_solve_preserves_factors_and_uses_them_in_route_totals():
    session = _session()
    plan = _solve(session)
    assert plan["routes"], "Wave 3 requires a non-empty daily VRP plan"
    assert plan["unassigned_sts"] == [], f"Unassigned STs prove a broken daily planning flow: {plan['unassigned_sts'][:10]}"

    route_counts = Counter()
    saw_non_default_tw = False
    saw_weight = False
    saw_unload_norm = False

    for route in plan["routes"]:
        route_counts[route["vehicle_num"]] += 1
        stop_pallets = sum(int(stop.get("pallets") or 0) for stop in route["stops"])
        stop_weight = sum(float(stop.get("weight_kg") or 0) for stop in route["stops"])
        assert stop_pallets == int(route["total_pallets"] or 0), "Route pallet total is not built from stop pallets"
        assert abs(stop_weight - float(route["total_kg"] or 0)) < 0.01, "Route weight total is not built from stop weights"
        assert route["total_pallets"] <= route["max_pallets"], "Pallet capacity was not enforced"
        assert route["vehicle_type"] is not None

        for stop in route["stops"]:
            missing = VRP_STOP_CONTRACT - set(stop)
            assert not missing, f"VRP stop misses end-to-end factor fields {missing}; check VrpRouteStop mapping"
            assert 0 <= int(stop["tw_from"]) <= int(stop["tw_to"]) <= 1440
            saw_non_default_tw = saw_non_default_tw or int(stop["tw_from"]) != 0 or int(stop["tw_to"]) != 1080
            saw_weight = saw_weight or float(stop.get("weight_kg") or 0) > 0
            saw_unload_norm = saw_unload_norm or int(stop.get("unload_norm_min") or 0) > 0

    assert saw_non_default_tw, "Store time windows are not visible in solved routes"
    assert saw_weight, "Weight did not survive into solved routes"
    assert saw_unload_norm, "Unload norm did not survive into solved routes"
    assert max(route_counts.values()) <= 4, f"A vehicle received more than 4 daily trips: {route_counts}"


def test_wave3_vrp_time_windows_match_planner_orders_when_oracle_value_exists():
    session = _session()
    orders = _get_json(session, "/api/admin/transport/planner/orders", date=PLAN_DATE)
    if not orders:
        pytest.skip("No planner orders for VRP time-window fidelity check")

    order_by_st = {str(row["ST_NUMBER"]): row for row in orders if row.get("ST_NUMBER")}
    plan = _solve(session)
    mismatches: list[str] = []
    checked = 0

    for route in plan["routes"]:
        for stop in route["stops"]:
            order = order_by_st.get(str(stop["st_number"]))
            if not order or order.get("TIME_FROM") is None:
                continue
            expected = _minutes_from_shift_start(order.get("TIME_FROM"))
            if expected is None:
                continue
            checked += 1
            actual = int(stop.get("tw_from") or 0)
            if abs(actual - expected) > 5:
                mismatches.append(
                    f"ST={stop['st_number']}: TIME_FROM={order.get('TIME_FROM')!r} "
                    f"expected tw_from~{expected}, actual={actual}"
                )

    if checked == 0:
        non_default = [
            stop
            for route in plan["routes"]
            for stop in route["stops"]
            if int(stop.get("tw_from") or 0) != 0 or int(stop.get("tw_to") or 1080) != 1080
        ]
        assert non_default, (
            "Seed has no parseable Oracle TIME_FROM values and VRP fallback windows are also default. "
            "Check ZONE_TIME_PLAN_IN/OUT seed data or _fallback_time_window_from_ord()."
        )
        return
    assert not mismatches, (
        "VRP stop tw_from does not match planner/orders TIME_FROM conversion. "
        "Check get_planner_orders() -> solve_vrp() -> VrpOrder(tw_from=...):\n"
        + "\n".join(mismatches[:10])
    )


def test_wave3_task_sts_preserve_available_sts_values_with_cleanup():
    session = _session()
    available = _get_json(
        session,
        "/api/admin/transport/available-sts",
        stdate=PLAN_DATE,
        unassigned_only="true",
    )
    chosen = [
        row
        for row in available
        if row.get("ST_NUMBER") and int(row.get("PALLETS_COUNT") or 0) > 0 and float(row.get("WEIGHT_KG") or 0) > 0
    ][:3]
    if len(chosen) < 3:
        pytest.skip("Not enough seed STs with pallets and weight for cleanup-bound flow")

    expected = {str(row["ST_NUMBER"]): row for row in chosen}
    with _temp_task(session, PLAN_DATE) as task_id:
        assign = session.post(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
            json={"st_numbers": list(expected)},
            timeout=30,
        )
        assert assign.status_code == 200, f"Assign STs failed: {assign.status_code} {assign.text}"
        task_sts = _get_json(session, f"/api/admin/transport/tasks/{task_id}/sts")
        actual_by_st: dict[str, dict[str, float]] = {}
        for row in task_sts:
            st_number = str(row.get("ST_NUMBER") or "")
            if not st_number:
                continue
            bucket = actual_by_st.setdefault(
                st_number,
                {"PALLETS_COUNT": 0.0, "WEIGHT_KG": 0.0, "VERIFY_PERC": float(row.get("VERIFY_PERC") or 0)},
            )
            bucket["PALLETS_COUNT"] += float(row.get("PALLETS_COUNT") or 0)
            bucket["WEIGHT_KG"] += float(row.get("WEIGHT_KG") or 0)

        assert set(expected) <= set(actual_by_st), (
            f"Assigned STs are missing from task composition: {set(expected) - set(actual_by_st)}"
        )
        for st_number, source in expected.items():
            actual = actual_by_st[st_number]
            assert int(actual.get("PALLETS_COUNT") or 0) == int(source.get("PALLETS_COUNT") or 0), (
                f"{st_number}: aggregated PALLETS_COUNT changed between available-sts and task/sts"
            )
            assert abs(float(actual.get("WEIGHT_KG") or 0) - float(source.get("WEIGHT_KG") or 0)) < 1.0, (
                f"{st_number}: aggregated WEIGHT_KG changed between available-sts and task/sts; "
                "check task composition SQL aggregation."
            )
            if source.get("VERIFY_PERC") is not None and actual.get("VERIFY_PERC") is not None:
                assert abs(float(actual["VERIFY_PERC"]) - float(source["VERIFY_PERC"])) < 1.0, (
                    f"{st_number}: VERIFY_PERC changed between available-sts and task/sts"
                )


def test_wave3_transport_type_filter_limits_the_e2e_planned_st_set_when_data_exists():
    session = _session()
    source_orders = _get_json(
        session,
        "/api/admin/transport/planner/orders",
        date=PLAN_DATE,
        transport_type="10",
    )
    if not source_orders:
        return

    source_sts = {str(row["ST_NUMBER"]) for row in source_orders}
    plan = _solve(session, transport_type="10")
    planned_sts = {
        str(stop["st_number"])
        for route in plan["routes"]
        for stop in route["stops"]
    }
    assert planned_sts, "Transport-type filtered solve returned no planned STs"
    assert planned_sts <= source_sts, "Solver planned STs outside the transport_type filtered source set"


def test_wave3_vehicle_availability_forecast_covers_four_dispatch_slots():
    session = _session()
    vehicles = _get_json(session, "/api/admin/transport/vehicles")
    seed_vehicles = {int(v.get("ID") or 0): v for v in vehicles if int(v.get("ID") or 0) in SEED_VEHICLE_IDS}
    assert set(seed_vehicles) == SEED_VEHICLE_IDS, "Dobrotseny seed fleet must be present for Wave 3"

    for slot in DISPATCH_SLOTS:
        available = _get_json(
            session,
            "/api/admin/transport/vehicles/available",
            shipment_time=f"{PLAN_DATE} {slot}",
            pallets=1,
        )
        by_id = {int(v.get("vehicle_id") or 0): v for v in available}
        blocked = [
            vehicle_id
            for vehicle_id in sorted(SEED_VEHICLE_IDS)
            if by_id.get(vehicle_id, {}).get("status") == "red"
        ]
        assert not blocked, f"Availability forecast blocks seed fleet at {slot}: {blocked}"
