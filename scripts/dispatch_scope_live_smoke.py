"""Actual dispatcher routes with isolated native grants; existing trips are read only."""
import io
import json
import secrets
import sys
import zipfile
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"api/wms_api_server"),str(ROOT/"scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize


def main():
    gateway=OracleGateway();access=AccessMetadataService(gateway)
    prefix="ds"+uuid4().hex[:10];actor=prefix+"u";role=prefix+"r";password=secrets.token_urlsafe(24)
    now=datetime.now(timezone.utc);checks=[];assignment_ids=[]
    def command(kind,payload):
        return access.command("admin",normalize(Command(operation_id=prefix+":"+uuid4().hex,command_type=kind,payload=payload),"ACCESS"))
    def grant(warehouse):
        identity=prefix+str(warehouse);assignment_ids.append(identity)
        command("ASSIGN",dict(assignment_id=identity,username=actor,role_id=role,scope_kind="WAREHOUSE",scope_id=str(warehouse),membership="CURRENT",valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason="Isolated dispatcher read acceptance"))
        return identity
    try:
        with gateway.transaction("dispatch.scope.fixture") as cur:
            cur.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Dispatcher fixture',:password,'NONE',1,0,1)",id=actor,password=password)
        command("ROLE_SAVE",dict(role_id=role,title="Dispatcher read fixture",permissions=["transport_dispatch_view"],active=True,expected_version=0))
        first=grant(9102)
        with httpx.Client(base_url="http://127.0.0.1:8088/api/admin/transport",timeout=30) as c:
            assert c.get("/tasks?task_id=33641").status_code==401
            c.auth=(actor,password)
            for suffix in ("","/sts","/operations"):
                response=c.get("/tasks/33641"+suffix)
                assert response.status_code==200,(suffix,response.status_code,response.text[:300])
            rows=c.get("/tasks?task_id=33641&include_readiness=true")
            assert rows.status_code==200 and [r["ID"] for r in rows.json()]==[33641],rows.text[:300]
            checks.append("native_only_grant_list_detail_sts_operations")
            context=c.get("http://127.0.0.1:8088/api/transport/preflight/trips/33641/time-context")
            assert context.status_code==200,context.text[:300]
            assert c.get("http://127.0.0.1:8088/api/transport/preflight/trips/33638/time-context").status_code==403
            checks.append("native_only_temporal_view_actual_trip_scope")
            for suffix in ("","/sts","/operations"):
                response=c.get("/tasks/33638"+suffix)
                assert response.status_code==404,(suffix,response.status_code,response.text[:300])
            assert c.get("/tasks?task_id=33638").json()==[]
            checks.append("foreign_trip_direct_reads_and_list_hidden")
            exported=c.get("/tasks/export.xlsx?task_id=33641")
            assert exported.status_code==200
            with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
                assert archive.testzip() is None
                sheet=archive.read("xl/worksheets/sheet1.xml").decode()
                assert "33641" in sheet
            checks.append("scoped_export_valid_complete_xlsx")
            gantt=c.get("/vehicles/gantt?gantt_date=2030-01-15")
            assert gantt.status_code==200,gantt.text[:300]
            assert {op["tt_id"] for vehicle in gantt.json() for op in vehicle["operations"]}=={33641}
            checks.append("scoped_gantt_only_admitted_trip")
            grant(9201)
            assert c.get("/tasks/31050").status_code==404
            assert c.get("/tasks?task_id=31050").json()==[]
            checks.append("mixed_trip_partial_warehouse_grant_denied")
            grant(9202)
            mixed=c.get("/tasks/31050")
            assert mixed.status_code==200,mixed.text[:300]
            assert c.get("/tasks/31050/sts").status_code==200
            checks.append("mixed_trip_all_warehouses_granted")
            command("REVOKE",dict(assignment_id=prefix+"9201",expected_version=1,reason="Revoke fixture source grant"))
            assert c.get("/tasks/31050").status_code==404
            checks.append("revoke_denies_mixed_trip_immediately")
            bad=c.get("/tasks?date_from=2025-01-01&date_to=2026-10-15")
            assert bad.status_code==422,bad.text[:300]
            checks.append("wide_period_rejected_before_query")
    finally:
        with gateway.transaction("dispatch.scope.cleanup") as cur:
            cur.execute("delete from RRL_ACCESS_ASSIGNMENT where USERNAME=:actor",actor=actor)
            for table in ("RRL_ACCESS_ROLE_RIGHT","RRL_ACCESS_ROLE"):
                cur.execute("delete from "+table+" where ROLE_ID=:role",role=role)
            cur.execute("delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix",prefix=prefix+":%")
            cur.execute("delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix",prefix=prefix+":%")
            cur.execute("delete from RUSERS where ID=:actor",actor=actor)
    result={"status":"PASS","checks":checks,"fixture_cleaned":True,"business_data":"READ_ONLY","stock_effect":"NONE"}
    target=ROOT/"reports/retailcase/2026-10-15/dispatch-scope";target.mkdir(parents=True,exist_ok=True)
    (target/"http-native.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))

if __name__=="__main__":main()
