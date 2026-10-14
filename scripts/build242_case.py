from pathlib import Path
import json
s=Path("scripts/continue230_to_store.py").read_text(encoding="utf-8").replace("context230.json","context242.json").replace("IW230","IW242").replace("QI230","QI242").replace("Own230","Own242").replace("READY230","READY242")
s=s.replace("import oracledb,httpx","import oracledb,httpx\nfrom uuid import uuid4\nfrom concurrent.futures import ThreadPoolExecutor",1)
anchor=' q.execute("select a.BARCODE_SHT'
insert=''' meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:w,:a,:cell,2,4)",w=ctx["target_ware"],a=ctx["article"],cell=ctx["outbound"])
 meta("insert into RRL_RECEIPT_CELL_RULE(WARE_ID,CELL,TEMP_MIN,TEMP_MAX)values(:w,:cell,2,4)",w=ctx["target_ware"],cell=ctx["outbound"])
 thermal={"operation_id":"IW242.MODE:"+tag,"plan_operation_id":ctx["plan"],"decision_kind":"PROCEED","expected_revision":0,"observed_c":"3","task_temp_min":"2","task_temp_max":"4","observation_reference":"Own manual act "+tag,"reason":"Own original task mode","decision_reference":"IW242:"+tag}
 api("POST","/api/inventory/interwarehouse/temperature-decisions",thermal)
'''
s=s.replace(anchor,insert+anchor,1)
anchor=' command={"contract_version":2'
insert=''' old_task=task
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**thermal,"operation_id":"IW242.NEW.MODE:"+tag,"expected_revision":1,"task_temp_min":"2.5","task_temp_max":"3.5","reason":"Own narrowed administrative task mode"})
 replan={"operation_id":"IW242.REPLAN:"+tag,"receipt_operation_id":receipt,"superseded_task_id":old_task,"replan_reason":"Own exact changed task range; old task unstarted"}
 refused=api("POST","/api/inventory/interwarehouse/placement",replan,409);assert "CELL_TEMPERATURE_INCOMPATIBLE"in json.dumps(refused),refused
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=old_task);assert q.fetchone()[0]=="PLANNED"
 meta("update RRL_RECEIPT_CELL_RULE set TEMP_MIN=2.5,TEMP_MAX=3.5 where WARE_ID=:w and CELL=:cell",w=ctx["target_ware"],cell=ctx["outbound"])
 actor="WR242"+tag;group=actor.upper();secret=uuid4().hex
 meta("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own replan receiver',:g,:w,0,0)",a=actor,p=secret,g=group,w=ctx["target_ware"])
 for permission in["interwarehouse_receive","warehouse_task_edit"]:meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,:p)",g=group,p=permission)
 own=httpx.Client(auth=(actor,secret),timeout=35)
 rolled={"contract_version":2,"operation_id":"IW242.ROLLBACK:"+tag,"command_type":"INTERWARE_PUTAWAY_PLAN","actor":actor,"source":{"receipt_operation_id":receipt},"lines":[],"units":[],"metadata":{"superseded_task_id":old_task,"replan_reason":replan["replan_reason"]}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(rolled),actor,out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  c.rollback()
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=old_task);assert q.fetchone()[0]=="PLANNED"
 q.execute("select count(*)from RRL_INTERWARE_PUT_PLAN where RECEIPT_OPERATION_ID=:r",r=receipt);assert q.fetchone()[0]==1
 def contender(i):
  body={**replan,"operation_id":"IW242.REPLAN:"+tag+str(i)}
  r=own.post(base+"/api/inventory/interwarehouse/placement",json=body);return body,r
 with ThreadPoolExecutor(2)as pool:attempts=list(pool.map(contender,[1,2]))
 assert sorted(r.status_code for _,r in attempts)==[200,409],[(r.status_code,r.text[:2400])for _,r in attempts]
 winner,response=next(x for x in attempts if x[1].status_code==200);saved=response.json();task=saved["task_id"]
 assert saved["superseded_task_id"]==old_task and saved["temperature"]["task_temp_min"]==2.5 and saved["temperature"]["task_temp_max"]==3.5
 repeated=own.post(base+"/api/inventory/interwarehouse/placement",json=winner);assert repeated.status_code==200 and repeated.json()==saved,repeated.text
 q.execute("select STATUS,CANCELLED_BY from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=old_task);assert q.fetchone()==("CANCELLED",actor)
 q.execute("select TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID=:t",t=old_task);assert q.fetchone()==(2,4)
 q.execute("select TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID=:t",t=task);assert q.fetchone()==(2.5,3.5)
 q.execute("select count(*)from RRL_INTERWARE_PUT_PLAN ip join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=ip.TASK_ID where ip.RECEIPT_OPERATION_ID=:r and wt.STATUS!='CANCELLED'",r=receipt);assert q.fetchone()[0]==1
 meta("delete from RIGHTS where USER_GROUP=:g and upper(RIGHT1)='WAREHOUSE_TASK_EDIT'",g=group)
 denied=own.post(base+"/api/inventory/interwarehouse/placement",json=winner);assert denied.status_code==403,denied.text
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'warehouse_task_edit')",g=group)
 denied=own.post(base+"/api/inventory/interwarehouse/placement",json={**replan,"operation_id":"IW242.OLD.AGAIN:"+tag});assert denied.status_code==409,denied.text
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(3,0)
 print("REPLAN242",old_task,task,"current scoped receiver/currentedit before cached/old2-4/new2.5-3.5/P3H0/native rollback/concurrent one winner/replay/no double plan",flush=True)
 meta("update RUSERS set DELETED=1 where ID=:a",a=actor)
'''
s=s.replace(anchor,insert+anchor,1)
s=s.replace(' print("READY242"',' print("PASS242 atomic original task replan/old cancelled/new one task/changed range/new old-native complete/QC/load-depart/same3units6codes/protected");\n print("READY242"',1)
print(json.dumps({"scripts/case242_replan.py":s},ensure_ascii=True))
