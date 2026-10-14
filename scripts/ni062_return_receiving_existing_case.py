"""Finish original committed receiving evidence after author SELECT bind-name failure."""
import sys,json
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor()
 q.execute("""
 select r.OPERATION_ID,r.UID_PALLET,r.RECEIVE_CELL,r.BASE_QTY,r.BASE_UOM,r.NAKLAD_ID,o.CANONICAL_REQUEST,o.ACTOR
 from RRL_STORE_RETURN_RECEIPT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID
 join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=r.APPROVAL_OPERATION_ID
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd'
 """)
 op,lot,cell,qty,uom,naklad,raw,actor=q.fetchone()
 if hasattr(raw,"read"):raw=raw.read()
 document=raw if isinstance(raw,dict) else json.loads(raw)
 assert actor.startswith("QWR")
 q.execute("select PASS,DELETED from RUSERS where ID=:actor",actor=actor);secret,deleted=q.fetchone()
 q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=actor);c.commit()
 try:
  client=httpx.Client(auth=(actor,secret),timeout=30)
  body={"operation_id":op,"pickup_operation_id":document["source"]["pickup_operation_id"],**document["metadata"]}
  response=client.post("http://127.0.0.1:8088/api/inventory/store-returns/receive",json=body)
  assert response.status_code==200,(response.status_code,response.text[:500])
  result=response.json();assert result["quantity"]=="1" and result["custody"]=="WAREHOUSE" and not result["available_for_reservation"]
  q.execute("select REMAIN,HARD_RESERVED_BASE,BASE_UOM from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=lot,cell=cell);assert q.fetchone()==(1,0,uom)
  q.execute("select RRL_STOCK_ELIGIBILITY.reason(:lot_id,:cell,9104,1,null,null,'ALLOCATE') from dual",lot_id=lot,cell=cell);reason=q.fetchone()[0];assert reason is not None and "BLOCK" in reason,reason
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,)
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=op);assert q.fetchone()==(1,)
  q.execute("select DOCUMENT_KIND,RETURN_DOCUMENT_REFERENCE,RETURN_APPROVAL_OPERATION_ID,POSTAVSHIK_NAME from RRL_PRIHOD_NAKLAD where ID=:id",id=naklad);header=q.fetchone();assert header[0]=="STORE_RETURN" and header[1] and header[2] and header[3]=="Возврат магазина",header
  q.execute("select count(*) from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=:id",id=naklad);assert q.fetchone()==(0,)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:bea258a7dd'");assert all(x==(0,0) for x in q)
  try:q.execute("delete from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=:op",op=op);c.commit();raise AssertionError("Receipt deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert "STORE_RETURN_RECEIPT_HISTORY_IMMUTABLE" in str(exc)
  print("PASS096 original actual committed receiving/exact API replay/new blocked P1H0/eligibility denial/original P0/one event+outbox/typed STORE_RETURN incoming document/no purchase/Russian text intact/immutable",flush=True)
 finally:q.execute("update RUSERS set DELETED=:deleted where ID=:actor",deleted=deleted,actor=actor);c.commit()
