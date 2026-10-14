import sys,json
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();ware=35993160;wave=462;case=1108
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_stock import StockCommand
post=StockPosting(OracleGateway()).post
def command(kind,source,metadata):
 return post(StockCommand(operation_id="CLEAN210:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
api=httpx.Client(auth=("admin","admin123"),timeout=30);base="http://127.0.0.1:8088"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select SSCC,CONTENT_VERSION,WARE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case)
 carrier,version,current_ware=q.fetchone();assert current_ware==ware
 q.execute("select h.LOT_UID,l.CELL_CODE from RRL_CASE_CARRIER_LOT h join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=h.CASE_PICK_LINE_ID join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case and r.REMAIN>0",p_case=case)
 destinations=dict(q.fetchall())
 command("CASE_CARRIER_RETURN",{"case_task_id":case},{"allow_empty":True,"scan_container":carrier,"expected_content_version":int(version),"destinations":destinations,"reason":"Own210 return to each original route cell"})
 q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:p_wave and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",p_wave=wave)
 for(rid,)in q.fetchall():command("RESERVATION_RELEASE",{"reservation_id":int(rid)},{"reason":"Own210 cleanup"})
 q.execute("select OPERATION_ID,PALLET_TYPE_ID from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID=:p_case and STATUS='HELD'",p_case=str(case))
 for book,typ in q.fetchall():
  r=api.post(base+"/api/inventory/tare/book-cancel",json={"operation_id":"CLEAN210.BOOK:"+str(case),"booking_operation_id":book});assert r.status_code==200,r.text[:1500]
  availability=api.get(base+f"/api/inventory/tare/warehouses/{ware}/availability").json();row=next(x for x in availability if x["pallet_type_id"]==typ)
  r=api.post(base+"/api/inventory/tare/count",json={"operation_id":"CLEAN210.TARE:"+str(case),"owner_ware_id":ware,"pallet_type_id":int(typ),"condition":"GOOD","observed_quantity":"0","expected_version":row["balance_version"]or 0,"reason":"Retire own empty fixture","decision_reference":"OWN210.END"});assert r.status_code==200,r.text[:1500]
 command("WAVE_EXECUTION_FINISH",{"wave_id":wave},{"disposition":"RETURNED_TO_PLANNING","reason":"Own210 actual returned fixture"})
 q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION,p.ARTICUL from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware and p.ARTICUL in('QC210F4094872C8','QC210F4094872C8B')and r.REMAIN>0",p_ware=ware)
 counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]}for uid,cell,unit,version,article in q.fetchall()]
 command("INVENTORY_COUNT",{"revision_id":312},{"reason":"Own210 native stock cleanup","counts":counts})
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(0,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("Own210 CASE1106/wave460 returned to each original cell, tare released, original demand retained, native P/H zero, protected13520/20",flush=True)
