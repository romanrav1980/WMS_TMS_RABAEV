"""Actual original accepted receipt approval: bounded cap, source, exact retry."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
client=httpx.Client(auth=("admin","admin123"),timeout=30)
source="STORE.RECEIPT:bea258a7dd"
def call(method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1400]);return r.json()
prefix="/api/delivery/store-returns/"+source
original=call("GET",prefix);line=original["lines"][0];assert line["available_for_approval"]=="2",original
body={"operation_id":"STORE.RETURN:"+tag,"line_no":1,"quantity":"1","disposition":"REUSE","reason":"Own returned complete ordinary box","decision_reference":"Own Supply Chain approval "+tag,"complete_good_box":True}
bad=call("POST",prefix+"/approve",{**body,"operation_id":"STORE.RETURN.BADBOX:"+tag,"complete_good_box":False},409);assert "STORE_RETURN_REUSE_COMPLETE_GOOD_BOX_REQUIRED" in bad["detail"]["message"]
bad=call("POST",prefix+"/approve",{**body,"operation_id":"STORE.RETURN.BADQTY:"+tag,"quantity":"3"},409);assert "STORE_RETURN_ACCEPTED_QUANTITY_EXCEEDED" in bad["detail"]["message"]
bad=call("POST",prefix+"/approve",{**body,"operation_id":"STORE.RETURN.BADLINE:"+tag,"line_no":2},409);assert "STORE_RETURN_ORIGINAL_RECEIPT_OR_UOM_NOT_FOUND" in bad["detail"]["message"]
result=call("POST",prefix+"/approve",body);assert result["quantity"]=="1" and result["status"]=="WAITING_SAP_AND_LOGISTICS" and not result["warehouse_stock_changed"] and not result["sap_verified"],result
assert call("POST",prefix+"/approve",body)==result
conflict=call("POST",prefix+"/approve",{**body,"quantity":"2"},409);assert conflict["detail"]["outcome_confirmed"],conflict
second={**body,"operation_id":"STORE.RETURN.SECOND:"+tag,"disposition":"SUPPLIER","complete_good_box":False}
done=call("POST",prefix+"/approve",second);assert done["quantity"]=="1"
bad=call("POST",prefix+"/approve",{**body,"operation_id":"STORE.RETURN.OVER:"+tag},409);assert "STORE_RETURN_ACCEPTED_QUANTITY_EXCEEDED" in bad["detail"]["message"]
dossier=call("GET",prefix);assert dossier["lines"][0]["approved_quantity"]=="2" and dossier["lines"][0]["available_for_approval"]=="0"
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor()
 for op in (body["operation_id"],second["operation_id"]):
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=op);assert q.fetchone()==(1,)
 q.execute("select count(*) from RRL_REMAINS where UID_POLETA='FULL.QA:bea258a7dd' and(REMAIN!=0 or HARD_RESERVED_BASE!=0)");assert q.fetchone()==(0,)
 try:q.execute("delete from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=:op",op=body["operation_id"]);conn.commit();raise AssertionError("Approval deleted")
 except oracledb.DatabaseError as exc:conn.rollback();assert "STORE_RETURN_APPROVAL_IMMUTABLE" in str(exc)
print("PASS092 actual original accepted2 approves1+1/cap/original-source/complete-box/exact replay/conflict/immutable/outbox1/events0/P0; SAP/logistics not invented",flush=True)
