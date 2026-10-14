import json,httpx
from pathlib import Path
r=json.loads(Path("tmp/context1086.json").read_text(encoding="utf-8"))
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=20)as c:
 out={}
 for k in("a","b"):
  res=c.post("/api/receiving/st-deferrals/waiting-tasks",json=r[k+"_request"]);assert res.status_code==200 and res.json()==r[k+"_plan"],(res.status_code,res.text[:400])
 read=c.get("/api/receiving/st-deferrals/waiting-tasks",params={"decision_operation_id":r["decision"],"limit":50});assert read.status_code==200
 assert len(read.json()["available_places"])==2 and all(x["place_kind"]=="HU"for x in read.json()["available_places"])
 wave=c.get("/api/picking/waves/553/execution");assert wave.status_code==200
 cases=[x for x in wave.json()["items"]if x["kind"]=="CASE"];assert len(cases)==2
 assert [x["case_content_version"]for x in cases]==[20,13]and all(x["control_identifier"]and x["current_cell"]=="QW4bb85f1f15"for x in cases)
 assert wave.json()["ready"]is False and wave.json()["completed"]is False
 for case in cases:
  qc=c.get("/api/outgoing-quality/"+case["control_identifier"]);assert qc.status_code==200 and qc.json()["case_content_version"]==case["case_content_version"]
 out={"waiting":read.json(),"wave":wave.json(),"cached_two_top_plans":True}
 Path("tmp/http1093_workflow.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
 print("PASS1093 twoTOP cache/current wait/wave CASE location-version/existing QC sameversion/no writes")
