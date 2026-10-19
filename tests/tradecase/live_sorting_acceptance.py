"""Live physical split of the confirmed subset; preserves pending financial holds."""
from copy import deepcopy
import json,os,secrets,sys
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T06'

def run():
 f=json.loads((OUT.parent/'T05/buyout-race-17cd4aae.json').read_text())['fixture']
 w=f['warehouse_id'];tag='T6'+uuid4().hex[:10];target=tag+'B';base=f'/api/tradecase/warehouses/{w}/stock';actor=tag;password=secrets.token_hex(24)
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:w,0,0,0,0,0,0,0)',cell=target,w=w)
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target);c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:p,'TRADECASE sorting QA','TC03QA',:w,0,1)",id=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:r,'TRADECASE sorting QA',1,1)",r=tag)
  for perm in ['tradecase_stock_sort','tradecase_view']:q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,:p)',r=tag,p=perm)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:r,:r,:r,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '6'hour,'admin','Isolated sorting acceptance',1)",r=tag,w=str(w));c.commit()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_CODE c join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID where u.CURRENT_UID=:p',p=f['pallet'])
  scan_map={key:dict(system_code=system,profile_code='TOBACCO',code=raw.read()if hasattr(raw,'read')else raw)for key,system,raw in q}
 def scan(key):return scan_map[key]
 try:
  expect(200,http('PUT',base+'/cells/'+target,dict(operation_id=tag+'.policy',expected_version=0,zone_kind='SORT',reason='Isolated physical split acceptance')))
  for owner in ['SNS','BLC']:expect(200,http('PUT',base+'/owner-grants',dict(operation_id=tag+'.grant.'+owner,expected_version=0,username=actor,owner_id=owner,can_view=True,can_operate=True,reason='Isolated physical split acceptance')))
  view=expect(200,http('GET',base+'?pallet_identifier='+f['pallet']+'&limit=100'));assert len(view['items'])==100 and view['has_more']
  body=dict(operation_id=tag+'.sort',source_pallet=f['pallet'],source_cell=f['current_cell'],target_cell=target,scans=[scan(k)for k in f['confirmed_unit_keys']])
  bad=deepcopy(body);bad['operation_id']=tag+'.pending';bad['scans']=[scan(f['pending_unit_keys'][0])];expect(409,http('POST',base+'/sort',bad,actor,password))
  with oracle_connection()as c:
   q=c.cursor();q.execute("select a.PHYSICAL_UNIT_KEY from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where u.CURRENT_UID=:p and a.OWNER_ID='SNS'and not exists(select 1 from RRL_TRADE_BUYOUT_UNIT b where b.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY and b.HOLD_ACTIVE=1)and rownum=1",p=f['pallet']);unheld=q.fetchone()[0]
  bad=deepcopy(body);bad['operation_id']=tag+'.mixed';bad['scans']=[body['scans'][0],scan(unheld)];expect(409,http('POST',base+'/sort',bad,actor,password))
  bad=deepcopy(body);bad['operation_id']=tag+'.duplicate';bad['scans']=[body['scans'][0]]*2;expect(422,http('POST',base+'/sort',bad,actor,password))
  result=expect(200,http('POST',base+'/sort',body,actor,password));assert result['base_quantity']=='80'and result['uid']!=f['pallet'],result
  assert expect(200,http('POST',base+'/sort',body,actor,password))==result
  bad=deepcopy(body);bad['scans']=bad['scans'][:-1];expect(409,http('POST',base+'/sort',bad,actor,password))
  expect(200,http('PUT',base+'/owner-grants',dict(operation_id=tag+'.revoke',expected_version=1,username=actor,owner_id='BLC',can_view=True,can_operate=False,reason='Verify current rights on cached physical result')))
  expect(403,http('POST',base+'/sort',body,actor,password))
  card=expect(200,http('GET',f'/api/tradecase/warehouses/{w}/buyouts/'+f['financial_partials'][0]));assert card['requires_sorting']is False,card
  with oracle_connection()as c:
   q=c.cursor();q.execute('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.REMAIN',w=w);stock=[list(row)for row in q];assert [r[2]for r in stock]==[80,170],stock
   q.execute('select count(*)from RRL_TRADE_BUYOUT_UNIT b join RRL_TRADE_BUYOUT p on p.BUYOUT_ID=b.BUYOUT_ID where p.WARE_ID=:w and b.HOLD_ACTIVE=1',w=w);assert q.fetchone()[0]==150
   q.execute('select sum(u.BASE_QTY),count(distinct a.OWNER_ID)from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=:p',p=result['uid']);assert q.fetchone()==(80,1)
  return dict(status='PASS',warehouse_id=w,source_pallet=f['pallet'],target=result,stock=stock,pending_buyout_holds=150,provider='LOCAL_SYNTHETIC_ONLY',actor=actor)
 finally:
  with oracle_connection()as c:
   q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:u and USER_GROUP='TC03QA'",u=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=tag);c.commit()

if __name__=='__main__':
 report={}
 try:report=run()
 except Exception as exc:report=dict(status='FAIL',error=str(exc));raise
 finally:
  report['http']=CALLS;p=OUT/('sorting-'+uuid4().hex[:8]+'.json');p.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps(dict(status=report['status'],file=str(p),http_calls=len(CALLS))))
