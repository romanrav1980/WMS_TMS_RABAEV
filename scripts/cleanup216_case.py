import sys,json
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();ware=38255845;wave=472;case=1118
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_stock import StockCommand
post=StockPosting(OracleGateway()).post
def command(kind,source,metadata):
 return post(StockCommand(operation_id="CLEAN216:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
api=httpx.Client(auth=("admin","admin123"),timeout=30);base="http://127.0.0.1:8088"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 from app.modules.platform.public import read_oracle_json
 outer="SMALL216.OUTER:7df96570";inner="SMALL216.HU:7df96570";slots=[(217,"UL216:7df96570:0"),(218,"UL216:7df96570:1"),(219,"UL216:7df96570:2")];cell="CPT_"+str(ware)
 def tree(uid):
  q.execute("select RRL_STOCK_HU_READ.snapshot_json(:p_uid)from dual",p_uid=uid);return read_oracle_json(q.fetchone()[0])
 def measures(version,mass):
  return {"origin":"MANUAL_CONFIRMED","content_version":version,"gross_weight_kg":mass,"width_m":"0.5","depth_m":"0.5","height_m":"0.5"}
 command("HU_UNPACK",{"uid":outer},{"child_uid":inner,"expected_version":tree(outer)["nodes"][0]["version"],"expected_child_version":tree(inner)["nodes"][0]["version"],"scan_container":outer,"scan_child":inner,"scan_cell":cell,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Own216 explicit native physical unpack","parent_measurements":measures(tree(outer)["nodes"][0]["version"],"1"),"child_measurements":measures(tree(inner)["nodes"][0]["version"],"1.45")})
 q.execute("select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);carrier,case_version=q.fetchone()
 command("HU_UNPACK",{"uid":inner},{"child_case_task_id":case,"expected_version":tree(inner)["nodes"][0]["version"],"expected_child_version":int(case_version),"scan_container":inner,"scan_child":carrier,"scan_cell":cell,"scan_parent_slot":slots[1][1],"scan_child_slot":slots[2][1],"child_slot_id":slots[2][0],"reason":"Own216 explicit native CASE unpack","parent_measurements":measures(tree(inner)["nodes"][0]["version"],"1"),"child_measurements":measures(int(case_version),"0.45")})
 q.execute("select SSCC,CONTENT_VERSION,WARE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case)
 carrier,version,current_ware=q.fetchone();assert current_ware==ware
 q.execute("select h.LOT_UID,l.CELL_CODE from RRL_CASE_CARRIER_LOT h join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=h.CASE_PICK_LINE_ID join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case and r.REMAIN>0",p_case=case)
 destinations=dict(q.fetchall())
 command("CASE_CARRIER_RETURN",{"case_task_id":case},{"scan_container":carrier,"expected_content_version":int(version),"destinations":destinations,"reason":"Own216 return to each original route cell"})
 q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:p_wave and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",p_wave=wave)
 for(rid,)in q.fetchall():command("RESERVATION_RELEASE",{"reservation_id":int(rid)},{"reason":"Own216 cleanup"})
 q.execute("select OPERATION_ID,PALLET_TYPE_ID from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID=:p_case and STATUS='HELD'",p_case=str(case))
 for book,typ in q.fetchall():
  r=api.post(base+"/api/inventory/tare/book-cancel",json={"operation_id":"CLEAN216.BOOK:"+str(case),"booking_operation_id":book});assert r.status_code==200,r.text[:1500]
  availability=api.get(base+f"/api/inventory/tare/warehouses/{ware}/availability").json();row=next(x for x in availability if x["pallet_type_id"]==typ)
  r=api.post(base+"/api/inventory/tare/count",json={"operation_id":"CLEAN216.TARE:"+str(case),"owner_ware_id":ware,"pallet_type_id":int(typ),"condition":"GOOD","observed_quantity":"0","expected_version":row["balance_version"]or 0,"reason":"Retire own empty fixture","decision_reference":"OWN216.END"});assert r.status_code==200,r.text[:1500]
 command("WAVE_EXECUTION_FINISH",{"wave_id":wave},{"disposition":"RETURNED_TO_PLANNING","reason":"Own216 actual returned fixture"})
 q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION,p.ARTICUL from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware and p.ARTICUL in('QPB2167DF96570')and r.REMAIN>0",p_ware=ware)
 counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]}for uid,cell,unit,version,article in q.fetchall()]
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 command("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Own216 native stock cleanup","counts":counts})
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(0,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor="UL2167df96570");c.commit()
 print("Own216 CASE1118/wave472 returned to each original cell, tare released, original demand retained, native P/H zero, protected13520/20",flush=True)
