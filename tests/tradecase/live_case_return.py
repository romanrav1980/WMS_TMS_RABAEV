"""Return one pre-fix QA CASE via the native writer; preserve owner and exact replay authority."""
from pathlib import Path
from uuid import uuid4
import sys,os,json,secrets
sys.path[:0]=['.','tests/tradecase','api/wms_api_server']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
from app.modules.inventory.contracts_stock import StockCommand
import oracledb
P=Path('runtime/test-evidence/tradecase/2026-10-19/T11/case-return.json');s=json.loads(P.read_text())if P.exists()else dict(warehouse_id=211559882,case_id=1157,history=[],checks=[])

def save():P.write_text(json.dumps(s,indent=2,default=str))
def totals(q):
 q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse_id']);return list(q.fetchone())
def own(method,path,body=None):return http(method,path,body,s['actor'],password)
try:
 w=s['warehouse_id'];cid=s['case_id'];path=f'/api/case-pick/tasks/{cid}/return-carrier'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  if 'actor'not in s:
   actor='T11R'+uuid4().hex[:8];password=secrets.token_hex(24)
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'QA bound CASE return','TC03QA',:w,0,1)",a=actor,p=password,w=w)
   q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'QA bound CASE return',1,1)",a=actor);q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'case_pick_manage')",a=actor)
   q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','BLC-only CASE return QA',1)",a=actor,w=str(w));c.commit();s['actor']=actor;save()
  q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=s['actor']);row=q.fetchone();assert row,'Do not reactivate retired QA actor';password=row[0]
  if 'body'not in s:
   q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=cid);carrier,version=q.fetchone()
   q.execute('select lot.LOT_UID,l.CELL_CODE from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID where lot.CASE_PICK_TASK_ID=:t',t=cid);targets=dict(q.fetchall());assert len(targets)==1
   s['body']=dict(operation_id='T11.RETURN.CLONE1',scan_container=carrier,expected_content_version=version,destinations=targets);s['before']=totals(q);assert s['before']==[250,11];save()
 def grant(key,operate):
  with oracle_connection()as c:
   q=c.cursor();q.execute("select nvl(max(VERSION_NO),0)from RRL_TRADE_OWNER_GRANT where WARE_ID=:w and USERNAME=:a and OWNER_ID='BLC'",w=w,a=s['actor']);version=q.fetchone()[0]
  return expect(200,http('PUT',f'/api/tradecase/warehouses/{w}/stock/owner-grants',dict(operation_id='T11.OWNER.'+key,expected_version=version,username=s['actor'],owner_id='BLC',can_view=True,can_operate=operate,reason='QA current BLC rights before and after native return')))
 if 'denied_owner'not in s:
  grant('READ',False);s['denied_owner']=expect(403,own('POST',path,s['body']));s['checks']+=['manager_without_owner_operate_denied'];save()
 if 'owner_enabled'not in s:grant('OPERATE',True);s['owner_enabled']=True;save()
 if 'wrong_cell'not in s:
  wrong=dict(s['body'],operation_id='T11.RETURN.WRONG_CELL',destinations={uid:'T6C.BLC.WAIT'for uid in s['body']['destinations']});s['wrong_cell']=expect(409,own('POST',path,wrong));s['checks']+=['wrong_original_cell_denied'];save()
 if 'no_manage'not in s:
  picker=json.loads(Path('runtime/test-evidence/tradecase/2026-10-19/T06/clone-case.json').read_text())['actor']
  with oracle_connection()as c:q=c.cursor();q.execute('select PASS from RUSERS where ID=:a',a=picker);pp=q.fetchone()[0]
  s['no_manage']=expect(403,http('POST',path,dict(s['body'],operation_id='T11.RETURN.PICKER'),picker,pp));s['checks']+=['picker_without_manage_denied'];save()
 if 'rollback'not in s:
  body=dict(s['body']);op=body.pop('operation_id')+'.ROLLBACK';command=StockCommand(op,'CASE_CARRIER_RETURN',s['actor'],(),{'case_task_id':cid},metadata=body)
  with oracle_connection()as c:
   q=c.cursor();wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,command.canonical_json());replay=q.var(oracledb.DB_TYPE_CLOB);result=q.var(oracledb.DB_TYPE_CLOB)
   try:
    q.callproc('RRL_STOCK_POSTING_API.prepare_command',[wire,s['actor'],replay]);assert replay.getvalue()is None;q.callproc('RRL_STOCK_POSTING_API.execute_prepared',[result]);assert totals(q)==[250,10]
    q.execute('select count(*)from RRL_TRADE_CASE_RETURN_UNIT where CASE_PICK_TASK_ID=:t',t=cid);assert q.fetchone()[0]==1
   finally:c.rollback();q.callproc('RRL_STOCK_POSTING_API.reset_connection')
   assert totals(q)==[250,11];q.execute('select count(*)from RRL_TRADE_CASE_RETURN_UNIT where CASE_PICK_TASK_ID=:t',t=cid);assert q.fetchone()[0]==0
  s['rollback']=True;s['checks']+=['caller_rollback_goods_history_and_receipt'];save()
 if 'returned'not in s:s['returned']=expect(200,own('POST',path,s['body']));save()
 assert expect(200,own('POST',path,s['body']))==s['returned'];s['checks']+=['return_and_exact_replay_once']
 if 'revoked_owner'not in s:grant('REVOKE',False);s['revoked_owner']=expect(403,own('POST',path,s['body']));s['checks']+=['cached_return_denied_after_owner_revoke'];save()
 if 'owner_restored'not in s:grant('RESTORE',True);s['owner_restored']=True;save()
 assert expect(200,own('POST',path,s['body']))==s['returned'];s['checks']+=['cached_return_restored_by_BLC_without_SNS']
 with oracle_connection()as c:
  q=c.cursor();assert totals(q)==[250,10];q.execute("select a.OWNER_ID,u.CURRENT_CELL,u.STOCK_STATUS,u.HARD_RESERVATION_ID from RRL_TRADE_CASE_RETURN_UNIT h join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=h.PHYSICAL_UNIT_KEY join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=h.PHYSICAL_UNIT_KEY where h.CASE_PICK_TASK_ID=:t",t=cid);s['returned_units']=[list(r)for r in q];assert s['returned_units']==[['BLC','T6C.BLC.PICK','AVAILABLE',None]]
  q.execute('select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=cid);assert q.fetchone()[0]=='CANCELLED'
  q.execute("select count(*)from RRL_TRADE_OWNER_GRANT where WARE_ID=:w and USERNAME=:a and OWNER_ID='SNS'and CAN_OPERATE=1",w=w,a=s['actor']);assert q.fetchone()[0]==0
 s['status']='PASS';s.pop('error',None);print(json.dumps(dict(status=s['status'],checks=s['checks'],units=s['returned_units'])))
except Exception as e:s.update(status='FAIL',error=str(e));raise
finally:s['history']+=CALLS;save()
