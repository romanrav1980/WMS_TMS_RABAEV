import httpx,json
from pathlib import Path
ctx=json.loads(Path("tmp/context966.json").read_text(encoding="utf-8"));base="http://127.0.0.1:8088"
with httpx.Client(auth=("admin","admin123"),timeout=25)as c:
 rows=c.get(base+"/api/warehouse-tasks",params={"queue_group":"DEFER_WAITING","limit":150});rows.raise_for_status();tasks=rows.json()
 assert all(t["task_type"]=="PUTAWAY"and t["task_source"]=="MANUAL"and t["source_doc_type"]in("ST_DEFER","ST_DEFER_CASE")for t in tasks)
 assert {1110,ctx["task"]}.issubset({t["task_id"]for t in tasks}),tasks
 exact=c.get(base+"/api/warehouse-tasks",params={"source_doc_type":"ST_DEFER","limit":150});exact.raise_for_status();assert all(t["source_doc_type"]=="ST_DEFER"for t in exact.json())
 replay=c.post(base+f'/api/warehouse-tasks/{ctx["task"]}/complete',json=ctx["move_request"]);replay.raise_for_status()
 assert replay.json().get("result")==ctx["result"],replay.text
 record={"family_count":len(tasks),"case_tasks":[t for t in tasks if t["source_doc_type"]=="ST_DEFER_CASE"],"exact_legacy_filter_preserved":True,"replay_http":replay.json()}
 Path("tmp/waiting971.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
 print(json.dumps(record,ensure_ascii=True))
