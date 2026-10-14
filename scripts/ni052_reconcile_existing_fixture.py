"""Finish owned original-HU fixture without repeating stock setup."""
import sys,json
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.transport_composition import build_transport_loading
from app.modules.transport.public import unassign_st
from app.oracle_gateway import OracleGateway
s=get_settings();original=sys.argv[1];tag=original.split(":")[-1]
client=httpx.Client(auth=("admin","admin123"),timeout=35)
def http(method,path,body=None,status=200):
 response=client.request(method,"http://127.0.0.1:8088/api/transport/loading"+path,json=body)
 assert response.status_code==status,(response.status_code,response.text[:1000])
 return response.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 preview=http("GET","/reconciliation-preview?shipping_operation_id="+original);tree=preview["snapshot"];version=tree["nodes"][0]["version"]
 q.execute("select tt.ID,tt.TRANSPORT,tt.DOCK from RRL_TRANSPORT_TASK tt join RRL_SBORKA_PALLETS sp on sp.TRANSTASK_ID=tt.ID where sp.ST_NUMBER=:n",n="FULL.ST:"+tag);trip,plate,dock=q.fetchone()
 body={"operation_id":"RECON.LOAD:"+tag,"identifier":original,"expected_version":version,
  "expected_composition_signature":preview["composition_signature"],"scan_container":tree["root"],"scan_cell":tree["cell"],
  "transport_task_id":trip,"scan_vehicle":plate,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":version,
  "gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 result=http("POST","/confirm-reconciliation",body);assert result["stock_consumed_again"] is False
 assert http("POST","/confirm-reconciliation",body)==result
 duplicate={**body,"operation_id":"RECON.DUPLICATE:"+tag}
 assert "RECONCILE_ORIGINAL_ALREADY_LINKED" in http("POST","/confirm-reconciliation",duplicate,409)["detail"]["message"]
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(0,)
 loading=build_transport_loading()
 try:loading.depart("RECON.PENDING:"+tag,trip,"admin");raise AssertionError("Pending ST departed")
 except Exception as exc:assert "DEPART_WAITING_FOR_ACTUAL_LOADED_STS" in str(exc),str(exc)
 unassign_st(OracleGateway(),trip,"TT.PENDING:"+tag)
 departure=loading.depart("RECON.DEPART:"+tag,trip,"admin");assert not departure["stock_consumed_again"]
 assert loading.depart("RECON.DEPART:"+tag,trip,"admin")==departure
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID in(:a,:b)",a=body["operation_id"],b="RECON.DEPART:"+tag);assert q.fetchone()==(0,)
 q.execute("select SHIPPING_OPERATION_ID from RRL_TT_LOAD_RECONCILE where LOAD_OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(original,)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0) from RRL_REMAINS where UID_POLETA like :p",p="FULL.QA:"+tag+"%");assert q.fetchone()==(0,0)
 print("PASS actual API reconciliation/no second quantity posting/exact replay/duplicate denial/pending ST gate/departure replay; own P/H0 retained",flush=True)
