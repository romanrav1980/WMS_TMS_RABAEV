from pathlib import Path
import json
s=Path("scripts/case1168_loading_temperature.py").read_text(encoding="utf-8").split(" from app.modules.transport.infrastructure.vehicle_profile",1)[0]
s=s.replace("context1168.json","context1206.json").replace("Own1168 thermal loading case","Own1206 full stock-pallet type case")
old=' vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QL"+tag,trtype,100,1,0,None]));conn.commit()'
assert old in s;s=s.replace(old,' vehicle=10100\n q.execute("select NUM,TR_TYPE from RRL_TR_VEHICLE where ID=:id",id=vehicle);vehicle_plate,trtype=q.fetchone()')
s=s.replace('"QL"+tag',"vehicle_plate").replace(';pending_st=seq("RRL_SBORKA_PALLETS_SQ")',"")
s+=''' from app.transport_composition import build_transport_loading
 from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
 from app.modules.inventory.infrastructure.pallet_floor_type import PalletFloorType
 from app.modules.platform.public import read_oracle_json
 service=PalletFloorType(OracleGateway(),StockPosting())
 current=service.read(lot,"admin");assert current["version"]==0
 type_meta={"pallet_type_id":1,"expected_version":0,"scan_pallet":lot,"scan_cell":shipcell,"evidence_reference":"DEV1206:software declaration, not real fleet evidence"}
 type_op="PALLET.TYPE1206:"+tag
 context.update(state="READY_TO_DECLARE_TYPE",vehicle_plate=vehicle_plate,type_meta=type_meta,type_operation=type_op)
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 trial=type_op+".ROLLBACK";command={"contract_version":2,"operation_id":trial,"command_type":"PALLET_FLOOR_TYPE_CONFIRM","actor":"admin","source":{"uid":lot},"lines":[],"units":[],"metadata":type_meta}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  result=read_oracle_json(out.getvalue());assert result["stock_changed"]is False
  q.execute("select TYPE_VERSION,PALLET_TYPE_ID from RRL_PALLET_FLOOR_TYPE where UID_PALLET=:u",u=lot);assert q.fetchone()==(1,1)
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_PALLET_FLOOR_TYPE where UID_PALLET=:u",u=lot);assert q.fetchone()==(0,)
 result=service.confirm(type_op,lot,type_meta,"admin");assert service.confirm(type_op,lot,type_meta,"admin")==result
 current=service.read(lot,"admin");assert current["version"]==1 and current["pallet_type_id"]==1
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:u",u=lot);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=type_op);assert q.fetchone()==(0,)
 loading=build_transport_loading();preview=loading.preview_single(st_uid,"admin")
 body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":shipcell,
       "loading_context":{"transport_task_id":trip,"scan_vehicle":vehicle_plate,"scan_dock":dock,
        "measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"},
        "temperature_confirmation":{"origin":"MANUAL_AT_LOADING","observed_c":"3.125","vehicle_profile_version":2,"observation_reference":"DEV1206.TEMP:"+tag}}}
 context.update(state="READY_TO_LOAD",type_result=result,current_type=current,body=body,load_operation_id="PALLET1206.LOAD:"+tag)
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 result=loading.load_single(context["load_operation_id"],st_uid,body,"admin")
 assert loading.load_single(context["load_operation_id"],st_uid,body,"admin")==result
 q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN,SOURCE_REFERENCE from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=context["load_operation_id"]);assert q.fetchone()==(1,"ROOT_STOCK_TYPE",type_op)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:u",u=lot);assert q.fetchone()==(0,0)
 assert service.confirm(type_op,lot,type_meta,"admin")==context["type_result"],"Cached declaration survives subsequent shipping"
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=5062399");assert q.fetchone()==(20,20)
 context.update(state="LOADED",result=result,protected_stock=[20,20]);context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 print(json.dumps({"case":"PASS1206","trip":trip,"vehicle":vehicle,"type":1,"metadata_goods_effect":0,"load_stock":[0,0],"protected":[20,20]}))
'''
print(json.dumps({"scripts/case1206_stock_floor.py":s}))
