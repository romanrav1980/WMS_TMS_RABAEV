from pathlib import Path
import json
s=Path("scripts/case1168_loading_temperature.py").read_text(encoding="utf-8").split(" from app.modules.transport.infrastructure.vehicle_profile",1)[0]
s=s.replace("context1168.json","context1194.json").replace("Own1168 thermal loading case","Own1194 physical top tare case")
old=' vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QL"+tag,trtype,100,1,0,None]));conn.commit()'
assert old in s
s=s.replace(old,' vehicle=10100\n q.execute("select NUM,TR_TYPE from RRL_TR_VEHICLE where ID=:id",id=vehicle);vehicle_plate,trtype=q.fetchone()')
s=s.replace('"QL"+tag',"vehicle_plate").replace(';pending_st=seq("RRL_SBORKA_PALLETS_SQ")',"")
s+=''' from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
 from app.transport_composition import build_transport_loading
 hu=WarehouseHu(OracleGateway());loading=build_transport_loading()
 context.update(state="READY_TO_ASSEMBLE",top=top,vehicle_plate=vehicle_plate);context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 hu.command("HU_CREATE",top,"FLOOR1194.CREATE:"+tag,{"cell":shipcell,"warehouse":ware,"container_type":"PALLET","tare_weight_kg":"1","scan_container":top,"scan_cell":shipcell},"admin")
 outer=hu.preview(top,"admin");leaf=hu.preview(lot,"admin")
 hu.command("HU_ATTACH",top,"FLOOR1194.ATTACH:"+tag,{"child_uid":lot,"expected_version":outer["nodes"][0]["version"],"expected_child_version":leaf["nodes"][0]["version"],"scan_container":top,"scan_child":lot},"admin")
 post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own1194 software dev tare opening","decision_reference":"DEV1194:"+tag},{},"FLOOR1194.COUNT:"+tag)
 post("TARE_BOOK",{"pallet_type_id":1},{"place_kind":"HU","place_id":top},"FLOOR1194.BOOK:"+tag)
 tree=hu.preview(top,"admin");assert tree["top_place_count"]==1 and len(tree["nodes"])==2
 body={"expected_version":tree["nodes"][0]["version"],"scan_container":top,"scan_cell":shipcell,
       "loading_context":{"transport_task_id":trip,"scan_vehicle":vehicle_plate,"scan_dock":dock,
        "measurements":{"origin":"MANUAL_CONFIRMED","content_version":tree["nodes"][0]["version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"},
        "temperature_confirmation":{"origin":"MANUAL_AT_LOADING","observed_c":"3.125","vehicle_profile_version":2,"observation_reference":"DEV1194.TEMP:"+tag}}}
 trial="FLOOR1194.ROLLBACK:"+tag
 command={"contract_version":2,"operation_id":trial,"command_type":"HU_SHIP","actor":"admin","source":{"uid":top},"lines":[],"units":[],"metadata":body}
 context.update(state="READY_TO_LOAD",body=body,tree=tree,trial_operation=trial,load_operation="FLOOR1194.LOAD:"+tag)
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=trial)
  assert q.fetchone()==(1,"HELD_HU_TARE_BOOK")
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=trial);assert q.fetchone()==(0,)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(3,3)
 result=loading.load(context["load_operation"],top,body,"admin")
 assert loading.load(context["load_operation"],top,body,"admin")==result
 q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN,PROFILE_VERSION from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=context["load_operation"]);assert q.fetchone()==(1,"HELD_HU_TARE_BOOK",2)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(0,0)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=5062399");assert q.fetchone()==(20,20)
 context.update(state="LOADED",result=result,protected_stock=[20,20])
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 print(json.dumps({"case":"PASS1194","trip":trip,"vehicle":vehicle,"top_type":1,"top_count":1,"nodes":2,"stock":[0,0],"protected":[20,20]}))
'''
print(json.dumps({"scripts/case1194_physical_floor.py":s}))
