"""AFTER_PICK buyout from real closed CASE content in WAIT, synthetic SKM outcomes."""
from datetime import datetime,timezone
from pathlib import Path
import json,os,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T05';PATH=OUT/'after-pick-1155.json'
s=json.loads(PATH.read_text())if PATH.exists()else dict(warehouse_id=215590763,case_id=1155,history=[])
def save():PATH.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def run():
 w=s['warehouse_id'];base=f'/api/tradecase/warehouses/{w}/buyouts';stamp='2026-10-19T12:00:00+03:00'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute('select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_CASE_CARRIER_LOT h on h.LOT_UID=u.CURRENT_UID where h.CASE_PICK_TASK_ID=:t order by u.PHYSICAL_UNIT_KEY',t=s['case_id']);keys=[r[0]for r in q];assert len(keys)==100
  q.execute('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.REMAIN',w=w);before=[list(r)for r in q]
 if 'basis'not in s:
  envelope=dict(schema_version=1,event_id='TC6.AFTER.FIN.BASIS',source_id='TC03.SAP',warehouse_id=w,document_id='TC6.FIN.AFTER',version=1,occurred_at=stamp,payload=dict(entity_type='ORDER',recipient_id='C.AFTER',order_kind='BUYOUT',buyout_mode='AFTER_PICK',planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='100',uom='EA',min_osg_days=0)]))
  s['basis']=expect(200,http('POST','/api/tradecase/messages',envelope));save()
 if 'request'not in s:
  s['request_body']=dict(operation_id='TC6.AFTER.request.1155',buyout_id='TC6.AFTER.1155',basis_order_id='TC6.FIN.AFTER',basis_line_id='1',expected_basis_version=1,unit_keys=keys,demand_order_id='AFTER',demand_line_id='1');save()
  with oracle_connection()as c:
   q=c.cursor();q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID='690000000312355716'and rownum=1");unpicked=q.fetchone()[0]
  bad=dict(s['request_body'],operation_id='TC6.AFTER.unpicked.1155',buyout_id='TC6.AFTER.unpicked.1155',unit_keys=[unpicked]);expect(409,http('POST',base,bad))
  s['request']=expect(200,http('POST',base,s['request_body']));assert s['request']['pending_units']==100;s['snapshot_before_buyout']=before;save()
 replay=expect(200,http('POST',base,s['request_body']));assert replay['replayed']and {k:v for k,v in replay.items()if k!='replayed'}=={k:v for k,v in s['request'].items()if k!='replayed'}
 if 'partial'not in s:
  s['partial_body']=dict(operation_id='TC6.AFTER.result.80',buyout_id='TC6.AFTER.1155',expected_version=1,skm_id='TC03.SKM',external_event_id='TC6.AFTER.result.80',external_document_id='TC6.AFTER.doc.1155',occurred_at=stamp,items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in keys[:80]]);save()
  s['partial']=expect(200,http('POST',base+'/results',s['partial_body']));assert s['partial']['confirmed_units']==80 and s['partial']['pending_units']==20 and s['partial']['requires_sorting'];save()
 if 'final'not in s:
  s['final_body']=dict(operation_id='TC6.AFTER.result.20',buyout_id='TC6.AFTER.1155',expected_version=2,skm_id='TC03.SKM',external_event_id='TC6.AFTER.result.20',external_document_id='TC6.AFTER.doc.1155',occurred_at=stamp,items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in keys[80:]]);save()
  s['final']=expect(200,http('POST',base+'/results',s['final_body']));assert s['final']['confirmed_units']==100 and s['final']['pending_units']==0 and not s['final']['requires_sorting'];save()
 replay=expect(200,http('POST',base+'/results',s['partial_body']));assert replay['replayed']and {k:v for k,v in replay.items()if k!='replayed'}=={k:v for k,v in s['partial'].items()if k!='replayed'}
 card=expect(200,http('GET',base+'/TC6.AFTER.1155'));assert card['confirmed_units']==100 and not card['requires_sorting'];s['current_card']=card
 with oracle_connection()as c:
  q=c.cursor();q.execute('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.REMAIN',w=w);after=[list(r)for r in q];assert after==s['snapshot_before_buyout'];s['snapshot_after_buyout']=after
  q.execute('select distinct a.OWNER_ID from RRL_WMS_RECEIPT_UNIT u join RRL_CASE_CARRIER_LOT h on h.LOT_UID=u.CURRENT_UID join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where h.CASE_PICK_TASK_ID=:t',t=s['case_id']);assert q.fetchall()==[('BLC',)]
 s['status']='PASS';s['provider']='LOCAL_SYNTHETIC_ONLY';s['box_aggregation']='NOT_PROVEN';s.pop('error',None)
if __name__=='__main__':
 try:run()
 except Exception as e:s['status']='FAIL';s['error']=str(e);raise
 finally:s['history']+=CALLS;save();print(json.dumps(dict(status=s.get('status'),file=str(PATH),http_calls=len(CALLS))))
