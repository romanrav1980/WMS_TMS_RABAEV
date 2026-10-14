"""Continue actual217 original full pallet via fresh existing QC and existing load."""
import sys,json
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
cfg=get_settings();st="FULL.ST:562cdaa306";uid="FULL.QA:562cdaa306";original="SINGLE.FULL.LOAD:562cdaa306"
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 conn.call_timeout=15000;q=conn.cursor();api=httpx.Client(auth=("admin","admin123"),timeout=40);base="http://127.0.0.1:8088"
 q.execute("select TT_ID,VEHICLE_NUMBER,DOCK,json_value(COMPOSITION_JSON,'$.cell'),STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=original)
 trip,vehicle,dock,cell,state=q.fetchone();assert state=="UNLOADED"
 loading=build_transport_loading();qc=OutgoingQuality(OracleGateway());preview=loading.preview_single(st);before=qc.status(st,"admin")
 assert before["rescan_required"]and not before["ready"]and preview["root"]==uid
 q.execute("select ff.PICKED_WAREHOUSE_TASK_ID,ff.PICKED_PALLET_UID,ff.STATUS,ff.PICKED_STOCK_VERSION,r.STOCK_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT ff join RRL_REMAINS r on r.UID_POLETA=ff.PICKED_PALLET_UID and r.CELL=:c join RRL_SBORKA_PALLETS sp on sp.ID=ff.LEGACY_SBORKA_PALLET_ID where sp.PALLET_UID=:s",c=cell,s=st)
 task,physical,status,picked,current=q.fetchone();assert status=="PICKED"and physical==uid and picked==current
 body={"operation_id":"FULL218.RELOAD:562cdaa306","identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":cell,"transport_task_id":trip,"scan_vehicle":vehicle,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 rejected=api.post(base+"/api/transport/loading/confirm-single",json=body);assert rejected.status_code==409 and "SHIPMENT_FULL_COMPOSITION_SCAN_REQUIRED"in rejected.text,rejected.text[:1500]
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell);assert q.fetchone()==(3,3)
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=uid);barcode=q.fetchone()[0]
 scan={"operation_id":"FULL218.QC:562cdaa306","expected_composition_signature":before["composition_signature"],"error_count":0,"item_scans":[{"scan_id":"FULL218.ITEM:"+str(i),"barcode":barcode,"quantity":"1"}for i in range(3)]}
 checked=api.post(base+"/api/outgoing-quality/"+st+"/scan",json=scan);assert checked.status_code==200,checked.text[:1500]
 assert api.post(base+"/api/outgoing-quality/"+st+"/scan",json=scan).json()==checked.json()
 after=qc.status(st,"admin");assert after["ready"],after
 # QC approval leaves original native physical quantity and HARD unchanged.
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell);assert q.fetchone()==(3,3)
 preview=loading.preview_single(st);body.update(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"]);body["measurements"]["content_version"]=preview["expected_version"]
 response=api.post(base+"/api/transport/loading/confirm-single",json=body);assert response.status_code==200,response.text[:2200];result=response.json()
 assert api.post(base+"/api/transport/loading/confirm-single",json=body).json()==result
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell);assert q.fetchone()==(0,0)
 q.execute("select ff.PICKED_WAREHOUSE_TASK_ID,ff.PICKED_PALLET_UID,ff.STATUS,ff.SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT ff join RRL_SBORKA_PALLETS sp on sp.ID=ff.LEGACY_SBORKA_PALLET_ID where sp.PALLET_UID=:s",s=st);assert q.fetchone()==(task,uid,"SHIPPED",body["operation_id"])
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=task);assert q.fetchone()[0]=="DONE"
 for operation,amount in[(original,-3),("FULL217.UNLOAD:562cdaa306:OTHER",3),(body["operation_id"],-3)]:
  q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=operation);assert q.fetchone()[0]==amount
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS218 same original FULLPAL/task/UID fresh item QC3 required, old control refused; actual reload native-3/P0H0/replay/original shipment and unload retained/protected13520/20",flush=True)
