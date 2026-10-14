from pathlib import Path
import json
s=Path("scripts/continue230_to_store.py").read_text(encoding="utf-8").replace("context230.json","context240.json").replace("IW230","IW240").replace("QI230","QI240").replace("Own230","Own240").replace("READY230","READY240")
anchor=' q.execute("select a.BARCODE_SHT'
insert=''' meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:w,:a,:cell,2,4)",w=ctx["target_ware"],a=ctx["article"],cell=ctx["outbound"])
 meta("insert into RRL_RECEIPT_CELL_RULE(WARE_ID,CELL,TEMP_MIN,TEMP_MAX)values(:w,:cell,2,4)",w=ctx["target_ware"],cell=ctx["outbound"])
 thermal={"operation_id":"IW240.HOLD:"+tag,"plan_operation_id":ctx["plan"],"decision_kind":"HOLD","expected_revision":0,"observed_c":"8.125","observation_reference":"Own manual act "+tag,"reason":"Own manual deviation awaiting dispatcher decision","decision_reference":"IW240:"+tag}
 held=api("POST","/api/inventory/interwarehouse/temperature-decisions",thermal);assert held["revision"]==1 and held["observed_c"]==8.125 and not held["stock_changed"]and not held["sensor_verified"],held
 assert api("POST","/api/inventory/interwarehouse/temperature-decisions",thermal)==held
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**thermal,"reason":"changed"},409)
'''
s=s.replace(anchor,insert+anchor,1)
anchor=' placed=api("POST","/api/inventory/interwarehouse/placement"'
insert=''' denied=api("POST","/api/inventory/interwarehouse/placement",{"operation_id":"IW240.EARLY:"+tag,"receipt_operation_id":receipt},409);assert "INTERWARE_TEMPERATURE_DISPATCHER_HOLD"in json.dumps(denied),denied
 denied=api("POST",f"/api/transport/loading/{ctx['target_trip']}/depart",{"operation_id":"IW240.EARLY.DEPART:"+tag},409);assert "INTERWARE_TEMPERATURE_DISPATCHER_HOLD"in json.dumps(denied),denied
 proceed={**thermal,"operation_id":"IW240.PROCEED:"+tag,"decision_kind":"PROCEED","expected_revision":1,"task_temp_min":"2","task_temp_max":"4","reason":"Own administrative quality disposition; preserve approved task range"}
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**proceed,"operation_id":"IW240.BAD.RANGE:"+tag,"task_temp_min":"1","task_temp_max":"6"},409)
 rolled={**proceed,"operation_id":"IW240.ROLLBACK:"+tag,"actor":"admin"}
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:q.callproc("RRL_INTERWARE_THERMAL.record_decision",[json.dumps(rolled,sort_keys=True,separators=(",",":")),"admin",out]);c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_INTERWARE_THERMAL_FACT where OPERATION_ID=:op",op=rolled["operation_id"]);assert q.fetchone()[0]==0
 released=api("POST","/api/inventory/interwarehouse/temperature-decisions",proceed);assert released["revision"]==2 and released["task_temp_min"]==2 and released["task_temp_max"]==4,released
'''
s=s.replace(anchor,insert+anchor,1)
anchor=' command={"contract_version":2'
insert=''' q.execute("select TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID=:id",id=task);assert q.fetchone()==(proceed["operation_id"],2,4)
 # HOLD after task creation prevents original native movement; later same-range release retains task mode.
 stop={**thermal,"operation_id":"IW240.TASK.HOLD:"+tag,"expected_revision":2}
 api("POST","/api/inventory/interwarehouse/temperature-decisions",stop)
 denied_command={"contract_version":2,"operation_id":"IW240.TASK.EARLY:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":cell,"scanned_to_cell":ctx["outbound"]}}
 denied_out=q.var(oracledb.DB_TYPE_CLOB)
 try:q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(denied_command),"admin",denied_out,None]);raise AssertionError("thermal HOLD movement escaped")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20886 and "TEMPERATURE_DISPATCHER_HOLD"in str(exc),str(exc)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**proceed,"operation_id":"IW240.TASK.PROCEED:"+tag,"expected_revision":3})
'''
s=s.replace(anchor,insert+anchor,1)
s=s.replace(' print("READY240"',' print("PASS240 manual HOLD/replay/conflict/known SKU range/native rollback/receipt blocked cell/P3/original task mode preserved/HOLD after planned prevents native move/same-range release/old complete-QC-load-depart/current original3units6codes");\n print("READY240"',1)
print(json.dumps({"scripts/case240_thermal.py":s},ensure_ascii=True))
