"""Current v7 approval/clock on the existing NI081 planning fixture; one caller rollback."""
import json
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import oracledb

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection
from app.modules.platform.public import AccessMetadataService, read_oracle_json
from app.modules.platform.api.metadata_inputs import Command, normalize
from app.modules.transport.public import update_existing_trip
from app.modules.transport.infrastructure.trip_time_approval import read_time_context
from app.modules.transport.infrastructure.timeline_clock import current_timeline_clock
from dispatch_edit_scope_smoke import RollbackGateway


def main():
    fixture = json.loads((ROOT / "reports/retailcase/2026-10-13/codex/NI081/fixture.json").read_text(encoding="utf-8"))
    assert fixture["trip_id"] == 33641 and fixture["planning_only"] and fixture["warehouse_id"] == 9102
    prefix = "clock" + uuid4().hex[:10]
    actor, foreign, role = prefix + "u", prefix + "f", prefix + "r"
    operation = prefix + ":approval"
    checks, timings = [], []
    with oracle_connection() as connection:
        cur = connection.cursor()
        gateway = RollbackGateway(cur)
        access = AccessMetadataService(gateway)
        def command(kind, payload):
            return access.command("admin", normalize(Command(operation_id=prefix + ":" + uuid4().hex,
                command_type=kind, payload=payload), "ACCESS"))
        def grant(username, warehouse):
            now = datetime.now(timezone.utc)
            command("ASSIGN", dict(assignment_id=username, username=username, role_id=role,
                scope_kind="WAREHOUSE", scope_id=str(warehouse), membership="CURRENT",
                valid_from=(now - timedelta(minutes=1)).isoformat(),
                valid_until=(now + timedelta(hours=1)).isoformat(), expected_version=0,
                reason="Caller rollback native timeline fixture"))
        def denied(username):
            try:
                current_timeline_clock(cur, fixture["trip_id"], username)
            except oracledb.DatabaseError as exc:
                assert getattr(exc.args[0], "code", 0) == 20882, str(exc)
            else:
                raise AssertionError("Foreign or revoked clock was exposed")
        before = read_time_context(cur, fixture["trip_id"], "admin")
        original_dock = before["source"]["dock"]
        connection.rollback()
        try:
            assert before["source"]["source_contract_version"] == 7
            assert before["source"]["warehouse_origins"][0]["depot_address"] == fixture["base"]
            assert all(leg["fresh"] for leg in before["source"]["route_material"]["legs"])
            body = dict(trip_id=fixture["trip_id"], expected_version=before["version"],
                source_hash=before["source_hash"], time_zone="Asia/Tbilisi",
                reason="Existing NI081 explicit region, native v7 proof; caller rollback")
            result = cur.var(oracledb.DB_TYPE_CLOB)
            started = perf_counter()
            cur.callproc("RRL_TT_TIME_API.approve", [operation, "admin", json.dumps(body), result])
            approved = read_oracle_json(result.getvalue())
            timings.append(dict(operation="native_v7_approval", ms=round((perf_counter() - started) * 1000, 2)))
            assert approved["source_contract_version"] == 7 and approved["route_schedule"]["issues"] == []
            assert approved["route_schedule"]["driver_breaks_included"] and not approved["operational_admission"]
            checks.append("native_v7_valid_route_approval_without_operational_admission")
            for username in (actor, foreign):
                cur.execute("""insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)
                    values(:id,'Clock fixture',:secret,'NONE',9102,0,0)""",
                    id=username, secret=secrets.token_urlsafe(24))
            command("ROLE_SAVE", dict(role_id=role, title="Clock read fixture",
                permissions=["transport_dispatch_view"], active=True, expected_version=0))
            grant(actor, fixture["warehouse_id"])
            grant(foreign, 9201)
            clock = current_timeline_clock(cur, fixture["trip_id"], actor)
            assert clock["status"] == "APPROVED" and clock["time_zone"] == "Asia/Tbilisi"
            assert len(clock["operations"]) == 2 and clock["version"] == before["version"] + 1
            for row in clock["operations"].values():
                assert row["plan_start_at"].endswith("+04:00") and row["plan_end_at"].endswith("+04:00")
            checks.append("native_view_only_actor_gets_two_approved_aware_operations")
            denied(foreign)
            checks.append("foreign_warehouse_clock_denied")
            update_existing_trip(gateway, fixture["trip_id"], {"dock": prefix}, "admin")
            changed = current_timeline_clock(cur, fixture["trip_id"], actor)
            assert changed["status"] == "SOURCE_CHANGED" and changed["operations"] == {}
            checks.append("source_change_removes_projection")
            update_existing_trip(gateway, fixture["trip_id"], {"dock": original_dock}, "admin")
            restored = current_timeline_clock(cur, fixture["trip_id"], actor)
            assert restored["status"] == "APPROVED" and restored["operations"] == clock["operations"]
            checks.append("exact_source_restoration_restores_original_projection")
            command("REVOKE", dict(assignment_id=actor, expected_version=1, reason="Caller rollback clock revoke"))
            denied(actor)
            checks.append("revocation_denies_previously_approved_clock")
        finally:
            connection.rollback()
        after = read_time_context(cur, fixture["trip_id"], "admin")
        assert after["source_hash"] == before["source_hash"] and after["version"] == before["version"]
        cur.execute("select count(*) from RRL_TT_TIME_APPROVAL where OPERATION_ID=:op", op=operation)
        assert cur.fetchone()[0] == 0
        cur.execute("select count(*) from RUSERS where ID in(:a,:b)", a=actor, b=foreign)
        assert cur.fetchone()[0] == 0
        connection.rollback()
        checks.append("approval_source_and_scoped_fixtures_rolled_back")
    report = dict(status="PASS", checks=checks, timings=timings, trip_id=fixture["trip_id"],
        source_contract_version=7, explicit_fixture_region="Asia/Tbilisi", projected_operations=2,
        approval_actor="admin", view_actor="NATIVE_VIEW_ONLY", road_provider="NI081TEST",
        business_commit=False, physical_site_verified=False, stock_effect="NONE")
    target = ROOT / "reports/retailcase/2026-10-15/resource-timeline/approved-clock-positive.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
