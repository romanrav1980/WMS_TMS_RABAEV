"""
Wave 3 full-system coverage lock for TMS-2.

This is the registry layer behind "all functionality must be covered by
business-factor end-to-end tests".  It owns every TMS-2 HTTP endpoint and ties
it to:

* a business process;
* business factors;
* source/state evidence;
* functional tests;
* load/UI/E2E evidence.

If a new endpoint appears without a Wave 3 owner, this test fails.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class BusinessProcess:
    process_id: str
    area: str
    business_factors: tuple[str, ...]
    route_patterns: tuple[str, ...]
    source_evidence: tuple[str, ...]
    state_evidence: tuple[str, ...]
    functional_gates: tuple[str, ...]
    load_gates: tuple[str, ...] = ()
    ui_gates: tuple[str, ...] = ()
    e2e_gates: tuple[str, ...] = ()


PROCESSES: tuple[BusinessProcess, ...] = (
    BusinessProcess(
        process_id="dispatcher_st_intake_and_selection",
        area="dispatcher",
        business_factors=("st date", "warehouse", "address", "transport type", "pallets", "weight", "volume", "readiness"),
        route_patterns=(
            "GET /api/admin/transport/types",
            "GET /api/admin/transport/available-sts",
            "GET /api/admin/transport/clusters",
            "GET /api/admin/transport/sts/{st_number}/pallets",
        ),
        source_evidence=("RRL_SBORKA_PALLETS", "RRL_SBORKA_PALLET_ROWS", "RRL_ADDR", "RRL_TRANSPORT_TYPE"),
        state_evidence=("available ST rows", "pallet rows", "cluster totals"),
        functional_gates=(
            "tests/transport/test_sprint1_functional.py",
            "tests/transport/test_sprint5_functional.py",
            "tests/transport/test_sprint6_functional.py",
            "tests/transport/test_sprint31_functional.py",
            "tests/transport/test_wave3_business_factor_trace.py",
        ),
        load_gates=(
            "tests/transport/transport_sprint1_load_test.py",
            "tests/transport/transport_sprint5_load_test.py",
            "tests/transport/transport_sprint6_load_test.py",
            "tests/transport/transport_wave3_business_factor_load_test.py",
        ),
        ui_gates=("tests/ui/transport_sprint1_ui_smoke.cjs", "tests/ui/transport_sprint60_95_ui_smoke.cjs"),
    ),
    BusinessProcess(
        process_id="dispatcher_trip_lifecycle",
        area="dispatcher",
        business_factors=("route requisites", "vehicle", "driver", "dock", "ST assignment", "cancel release", "close protection"),
        route_patterns=(
            "GET /api/admin/transport/tasks",
            "POST /api/admin/transport/tasks",
            "GET /api/admin/transport/tasks/{task_id}",
            "PATCH /api/admin/transport/tasks/{task_id}",
            "POST /api/admin/transport/tasks/{task_id}/close",
            "POST /api/admin/transport/tasks/{task_id}/cancel",
            "GET /api/admin/transport/tasks/{task_id}/sts",
            "POST /api/admin/transport/tasks/{task_id}/sts",
            "DELETE /api/admin/transport/tasks/{task_id}/sts/{st_number}",
            "PATCH /api/admin/transport/tasks/{task_id}/sts/{st_number}/load-type",
            "PATCH /api/admin/transport/tasks/{task_id}/sts/{st_number}/order",
            "GET /api/admin/transport/tasks/export.xlsx",
            "POST /api/admin/transport/clusters/{raion}/create-task",
            "GET /api/admin/transport/ws/status",
        ),
        source_evidence=("RRL_TRANSPORT_TASK", "RRL_SBORKA_PALLETS"),
        state_evidence=("created task", "assigned STs", "released STs", "route export"),
        functional_gates=tuple(f"tests/transport/test_sprint{i}_functional.py" for i in (2, 3, 4, 29, 34, 36, 38, 57, 88)),
        load_gates=tuple(f"tests/transport/transport_sprint{i}_load_test.py" for i in (2, 3, 4, 29, 34, 36, 38, 57, 88)),
        ui_gates=("tests/ui/transport_sprint60_95_ui_smoke.cjs",),
    ),
    BusinessProcess(
        process_id="fleet_driver_admin_and_availability",
        area="fleet",
        business_factors=("vehicle capacity", "transport type", "driver", "active/deleted flags", "availability forecast"),
        route_patterns=(
            "GET /api/admin/transport/vehicles",
            "GET /api/admin/transport/vehicles/full",
            "POST /api/admin/transport/vehicles",
            "PATCH /api/admin/transport/vehicles/{vehicle_id}",
            "DELETE /api/admin/transport/vehicles/{vehicle_id}",
            "GET /api/admin/transport/drivers",
            "GET /api/admin/transport/drivers/full",
            "POST /api/admin/transport/drivers",
            "PATCH /api/admin/transport/drivers/{driver_id}",
            "DELETE /api/admin/transport/drivers/{driver_id}",
            "GET /api/admin/transport/vehicles/available",
        ),
        source_evidence=("RRL_TR_VEHICLE", "RRL_DRIVERS", "RRL_TT_OPERATIONS"),
        state_evidence=("fleet CRUD", "driver CRUD", "green/yellow/red availability"),
        functional_gates=("tests/transport/test_sprint13_functional.py", "tests/transport/test_sprint97_98_functional.py", "tests/transport/test_wave3_business_factor_trace.py"),
        load_gates=("tests/transport/transport_sprint13_load_test.py", "tests/transport/transport_wave3_business_factor_load_test.py"),
        ui_gates=("tests/ui/transport_sprint13_ui_smoke.cjs", "tests/ui/transport_sprint97_98_ui_smoke.cjs"),
    ),
    BusinessProcess(
        process_id="map_vrp_planning",
        area="map_vrp",
        business_factors=("coordinates", "distance provider", "pallet capacity", "weight", "transport type", "time windows", "unload norm", "route score"),
        route_patterns=(
            "GET /api/admin/transport/planner/orders",
            "GET /api/admin/transport/routing/status",
            "POST /api/admin/transport/distance-matrix/rebuild",
            "POST /api/admin/transport/planner/solve",
            "GET /api/admin/transport/planner/solve/{job_id}/stream",
            "DELETE /api/admin/transport/planner/solve/{job_id}",
            "POST /api/admin/transport/planner/apply",
            "GET /api/admin/transport/planner/metrics",
            "GET /api/admin/transport/planner/templates",
            "GET /api/admin/transport/planner/history",
            "GET /api/admin/transport/planner/demand-forecast",
        ),
        source_evidence=("RRL_ADDR", "RRL_ADDR_DISTANCE_MATRIX", "RRL_PLANNER_PLANS", "RRL_SBORKA_PALLETS"),
        state_evidence=("saved plan", "route stops", "applied tasks", "history/template rows"),
        functional_gates=(
            "tests/transport/test_sprint7_functional.py",
            "tests/transport/test_sprint8_functional.py",
            "tests/transport/test_sprint9_functional.py",
            "tests/transport/test_sprint10_functional.py",
            "tests/transport/test_sprint101_102_functional.py",
            "tests/transport/test_final_vrp_daily_acceptance.py",
            "tests/transport/test_wave3_business_factor_trace.py",
        ),
        load_gates=("tests/transport/transport_sprint7_load_test.py", "tests/transport/transport_sprint8_load_test.py", "tests/transport/transport_sprint9_load_test.py", "tests/transport/transport_sprint10_load_test.py", "tests/transport/transport_wave3_business_factor_load_test.py"),
        ui_gates=("tests/ui/transport_sprint7_ui_smoke.cjs", "tests/ui/transport_sprint8_ui_smoke.cjs", "tests/ui/transport_sprint9_ui_smoke.cjs", "tests/ui/transport_sprint10_ui_smoke.cjs"),
        e2e_gates=("tests/transport/test_final_vrp_daily_acceptance.py",),
    ),
    BusinessProcess(
        process_id="arm_gantt_plan_fact",
        area="arm_gantt",
        business_factors=("operation norm", "planned time", "fact time", "vehicle Gantt", "delta", "rest/load conflict"),
        route_patterns=(
            "POST /api/admin/transport/tasks/{task_id}/plan-operations",
            "GET /api/admin/transport/tasks/{task_id}/operations",
            "PATCH /api/admin/transport/operations/{op_id}/fact",
            "GET /api/admin/transport/vehicles/gantt",
            "GET /api/admin/transport/plan-fact",
        ),
        source_evidence=("RRL_TT_OPERATIONS", "RRL_TRANSPORT_NORMS", "RRL_TRANSPORT_TASK"),
        state_evidence=("operation rows", "fact start/end", "plan-fact deltas"),
        functional_gates=tuple(f"tests/transport/test_sprint{i}_functional.py" for i in (11, 12, 13, 14)),
        load_gates=tuple(f"tests/transport/transport_sprint{i}_load_test.py" for i in (11, 12, 13, 14)),
        ui_gates=tuple(f"tests/ui/transport_sprint{i}_ui_smoke.cjs" for i in (11, 12, 13, 14)),
    ),
    BusinessProcess(
        process_id="billing_lifecycle_and_protection",
        area="billing",
        business_factors=("carrier", "price", "billing order", "closed", "paid", "billed trip protection", "exports"),
        route_patterns=(
            "GET /api/admin/transport/billing/orders",
            "GET /api/admin/transport/billing/orders/export.xlsx",
            "POST /api/admin/transport/billing/orders",
            "GET /api/admin/transport/billing/orders/{order_id}",
            "PATCH /api/admin/transport/billing/orders/{order_id}/close",
            "PATCH /api/admin/transport/billing/orders/{order_id}/pay",
            "GET /api/admin/transport/billing/orders/{order_id}/tasks",
            "GET /api/admin/transport/billing/orders/{order_id}/export.xlsx",
            "POST /api/admin/transport/billing/orders/{order_id}/tasks",
            "GET /api/admin/transport/tasks/{task_id}/billing",
            "POST /api/admin/transport/tasks/{task_id}/billing/open",
            "DELETE /api/admin/transport/billing/orders/{order_id}/tasks/{tt_id}",
            "POST /api/admin/transport/tasks/{task_id}/recalculate-price",
            "PATCH /api/admin/transport/tasks/{task_id}/price",
            "GET /api/admin/transport/billing/companies",
        ),
        source_evidence=("RRL_BILL_ORDERS", "RRL_TRANSPORT_TASK", "RRL_BILL_COMPANY"),
        state_evidence=("PAY_ORDER_ID", "PRICE", "CLOSED", "PAYED", "export payload"),
        functional_gates=tuple(f"tests/transport/test_sprint{i}_functional.py" for i in range(15, 29)),
        load_gates=tuple(f"tests/transport/transport_sprint{i}_load_test.py" for i in range(15, 29)),
        ui_gates=tuple(f"tests/ui/transport_sprint{i}_ui_smoke.cjs" for i in range(15, 29)),
    ),
    BusinessProcess(
        process_id="dispatcher_ux_surface_30_95",
        area="dispatcher_ux",
        business_factors=("sorting", "filters", "selection", "readiness", "exports", "keyboard actions", "visible totals", "print/copy UX"),
        route_patterns=(),
        source_evidence=("TransportDispatchPage.tsx", "available ST/task response contracts"),
        state_evidence=("client state", "localStorage", "CSV/clipboard/print payloads"),
        functional_gates=tuple(f"tests/transport/test_sprint{i}_functional.py" for i in range(30, 96)),
        load_gates=tuple(f"tests/transport/transport_sprint{i}_load_test.py" for i in range(30, 96)),
        ui_gates=("tests/ui/transport_sprint60_95_ui_smoke.cjs",),
    ),
    BusinessProcess(
        process_id="user_rights_and_permissions",
        area="admin_rights",
        business_factors=("RUSERS", "USER_GROUP", "RIGHTS", "GLOBAL_ADMIN wildcard", "transport permissions", "billing permissions"),
        route_patterns=(
            "GET /api/admin/users",
            "POST /api/admin/users",
            "PATCH /api/admin/users/{login}",
            "DELETE /api/admin/users/{login}",
            "PATCH /api/admin/users/{login}/password",
            "GET /api/admin/users/groups",
            "POST /api/admin/users/groups",
            "GET /api/admin/users/rights",
            "POST /api/admin/users/groups/{group}/rights",
            "DELETE /api/admin/users/groups/{group}/rights/{right}",
            "GET /api/admin/rights/users",
            "GET /api/admin/rights/groups",
            "POST /api/admin/rights/groups",
            "GET /api/admin/rights/groups/{group_id}/rights",
            "POST /api/admin/rights/groups/{group_id}/rights",
            "DELETE /api/admin/rights/groups/{group_id}/rights/{right_name}",
            "PUT /api/admin/rights/users/{user_id}/group",
        ),
        source_evidence=("RUSERS", "USER_GROUP", "RIGHTS"),
        state_evidence=("users list", "group rights", "permission mutation"),
        functional_gates=("tests/transport/test_sprint21_functional.py", "tests/transport/test_sprint99_100_functional.py"),
        load_gates=("tests/transport/transport_sprint21_load_test.py",),
        ui_gates=("tests/ui/transport_sprint21_ui_smoke.cjs", "tests/ui/transport_sprint99_100_ui_smoke.cjs"),
    ),
    BusinessProcess(
        process_id="driver_mobile_execution",
        area="driver_mobile",
        business_factors=("driver", "assigned trips", "ST composition", "operation start", "operation done", "offline sync contract"),
        route_patterns=(
            "GET /api/driver/trips",
            "GET /api/driver/trips/{task_id}/sts",
            "GET /api/driver/trips/{task_id}/ops",
            "POST /api/driver/ops/{op_id}/start",
            "POST /api/driver/ops/{op_id}/done",
        ),
        source_evidence=("RRL_TRANSPORT_TASK", "RRL_SBORKA_PALLETS", "RRL_TT_OPERATIONS"),
        state_evidence=("driver trip list", "operation facts"),
        functional_gates=("tests/transport/test_sprint103_107_functional.py",),
        ui_gates=("tests/ui/transport_sprint103_ui_smoke.cjs",),
    ),
    BusinessProcess(
        process_id="gps_geofence_tracking",
        area="gps",
        business_factors=("vehicle position", "track history", "geofence radius", "auto unload fact", "store coordinates"),
        route_patterns=(
            "POST /api/gps/track",
            "GET /api/admin/transport/geofences",
            "PATCH /api/admin/transport/geofences/{addr_id}",
            "GET /api/admin/transport/vehicles/positions",
            "GET /api/admin/transport/vehicles/{vehicle_id}/track",
        ),
        source_evidence=("RRL_VEHICLE_GPS_LAST", "RRL_VEHICLE_GPS_TRACK", "RRL_ADDR", "RRL_TT_OPERATIONS"),
        state_evidence=("last vehicle position", "track rows", "geofence fact update"),
        functional_gates=("tests/transport/test_sprint108_114_functional.py", "tests/transport/test_sprint115_119_functional.py"),
        ui_gates=("tests/ui/transport_sprint108_109_ui_smoke.cjs",),
    ),
    BusinessProcess(
        process_id="kpi_dashboard",
        area="kpi",
        business_factors=("fleet utilization", "closed trips", "regions", "billing totals", "carrier spend"),
        route_patterns=(
            "GET /api/admin/transport/kpi/fleet",
            "GET /api/admin/transport/kpi/summary",
            "GET /api/admin/transport/kpi/regions",
            "GET /api/admin/transport/kpi/billing",
            "GET /api/admin/transport/kpi/billing/by-company",
        ),
        source_evidence=("RRL_TRANSPORT_TASK", "RRL_SBORKA_PALLETS", "RRL_BILL_ORDERS"),
        state_evidence=("KPI aggregates", "billing aggregates"),
        functional_gates=("tests/transport/test_sprint108_114_functional.py",),
        ui_gates=("tests/ui/transport_sprint108_109_ui_smoke.cjs",),
    ),
    BusinessProcess(
        process_id="tariffs_and_external_exports",
        area="tariffs",
        business_factors=("region", "transport type", "base price", "price per km", "price per pallet", "1C export contract"),
        route_patterns=(
            "GET /api/admin/transport/tariffs",
            "GET /api/admin/transport/tariffs/table-info",
        ),
        source_evidence=("RRL_TT_PRICE/RRL_TRANSPORT_PRICE/RRL_TARIFF", "RRL_BILL_ORDERS"),
        state_evidence=("tariff rows", "table-info columns"),
        functional_gates=("tests/transport/test_sprint108_114_functional.py",),
        ui_gates=("tests/ui/transport_sprint108_109_ui_smoke.cjs",),
    ),
)


def _router_routes() -> set[str]:
    from api.wms_api_server.app.routers import admin_rights, driver_mobile, gps, transport, transport_kpi, transport_tariffs, users

    routers = (
        transport.router,
        transport_kpi.router,
        transport_tariffs.router,
        driver_mobile.router,
        gps.router,
        users.router,
        admin_rights.router,
    )
    routes: set[str] = set()
    for router in routers:
        for route in router.routes:
            methods = getattr(route, "methods", None)
            if not methods:
                continue
            for method in sorted(set(methods) - {"HEAD", "OPTIONS"}):
                routes.add(f"{method} {route.path}")
    return routes


def _owned_routes() -> dict[str, list[str]]:
    actual = _router_routes()
    ownership: dict[str, list[str]] = {route: [] for route in actual}
    for process in PROCESSES:
        for pattern in process.route_patterns:
            matched = False
            for route in actual:
                if fnmatch(route, pattern):
                    ownership[route].append(process.process_id)
                    matched = True
            assert matched, f"{process.process_id} has stale route pattern: {pattern}"
    return ownership


def _paths_exist(paths: Iterable[str]) -> list[str]:
    return [path for path in paths if not (ROOT / path).exists()]


def test_wave3_registry_covers_every_tms2_http_endpoint():
    ownership = _owned_routes()
    unowned = sorted(route for route, owners in ownership.items() if not owners)
    assert not unowned, "TMS-2 endpoints without Wave 3 business-process owner:\n" + "\n".join(unowned)


def test_wave3_routes_have_single_primary_owner():
    ownership = _owned_routes()
    duplicate = {route: owners for route, owners in ownership.items() if len(owners) > 1}
    assert not duplicate, f"Routes have ambiguous Wave 3 ownership: {duplicate}"


def test_wave3_every_process_has_factor_evidence_and_real_gates():
    for process in PROCESSES:
        assert process.business_factors, f"{process.process_id}: missing business factors"
        assert process.source_evidence, f"{process.process_id}: missing source evidence"
        assert process.state_evidence, f"{process.process_id}: missing state evidence"
        assert process.functional_gates, f"{process.process_id}: missing functional gates"
        assert process.load_gates or process.ui_gates or process.e2e_gates, (
            f"{process.process_id}: missing load/UI/E2E evidence"
        )
        missing = _paths_exist(process.functional_gates + process.load_gates + process.ui_gates + process.e2e_gates)
        assert not missing, f"{process.process_id}: referenced gates do not exist: {missing}"


def test_wave3_registry_has_expected_system_areas():
    expected = {
        "dispatcher",
        "dispatcher_ux",
        "fleet",
        "map_vrp",
        "arm_gantt",
        "billing",
        "admin_rights",
        "driver_mobile",
        "gps",
        "kpi",
        "tariffs",
    }
    actual = {process.area for process in PROCESSES}
    assert expected <= actual, f"Wave 3 registry misses system areas: {sorted(expected - actual)}"


def test_wave3_release_runners_include_full_system_coverage_lock():
    ps1 = (ROOT / "scripts/tms2-release-gate.ps1").read_text(encoding="utf-8")
    py = (ROOT / "scripts/tms2_release_gate.py").read_text(encoding="utf-8")
    assert "test_wave3_full_system_coverage.py" in ps1
    assert "test_wave3_full_system_coverage.py" in py
