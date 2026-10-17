"""Native empty-trip vehicle assignment; all headers and edits are caller-rolled back."""
import json
import sys
from datetime import date
from pathlib import Path

import oracledb

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection
from app.modules.transport.public import create_existing_trip, update_existing_trip
from dispatch_edit_scope_smoke import RollbackGateway


def output_json(value):
    raw = value.read() if hasattr(value, "read") else value
    return json.loads(raw)


def reject_check(cur, vehicle, sources, complete, marker):
    result = cur.var(oracledb.DB_TYPE_CLOB)
    try:
        cur.callproc("RRL_TRANSPORT_PLAN_RULES.check_vehicle", [vehicle, json.dumps(sources), complete, result])
    except oracledb.DatabaseError as exc:
        assert marker in str(exc), str(exc)
    else:
        raise AssertionError("Native validation accepted " + marker)


def configured_vehicle(cur):
    cur.execute("""select ID,NUM from RRL_TR_VEHICLE v where nvl(BLOCKED,0)=0
        and nvl(DELETED,0)=0 and PALLETS>0 and MAX_WEIGHT_KG>0 and TR_TYPE is not null
        and exists(select 1 from RRL_VEHICLE_PROFILE_HIST h where h.VEHICLE_ID=v.ID)
        order by ID fetch first 20 rows only""")
    candidates = cur.fetchall()
    for vehicle, number in candidates:
        result = cur.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile", oracledb.DB_TYPE_CLOB, [vehicle])
        profile = output_json(result)
        if profile.get("state") == "READY" and "floor_capacity" in profile.get("profile", {}):
            return int(vehicle), number
    raise AssertionError("No READY configured vehicle fixture available")


def main():
    checks = []
    created = None
    with oracle_connection() as connection:
        cur = connection.cursor()
        try:
            vehicle, number = configured_vehicle(cur)
            gateway = RollbackGateway(cur)
            created = create_existing_trip(gateway, "10", date(2030, 1, 15), "admin")
            result = update_existing_trip(gateway, created, {"transport": number}, "admin")
            assert result["declared_places"] == 0 and result["declared_weight_kg"] == "0", result
            assert result["stock_changed"] is False and result["physical_load_admission"] is False
            assert result["floor_capacity"]["counts"] == []
            checks.append("configured_vehicle_assigned_to_empty_owned_draft")
            reject_check(cur, vehicle, [], 1, "PLAN_TARE_ST_BOUND_200")
            reject_check(cur, vehicle, ["BOUND"] * 201, 0, "PLAN_TARE_ST_BOUND_200")
            reject_check(cur, vehicle, [42], 0, "PLAN_TARE_ST_NUMBER_REQUIRED")
            reject_check(cur, vehicle, [""], 0, "PLAN_TARE_ST_NUMBER_REQUIRED")
            checks.extend(["complete_empty_not_admitted", "nonempty_bound_200_preserved",
                           "nonempty_numeric_source_rejected", "nonempty_blank_source_rejected"])
            floor = output_json(cur.callfunc("RRL_VEHICLE_PROFILE_API.check_floor_capacity",
                oracledb.DB_TYPE_CLOB, [vehicle, "[]", 1]))
            assert floor["status"] == "TARE_TYPE_UNCONFIRMED", floor
            checks.append("unknown_tare_proof_stays_unconfirmed")
        finally:
            connection.rollback()
        cur.execute("select count(*) from RRL_TRANSPORT_TASK where ID=:trip", trip=created)
        assert cur.fetchone()[0] == 0
        checks.append("created_header_and_vehicle_assignment_rolled_back")
    report = dict(status="PASS", checks=checks, business_commit=False, stock_effect="NONE")
    target = ROOT / "reports/retailcase/2026-10-15/dispatch-scope/empty-draft.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
