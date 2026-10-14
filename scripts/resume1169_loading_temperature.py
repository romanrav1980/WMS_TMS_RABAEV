exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
from app.oracle_gateway import OracleGateway
context_path=Path("tmp/context1168.json");context=json.loads(context_path.read_text(encoding="utf-8"))
assert context["state"]=="BUILDING","This continuation starts after pick/bind/move; do not replay after loading"
tag=context["tag"];lot=context["lot"];ware=context["warehouse_id"];shipcell=context["ship_cell"];dst=context["target_cell"]
st_uid=context["st_identifier"];article=context["article"];vehicle=context["vehicle_id"];trip=context["trip_id"];dock=context["dock"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**b):
  if ":ware" in sql:b["ware"]=ware
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):
  q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def post(kind,body,source,op=None):
  command={"contract_version":2,"operation_id":op or "FULL.QA:"+uuid4().hex,"command_type":kind,"actor":"admin","source":source,"lines":[],"units":[],"metadata":body}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=out.getvalue();conn.commit();return json.loads(result.read() if hasattr(result,"read") else result)
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SKU_RULE'and NULLABLE='N'order by COLUMN_ID");print("Required SKU columns",json.dumps(q.fetchall()),flush=True)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:ware,:a,:cell,2,6)",a=article,cell=dst)
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
