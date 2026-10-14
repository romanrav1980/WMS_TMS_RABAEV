"""One READ ONLY snapshot and original native checks; no validation token/write."""
import json
from hashlib import sha256
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_plan import TransportPlanError
from ..domain.preflight_routes import plan_routes
from ..domain.temperature_preflight import temperature_preflight


from .preflight_scope import dispatcher
from ...inventory.public import read_shipping_temperature_requirements


def native_check(cur: Any, vehicle: int | None, numbers: list[str], complete: int) -> dict[str, Any]:
    result = cur.var(oracledb.DB_TYPE_CLOB)
    try:
        cur.callproc("RRL_TRANSPORT_PLAN_RULES.check_vehicle",
                     [vehicle, json.dumps(numbers, ensure_ascii=False), complete, result])
        return {"status": "CHECKED_CURRENT_NATIVE_RULES", "result": read_oracle_json(result.getvalue())}
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 1403:
            return {"status": "BLOCKED", "code": "PLAN_CURRENT_VEHICLE_NOT_FOUND"}
        if 20800 <= code <= 20999:
            message = str(exc.args[0]).split("\n", 1)[0]
            return {"status": "BLOCKED", "code": message.partition(":")[2].strip()}
        raise


def current_sources(cur: Any, numbers: list[str], actor: str, trip: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset in range(0, len(numbers), 200):
        batch = numbers[offset:offset + 200]
        binds = {f"st{index}": number for index, number in enumerate(batch)}
        names = ",".join(f":st{index}" for index in range(len(batch)))
        binds["row_limit"] = 5001 - len(rows)
        cur.execute(
            """select p.ID,p.ST_NUMBER,p.WARE_ID,p.TRANSTASK_ID,p.CONDITION,
              (select count(*) from RRL_TT_HU_LOAD_ST m
               join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID
               join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
               join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID
               join RRL_TR_VEHICLE v on v.ID=l.VEHICLE_ID
               where m.SBORKA_PALLET_ID=p.ID and m.ACTIVE_FLAG=1
                and l.TT_ID=p.TRANSTASK_ID and t.TRANSPORT=l.VEHICLE_NUMBER
                and v.NUM=l.VEHICLE_NUMBER and l.STATUS='LOADED'
                and l.CUSTODY_RELEASED_AT is null and o.STATE='APPLIED'
                and t.CONDITION='Спланирован' and nvl(t.DELETED,0)=0
                and nvl(t.PAY_ORDER_ID,0)=0) RETAINED_LOAD_PROOFS
              from RRL_SBORKA_PALLETS p """
            f"where p.ST_NUMBER in ({names}) order by p.ID fetch first :row_limit rows only", binds,
        )
        rows.extend(dict(zip(["id", "st_number", "warehouse_id", "trip_id", "condition", "retained_load_proofs"], row))
                    for row in cur.fetchall())
        if len(rows) > 5000:
            raise TransportPlanError("PLAN_ACTUAL_ROWS_BOUND_5000", "Превышена граница исходных строк")
    rows.sort(key=lambda row: row["id"])
    for ware in sorted({row["warehouse_id"] for row in rows}, key=lambda value: (value is None, value or 0)):
        try:
            cur.callproc("RRL_TRANSPORT_PLAN_RULES.assert_actor", [actor, ware])
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0], "code", 0)
            if code == 20882:
                raise TransportPlanError("PLAN_CURRENT_WARE_ACTOR_REQUIRED", "Недоступный склад текущей СТ", 403) from exc
            if 20800 <= code <= 20999:
                raise TransportPlanError("PLAN_CURRENT_WARE_REQUIRED", "Недействующий склад текущей СТ") from exc
            raise
    return rows


def route_result(cur: Any, route: dict[str, Any], rows: list[dict[str, Any]], trip: int | None, actor: str) -> dict[str, Any]:
    numbers = route["stops"]
    selected = [row for row in rows if row["st_number"] in numbers]
    found = {row["st_number"] for row in selected}
    blockers = [{"code": "PLAN_ST_NOT_FOUND", "st_number": number} for number in numbers if number not in found]
    blockers += [{"code": "PLAN_ST_FOREIGN_OR_SHIPPED", "st_number": row["st_number"], "source_id": row["id"]}
                 for row in selected if (row["trip_id"] or 0) not in (0, trip or 0)
                 or (row["condition"] == 2 and not (
                     trip is not None and row["trip_id"] == trip and row["retained_load_proofs"] == 1))]
    cur.execute("select NUM,REF_REJIM from RRL_TR_VEHICLE where ID=:id", id=route["vehicle_id"])
    vehicle_row = cur.fetchone()
    current_plate = vehicle_row[0] if vehicle_row else None
    if "vehicle_num" in route and (not route["vehicle_num"] or route["vehicle_num"] != current_plate):
        blockers.append({"code": "PLAN_VEHICLE_ID_PLATE_CONFLICT"})
    try:
        thermal = read_shipping_temperature_requirements(cur, [int(row["id"]) for row in selected], actor)
    except PermissionError as exc:
        raise TransportPlanError("PLAN_THERMAL_CURRENT_SCOPE_REQUIRED", str(exc), 403) from exc
    except ValueError as exc:
        raise TransportPlanError("PLAN_THERMAL_READ_REJECTED", str(exc), 409) from exc
    current_profile = None
    if vehicle_row:
        current_profile=read_oracle_json(cur.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile",oracledb.DB_TYPE_CLOB,[route["vehicle_id"]]))
    thermal["planning"]=temperature_preflight(thermal,current_profile)
    thermal["vehicle_legacy_mode"] = vehicle_row[1] if vehicle_row else None
    capacity = native_check(cur, route["vehicle_id"], numbers, 0)
    application = native_check(cur, route["vehicle_id"], numbers, 1)
    return {
        "vehicle_id": route["vehicle_id"], "current_vehicle_num": current_plate, "st_numbers": numbers, "current_sources": selected,
        "source_blockers": blockers, "capacity_and_type": capacity, "temperature_requirements": thermal,
        "current_native_application": application,
        "status": "BLOCKED" if blockers or application["status"] == "BLOCKED" else "CURRENT_NATIVE_RULES_CHECKED",
        "schedule_status": route.get("schedule_status", "UNAVAILABLE"),
        "operational_admission": False,
        "unverified_constraints": ["AWARE_TIME_SCHEDULE", "DRIVER_AND_BREAKS", "WAREHOUSE_RELEASE_AND_LOADING", "VEHICLE_TEMPERATURE_RANGE_AND_FACT"],
    }


class TransportPreflight:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def trip_time(self, trip: int, zone: str, actor: str) -> dict[str, Any]:
        from .time_preflight import trip_time_preview
        return trip_time_preview(self.gateway, trip, zone, actor)

    def time_context(self, trip: int, actor: str) -> dict[str, Any]:
        from .trip_time_approval import time_context
        return time_context(self.gateway, trip, actor)

    def coordination(self, trip: int, actor: str) -> dict[str, Any]:
        from .coordination_preflight import coordination
        return coordination(self.gateway, trip, actor)

    def approve_time(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        from .trip_time_approval import approve_time
        return approve_time(self.gateway, operation, body, actor)

    def route_context(self, trip: int, actor: str) -> dict[str, Any]:
        from .route_input import route_context
        return route_context(self.gateway, trip, actor)

    def apply_route_input(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        from .route_input import apply_route_input
        return apply_route_input(self.gateway, operation, body, actor)

    def plan(self, plan: int, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Existing plan preflight READ ONLY snapshot") as cur:
            cur.execute("set transaction read only")
            dispatcher(cur, actor)
            cur.execute("select to_clob(PAYLOAD),APPLIED_AT from RRL_PLANNER_PLANS where ID=:id", id=plan)
            row = cur.fetchone()
            if row is None:
                raise TransportPlanError("PLAN_CURRENT_SOURCE_NOT_FOUND", "План отсутствует", 404)
            raw = row[0].read() if isinstance(row[0], oracledb.LOB) else row[0]
            if isinstance(raw, str) and len(raw) > 4194304:
                raise TransportPlanError("PLAN_SOURCE_BOUND_4MB", "Превышена граница исходного плана")
            if not isinstance(raw, str):
                raise TransportPlanError("PLAN_SOURCE_INVALID", "Отсутствует содержимое плана")
            try:
                routes = plan_routes(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise TransportPlanError("PLAN_SOURCE_INVALID", "Некорректный JSON плана") from exc
            numbers = [number for route in routes for number in route["stops"]]
            sources = current_sources(cur, numbers, actor, None)
            result = [route_result(cur, route, sources, None, actor) for route in routes]
        return {"plan_id": plan, "source_signature": sha256(raw.encode()).hexdigest(),
                "already_applied": row[1] is not None, "routes": result,
                "status": "BLOCKED" if row[1] is not None or any(r["status"] == "BLOCKED" for r in result) else "CURRENT_NATIVE_RULES_CHECKED",
                "read_only": True, "apply_requires_current_locked_recheck": True, "operational_admission": False}

    def trip(self, trip: int, additions: list[str], actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Existing manual trip preflight READ ONLY snapshot") as cur:
            cur.execute("set transaction read only")
            dispatcher(cur, actor)
            cur.execute("""select t.TRANSPORT,t.DELETED,t.CONDITION,t.PAY_ORDER_ID,v.ID
                from RRL_TRANSPORT_TASK t left join RRL_TR_VEHICLE v on v.NUM=t.TRANSPORT where t.ID=:id""", id=trip)
            header = cur.fetchone()
            if header is None:
                raise TransportPlanError("PLAN_CURRENT_SOURCE_NOT_FOUND", "Рейс отсутствует", 404)
            cur.execute("select distinct ST_NUMBER from RRL_SBORKA_PALLETS where TRANSTASK_ID=:id", id=trip)
            numbers = sorted(set(additions) | {row[0] for row in cur.fetchall()})
            if not 1 <= len(numbers) <= 200:
                raise TransportPlanError("PLAN_SELECT_1_200_STS", "Требуется от1 до200 СТ")
            sources = current_sources(cur, numbers, actor, trip)
            result = route_result(cur, {"vehicle_id": header[4], "stops": numbers}, sources, trip, actor)
            if (header[1] or 0) != 0 or header[2] == "Отгружен" or (header[3] or 0) > 0:
                result["source_blockers"].append({"code": "PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED"})
                result["status"] = "BLOCKED"
        return {"trip_id": trip, "routes": [result], "status": result["status"], "read_only": True,
                "apply_requires_current_locked_recheck": True, "operational_admission": False}

    def delivery_windows(self,trip: int,depot: str,max_age: int,zone: str,actor: str) -> dict[str,Any]:
        from .delivery_window_preview import delivery_window_preview
        return delivery_window_preview(self.gateway,trip,depot,max_age,zone,actor)

    def road_legs(self,trip: int,depot: str,max_age: int,actor: str) -> dict[str,Any]:
        from .road_leg_estimate import road_leg_estimate
        return road_leg_estimate(self.gateway,trip,depot,max_age,actor)
