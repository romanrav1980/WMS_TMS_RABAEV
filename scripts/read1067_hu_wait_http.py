import httpx,json
from pathlib import Path
record=json.loads(Path("tmp/context1057.json").read_text(encoding="utf-8"))
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 r=c.get("/api/warehouse-tasks",params={"status":"DONE","queue_group":"DEFER_WAITING","limit":500})
 assert r.status_code==200,(r.status_code,r.text[:600]);task=next(t for t in r.json()if t["task_id"]==1149)
 assert task["wait_st_number"]==record["st"] and task["unit_code"]=="HU"
 waiting=c.get("/api/receiving/st-deferrals/waiting-tasks",params={"decision_operation_id":record["decision"],"after_task_id":1148})
 assert waiting.status_code==200 and waiting.json()["tasks"][0]["task_id"]==1149
 replay=c.post("/api/receiving/st-deferrals/waiting-tasks",json={"operation_id":"HU1057.PLAN:4bb85f1f15","decision_operation_id":record["decision"]})
 assert replay.status_code==200 and replay.json()==record["plan"],(replay.status_code,replay.text[:600])
 detail=c.get("/api/warehouse-tasks/1149");assert detail.status_code==200
 Path("tmp/http1067_hu_wait.json").write_text(json.dumps({"task":task,"detail":detail.json(),"waiting":waiting.json(),"original_plan_replay":replay.json()},indent=2),encoding="utf-8")
print("PASS1067 actual HTTP originalHU waiting family/currentdetail/DONE1HU/SYNCED/exact cachedplan outbox5131/no new move")
