"""Native scoped wave reads on existing dev waves, metadata fixtures cleaned."""
import json,secrets,sys
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
    gateway=OracleGateway();access=AccessMetadataService(gateway);prefix="wv"+uuid4().hex[:9]
    actor=prefix+"u";role=prefix+"r";password=secrets.token_urlsafe(24);now=datetime.now(timezone.utc);checks=[]
    def command(kind,payload):
        return access.command("admin",normalize(Command(operation_id=prefix+":"+uuid4().hex,command_type=kind,payload=payload),"ACCESS"))
    def grant(warehouse):
        command("ASSIGN",dict(assignment_id=prefix+str(warehouse),username=actor,role_id=role,scope_kind="WAREHOUSE",scope_id=str(warehouse),membership="CURRENT",valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),reason="Isolated wave scope acceptance",expected_version=0))
    try:
        with gateway.transaction("wave.scope.fixture") as cur:
            cur.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Wave fixture',:password,'NONE',1,0,1)",id=actor,password=password)
        command("ROLE_SAVE",dict(role_id=role,title="Wave view fixture",permissions=["pick_wave_view"],active=True,expected_version=0));grant(16447976)
        with httpx.Client(base_url="http://127.0.0.1:8088",auth=(actor,password),timeout=30) as c:
            for suffix in ("","/header","/readiness","/pick-readiness","/execution"):
                r=c.get("/api/picking/waves/561"+suffix);assert r.status_code==200,(suffix,r.status_code,r.text[:300])
            checks.append("native_only_wave_header_detail_readiness_pick_execution")
            r=c.get("/api/resources/workload/waves/561/time-context");assert r.status_code==200,r.text[:300]
            checks.append("native_only_approved_time_read_context")
            bundle=c.post("/api/picking/shift-overview",json={"warehouse_id":16447976,"wave_ids":[561]})
            assert bundle.status_code==200,bundle.text[:300]
            data=bundle.json();assert data["snapshot"]=="ORACLE_READ_ONLY" and data["all_sources_available"] is True
            assert data["stock_changed"] is False and data["waves"][0]["wave_id"]==561
            assert c.post("/api/picking/shift-overview",json={"warehouse_id":16447976,"wave_ids":[561,560]}).status_code==404
            assert c.post("/api/picking/shift-overview",json={"warehouse_id":16447976,"wave_ids":[561,561]}).status_code==422
            assert c.post("/api/picking/shift-overview",json={"warehouse_id":16447976,"wave_ids":list(range(1,52))}).status_code==422
            checks.append("single_snapshot_bundle_all_sources_no_foreign_or_unbounded_batch")
            own_repl=c.get("/api/inventory/replenishment-progress?wave_id=561&limit=100")
            assert own_repl.status_code==200,own_repl.text[:300]
            assert c.get("/api/inventory/replenishment-progress?wave_id=560&limit=100").status_code==403
            checks.append("replenishment_progress_actual_wave_scope")
            for suffix in ("","/header","/readiness","/pick-readiness","/execution"):
                r=c.get("/api/picking/waves/560"+suffix);assert r.status_code==403,(suffix,r.status_code,r.text[:300])
            assert c.get("/api/resources/workload/waves/560/time-context").status_code==403
            checks.append("foreign_wave_all_direct_reads_denied")
            r=c.get("/api/picking/waves?limit=10");assert r.status_code==200,r.text[:300]
            assert r.json() and all(w["ware_id"]==16447976 for w in r.json())
            checks.append("single_granted_warehouse_queue_default")
            grant(31217707)
            assert c.get("/api/picking/waves?limit=10").status_code==422
            r=c.get("/api/picking/waves?ware_id=31217707&limit=10");assert r.status_code==200,r.text[:300]
            assert r.json() and all(w["ware_id"]==31217707 for w in r.json())
            checks.append("multiple_grants_require_explicit_warehouse")
            command("REVOKE",dict(assignment_id=prefix+"16447976",expected_version=1,reason="Revoke fixture read scope"))
            assert c.get("/api/picking/waves/561").status_code==403
            checks.append("revoked_wave_read_denied")
    finally:
        with gateway.transaction("wave.scope.cleanup") as cur:
            cur.execute("delete from RRL_ACCESS_ASSIGNMENT where USERNAME=:actor",actor=actor)
            for table in ("RRL_ACCESS_ROLE_RIGHT","RRL_ACCESS_ROLE"):
                cur.execute("delete from "+table+" where ROLE_ID=:role",role=role)
            cur.execute("delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix",prefix=prefix+":%")
            cur.execute("delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix",prefix=prefix+":%")
            cur.execute("delete from RUSERS where ID=:actor",actor=actor)
    result={"status":"PASS","checks":checks,"fixture_cleaned":True,"wave_effect":"READ_ONLY","stock_effect":"NONE"}
    target=ROOT/"reports/retailcase/2026-10-15/wave-scope";target.mkdir(parents=True,exist_ok=True)
    (target/"http-native.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))

if __name__=="__main__":main()
