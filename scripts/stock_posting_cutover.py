"""One authorized cutover of the empty RABAEV dev stock; never delete stock/history."""
import hashlib
import json
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"db/migrations/2026-10-08_stock_posting_core"
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
m=json.loads((D/"current_runtime_manifest.json").read_text(encoding="utf-8"))
paths=sorted(set(m["components"]+m["additional_scripts"]))
hashes={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in paths}
digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
checkpoint=ROOT/"runtime/stock_posting_20261009/cutover-checkpoint"
checkpoint.mkdir(parents=True,exist_ok=False)
(checkpoint/"source_manifest.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000
 q=c.cursor()
 try:
  q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
  assert q.fetchone()==("RABAEV","orcl")
  q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
  assert q.fetchone()==("PREPARED",)
  bad=[]
  for name in m["packages"]:
   q.execute("select OBJECT_TYPE,STATUS from user_objects where OBJECT_NAME=:n and OBJECT_TYPE in ('PACKAGE','PACKAGE BODY')",n=name)
   rows=q.fetchall()
   if len(rows)!=2 or any(r[1]!="VALID" for r in rows):bad.append(name)
  assert not bad, "Invalid/missing runtime packages: "+repr(bad)
  q.execute("select WRITER_KEY from RRL_STOCK_WRITER_REGISTRY where STATE='UNCONVERTED'")
  assert not q.fetchall(), "Unconverted stock writer"
  q.execute("select count(*) from user_triggers where TRIGGER_NAME like 'RRL%STOCK%' and STATUS!='ENABLED'")
  assert q.fetchone()==(0,), "Disabled stock guard"
  q.execute("select rawtohex(POLICY_KEY) from RRL_STOCK_POLICY_GUARD where POLICY_KEY in (RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK'),RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'))")
  policies=[{"key_hex":r[0],"mode":6} for r in q]
  assert len(policies)==2
  q.callproc("RRL_STOCK_LOCK_API.begin_plan")
  q.callproc("RRL_STOCK_LOCK_API.acquire_policies",[json.dumps(policies)])
  # Drain old writers without a VM/DB copy. NOWAIT failure aborts this whole cutover.
  for table in ("RRL_EVENTS","RRL_REMAINS","RRL_STOCK_RESERVATION","RRL_WMS_RECEIPT_UNIT"):
   q.execute("lock table "+table+" in exclusive mode nowait")
  q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1 for update nowait")
  assert q.fetchone()==("PREPARED",)
  q.execute("select SETTING_VALUE from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED'")
  assert q.fetchone()==("0",)
  for table in ("RRL_REMAINS","RRL_EVENTS","RRL_WMS_RECEIPT_UNIT","RRL_STOCK_OPERATION"):
   q.execute("select count(*) from "+table)
   assert q.fetchone()==(0,), "This dev cutover requires an empty "+table
  q.execute("select * from RRL_STOCK_RESERVATION where STATUS in ('ACTIVE','ALLOCATED','PICKING') order by RESERVATION_ID")
  cols=[x[0] for x in q.description]
  reserves=[dict(zip(cols,row)) for row in q]
  assert all(r["RESERVATION_KIND"]=="SOFT" and r["RESERVATION_DOMAIN"]=="MES_RAW" and r["BASE_QTY"] is None for r in reserves)
  (checkpoint/"legacy_soft_reservations.json").write_text(json.dumps(reserves,default=str,indent=2,ensure_ascii=False),encoding="utf-8")
  q.execute("update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RELEASED_AT=systimestamp,RELEASED_BY='admin',RELEASE_REASON='Empty dev stock cutover: obsolete untyped SOFT forecast',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_KIND='SOFT' and STATUS in ('ACTIVE','ALLOCATED','PICKING') and RESERVATION_DOMAIN='MES_RAW' and BASE_QTY is null")
  assert q.rowcount==len(reserves)
  q.execute((D/"214_cutover.sql").read_text(encoding="utf-8"),baseline="B0-20261009-STOCK-V2",manifest=digest)
  c.commit()
  print("ACTIVE: B0-20261009-STOCK-V2; compatibility=0; empty P/H/unit baseline; cancelled legacy SOFT="+str(len(reserves)))
 except BaseException:
  c.rollback()
  raise
 finally:
  q.callproc("RRL_STOCK_POSTING_API.reset_connection")
