import sys
from pathlib import Path
from uuid import uuid4
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.services.case_pick_service import CasePickService
from app.modules.inventory.contracts_stock import StockCommand,StockPostingError
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
s=get_settings();posting=StockPosting()
def post(kind,source,metadata):
 return posting.post(StockCommand(operation_id="QA182.CLEAN:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for wave in [412,413,414]:
  q.execute("select WARE_ID,STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=wave);ware,status=q.fetchone()
  if status not in("DONE","CANCELLED"):
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION,STATUS from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave);tasks=q.fetchall()
   for task,carrier,version,task_status in tasks:
    if task_status != "CANCELLED":post("CASE_CARRIER_RETURN",{"case_task_id":int(task)},{"allow_empty":True,"destinations":{},"scan_container":carrier,"expected_content_version":int(version),"reason":"Retire owned182 empty CASE after rejected scan"})
    q.execute("select OPERATION_ID from RRL_TARE_BOOK where PLACE_KIND=\'CASE\' and PLACE_ID=to_char(:p_task,\'TM9\') and STATUS='HELD'",p_task=task)
    for(book,)in q.fetchall():
     response=httpx.post("http://127.0.0.1:8088/api/inventory/tare/book-cancel",auth=("admin","admin123"),json={"operation_id":"QA182.BOOK.CLEAN:"+book,"booking_operation_id":book},timeout=30)
     assert response.status_code==200,(response.status_code,response.text[:1200])
   try:post("WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":wave},{"reason":"Retire owned182 failed launch fixture"})
   except StockPostingError as exc:
    print("Native cancel refused, retain wave history:",wave,exc.rule_reason,flush=True)
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION,p.ARTICUL from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware and r.REMAIN>0",p_ware=ware);stocks=q.fetchall()
  for uid,cell,base,version,article in stocks:
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:p_uid and CELL=:p_cell and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",p_uid=uid,p_cell=cell)
   for(sid,)in q.fetchall():post("RESERVATION_RELEASE",{"reservation_id":int(sid)},{"reason":"Owned182 fixture cleanup"})
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:p_cell and STOCK_STATUS='AVAILABLE'",p_uid=uid,p_cell=cell);keys=[r[0]for r in q.fetchall()]
   q.execute("select min(ID)from RRL_REVIZION where WARE_ID=:p_ware and CONDITION=0",p_ware=ware);revision=q.fetchone()[0]
   if revision is None:
    q.execute("select min(ID)from RRL_REVIZION where WARE_ID=:p_ware",p_ware=ware);revision=q.fetchone()[0]
   q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);version=q.fetchone()[0]
   post("INVENTORY_COUNT",{"revision_id":int(revision)},{"reason":"Native own182 cleanup","counts":[{"uid":uid,"cell":cell,"article":article,"unit":base,"quantity":"0","expected_stock_version":int(version),"unit_keys":keys}]})
  print("Owned182 wave stock cleared by native commands",wave,flush=True)
