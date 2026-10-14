import json,httpx
from pathlib import Path
deep=json.loads(Path("tmp/context1069.json").read_text(encoding="utf-8"));already=json.loads(Path("tmp/context1072.json").read_text(encoding="utf-8"))
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 tree=c.get("/api/warehouse-hus/composition",params={"identifier":deep["root"]});assert tree.status_code==200,(tree.status_code,tree.text[:300])
 record={}
 replay=c.post("/api/receiving/st-deferrals/waiting-tasks",json=already["request"])
 assert replay.status_code==200 and replay.json()==already["result"],(replay.status_code,replay.text[:700])
 task=c.get("/api/warehouse-tasks/"+str(deep["task"]));assert task.status_code==200 and task.json()["status"]=="DONE"and task.json()["unit_code"]=="HU"
 query=c.get("/api/receiving/st-deferrals/waiting-tasks",params={"decision_operation_id":deep["decision"],"after_task_id":deep["task"]-1,"limit":10});assert query.status_code==200
 rows=query.json()["tasks"];assert rows[0]["task_id"]==deep["task"]and rows[0]["sync_status"]=="SYNCED"
 record={"already_waiting_replay":replay.json(),"task":task.json(),"waiting_read":query.json()}
 Path("tmp/http1073_deep_wait.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
print("PASS1073 actual HTTP deep1HU/DONE/SYNCED/alreadyWaiting emptytasks exactreplay/no new movement")
