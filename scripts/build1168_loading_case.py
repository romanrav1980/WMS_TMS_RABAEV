from pathlib import Path
import json
old=Path("scripts/ni052_single_fullpal_case.py").read_text(encoding="utf-8")
prefix=old.split(" try:\n  for u,cell in",1)[0]
prefix=prefix.replace('"""Actual full-pallet move -> existing ST binding -> pinned shipment; clean only own P/H through root."""','"""One fresh thermal loading case through real root; retain receipt for continuation, never rerun factory."""')
prefix=prefix.replace("cfg=get_settings();tag=", 'context_path=Path("tmp/context1168.json");assert not context_path.exists(),"Retained fixture; continue from context, do not recreate"\ncfg=get_settings();tag=')
prefix=prefix.replace('with oracledb.connect(user=cfg.oracle_user', 'context={"tag":tag,"lot":lot,"state":"BUILDING"};context_path.write_text(json.dumps(context),encoding="utf-8")\nwith oracledb.connect(user=cfg.oracle_user')
prefix=prefix.replace("ware=100000+int(tag[:6],16);shipcell=", "ware=100000+int(tag[:6],16);context['warehouse_id']=ware;context_path.write_text(json.dumps(context),encoding='utf-8');shipcell=")
prefix=prefix.replace("where ID>0","where ID>0 and nvl(DELETED,0)=0")
prefix=prefix.replace("values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',0.125)","values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'EA',3)")
line=' meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,TRANSTASK_ID) values(:id,:u,:u,:ware,0,:tt)",id=pending_st,u="TT.PENDING:"+tag,tt=trip)\n'
assert line in prefix;prefix=prefix.replace(line,"")
tail="""
 context.update({"article":article,"order_id":order,"task_id":task,"st_id":st,"st_identifier":st_uid,"vehicle_id":vehicle,"trip_id":trip,"dock":dock,"ship_cell":shipcell,"source_cell":src,"target_cell":dst})
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"Own1168 thermal loading case"},{"revision_id":revision})
 post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
 post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
 post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
 preview=FullPalletShipment(OracleGateway()).preview(task)
 post("PICK_PALLET_BIND_SHIPMENT",{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])},{"task_id":task})
 post("INTERNAL_MOVE",{"uid":lot,"source_cell":dst,"target_cell":shipcell,"quantity":"0","unit":"EA"},{})
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,TEMP_MIN,TEMP_MAX)values(:ware,:a,2,6)",a=article)
 from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
 profile_service=VehicleProfiles(OracleGateway());profile=profile_service.read(vehicle,"admin")
 profile_body={"operation_id":"THERMAL1168.PROFILE:"+tag,"vehicle_id":vehicle,"expected_version":0,"expected_source_hash":profile["base_hash"],"vehicle_size_class":"DEV.THERMAL1168","cargo_length_mm":6000,"cargo_width_mm":2400,"cargo_height_mm":2600,"reason":"Private thermal loading case","evidence_reference":"DEV1168:"+tag,"temp_min_c":"-20","temp_max_c":"8"}
 profile_service.configure(profile_body,"admin")
 from app.transport_composition import build_transport_loading
 loading=build_transport_loading();preview=loading.preview_single(st_uid,"admin")
 loading_context={"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 ship_body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":shipcell,"loading_context":loading_context}
 context.update({"state":"READY_TO_LOAD","preview":preview,"body_without_temperature":ship_body,"profile_body":profile_body});context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 for metadata,expected in((ship_body,"LOAD_THERMAL_CURRENT_CONFIRMATION_REQUIRED"),({**ship_body,"loading_context":{**loading_context,"temperature_confirmation":{"origin":"MANUAL_AT_LOADING","observed_c":"20","vehicle_profile_version":1,"observation_reference":"DEV1168.BAD:"+tag}}},"LOAD_THERMAL_OBSERVATION_INCOMPATIBLE")):
  try:post("LOAD_SHIPMENT",metadata,{"pallet_identifier":st_uid});raise AssertionError("Bad thermal load accepted")
  except oracledb.DatabaseError as exc:assert expected in str(exc),str(exc)
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 confirmation={"origin":"MANUAL_AT_LOADING","observed_c":"3.125","vehicle_profile_version":1,"observation_reference":"DEV1168.MEASURE:"+tag}
 final_body={**ship_body,"loading_context":{**loading_context,"temperature_confirmation":confirmation}}
 trial_op="THERMAL1168.ROLLBACK:"+tag
 command={"contract_version":2,"operation_id":trial_op,"command_type":"LOAD_SHIPMENT","actor":"admin","source":{"pallet_identifier":st_uid},"lines":[],"units":[],"metadata":final_body}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select count(*)from RRL_TT_LOAD_THERMAL_FACT where LOAD_OPERATION_ID=:o",o=trial_op);assert q.fetchone()==(1,)
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o",o=trial_op);assert q.fetchone()==(0,)
 ship_op="THERMAL1168.LOAD:"+tag
 context.update({"state":"LOADING","load_operation_id":ship_op,"body":final_body});context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 result=loading.load_single(ship_op,st_uid,final_body,"admin");assert loading.load_single(ship_op,st_uid,final_body,"admin")==result
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 q.execute("select VEHICLE_ID,PROFILE_VERSION,OBSERVED_C,OBSERVATION_BASIS,SENSOR_VERIFIED from RRL_TT_LOAD_THERMAL_FACT where LOAD_OPERATION_ID=:o",o=ship_op);assert q.fetchone()==(vehicle,1,3.125,"MANUAL_AT_LOADING",0)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
 context.update({"state":"LOADED","result":result,"protected_stock":[20,20]});context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 print(json.dumps({"case":"PASS1168","trip":trip,"vehicle":vehicle,"load_operation":ship_op,"observed_c":"3.125","stock":[0,0],"protected":[20,20]}))
"""
print(json.dumps({"scripts/case1168_loading_temperature.py":prefix+tail}))
