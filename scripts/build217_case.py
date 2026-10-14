from pathlib import Path
import json
s=Path("scripts/ni063_fullpal_tare_case.py").read_text(encoding="utf-8")
start=s.index('  post("TARE_COUNT"');end=s.index('  post("WAVE_PICK_RELEASE"',start);s=s[:start]+s[end:]
end=s.index("  import httpx",s.index('shipop="SINGLE.FULL.LOAD:"'))
s=s[:end]+"""
  import httpx
  from concurrent.futures import ThreadPoolExecutor
  from app.modules.inventory.contracts_stock import StockCommand
  actor="UL217"+tag;group=actor.upper();secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p_actor,:p_secret,'Own217 unload',:p_group,:p_ware,0,0)",p_actor=actor,p_secret=secret,p_group=group,p_ware=ware);conn.commit()
  admin_api=httpx.Client(auth=("admin","admin123"),timeout=35)
  for path,data in[("/api/admin/rights/groups",{"id":group,"name":"Own217 unload"}),(f"/api/admin/rights/groups/{group}/rights",{"right_name":"stock_posting_shipping","description":"Own217 original warehouse"})]:
   response=admin_api.post("http://127.0.0.1:8088"+path,json=data);assert response.status_code==200,response.text[:1400]
  client=httpx.Client(auth=(actor,secret),timeout=35);uri="http://127.0.0.1:8088/api/transport/loading/unload"
  request={"operation_id":"FULL217.UNLOAD:"+tag,"load_operation_id":shipop,"expected_version":preview["expected_version"],"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own217 whole fullpal physically unloaded before departure"}
  canonical=StockCommand(operation_id=request["operation_id"],command_type="UNLOAD_SHIPMENT",actor=actor,source={"load_operation_id":shipop},metadata={k:v for k,v in request.items()if k not in("operation_id","load_operation_id")},lines=()).canonical_json()
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,actor,out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=lot,p_cell=shipcell);assert q.fetchone()==(3,3)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p_load",p_load=shipop);assert q.fetchone()[0]=="LOADED"
  with ThreadPoolExecutor(2)as pool:responses=list(pool.map(lambda body:client.post(uri,json=body),[request,{**request,"operation_id":request["operation_id"]+":OTHER"}]))
  assert sorted(r.status_code for r in responses)==[200,409],[(r.status_code,r.text[:1900])for r in responses]
  result=next(r.json()for r in responses if r.status_code==200);request["operation_id"]=result["operation_id"]
  assert client.post(uri,json=request).json()==result
  q.execute("select ff.STATUS,ff.PICKED_STOCK_VERSION,rem.STOCK_VERSION,ff.PICKED_WAREHOUSE_TASK_ID,ff.PICKED_PALLET_UID,rem.REMAIN,rem.HARD_RESERVED_BASE from RRL_CUSTOMER_ORDER_FULFILLMENT ff join RRL_REMAINS rem on rem.UID_POLETA=ff.PICKED_PALLET_UID and rem.CELL=:p_cell where ff.FULFILLMENT_ID=:p_id",p_cell=shipcell,p_id=ff)
  state,picked,current,original_task,uid,physical,hard=q.fetchone();assert state=="PICKED"and picked==current and original_task==task and uid==lot and(physical,hard)==(3,3)
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="DONE"
  q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=shipop);assert q.fetchone()[0]==-3
  q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=result["operation_id"]);assert q.fetchone()[0]==3
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=actor);conn.commit()
  try:assert client.post(uri,json=request).status_code==403
  finally:q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=actor);conn.commit()
  print("PASS217 original FULLPAL3 native unload/rollback/concurrent1winner/replay/currentWARE403/original-3/new+3/P3H3/FF PICKED current stock version/same original DONE task and UID retained",ware,wave,st_uid,shipop,result["operation_id"],flush=True)
 finally:
  # Keep actual restored primary cargo/owner for the next original QC/reload scenario.
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:p_uid and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",p_uid=other)
  for(rid,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Own217 spare fixture cleanup"},{"reservation_id":int(rid)})
  q.execute("select CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and REMAIN>0",p_uid=other)
  counts=[{"uid":other,"cell":cell,"article":article,"unit":uom,"quantity":"0","expected_stock_version":int(v),"unit_keys":[]}for cell,uom,v in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"Own217 spare fixture zero","counts":counts},{"revision_id":revision})
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own217 spare zero/protected13520/20; actual primary3/3 remains for fresh QC and existing reload, no fabricated cleanup",flush=True)
"""
# Use ASCII VARCHAR canonical input, avoiding unnecessary temporary CLOB input.
s=s.replace('q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])','q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])')
print(json.dumps({"scripts/ni052_fullpal_unload_case.py":s},ensure_ascii=True))
