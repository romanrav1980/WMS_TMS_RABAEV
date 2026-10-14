import json,httpx
from pathlib import Path
r=json.loads(Path("tmp/context1080.json").read_text(encoding="utf-8"))
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 read=c.get("/api/receiving/st-deferrals/waiting-tasks",params={"decision_operation_id":r["decision"],"limit":50})
 assert read.status_code==200,(read.status_code,read.text[:500])
 result=read.json()
 assert result["selection_required"]is True and {p["place_kind"]for p in result["available_places"]}=={"HU","CASE"},result
 for kind in("hu","case"):
  response=c.post("/api/receiving/st-deferrals/waiting-tasks",json=r[kind+"_plan_request"])
  assert response.status_code==200 and response.json()==r[kind+"_plan"],(response.status_code,response.text[:700])
  task=c.get("/api/warehouse-tasks/"+str(r[kind+"_task"]))
  assert task.status_code==200 and task.json()["status"]=="DONE",task.text[:400]
 no=c.post("/api/receiving/st-deferrals/waiting-tasks",json={"operation_id":"HU1083.NOSELECTION:4bb85f1f15","decision_operation_id":r["decision"]})
 assert no.status_code==409 and no.json()["detail"]["code"]=="ST_WAITING_ROOT_SELECTION_REQUIRED",(no.status_code,no.text[:600])
 Path("tmp/http1083_mixed.json").write_text(json.dumps({"read":result,"missing_selection":no.json(),"exact_replays":True},indent=2),encoding="utf-8")
 print("PASS1083 mixed places HTTP/current typed DONE/two exact plan replays/missing choice409")
