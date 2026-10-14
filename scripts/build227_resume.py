from pathlib import Path
import json
s=Path("scripts/ni061_marked_placement_case.py").read_text(encoding="utf-8")
prefix=s[:s.index(' metadata=')]
tail=s[s.index(' q.execute("select STATUS,SYNC_STATUS'):].replace('select STATUS,SYNC_STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t',"select t.STATUS,s.SYNC_STATUS from RRL_WAREHOUSE_TASK t join RRL_WAREHOUSE_TASK_SYNC s on s.TASK_ID=t.TASK_ID where t.TASK_ID=:t")
middle=' q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=\'IW227.COMPLETE:13508027ed0\'");saved=read_oracle_json(q.fetchone()[0]);winner=dict(saved["metadata"],operation_id=saved["operation_id"]);api(client,"POST",f"/api/warehouse-tasks/{task}/complete",winner)\n'
print(json.dumps({"scripts/resume227_case.py":prefix+middle+tail},ensure_ascii=True))
