from pathlib import Path
import json,httpx
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));m=json.loads(Path("tmp/context773.json").read_text(encoding="utf-8"))
url="http://127.0.0.1:8088/api/receiving/st-deferrals/waiting-tasks"
with httpx.Client(auth=("admin","admin123"),timeout=30)as c:
 body={"operation_id":m["plan_operation"],"decision_operation_id":ctx["defer_operation"]}
 r=c.post(url,json=body);assert r.status_code==200 and r.json()==m["plan_result"],r.text
 r=c.get(url,params={"decision_operation_id":ctx["defer_operation"],"limit":1});assert r.status_code==200,r.text
 result=r.json();assert len(result["tasks"])==1 and result["tasks"][0]["task_id"]==m["task"] and result["tasks"][0]["status"]=="DONE"and result["tasks"][0]["sync_status"]=="SYNCED"
 r=c.get(url,params={"decision_operation_id":ctx["defer_operation"],"after_task_id":m["task"],"limit":1});assert r.status_code==200 and r.json()["tasks"]==[],r.text
 r=c.get(url,params={"decision_operation_id":ctx["defer_operation"],"limit":201});assert r.status_code==422,r.text
 r=c.get(url,params={"decision_operation_id":"NOT_A_DECISION785"});assert r.status_code==404,r.text
 body={"operation_id":"WAIT785:"+ctx["tag"],"decision_operation_id":ctx["defer_operation"]}
 r=c.post(url,json=body);assert r.status_code==200,r.text
 skip=r.json();assert skip["tasks"]==[] and skip["already_waiting"]==[ctx["lot"]]and skip["stock_changed"]is False
 r=c.post(url,json=body);assert r.status_code==200 and r.json()==skip,r.text
 Path("tmp/context785.json").write_text(json.dumps({"body":body,"result":skip,"read":result}),encoding="utf-8")
 r=c.get("http://127.0.0.1:8088/api/transport/st-deferrals/context",params={"st_number":ctx["st_uid"]});assert r.status_code==200 and r.json()["physical_preparation"]["physical_move_required"]is False,r.text
print("785 PASS currentHTTP original773 replay/current taskDONE-SYNCED/keyset/bounds/scope404/already waiting no new task/exact repeat")
