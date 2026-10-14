import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag="349bc1ff57";actor="QIR"+tag;secret=uuid4().hex
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("update RUSERS set DELETED=0,PASS=:secret,WARE_ID=9104 where ID=:actor",secret=secret,actor=actor);c.commit()
 client=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088/api/inventory/interwarehouse"
 def api(path,body=None,status=200):
  r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
 try:
  body={"operation_id":"INTERWARE.RECEIVE:"+tag,"plan_operation_id":"INTERWARE.PLAN:ec6052b26e","scan_pallet":"FULL.QA:9b15cf997d","scan_cell":"QIR"+tag,"scan_article":"NS00-TEST-D10","article":"DS-BASE-D10","quantity":"3","base_uom":"EA"}
  result=api("/receive",body);assert result["status"]=="RECEIVED_PENDING_PLACEMENT" and result["quantity"]=="3" and not result["customer_fulfillment_repeated"]
  assert api("/receive",body)==result
  api("/receive",{**body,"quantity":"2"},409)
  api("/receive",{**body,"operation_id":"INTERWARE.SECONDRECEIVE:"+tag},409)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=body["scan_pallet"],cell=body["scan_cell"]);assert q.fetchone()==(3,0)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id and CELL!=:cell",lot_id=body["scan_pallet"],cell=body["scan_cell"]);assert q.fetchone()==(0,0)
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,3)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op="INTERWARE.UNLOAD:"+tag);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='INTERWAREHOUSE_RECEIVED' and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  assert any(x["receipt_operation_id"]==body["operation_id"] for x in api("/warehouses/9104"))
  print("PASS119 continued original unload349bc1ff57 /target native receiptP3H0/event1/SAP1/oldsource0/originalST/replay/conflict/second; prior early/scans/foreign denials. Initial ORA40573 transaction rolled back; j payload assigned CLOB before SQL. tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
