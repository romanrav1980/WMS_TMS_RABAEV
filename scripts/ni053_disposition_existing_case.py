import sys,json
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag="bea258a7dd";lot="FULL.QA:"+tag;shipop="FULL.HU.SHIP:"+tag;store_addr="STORE.QA:"+tag;top="HU.FULL:"+tag
client=httpx.Client(auth=("admin","admin123"),timeout=35)
def http(method,path,body=None,expected=200):
 response=client.request(method,"http://127.0.0.1:8088/api/delivery/store-receipts"+path,json=body)
 assert response.status_code==expected,(response.status_code,response.text[:1200])
 return response.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor()
 preview=http("GET",f"/preview?load_operation_id={shipop}&store_address={store_addr}")
 receipt={"operation_id":"STORE.RECEIPT:"+tag,"load_operation_id":shipop,"store_address":store_addr,"scan_place":top,"expected_composition_signature":preview["composition_signature"],"before_cameras":True}
 counts=[{"lot_uid":lot,"accepted":"2","missing":"1","refused":"0","damaged":"0","extra":"1"}]
 receipt.update(observations=counts,case_note="Одной единицы не хватает; обнаружена лишняя единица для разбирательства")
 for suffix,changes,rule in (
  ("TOTAL",{"observations":[{**counts[0],"accepted":"1"}]},"STORE_DISPOSITION_TOTAL_MISMATCH"),
  ("FOREIGN",{"observations":[{**counts[0],"lot_uid":"FOREIGN"}]},"STORE_DISPOSITION_COMPLETE_LEAF_COVERAGE_REQUIRED"),
  ("DUPLICATE",{"observations":counts+counts},"STORE_DISPOSITION_DUPLICATE_OR_MISSING_LEAF"),
  ("REASON",{"case_note":""},"STORE_DISCREPANCY_REASON_REQUIRED")):
  failure=http("POST","/confirm",{**receipt,**changes,"operation_id":"STORE.BAD."+suffix+":"+tag},409)
  assert rule in failure["detail"]["message"],failure
 accepted=http("POST","/confirm",receipt)
 assert accepted["status"]=="DISCREPANCY" and accepted["accepted_lines"][0]["accepted_quantity"]=="2",accepted
 assert accepted["discrepancy_case_id"]==receipt["operation_id"]
 assert not accepted["warehouse_stock_consumed_again"] and not accepted["government_ack_created"]
 assert http("POST","/confirm",receipt)==accepted
 conflict=http("POST","/confirm",{**receipt,"case_note":"Другая причина"},409)
 assert "OPERATION_CONFLICT" in conflict["detail"]["message"],conflict
 duplicate=http("POST","/confirm",{**receipt,"operation_id":"STORE.DUPLICATE:"+tag},409)
 assert "STORE_PLACE_ALREADY_RECEIVED" in duplicate["detail"]["message"],duplicate
 q.execute("select RECEIPT_STATE from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==("DISCREPANCY",)
 q.execute("select SHIPPED_BASE_QTY,ACCEPTED_BASE_QTY,MISSING_BASE_QTY,REPORTED_EXTRA_BASE_QTY from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==(3,2,1,1)
 q.execute("select KIND,BASE_QTY,STATUS from RRL_STORE_DELIVERY_OBLIGATION where CASE_ID=:op order by KIND",op=receipt["operation_id"]);assert q.fetchall()==[("EXCESS_REVIEW",1,"OPEN"),("MISSING_INVESTIGATION",1,"OPEN")]
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==(0,)
 q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==(1,)
 print("PASS086 actual API accepted2/missing1/extra1, exact replay/conflict/duplicate/foreign/total/reason refusal, two OPEN obligations, no second stock journal",flush=True)
