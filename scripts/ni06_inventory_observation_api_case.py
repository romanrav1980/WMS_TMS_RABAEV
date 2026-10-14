"""Targeted actual HTTP observation-port case. Only own stock cleared through root."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx, oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];ware=100000+int(tag[:6],16);cell="QI"+tag;uid="OBS.QA:"+tag
session=httpx.Client(auth=("admin","admin123"))
def call(method,path,body=None,status=200):
 r=session.request(method,"http://127.0.0.1:8088/api/inventory/stock-posting"+path,json=body,timeout=35)
 assert r.status_code==status,(r.status_code,r.text[:700])
 return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor()
 def meta(sql,**bind):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,bind);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");article=q.fetchone()[0]
 meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:w,:n,:p)",w=ware,n="Observation private "+tag,p="Q"+tag[:2])
 meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:w,0,0,0,0,0,0,0)",c=cell,w=ware)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 revision=call("POST","/inventory/revisions",{"warehouse_id":ware})["revision_id"]
 def lot():
  rows=call("GET",f"/inventory/{revision}/lots?cell={cell}")["lots"]
  return next((row for row in rows if row["uid"]==uid),None)
 def count(qty,op=None):
  row=lot()
  return {"operation_id":op or "OBS.COUNT:"+uuid4().hex,"revision_id":revision,"reason":"Own observation-port case",
   "counts":[{"uid":uid,"cell":cell,"article":article,"unit":row["unit"],"quantity":str(qty),
   "expected_stock_version":int(row["stock_version"]),"scans":[],"unit_keys":[]}]}
 try:
  call("POST","/inventory/lots",{"operation_id":"OBS.BIRTH:"+tag,"revision_id":revision,"uid":uid,"cell":cell,
   "article":article,"quantity":"5","expiry_date":"2030-01-01","price":"0","reason":"Own observation-port case"})
  assert str(lot()["physical_qty"])=="5"
  command=count(4);first=call("POST","/inventory/counts",command);assert str(lot()["physical_qty"])=="4"
  replay=call("POST","/inventory/counts",command);assert replay["operation_id"]==first["operation_id"]
  conflict={**command,"reason":"Different reason"}
  assert call("POST","/inventory/counts",conflict,409)["detail"]["code"]=="OPERATION_CONTENT_CONFLICT"
  print("PASS actual API revision/birth5/count4/exact replay/conflict; observation port, root posting unchanged",flush=True)
 finally:
  row=lot()
  if row and float(row["physical_qty"])>0:call("POST","/inventory/counts",count(0))
  row=lot();assert row and float(row["physical_qty"])==0 and float(row["hard_qty"])==0
  print("Own P/H0 via actual API/root; journal retained",flush=True)
