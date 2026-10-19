"""Maximum200line external plan preview: compare owner query count and native timings, no stock writes."""
from pathlib import Path
from datetime import datetime,timezone
from uuid import uuid4
import os,sys,json,time,subprocess,importlib.util,statistics
sys.path[:0]=['.','tests/tradecase','api/wms_api_server']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
from app.modules.integrations.infrastructure import trade_capacity as current
P=Path('runtime/test-evidence/tradecase/2026-10-19/T08/capacity-200.json');assert not P.exists(),'Factory already recorded; do not recreate'
w=224274301;tag='TC8B'+uuid4().hex[:8];now=datetime.now(timezone.utc).isoformat();out={'warehouse_id':w,'tag':tag,'physical_writes':0}
def doc(kind,id):return expect(200,http('GET',f'/api/tradecase/warehouses/{w}/documents/{kind}/{id}'))['payload']
def send(kind,id,value):return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id=id+'.EVENT',source_id='TC03.SAP',warehouse_id=w,document_id=id,version=1,occurred_at=now,payload={**value,"entity_type":kind})))
try:
 with oracle_connection()as c:q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 trip=doc('TRIP','TC8.R1');source=doc('ORDER',trip['orders'][0]['order_id']);line=source['lines'][0];source['lines']=[dict(line,line_id=str(i+1),quantity='3',uom='BOX')for i in range(200)]
 orderid=tag+'.ORDER';tripid=tag+'.TRIP';send('ORDER',orderid,source);trip['orders']=[dict(order_id=orderid,line_id=str(i+1),quantity='3')for i in range(200)];send('TRIP',tripid,trip);out.update(order_id=orderid,trip_id=tripid)
 text=subprocess.check_output(['git','show','fdf72479:api/wms_api_server/app/modules/integrations/infrastructure/trade_capacity.py'],text=True,encoding='utf-8');oldfile=P.parent/'capacity-before-query.py';oldfile.write_text(text,encoding='utf-8')
 spec=importlib.util.spec_from_file_location('app.modules.integrations.infrastructure.trade_capacity_benchmark_before',oldfile);previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
 class Counted:
  def __init__(self,c):self.c=c;self.calls=0;self.owner=0
  def execute(self,sql,**binds):self.calls+=1;self.owner+=int('owner_allowed'in sql);return self.c.execute(sql,**binds)
  def __iter__(self):return iter(self.c)
  def fetchone(self):return self.c.fetchone()
 measurements={};results={}
 # Same session/cache order alternates; only SELECT statements inside both candidates.
 with oracle_connection()as c:
  q=c.cursor()
  for i in range(4):
   for label,module in ([('before',previous),('after',current)]if i%2==0 else[('after',current),('before',previous)]):
    cursor=Counted(q);start=time.perf_counter();items,versions,boxes=module._planned(cursor,w,trip,'admin');elapsed=round((time.perf_counter()-start)*1000,3);measurements.setdefault(label,[]).append(dict(ms=elapsed,sql_calls=cursor.calls,owner_calls=cursor.owner));results[label]=(items,versions,boxes)
  c.rollback()
 assert results['before']==results['after'];assert all(x['owner_calls']==200 for x in measurements['before'])and all(x['owner_calls']==1 for x in measurements['after'])
 preview=expect(200,http('GET',f'/api/tradecase/warehouses/{w}/trips/{tripid}/capacity?sku_id=A&requested_boxes=60'));assert preview['planned_volume_m3']=='60'and preview['fitting_boxes']==40
 # The201st line is rejected before native intake.
 extra=dict(source,lines=source['lines']+[dict(line,line_id='201',quantity='3',uom='BOX')]);expect(422,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id=tag+'.BOUND',source_id='TC03.SAP',warehouse_id=w,document_id=tag+'.BOUND',version=1,occurred_at=now,payload={**extra,'entity_type':'ORDER'})))
 out.update(status='PASS',measurements=measurements,preview=preview,equal_plan_results=True,limit201_rejected=True,limitations='One SKU and owner pair, 200lines oneorder, metadata fixtures only; not mixed SKU/owner or physical shipment/load acceptance')
 print(json.dumps(dict(status=out['status'],measurements=measurements,api_ms=CALLS[-2]['elapsed_ms'],fitting_boxes=preview['fitting_boxes'])))
except Exception as e:out.update(status='FAIL',error=str(e));raise
finally:out['http']=CALLS;P.write_text(json.dumps(out,indent=2,default=str))
