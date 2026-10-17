"""Independent real Oracle clock acceptance; no stock commit."""
import hashlib,json,re,time
from uuid import uuid4
import oracledb
from warehouse_task_scoped_complete_smoke import OracleGateway,ROOT,OLD_REPLAY,RollbackTrial,cleanup,post,scalar,setup,snapshot
from warehouse_task_scoped_extra import command_body,original_replay
OUT=ROOT/'reports/retailcase/2026-10-15/stock-operation-clock'

def counts(g):
 return {t:g.fetch_all('select count(*) N from '+t)[0]['n'] for t in ('RRL_STOCK_OPERATION','RRL_STOCK_OP_CLOCK')}

def checkpoint(g):
 schema=(ROOT/'db/migrations/2026-10-15_stock_operation_clock/schema.sql').read_text(encoding='utf-8');hashes={}
 for name in ('RRL_STOCK_CLOCK_GUARD','RRL_STOCK_APPLIED_CLOCK'):
  actual=''.join(r['text'] for r in g.fetch_all("select TEXT from USER_SOURCE where NAME=:name and TYPE='TRIGGER' order by LINE",{'name':name}))
  match=re.search(r'create or replace (trigger '+name+r'\b.*?)(?:\n/)',schema,re.I|re.S)
  assert match,name
  norm=lambda s:re.sub(r'\s+','',s).lower()
  assert norm(actual)==norm(match.group(1)),name
  hashes[name]=hashlib.sha256(actual.encode()).hexdigest()
 assert not g.fetch_all("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_CLOCK_GUARD','RRL_STOCK_APPLIED_CLOCK')")
 assert g.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]['n']==0
 assert g.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-stock-operation-clock'")==[{'status':'APPLIED'}]
 return dict(trigger_source_sha256=hashes,invalid_count=0,migration_status='APPLIED')

def positive(g,ctx,checks):
 body=command_body(g,ctx);body['operation_id']='CLOCK.QA:'+uuid4().hex;op=body['operation_id'];before=snapshot(g,ctx)
 try:
  with g.transaction('Independent clock positive and append-only caller rollback')as c:
   start=scalar(c,"select to_char(systimestamp at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM')from dual")
   result=post(c,body);assert result['status']=='DONE',result
   c.execute("""select ACTOR,COMMAND_TYPE,TIME_SOURCE,extract(timezone_hour from RECORDED_AT_UTC),extract(timezone_minute from RECORDED_AT_UTC),
    case when RECORDED_AT_UTC between to_timestamp_tz(:clock_begin,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') and systimestamp at time zone 'UTC' then 1 else 0 end
    from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op""",clock_begin=start,op=op)
   rows=c.fetchall();assert rows==[(ctx['actor'],'TASK_COMPLETE','ORACLE_SYSTIMESTAMP',0,0,1)],rows
   assert scalar(c,"select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE='APPLIED'",op=op)==1
   for sql in ('update RRL_STOCK_OP_CLOCK set ACTOR=ACTOR where OPERATION_ID=:op','delete from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op'):
    try:c.execute(sql,op=op)
    except oracledb.DatabaseError as e:assert 'STOCK_CLOCK_APPEND_ONLY'in str(e),str(e)
    else:raise AssertionError('Clock mutation accepted')
   assert scalar(c,'select count(*)from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op',op=op)==1
   checks.extend(['native_applied_one_clock_actor_kind_source_utc_in_db_time_window','clock_direct_update_and_delete_rejected'])
   raise RollbackTrial()
 except RollbackTrial:pass
 assert snapshot(g,ctx)==before
 for table in ('RRL_STOCK_OPERATION','RRL_STOCK_OP_CLOCK'):
  assert g.fetch_all('select count(*) N from '+table+' where OPERATION_ID=:op',{'op':op})[0]['n']==0
 checks.append('caller_rollback_restores_operation_clock_and_physical_hard_version')
 return op

def main():
 OUT.mkdir(parents=True,exist_ok=True);g=OracleGateway();ctx=dict(tag=uuid4().hex[:9],grants=[]);ctx['prefix']='clk'+ctx['tag'];checks=[]
 before=counts(g);marker=g.fetch_all('select nvl(max(LOG_ID),0) N from RRL_SQL_SLOW_LOG')[0]['n'];cp=checkpoint(g);started=time.monotonic()
 try:
  setup(g,ctx);op=positive(g,ctx,checks)
  old=g.fetch_all('select count(*) N from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op',{'op':OLD_REPLAY})[0]['n']
  original_replay(g,ctx,checks)
  assert g.fetch_all('select count(*) N from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op',{'op':OLD_REPLAY})[0]['n']==old
  checks.append('original_committed_replay_does_not_backfill_clock')
 finally:cleanup(g,ctx)
 for table,key,value in [('RRL_WAREHOUSE_TASK','TASK_ID',ctx['task']),('RRL_RESOURCE_SESSION','SESSION_ID',ctx['session']),('RRL_RESOURCE','RESOURCE_ID',ctx['resource']),('RRL_RESOURCE_EQUIPMENT','EQUIPMENT_ID',ctx['equipment']),('RRL_RESOURCE_SHIFT','SHIFT_ID',ctx['shift']),('RUSERS','ID',ctx['actor']),('RUSERS','ID',ctx['other']),('RRL_CELLS','CELL',ctx['cell'])]:
  assert g.fetch_all('select count(*) N from '+table+' where '+key+'=:id',{'id':value})[0]['n']==0
 for role,assignment in ctx['grants']:
  for table,key,value in [('RRL_ACCESS_ROLE','ROLE_ID',role),('RRL_ACCESS_ASSIGNMENT','ASSIGNMENT_ID',assignment)]:
   assert g.fetch_all('select count(*) N from '+table+' where '+key+'=:id',{'id':value})[0]['n']==0
 assert g.fetch_all('select USER_GROUP,DELETED,WARE_ID from RUSERS where ID=:actor',{'actor':ctx['old_actor']})==[dict(user_group=ctx['old_group'],deleted=ctx['old_deleted'],ware_id=ctx['old_ware'])]
 after=counts(g);assert before==after,(before,after)
 checks.append('temporary_metadata_absent_original_identity_restored_global_counts_unchanged')
 slow=g.fetch_all('select * from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker})
 result=dict(status='PASS',checks=checks,before=before,after=after,checkpoint=cp,checkpoint_after=checkpoint(g),elapsed_seconds=round(time.monotonic()-started,3),trial_operation_id=op,metadata_fixture_committed_temporarily=True,metadata_fixture_cleaned=True,native_access_audit_retained=True,stock_execute='CALLER_ROLLBACK_ONLY',physical_hardware=False,slow_sql=slow)
 (OUT/'native-report.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8');print(json.dumps(result,default=str))
if __name__=='__main__':main()

