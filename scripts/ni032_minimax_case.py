"""One isolated warehouse: partial delivery keeps the original MAX cycle; no duplicate task."""
import sys,json,time
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.replenishment_composition import build_minimax_service
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_stock import StockCommand
g=OracleGateway();svc=build_minimax_service();tag=uuid4().hex[:10];src="MXS"+tag;dst="MXT"+tag;lot="MIN.QA:"+tag
def metadata(sql,**b):
 with g.transaction("Own minimax fixture metadata") as c:
  c.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:c.execute(sql,b)
  finally:c.callproc("RRL_STOCK_CONFIG_API.end_change")
def scalar(sql,**b):return next(iter(g.fetch_all(sql,b)[0].values()))
def post(kind,source,body,operation=None):
 return StockPosting().post(StockCommand(operation_id=operation or "MIN.QA:"+uuid4().hex,command_type=kind,actor="admin",lines=(),source=source,metadata=body))
with g.transaction("Own minimax warehouse") as c:
 c.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  c.execute("select nvl(max(ID),0)+1 from RRL_WARES");ware=int(c.fetchone()[0])
  c.execute("insert into RRL_WARES(ID,NAME) values(:id,:name)",{"id":ware,"name":"QA minimax "+tag})
 finally:c.callproc("RRL_STOCK_CONFIG_API.end_change")
article=scalar("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'")
for cell,pick in ((src,0),(dst,1)):
 metadata("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:cell,:ware,0,0,0,:pick,0)",cell=cell,ware=ware,pick=pick)
 metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
face=int(scalar("select RRL_PICK_FACE_SQ.nextval from dual"))
metadata("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,:ware,:cell,0.03,'admin')",id=face,ware=ware,cell=dst)
cv=g.fetch_all("select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and INPUT_UOM='BOX' order by POLICY_VERSION desc fetch first 1 row only",{"a":article})[0]
volume=Decimal(str(cv["numerator"]))/Decimal(str(cv["denominator"]))*Decimal("0.01")
metadata("""insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,
 MIN_QTY,MAX_QTY,REPLENISHMENT_METHOD,REPLENISHMENT_QTY_MODE)
 values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:a,:volume,0,0,3,'MINIMAX','FILL_TO_VOLUME')""",face=face,a=article,volume=volume)
with g.transaction("Own minimax count revision") as c:revision=int(c.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]))
wave=None
try:
 def birth(uid,qty):
  return post("INVENTORY_REGISTER_LOT",{"revision_id":revision},{"uid":uid,"cell":src,"article":article,"quantity":qty,"expiry_date":"2030-01-01","price":0,"reason":"Own minimax lifecycle fixture"})
 before=svc.preview(ware);assert before["faces"][0]["reason"]=="WAIT_STOCK",before
 birth(lot,"1")
 started=time.perf_counter();first=svc.reconcile(ware,"admin");elapsed_ms=round((time.perf_counter()-started)*1000,2);wave=first["wave_id"]
 assert first["created"]==1,first
 assert svc.reconcile(ware,"admin")["created"]==0,"Duplicated open minimax"
 def complete_one():
  rows=g.fetch_all("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where SOURCE_DOC_ID=:wave and TASK_SOURCE='WAVE' and TASK_TYPE='REPLENISHMENT' and STATUS='PLANNED' order by TASK_ID",{"wave":wave})
  assert len(rows)==1,rows
  r=rows[0];body={"fact_qty":str(r["qty"]),"scanned_pallet":r["uid_pallet"],"scanned_from_cell":r["from_cell"],"scanned_to_cell":r["to_cell"]}
  op="MIN.QA.COMPLETE:"+uuid4().hex
  answer=post("TASK_COMPLETE",{"task_id":int(r["task_id"])},body,op)
  assert post("TASK_COMPLETE",{"task_id":int(r["task_id"])},body,op)==answer
 complete_one()
 pending=svc.preview(ware)["faces"][0]
 assert pending["physical_base"]=="1" and pending["cycle_target"]=="3" and pending["reason"]=="WAIT_STOCK",pending
 birth(lot+"B","2")
 next_cycle=svc.reconcile(ware,"admin");assert next_cycle["created"]==1,next_cycle
 complete_one()
 final=svc.reconcile(ware,"admin");assert final["created"]==0,final
 rows=g.fetch_all("select sum(REMAIN) P,sum(HARD_RESERVED_BASE) H from RRL_REMAINS where CELL=:cell",{"cell":dst});assert rows[0]=={"p":3,"h":0},rows
 assert scalar("select count(*) from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:wave and MINIMAX_FINISHED_AT is null",wave=wave)==0
 print(json.dumps({"passed":True,"warehouse":ware,"wave":wave,"reconcile_ms":elapsed_ms,"case":"MAX3 via deliveries1+2; duplicate check; original cycle continued above MIN0; surplus free"}),flush=True)
finally:
 metadata("update RRL_PICK_FACE_ARTICUL set ACTIVE=0 where PICK_FACE_ID=:face",face=face)
 metadata("update RRL_PICK_FACE set ACTIVE=0 where PICK_FACE_ID=:face",face=face)
 if wave is not None:post("DOCUMENT_RELEASE_RESERVATIONS",{"document_type":"PICK_WAVE","document_id":wave},{"reason":"Close own minimax fixture","only_cancelled_replenishment":0,"reservation_kind":None})
 if wave is not None:metadata("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:wave",wave=wave)
 rows=g.fetch_all("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",{"ware":ware})
 counts=[{"uid":r["uid_poleta"],"cell":r["cell"],"article":article,"unit":r["base_uom"],"quantity":"0","expected_stock_version":int(r["stock_version"]),"unit_keys":[]} for r in rows]
 if counts:post("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Close own minimax fixture","counts":counts})
 print("Own warehouse stock restored through root; minimax metadata disabled; immutable history retained",flush=True)
