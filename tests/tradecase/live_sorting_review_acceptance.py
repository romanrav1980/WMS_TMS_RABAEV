"""Repeat split from a cloned pallet under BLC-only rights; empty target and paused replay."""
from pathlib import Path
from uuid import uuid4
import json,os,secrets,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T06';old=json.loads((OUT/'sorting-84af382c.json').read_text());w=old['warehouse_id'];t=old['target'];tag='T6X'+uuid4().hex[:8];actor=tag;password=secrets.token_hex(24);target=tag+'S';base=f'/api/tradecase/warehouses/{w}';paused=False;report={}
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:w,0,0,0,0,1,0,0)',cell=target,w=w)
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target);c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:p,'TRADECASE repeat split QA','TC03QA',:w,0,1)",id=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:r,'TRADECASE repeat split QA',1,1)",r=tag)
  q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,'tradecase_stock_sort')",r=tag)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:r,:r,:r,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '6'hour,'admin','Isolated clone owner acceptance',1)",r=tag,w=str(w));c.commit()
  q.execute('select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where u.CURRENT_UID=:p order by u.PHYSICAL_UNIT_KEY fetch first 2 rows only',p=t['uid']);scans=[dict(system_code=s,profile_code='TOBACCO',code=raw.read()if hasattr(raw,'read')else raw)for s,raw in q];assert len(scans)==2
 expect(200,http('PUT',base+'/stock/cells/'+target,dict(operation_id=tag+'.policy',expected_version=0,zone_kind='SORT',reason='Verify empty system target and cloned source')))
 expect(200,http('PUT',base+'/stock/owner-grants',dict(operation_id=tag+'.grant',expected_version=0,username=actor,owner_id='BLC',can_view=True,can_operate=True,reason='Only current BLC rights, not historical SNS stock')))
 body=dict(operation_id=tag+'.split',source_pallet=t['uid'],source_cell=t['cell'],target_cell=target,scans=[scans[0]])
 result=expect(200,http('POST',base+'/stock/sort',body,actor,password));assert result['base_quantity']=='1',result
 bad=dict(body,operation_id=tag+'.occupied',scans=[scans[1]]);refusal=expect(409,http('POST',base+'/stock/sort',bad,actor,password));assert 'TARGET_NOT_EMPTY'in refusal['detail']['code'],refusal
 site=expect(200,http('GET',base+'/site'));version=site['version']
 settings=dict(source_id='TC03.SAP',active_skm='TC03.SKM',planning_source='SAP',reason='Temporary pause to verify exact previous physical outcome')
 expect(200,http('PUT',base+'/site',dict(settings,operation_id=tag+'.pause',expected_version=version,enabled=False)));paused=True
 assert expect(200,http('POST',base+'/stock/sort',body,actor,password))==result
 expect(200,http('PUT',base+'/site',dict(settings,operation_id=tag+'.resume',expected_version=version+1,enabled=True)));paused=False
 items=[];after=''
 while True:
  page=expect(200,http('GET',base+'/stock?pallet_identifier='+old['source_pallet']+'&limit=100&after='+after));items+=page['items']
  if not page['has_more']:break
  after=page['next_after']
 assert len(items)==170 and sum(u['buyout_hold']for u in items)==150 and sum(not u['buyout_hold']and not u['hard_reserved']for u in items)==20
 with oracle_connection()as c:
  q=c.cursor();q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);assert q.fetchone()==(250,0)
 report=dict(status='PASS',warehouse_id=w,source=t['uid'],target=result,source_free_units=20,source_financial_held=150,checks=['clone_from_clone_BLC_only','occupied_system_target_denied','paused_site_exact_replay','holds_visible'],stock_total=250)
except Exception as e:report=dict(status='FAIL',error=str(e));raise
finally:
 if paused:
  expect(200,http('PUT',base+'/site',dict(settings,operation_id=tag+'.recover',expected_version=version+1,enabled=True)))
 with oracle_connection()as c:
  q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:u and USER_GROUP='TC03QA'",u=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=tag);c.commit()
 report['http']=CALLS;p=OUT/('sorting-review-'+tag+'.json');p.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps(dict(status=report['status'],file=str(p),http_calls=len(CALLS))))
