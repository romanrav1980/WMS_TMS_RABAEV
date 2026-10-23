"""Real Oracle/native trip, controlled routing response; no physical stock writes."""
from datetime import datetime
import json
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.plan_preflight import TransportPreflight
from app.modules.transport.contracts_plan import TransportPlanError
from tools.mcp.tms_mcp_server import oracle_connection

TAG = "RD23" + uuid4().hex[:10]
WARE = 240000000 + secrets.randbelow(9000000)
DEPOT, STORE = TAG + ".DEPOT", TAG + ".STORE"
report = {"status": "FAIL", "provider": "LIVE ROAD PROVIDER" if any(x in sys.argv for x in ("--live-provider", "--served-api")) else "CONTROLLED TEST RESPONSE, not a live road calculation", "checks": [], "timings": []}
trip = pallet = None
depot_version = 0
created = False
calls = 0


def stock(q):
    q.execute("select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID")
    return [list(r) for r in q]


def depot(address, version):
    from app.modules.transport.infrastructure.warehouse_depot import WarehouseDepot
    return WarehouseDepot(OracleGateway()).apply(TAG + ".depot." + str(version),
        dict(warehouse_id=WARE, expected_version=version, depot_address=address,
             reason="Owned route cache acceptance"), "admin")["version"]

def provider(points):
    global calls
    calls += 1
    assert points == [(56.8389, 60.5975), (56.8519, 60.6122)]
    if "--live-provider" in sys.argv:
        from app.transport_preflight_composition import road_costs
        return road_costs(points)
    return "osrm", [[0, 9], [10, 0]], [[0, 15], [20, 0]]


def command(service, operation, body):
    start = time.perf_counter()
    try:
        if "--served-api" in sys.argv:
            from live_document_acceptance import http
            status,result=http('POST','/api/transport/preflight/road-refreshes',dict(body,operation_id=operation))
            report.setdefault('http',[]).append(dict(status=status,result=result))
            if status!=200:
                detail=result['detail'];raise TransportPlanError(detail['code'],detail.get('message',detail['code']),status)
            return result
        from fastapi.testclient import TestClient
        from app.main import app
        from app.modules.transport.contracts_preflight import transport_preflight_service
        app.dependency_overrides[transport_preflight_service] = lambda: service
        try:
            response = TestClient(app).post("/api/transport/preflight/road-refreshes", json=dict(body, operation_id=operation), auth=("admin", "admin123"))
            result = response.json()
            report.setdefault("http", []).append(dict(status=response.status_code, result=result))
            if response.status_code != 200:
                detail = result["detail"]
                raise TransportPlanError(detail["code"], detail.get("message", detail["code"]), response.status_code)
            return result
        finally:
            app.dependency_overrides.pop(transport_preflight_service, None)
    finally:
        report["timings"].append(round((time.perf_counter() - start) * 1000, 2))


if __name__ == "__main__":
    try:
        with oracle_connection() as c:
            q = c.cursor(); q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
            assert q.fetchone() == ("RABAEV", "orcl")
            q.execute('select (select count(*)from RRL_WARES where ID=:w)+(select count(*)from RRL_CELLS where WARE_ID=:w)+(select count(*)from RRL_TRADE_SITE where WARE_ID=:w)from dual',w=WARE)
            assert q.fetchone()==(0,), 'Fixture warehouse must be absent before any write'
            before = stock(q)
            q.execute("select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG"); marker = q.fetchone()[0]
            q.execute("insert into RRL_WARES(ID,NAME)values(:w,:n)", w=WARE, n="TRADECASE QA road " + TAG)
            for address, lat, lon in [(DEPOT, 56.8389, 60.5975), (STORE, 56.8519, 60.6122)]:
                q.execute("insert into RRL_ADDR(ADDR,SHIROTA,DOLGOTA,DELETED3)values(:a,:lat,:lon,0)", a=address, lat=lat, lon=lon)
            c.commit(); created = True
        depot_version = depot(DEPOT, 0)
        with oracle_connection() as c:
            q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"]); out = q.var(oracledb.DB_TYPE_NUMBER)
            q.callproc("RRL_TRANSPORT_EDIT_API.create_trip", ["1", datetime(2026, 10, 23), "admin", out])
            trip = int(out.getvalue())
            pallet = int(q.callfunc("RRL_SBORKA_PALLETS_ADD2", oracledb.DB_TYPE_NUMBER,
                                   [TAG + ".ST", STORE, 1, TAG + ".PALLET", "1", datetime(2026, 10, 23), "", "admin", WARE]))
            q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:t where ID=:p", t=trip, p=pallet)
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
            c.commit()
        service = TransportPreflight(OracleGateway(), provider)
        snapshot = service.road_legs(trip, "", 24, "admin")
        body = dict(trip_id=trip, expected_version=snapshot["route_input_version"], source_hash=snapshot["source_hash"])
        first = command(service, TAG + ".refresh", body)
        assert first["updated_legs"] == 2 and calls == (0 if "--served-api" in sys.argv else 1)
        assert command(service, TAG + ".refresh", body) == first and calls == (0 if "--served-api" in sys.argv else 1)
        report["checks"].append("Actual native snapshot, atomic cache publication and exact replay; provider spy confirms no recomputation only in the in-process mode")
        current = service.road_legs(trip, "", 24, "admin")
        assert current["drive_min"] > 0 and current["drive_back_min"] > 0 and current["unknown_leg_count"] == 0
        report["road_result"] = current
        assert current["operational_admission"] is False
        try:
            command(service, TAG + ".stale", body)
            raise AssertionError("Stale basis accepted")
        except TransportPlanError as error:
            assert error.code == "ROAD_REFRESH_SOURCE_CHANGED"
        report["checks"].append("Stale source rejected; no extra provider call; native read returns the two directed legs")
        changed = dict(body, expected_version=body["expected_version"] + 1)
        try:
            command(service, TAG + ".refresh", changed)
            raise AssertionError("Changed request accepted")
        except TransportPlanError as error:
            assert error.code == "ROAD_REFRESH_OPERATION_CONFLICT"
        with oracle_connection() as c:
            q = c.cursor(); q.execute("select count(*)from RRL_TT_ROAD_REFRESH where TT_ID=:t", t=trip)
            assert q.fetchone() == (1,)
        report["checks"].append("Changed-body replay rejected; one durable receipt")
        report["status"] = "PASS"
    finally:
        if created:
            if depot_version:
                depot_version = depot(None, depot_version)
            with oracle_connection() as c:
                q = c.cursor()
                # Only own empty planning metadata and synthetic road pairs; receipt history stays immutable.
                if pallet is not None:
                    q.execute("delete from RRL_SBORKA_PALLETS where ID=:p and PALLET_UID=:u", p=pallet, u=TAG + ".PALLET")
                if trip is not None:
                    q.execute("update RRL_TRANSPORT_TASK set DELETED=1 where ID=:t and USER_ID='admin'", t=trip)
                q.execute("delete from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR in(:d,:s)or TO_ADDR in(:d,:s)", d=DEPOT, s=STORE)
                q.execute("update RRL_ADDR set DELETED3=1 where ADDR in(:d,:s)", d=DEPOT, s=STORE)
                c.commit()
                assert stock(q) == before
                q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'"); assert q.fetchone() == (0,)
                q.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only", m=marker)
                report.update(fixture_retired=True, stock=before, slow_sql=[list(r) for r in q])
        report.update(trip=trip, warehouse=WARE, tag=TAG)
        path = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T09" / (TAG + ".json")
        path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(dict(status=report["status"], checks=len(report["checks"]), evidence=str(path))))
