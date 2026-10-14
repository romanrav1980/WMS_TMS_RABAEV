from pathlib import Path
import json
s=Path("scripts/ni052_fullpal_current_slot_case.py").read_text(encoding="utf-8");prefix=s[:s.index(' admin_api=')]
prefix=prefix.replace("from app.config import get_settings","from app.config import get_settings")
body="""
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);qc=OutgoingQuality(OracleGateway());loading=build_transport_loading();st="FULL.ST:"+tag;slot=221;place_task=949
 q.execute("select STATUS from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t",t=place_task);assert q.fetchone()[0]=="OCCUPIED"
 before=qc.status(st,"admin");assert before["rescan_required"]and not before["ready"]
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=lot);barcode=q.fetchone()[0]
 scan={"operation_id":"FULL223.QC:"+tag,"expected_composition_signature":before["composition_signature"],"error_count":0,"item_scans":[{"scan_id":"ITEM223:"+str(i),"barcode":barcode,"quantity":"1"}for i in range(3)]}
 api(admin_api,"POST","/api/outgoing-quality/"+st+"/scan",scan);assert qc.status(st,"admin")["ready"]
 current=loading.preview_single(st);load_id="FULL223.LOAD:"+tag
 load={"operation_id":load_id,"identifier":st,"expected_version":current["expected_version"],"expected_composition_signature":current["composition_signature"],"scan_container":lot,"scan_cell":shipcell,"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":current["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 metadata={k:v for k,v in load.items()if k not in("operation_id","identifier","transport_task_id","scan_vehicle","scan_dock","measurements")}
 metadata["loading_context"]={"transport_task_id":trip,"scan_vehicle":load["scan_vehicle"],"scan_dock":dock,"measurements":load["measurements"]}
 canonical=StockCommand(operation_id=load_id,command_type="LOAD_SHIPMENT",actor="admin",source={"pallet_identifier":st},metadata=metadata,lines=()).canonical_json();out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,"admin",out,None]);assert out.getvalue()is None;q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t",t=place_task);assert q.fetchone()[0]==0
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t",t=place_task);assert q.fetchone()[0]=="OCCUPIED"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 with ThreadPoolExecutor(2)as pool:rs=list(pool.map(lambda b:admin_api.post(base+"/api/transport/loading/confirm-single",json=b),[load,{**load,"operation_id":load_id+":OTHER"}]))
 assert sorted(r.status_code for r in rs)==[200,409],[(r.status_code,r.text[:1600])for r in rs];result=next(r.json()for r in rs if r.status_code==200);load_id=result["operation_id"];load["operation_id"]=load_id
 assert api(admin_api,"POST","/api/transport/loading/confirm-single",load)==result
 q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t",t=place_task);assert q.fetchone()[0]==0
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=place_task);assert q.fetchone()[0]=="DONE"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=load_id);assert q.fetchone()[0]==-3
 q.execute("select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:p",p=load_id);value=q.fetchone()[0];proof=value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,"read")else value);assert proof["domain"]["source_stock_claims"][0]["task"]==place_task and proof["domain"]["source_stock_claims"][0]["slot"]==slot
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS223 existing SINGLE fullpal load releases original measured source SLOT221 atomically with native-3/P0H0; outer rollback restores original claim/P3H3; concurrent one winner/replay/source occupancy frozen/archive PUTAWAY949 DONE retained/protected13520/20",load_id,flush=True)
"""
print(json.dumps({"scripts/ni052_single_load_slot_release_case.py":prefix+body},ensure_ascii=True))
