"""A new financial basis reverses one returned unit BLC to SNS; native quantity stays unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,json
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T05/reverse-sale.json');s=json.loads(P.read_text())if P.exists()else dict(warehouse_id=211559882,stamp=datetime.now(timezone.utc).isoformat(),target_cell='T11.SNS.RETURN',history=[],checks=[])
def save():P.write_text(json.dumps(s,indent=2,default=str))
def source(kind,id,payload):return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id='T11.REVERSE.'+kind,source_id='TC03.SAP',warehouse_id=s['warehouse_id'],document_id=id,version=1,occurred_at=s['stamp'],payload=dict(entity_type=kind,**payload))))
try:
 w=s['warehouse_id'];base=f'/api/tradecase/warehouses/{w}'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  if 'physical_unit_key'not in s:
   q.execute("select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,a.OWNER_ID,u.HARD_RESERVATION_ID from RRL_TRADE_CASE_RETURN_UNIT h join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=h.PHYSICAL_UNIT_KEY join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where h.CASE_PICK_TASK_ID=1157");row=q.fetchone();assert row[3:] == ('BLC',None);s.update(physical_unit_key=row[0],source_uid=row[1],source_cell=row[2]);save()
  if 'cell_created'not in s:
   q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,1,0,0)',c=s['target_cell'],w=w)
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=s['target_cell']);c.commit();s['cell_created']=True;save()
   finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  q.execute("select rc.SYSTEM_CODE,f.PROFILE_CODE,rc.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE rc on rc.UID_PALLET=u.UID_PALLET and rc.UNIT_ID=u.UNIT_ID join RRL_PALLETS p on p.UID_PALLET=u.CURRENT_UID join RRL_SKU_RECEIPT_PROFILE f on f.ARTICUL=p.ARTICUL and f.SYSTEM_CODE=rc.SYSTEM_CODE where u.PHYSICAL_UNIT_KEY=:k",k=s['physical_unit_key']);scans=[dict(system_code=system,profile_code=profile,code=raw.read()if hasattr(raw,'read')else raw)for system,profile,raw in q];assert len(scans)==1
 if 'cell_policy'not in s:s['cell_policy']=expect(200,http('PUT',base+'/stock/cells/'+s['target_cell'],dict(operation_id='T11.REVERSE.CELL',expected_version=0,zone_kind='SORT',owner_id=None,reason='Owned reverse sale staging, not mixed picking stock')));save()
 if 'sort'not in s:
  s['sort_body']=dict(operation_id='T11.REVERSE.SORT',source_pallet=s['source_uid'],source_cell=s['source_cell'],target_cell=s['target_cell'],scans=scans);save();s['sort']=expect(200,http('POST',base+'/stock/sort',s['sort_body']));save()
 assert expect(200,http('POST',base+'/stock/sort',s['sort_body']))==s['sort'];s['checks']+=['returned_unit_staged_by_scan_with_replay']
 if 'recipient'not in s:s['recipient']=source('RECIPIENT','C.REVERSE.SNS',dict(title='QA reverse sale recipient SNS',target_owner_id='SNS',permitted_source_owners=['BLC'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0));save()
 if 'basis'not in s:s['basis']=source('ORDER','FIN.REVERSE.SNS',dict(recipient_id='C.REVERSE.SNS',order_kind='BUYOUT',buyout_mode='BEFORE_PICK',planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='BLC',target_owner_id='SNS',mrc='200',quantity='1',uom='EA',min_osg_days=0)]));save()
 if 'outbound_denied'not in s:s['outbound_denied']=expect(409,http('POST',base+'/buyouts',dict(operation_id='T11.REVERSE.WRONG.BASIS',buyout_id='T11.REVERSE.WRONG',basis_order_id='CLONE10',basis_line_id='1',expected_basis_version=1,unit_keys=[s['physical_unit_key']])));s['checks']+=['shipment_order_cannot_replace_new_financial_basis'];save()
 if 'storage'not in s:
  cell='T11.REV.STORE'
  with oracle_connection()as c:
   q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,0,0,0)',c=cell,w=w)
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell);c.commit()
   finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  expect(200,http('PUT',base+'/stock/cells/'+cell,dict(operation_id='T11.REVERSE.STORAGE.CELL',expected_version=0,zone_kind='STORAGE',owner_id=None,reason='Owned return putaway before reverse financial instruction')))
  s['putaway_body']=dict(operation_id='T11.REVERSE.PUTAWAY',source_pallet=s['sort']['uid'],source_cell=s['target_cell'],target_cell=cell,scans=scans);save()
  s['storage']=expect(200,http('POST',base+'/stock/sort',s['putaway_body']));s['financial_cell']=cell;s['checks']+=['reverse_financial_instruction_requires_prepared_storage'];save()
 if 'requested'not in s:s['request_body']=dict(operation_id='T11.REVERSE.REQUEST',buyout_id='T11.REVERSE.SALE1',basis_order_id='FIN.REVERSE.SNS',basis_line_id='1',expected_basis_version=1,unit_keys=[s['physical_unit_key']]);save();s['requested']=expect(200,http('POST',base+'/buyouts',s['request_body']));save()
 if 'result'not in s:
  card=expect(200,http('GET',base+'/buyouts/T11.REVERSE.SALE1'));s['result_body']=dict(operation_id='T11.REVERSE.RESULT',buyout_id='T11.REVERSE.SALE1',expected_version=card['version'],skm_id='TC03.SKM',external_event_id='TEST.REVERSE.RESULT1',external_document_id='TEST.REVERSE.DOC1',occurred_at=s['stamp'],items=[dict(physical_unit_key=s['physical_unit_key'],outcome='CONFIRMED')]);save();s['result']=expect(200,http('POST',base+'/buyouts/results',s['result_body']));save()
 assert expect(200,http('POST',base+'/buyouts/results',s['result_body']))==dict(s['result'],replayed=True);s['checks']+=['reverse_owner_result_and_exact_replay']
 with oracle_connection()as c:
  q=c.cursor();q.execute('select a.OWNER_ID,u.CURRENT_CELL,u.STOCK_STATUS from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where a.PHYSICAL_UNIT_KEY=:k',k=s['physical_unit_key']);s['unit_after']=list(q.fetchone());assert s['unit_after']==['SNS',s['financial_cell'],'AVAILABLE']
  q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);assert list(q.fetchone())==[250,0]
  q.execute("select a.OWNER_ID,count(*)from RRL_TRADE_STOCK_ATTR a where a.CAPTURE_WARE_ID=:w group by a.OWNER_ID order by a.OWNER_ID",w=w);s['owners_after']=[list(r)for r in q];assert s['owners_after']==[['BLC',79],['SNS',171]]
  q.execute("select count(*)from RRL_TRADE_BUYOUT_UNIT where OUTCOME='PENDING'and PHYSICAL_UNIT_KEY in(select PHYSICAL_UNIT_KEY from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w)",w=w);assert q.fetchone()[0]==150
 s.update(status='PASS',provider='LOCAL_SYNTHETIC_ONLY',stock=[250,0]);s.pop('error',None);print(json.dumps(dict(status=s['status'],checks=s['checks'],owner=s['unit_after'][0],stock=s['stock'])))
except Exception as e:s.update(status='FAIL',error=str(e));raise
finally:s['history']+=CALLS;save()
