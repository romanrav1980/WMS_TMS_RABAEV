import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.finance.infrastructure.cost_period_lines import load_period_lines
from app.modules.finance.domain.cost_summary import recognized_cost_summary
from app.modules.finance.contracts import LogisticsCostError
class Cursor:
 def setinputsizes(self,**kw):pass
 def execute(self,sql,binds=None,**kw):
  self.sql=sql;self.binds=binds or kw
 def fetchall(self):return [(1,"2026-10-11"),(2,"2026-10-12"),(3,"2026-10-12")]
 def fetchone(self):
  if 'RRL_BOX_ASSEMBLY_READ'in self.sql:return ([dict(state='READY',business_date=d)for d in ['2026-10-11','2026-10-12','2026-10-12']],)
  if "for update"in self.sql:return ("R1",)
  return ("R1",1,"2.5")if self.binds["day"]=="2026-10-11"else("R1",2,"3")
policy=dict(period_mode="CASE_ASSEMBLY",timezone_region="UTC",version=1)
tree={"nodes":[dict(uid="CASE:"+str(i),kind="CASE",case_task_id=i)for i in [1,2,3]]}
lines=load_period_lines(Cursor(),tree,3,"LOAD","2026-10-13",1,"GEL",policy)
assert [(r["rate_date"],r["quantity"],r["version"],r["amount"])for r in lines]==[("2026-10-11",1,1,"2.50"),("2026-10-12",2,2,"6.00")],lines
rows=[dict(operation_id="C1",ware_id=1,tt_id=1,currency="GEL",rate_value=r["rate"],version_no=r["version"],period_time_zone=r["period_timezone"],**r)for r in lines]
assert recognized_cost_summary(rows)["currency_totals"]==[dict(currency="GEL",original_amount="8.50")]
try:recognized_cost_summary(rows+[rows[0]])
except ValueError:pass
else:raise AssertionError("Duplicate dated row accepted")
print("PASS513 one load/two actual clock dates/three CASE ->1x2.50 +2x3.00 =8.50; separate historical versions; same dated source duplicated denied. Projection only, not physical multi-date Oracle acceptance.")
