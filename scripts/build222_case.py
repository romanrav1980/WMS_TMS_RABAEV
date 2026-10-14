from pathlib import Path
import json
s=Path("scripts/ni063_repeated_load_recovery_case.py").read_text(encoding="utf-8");prefix=s[:s.index(' previous="TARE220.RECOVERY:')].replace("FULL221.QC:","FULL222.QC:").replace("ITEM221:","ITEM222:").replace("FULL221.LOAD:","FULL222.LOAD:")
body="""
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):
  q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def topology(label,weight):
  topo=seq("RRL_WH_TOPOLOGY_SQ");tc=seq("RRL_TOPOLOGY_CELL_SQ");slot=seq("RRL_TOPO_CELL_SLOT_SQ");code="UL222:"+tag+":"+label
  meta("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,STATUS)values(:id,:w,:code,'PUBLISHED')",id=topo,w=ware,code="UNLOAD222:"+tag+":"+label)
  meta("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,SLOT_LAYER_KIND,MAX_WEIGHT_KG,MAX_VOLUME_M3)values(:id,:t,:w,:c,:c,'STORAGE_SLOT',100,4)",id=tc,t=topo,w=ware,c=shipcell)
  meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO)values(:id,:t,:tc,'STORAGE_SLOT','STORAGE_SLOT',:code,1,:kg,3,1.2,1.2,2,1)",id=slot,t=topo,tc=tc,code=code,kg=weight)
  return slot,code
 oldslot,oldcode=topology("OLD",100);slot,code=topology("CURRENT",1)
 unload={"operation_id":"FULL222.UNLOAD:"+tag,"load_operation_id":load_id,"expected_version":current["expected_version"],"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own222 original full pallet into latest current measured physical slot"}
 api(sender_api,"POST","/api/transport/loading/unload",unload,status=409)
 api(sender_api,"POST","/api/transport/loading/unload",{**unload,"target_slot_id":oldslot,"scanned_to_slot_code":oldcode},status=409)
 unload.update(target_slot_id=slot,scanned_to_slot_code=code)
 rejected=sender_api.post(base+"/api/transport/loading/unload",json=unload);assert rejected.status_code==409 and "HU_SLOT_WEIGHT_VOLUME_OR_DIMENSIONS_EXCEEDED"in rejected.text,(rejected.status_code,rejected.text[:1800])
 q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load_id);assert q.fetchone()[0]=="LOADED"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=:s",s=slot);assert q.fetchone()[0]==0
 meta("update RRL_TOPOLOGY_CELL_SLOT set CAPACITY_WEIGHT_KG=100 where CELL_SLOT_ID=:s",s=slot)
 canonical=StockCommand(operation_id=unload["operation_id"],command_type="UNLOAD_SHIPMENT",actor=sender,source={"load_operation_id":load_id},metadata={k:v for k,v in unload.items()if k not in("operation_id","load_operation_id")},lines=()).canonical_json();out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,sender,out,None]);assert out.getvalue()is None;q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select STATUS,HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3 from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=:s",s=slot);assert q.fetchone()==("OCCUPIED",10,1.5)
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=:s",s=slot);assert q.fetchone()[0]==0
 with ThreadPoolExecutor(2)as pool:rs=list(pool.map(lambda b:sender_api.post(base+"/api/transport/loading/unload",json=b),[unload,{**unload,"operation_id":unload["operation_id"]+":OTHER"}]))
 assert sorted(r.status_code for r in rs)==[200,409],[(r.status_code,r.text[:1700])for r in rs];result=next(r.json()for r in rs if r.status_code==200);unload["operation_id"]=result["operation_id"]
 assert api(sender_api,"POST","/api/transport/loading/unload",unload)==result
 q.execute("select c.TASK_ID,c.STATUS,c.HU_GROSS_WEIGHT_KG,c.HU_BOUNDING_VOLUME_M3,t.STATUS from RRL_RECEIPT_SLOT_CLAIM c join RRL_WAREHOUSE_TASK t on t.TASK_ID=c.TASK_ID where c.CELL_SLOT_ID=:s",s=slot);task,status,mass,volume,task_status=q.fetchone();assert(status,mass,volume,task_status)==("OCCUPIED",10,1.5,"DONE")
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:t",t=task);assert q.fetchone()[0]=="SYNCED"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select distinct CELL_SLOT_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",u=lot);assert q.fetchall()==[(slot,)]
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS222 original FULLPAL current slot required/obsolete published slot refused/late capacity rollback/native late outer rollback/concurrent one winner/replay/native+3/P3H3/current measured OCCUPIED10kg1.5m3/DONE-SYNCED/same HARD coverage/current slot/protected13520/20",load_id,slot,code,task,unload["operation_id"],flush=True)
 print("Own primary3/3 and measured current slot retained for next existing reload; no fabricated release",flush=True)
"""
print(json.dumps({"scripts/ni052_fullpal_current_slot_case.py":prefix+body},ensure_ascii=True))
