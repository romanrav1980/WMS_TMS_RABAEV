"""IN_TRANSIT buyout after actual native LOAD/DEPART; synthetic SKM results, no second shipment."""
from datetime import datetime,timezone
from pathlib import Path
import json,os,sys
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T05/in-transit-1156.json');s=json.loads(P.read_text())if P.exists()else dict(warehouse_id=215590763,history=[])
base='/api/tradecase/warehouses/215590763';load='T7.LOAD.1156'
def save():P.write_text(json.dumps(s,indent=2,default=str))
def same(new,old):assert new['replayed']and {k:v for k,v in new.items()if k!='replayed'}=={k:v for k,v in old.items()if k!='replayed'}
def snapshot():
 with oracle_connection()as c:
  q=c.cursor();q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=215590763');stock=list(q.fetchone())
  q.execute('select STATUS,DEPARTURE_OPERATION_ID,DEPARTED_AT,CONTENT_VERSION from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o',o=load);return dict(stock=stock,load=[str(x) if hasattr(x,'isoformat') else x for x in q.fetchone()])
def run():
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 cargo=expect(200,http('GET',base+'/stock/transit?load_operation_id='+load+'&limit=100'));keys=sorted(x['physical_unit_key']for x in cargo['items']);assert len(keys)==40 and not cargo['has_more'];assert all(x['cell']is None and x['location_kind']=='VEHICLE_TRANSIT'for x in cargo['items'])
 stamp=datetime.now(timezone.utc).isoformat()
 if 'basis'not in s:
  s['basis_body']=dict(schema_version=1,event_id='TC7.TRANSIT.FIN.BASIS',source_id='TC03.SAP',warehouse_id=215590763,document_id='TC7.FIN.TRANSIT',version=1,occurred_at=stamp,payload=dict(entity_type='ORDER',recipient_id='C.TRANSIT',order_kind='BUYOUT',buyout_mode='IN_TRANSIT',planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='40',uom='EA',min_osg_days=0)]));save()
  s['basis']=expect(200,http('POST','/api/tradecase/messages',s['basis_body']));save()
 if 'request'not in s:
  s['before']=snapshot();s['request_body']=dict(operation_id='TC7.TRANSIT.request.1156',buyout_id='TC7.TRANSIT.1156',basis_order_id='TC7.FIN.TRANSIT',basis_line_id='1',expected_basis_version=1,unit_keys=keys,demand_order_id='TRANSIT',demand_line_id='1',load_operation_id=load);save()
  bad=dict(s['request_body'],operation_id='TC7.TRANSIT.wrongload.1156',buyout_id='TC7.TRANSIT.wrongload.1156',load_operation_id='T7.LOAD.1155');expect(409,http('POST',base+'/buyouts',bad))
  s['request']=expect(200,http('POST',base+'/buyouts',s['request_body']));assert s['request']['pending_units']==40;save()
 same(expect(200,http('POST',base+'/buyouts',s['request_body'])),s['request'])
 for name,n,version in [('partial',32,1),('final',8,2)]:
  if name not in s:
   use=keys[:32]if name=='partial'else keys[32:]
   body=dict(operation_id='TC7.TRANSIT.result.'+name,buyout_id='TC7.TRANSIT.1156',expected_version=version,skm_id='TC03.SKM',external_event_id='TC7.TRANSIT.result.'+name,external_document_id='TC7.TRANSIT.doc.1156',occurred_at=stamp,items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in use]);s[name+'_body']=body;save()
   s[name]=expect(200,http('POST',base+'/buyouts/results',body));save()
   after=expect(200,http('GET',base+'/stock/transit?load_operation_id='+load+'&limit=100'));owners={owner:sum(1 for x in after['items']if x['owner_id']==owner)for owner in ['SNS','BLC']};assert owners==({'SNS':8,'BLC':32}if name=='partial'else {'SNS':0,'BLC':40}),owners;s[name+'_owners']=owners;save()
 same(expect(200,http('POST',base+'/buyouts/results',s['partial_body'])),s['partial'])
 s['after']=snapshot();assert s['after']==s['before'];assert s['after']['stock']==[110,0];assert s['after']['load'][0]=='DEPARTED'
 card=expect(200,http('GET',base+'/buyouts/TC7.TRANSIT.1156'));assert card['confirmed_units']==40 and card['pending_units']==0;s['card']=card;s['status']='PASS';s['provider']='LOCAL_SYNTHETIC_ONLY';s.pop('error',None);print(json.dumps(dict(status=s['status'],owners=s['final_owners'],warehouse=s['after']['stock'],shipment_unchanged=True)))
if __name__=='__main__':
 try:run()
 except Exception as e:s['status']='FAIL';s['error']=str(e);raise
 finally:s['history']+=CALLS;save()

