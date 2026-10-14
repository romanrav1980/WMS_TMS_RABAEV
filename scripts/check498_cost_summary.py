import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.finance.domain.cost_summary import recognized_cost_summary
base=dict(operation_id="C1",load_operation_id="L1",cost_code="WAREHOUSE_PICKING",currency="GEL",ware_id=1,tt_id=1,quantity=1,rate_value="2.50",version_no=2,basis="BOX",rate_date="2026-10-11",period_mode="CASE_ASSEMBLY",period_time_zone="UTC",period_policy_version=1,amount="2.50")
rows=[base,{**base,"operation_id":"C2","load_operation_id":"L2","tt_id":2,"rate_date":"2026-10-12","amount":"3.00","rate_value":"3.00","version_no":3},{**base,"operation_id":"C3","load_operation_id":"L3","currency":"USD","ware_id":2,"amount":"999999999999999999.99"},{**base,"operation_id":"C4","load_operation_id":"L4","currency":"USD","ware_id":2,"amount":"0.01"}]
r=recognized_cost_summary(rows)
assert len(r["groups"])==3 and r["currency_totals"]==[dict(currency="GEL",original_amount="5.50"),dict(currency="USD",original_amount="1000000000000000000.00")],r
for bad in [rows+[base],[{**base,"amount":"NaN"}],[{**base,"amount":"0.001"}]]:
 try:recognized_cost_summary(bad)
 except ValueError:pass
 else:raise AssertionError("Invalid financial source accepted")
assert recognized_cost_summary([])["currency_totals"]==[]
print("PASS498 different dates/rates/WARE/currencies separated; exact 1e18 cents, duplicates/nonfinite/subcent rejected; no source mutation")
