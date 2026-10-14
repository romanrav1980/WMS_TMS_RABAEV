"""Existing aware departures only: projection does not create stock."""
import httpx
from decimal import Decimal
base='http://127.0.0.1:8088/api/transport/warehouse-forecast'
client=httpx.Client(auth=('admin','admin123'),timeout=40)
def request(path,body=None):
 r=client.post(base+path,json=body)
 assert r.status_code==200,(r.status_code,r.text[:3000])
 return r.json()
query={'history_days':1,'horizon_days':7,'minimum_active_days':1,'include_current_day':True,'scope':'CASE_DISPATCH'}
before=request('/warehouses/11027346/view',query)
print('Initial source gaps',before['projection_gaps_at_least'],flush=True)
result=request('/warehouses/11027346/project?limit=100')
assert not result['errors'],result
first=request('/warehouses/11027346/view',query)
assert first['projection_gaps_at_least']==0 and first['status']=='ADVISORY',first
assert sum(Decimal(r['observed_quantity'])for r in first['series'])==20,first
assert sum(r['top_places']for r in first['observed_days'])==2,first
assert first['includes_partial_current_day'] and not first['stock_changed']and not first['plan_applied']
for row in result['projected']:
 print('Projection',row,flush=True)
again=request('/warehouses/11027346/project?limit=100')
assert again['sources_seen']==0,again
second=request('/warehouses/11027346/view',query)
assert first['source_data_signature']==second['source_data_signature']
blocked=request('/warehouses/11027346/view',{**query,'minimum_active_days':3})
assert all(row['estimated_quantity']is None for row in blocked['series']),blocked
closed=request('/warehouses/11027346/view',{**query,'include_current_day':False})
assert closed['status']=='NO_SERIES',closed
print('PASS133 actual CASE8+12=20/top2, immutable replay/batch0, no stock/no plan, insufficient active history blocked and closedUTCday empty',flush=True)
other=request('/warehouses/9104/project?limit=100');assert not other['errors'],other
full=request('/warehouses/9104/view',{**query,'scope':'FULLPAL_DISPATCH'})
assert sum(Decimal(r['observed_quantity'])for r in full['series'])==4,full
assert request('/warehouses/9104/view',query)['status']=='NO_SERIES'
print('PASS133 existing intermediate FULLPAL3+return1=4 kept distinct from CASE demand; physical work not final customer sales',flush=True)
