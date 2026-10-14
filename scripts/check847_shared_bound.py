import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.modules.inventory.infrastructure.shared_arrival_reconciliation import reconcile_warehouse_arrivals
from fastapi import HTTPException
import json
class Gateway:
 def __init__(self,rows,allowed=1):self.rows=rows;self.allowed=allowed;self.calls=[]
 def fetch_all(self,sql,binds):
  return [{"allowed":self.allowed}]if "count(*)ALLOWED" in sql else self.rows
 def execute(self,sql,binds):
  self.calls.append((sql,binds));return 0 if "SOURCE_RESERVATION_ID=null" in sql else len(json.loads(binds["selection"]))
g=Gateway([{"pick_wave_id":10,"pick_wave_replenish_task_id":1},{"pick_wave_id":10,"pick_wave_replenish_task_id":2},{"pick_wave_id":11,"pick_wave_replenish_task_id":3}])
assert reconcile_warehouse_arrivals(g,5,"actor")==3
assert [json.loads(b[1]["selection"])for b in g.calls]==[[1,2],[1,2],[3],[3]]
for g,expected in [(Gateway([],0),403),(Gateway([{"pick_wave_id":i,"pick_wave_replenish_task_id":i}for i in range(201)]),409)]:
 try:reconcile_warehouse_arrivals(g,5,"actor");raise AssertionError("Expected bounded scope refusal")
 except HTTPException as e:assert e.status_code==expected
 assert g.calls==[]
print("847 PASS total200 row bound and current warehouse rejection before updates; selected row IDs preserved")
