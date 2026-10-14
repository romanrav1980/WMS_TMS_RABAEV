from pathlib import Path
import json,httpx
with httpx.Client(auth=('admin','admin123'),timeout=30)as c:
 url='http://127.0.0.1:8088/api/warehouse-tasks'
 r=c.get(url,params={'queue_group':'SHIPPING','limit':100});assert r.status_code==200,r.text
 rows=r.json();assert rows and all(x['task_type']=='PICKING_MOVE' or(x['task_type']=='REPLENISHMENT'and x['source_doc_type']=='SHIPMENT')for x in rows)
 for params in ({'queue_group':'INVENTED'},{'limit':501},{'limit':0}):
  r=c.get(url,params=params);assert r.status_code==422,r.text
 Path('tmp/context814.json').write_text(json.dumps({'rows':rows}),encoding='utf-8');print('814 PASS original shipping task group before bounded list; invalid group/limits422;',len(rows),'rows')
