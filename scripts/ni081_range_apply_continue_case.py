"""158 original20H20 retained; coherent owned QA norms/dates, two versioned approvals and empty drain."""
import sys,json
from pathlib import Path
from datetime import date
from decimal import Decimal
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import build_slotting_demand,build_range_proposal
from app.modules.inventory.contracts_range_proposal import RangeDraft
from app.modules.inventory.contracts_slotting import SlottingError
from app.modules.inventory.infrastructure.range_command import range_command
s=get_settings();tag='243f5283';ware=6667491;article="QNATIVED9A5C53B54";old_cell="QGd9a5c53b54"
print("QA158 owned configuration stage",tag,flush=True)
reader=build_slotting_demand(OracleGateway());service=build_range_proposal(OracleGateway())
costs=[{"pick_face_id":518,"pick_seconds_per_base":"1","replenish_seconds_per_pallet":"60","basis":"Own explicit route assumption"},
       {"pick_face_id":519,"pick_seconds_per_base":"0.5","replenish_seconds_per_pallet":"150","basis":"Own explicit route assumption"}]
def denied(fn,code):
 try:fn()
 except SlottingError as exc:assert code in str(exc)or code==exc.code,(exc.code,str(exc))
 else:raise AssertionError("Expected refusal")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def stock():
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware)
  return q.fetchone()
 before=stock();assert before==(20,20)
 wave=396;repl=1502
 preview=reader.preview(ware,article,date(2026,10,10),date(2026,10,11),Decimal(44),"EA","admin",Decimal(2),costs)
 assert preview["undated_unpicked_quantity"]=="0"and preview["scenario"]["old_stock_credit"]=="20",preview["scenario"]
 assert preview["range_recommendation"]["status"]=="NOMINAL_RECOMMENDATION",preview["range_recommendation"]
 assert preview["range_recommendation"]["selected_faces"][0]["pick_face_id"]==518
 draft="RANGE158.DRAFT:"+tag
 command=RangeDraft(draft,date(2026,10,10),date(2026,10,11),Decimal(44),"EA",Decimal(2),costs,preview["source_signature"],"Owned QA complete period and coherent24 EA pallet")
 assert service.save(ware,article,command,"admin")["status"]=="DRAFT"
 denied(lambda:service.approve(ware,article,"RANGE157.ACTIVE2:52470cc7","RANGE158.STALE:"+tag,"Old draft must not silently rebase",True,True,"admin"),"PICK_RANGE_SOURCE_CHANGED")
 denied(lambda:service.approve(ware,article,draft,"RANGE158.NOINSPECT:"+tag,"Missing physical inspection declaration",False,True,"admin"),"PICK_RANGE_OPERATOR_LAYOUT_INSPECTION_REQUIRED")
 operation="RANGE158.APPROVE:"+tag
 body={"proposal_id":draft,"reason":"Own synthetic inspection of geometry and compatibility","geometry_checked":True,"product_compatibility_checked":True}
 # Entire native publication rolled back by command owner, then same operation can be performed.
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","pick_topology_edit"])
 try:
  current=reader.snapshot(q,ware,article,date(2026,10,10),date(2026,10,11),Decimal(44),"EA","admin",Decimal(2),costs)
  saved=range_command(q,ware,article,operation,"APPROVE","admin",body,current);assert saved["status"]=="APPROVED"
  q.callproc("RRL_STOCK_CONFIG_API.end_change");c.rollback()
 except BaseException:
  q.callproc("RRL_STOCK_CONFIG_API.end_change");c.rollback();raise
 q.execute("select count(*)from RRL_PICK_RANGE_OPERATION where OPERATION_ID=:id",id=operation);assert q.fetchone()==(0,)
 q.execute("select count(*)from RRL_PICK_FACE_ARTICUL where PICK_FACE_ID=518 and ACTIVE=1");assert q.fetchone()==(0,)
 with ThreadPoolExecutor(max_workers=2)as pool:
  results=list(pool.map(lambda _:service.approve(ware,article,draft,operation,body["reason"],True,True,"admin"),range(2)))
 assert results[0]==results[1]and results[0]["status"]=="APPROVED",results
 first_mapping=results[0]["new_mapping_ids"][0]
 assert results[0]["draining_mapping_ids"]==[207],results
 assert service.get(ware,article,draft,"admin")["status"]=="APPROVED"
 denied(lambda:service.cancel(ware,article,draft,"RANGE158.CANCEL:"+tag,"Cannot cancel published range as draft","admin"),"PICK_RANGE_PROPOSAL_NOT_CURRENT_DRAFT")
 denied(lambda:service.close(ware,article,207,"RANGE158.CLOSEOCCUPIED:"+tag,"Old stock and existing CASE obligations remain","admin"),"PICK_RANGE_OLD_STOCK_OR_COMMITMENT_REMAINS")
 q.execute("select RRL_PICK_RANGE_POLICY.new_target_allowed(:cell,:article),RRL_PICK_RANGE_POLICY.new_target_allowed(:cell,:article,:repl)from dual",cell=old_cell,article=article,repl=repl)
 assert q.fetchone()==(0,1)
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","pick_wave_launch"])
 try:
  try:q.execute("update RRL_PICK_WAVE_REPLENISH_TASK set QTY=13 where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl)
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,str(exc)
  else:raise AssertionError("Old frozen commitment expanded")
  q.execute("select RRL_PICK_WAVE_REPL_SQ.nextval from dual");new_id=int(q.fetchone()[0])
  try:
   q.execute("insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,ARTICUL,TARGET_CELL_CODE,QTY,DEMAND_BASE_QTY,STATUS,REPLENISHMENT_METHOD,REPLENISHMENT_QTY_MODE,CREATED_BY)values(:id,:wave,:article,:cell,1,1,'RELEASED','IMMEDIATE','HALF_PALLET','admin')",id=new_id,wave=wave,article=article,cell=old_cell)
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,str(exc)
  else:raise AssertionError("New refill of draining cell admitted")
  q.execute("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED'where PICK_WAVE_REPLENISH_TASK_ID=:id and SOURCE_RESERVATION_ID is null",id=repl);assert q.rowcount==1
  q.callproc("RRL_STOCK_METADATA_TX.end_change");c.commit()
 except BaseException:
  q.callproc("RRL_STOCK_METADATA_TX.end_change");c.rollback();raise
 # Replace first still-empty new face with second; oldoccupied207 remainsdraining.
 preview2=reader.preview(ware,article,date(2026,10,10),date(2026,10,11),Decimal(44),"EA","admin",Decimal(2),costs)
 assert preview2["range_recommendation"]["status"]=="NOMINAL_RECOMMENDATION",preview2["range_recommendation"]
 assert preview2["range_recommendation"]["selected_faces"][0]["pick_face_id"]==519
 draft2="RANGE158.DRAFT2:"+tag
 command2=RangeDraft(draft2,date(2026,10,10),date(2026,10,11),Decimal(44),"EA",Decimal(2),costs,preview2["source_signature"],"Own next range version keeps old stock obligations")
 service.save(ware,article,command2,"admin")
 second=service.approve(ware,article,draft2,"RANGE158.APPROVE2:"+tag,"Own synthetic second layout inspection",True,True,"admin")
 closed=service.close(ware,article,first_mapping,"RANGE158.CLOSEEMPTY:"+tag,"Own previously approved face is still physically empty","admin")
 assert closed["status"]=="DRAIN_CLOSED"
 assert service.close(ware,article,first_mapping,"RANGE158.CLOSEEMPTY:"+tag,"Own previously approved face is still physically empty","admin")==closed
 old=service.get(ware,article,draft,"admin");assert old["approved_range_superseded"]is True
 assert stock()==before==(20,20)
 q.execute("select ACTIVE,CASE_PICK_ENABLED from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=207");assert q.fetchone()==(1,1)
 q.execute("select t.STATUS,sum(nvl(l.PICKED_QTY,0))from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.CASE_PICK_TASK_ID in(1031,1032)group by t.STATUS")
 assert all(row[1]==0 for row in q.fetchall())
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  response=client.get(f"http://127.0.0.1:8088/api/inventory/slotting/warehouses/{ware}/articles/{article}/recommendations/"+draft2)
  assert response.status_code==200,(response.status_code,response.text[:1000]);assert response.json()["status"]=="APPROVED"
 print("PASS158 rollback allpublication/concurrent sameOP once/source stale and inspection denied/old207stillactiveP20H20+CASE unchanged/future refill blocked/oldqty12 grandfatheredno expansion/secondversion emptyoldclose/replay/history",tag,"drafts",draft,draft2,"newmapping",second["new_mapping_ids"],"closed",first_mapping,"ownwave",wave,flush=True)
