exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import build_stock_posting_service,StockCommand
from concurrent.futures import ThreadPoolExecutor
import httpx
ctx=json.loads(Path("tmp/context307.json").read_text(encoding="utf-8"));previous=json.loads(Path("tmp/context307_cancel.json").read_text(encoding="utf-8"));p=Path("tmp/context308.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
posting=build_stock_posting_service();request_id=previous["replacement_operation_id"];unit_key=previous["replacement"]["source_units"][0]["key"]
if "approval_result"not in saved:
 op="IW308.APPROVE:"+ctx["tag"];metadata=dict(quantity="1",reason="Проверена новая исправленная находка одной единицы",evidence_reference="DEV308:independentapproval")
 saved["approval_result"]=posting.post(StockCommand(operation_id=op,command_type="INTERWARE_RECOVERY_APPROVE",actor="admin",source=dict(request_operation_id=request_id),lines=(),metadata=metadata))
 saved["approval_operation_id"]=op;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "outcome"not in saved:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:unit_key",unit_key=unit_key);unit_id=q.fetchone()[0]
 scans=next(u["codes"]for u in ctx["units"]if u["unit_id"]==unit_id);lot="RACE308:"+ctx["tag"]
 receive=dict(operation_id="IW308.RECEIVE:"+ctx["tag"],approval_operation_id=saved["approval_operation_id"],quantity="1",gross_weight_kg="2",receipt_pallet_identifier=lot,scan_source_pallet=ctx["lot"],scan_pallet=lot,scan_cell=ctx["receive_cell"],scan_article=ctx["barcode"],article=ctx["article"],base_uom="EA",discrepancy_reason="Физическая приёмка найденной единицы конкурирует с отменой",discrepancy_reference="DEV308:physical-vs-cancel",scans=scans)
 cancel=dict(operation_id="IW308.CANCEL:"+ctx["tag"],request_operation_id=request_id,quantity="1",reason="Проверенная отмена до возможной физической приёмки",evidence_reference="DEV308:cancel-vs-physical")
 def send(action):
  path,body=action
  with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
   r=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/"+path,json=body);return path,body,r.status_code,r.json()
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,[("recovery-receipts",receive),("recovery-cancellations",cancel)]))
 assert sorted(result[2]for result in results)==[200,409],[(r[0],r[2],r[3])for r in results]
 win=next(r for r in results if r[2]==200);saved.update(outcome=win[0],body=win[1],result=win[3],lot=lot,results=results);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 r=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/"+saved["outcome"],json=saved["body"]);assert r.status_code==200 and r.json()==saved["result"],r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=:request_id",request_id=request_id);cancel_count=q.fetchone()[0]
 q.execute("select count(*)from RRL_INTERWARE_RECOVERY_RECEIPT where APPROVAL_OPERATION_ID=:approval_id",approval_id=saved["approval_operation_id"]);receipt_count=q.fetchone()[0]
 assert cancel_count+receipt_count==1
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=saved["lot"]);assert q.fetchone()==(receipt_count,0)
 q.execute("select STOCK_STATUS,CURRENT_UID from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:unit_key",unit_key=unit_key);assert q.fetchone()==(("AVAILABLE",saved["lot"])if receipt_count else("ISSUED",ctx["lot"]))
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS308 actual concurrent cancel-vs-receive200/409/exactwinnerreplay/one terminal fact/P either0or1/currentUNITconsistent/protected20-20; winner="+saved["outcome"])
