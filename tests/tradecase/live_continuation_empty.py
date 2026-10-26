"""A real empty continuation must not request CONFIG6; test rights before the early return."""
from contextlib import contextmanager
import json,secrets,sys,time
from pathlib import Path
from uuid import uuid4
sys.path[:0]=[str(Path(__file__).resolve().parents[2]/'scripts'),str(Path(__file__).resolve().parents[2]/'api/wms_api_server'),str(Path(__file__).parent),str(Path(__file__).resolve().parents[2])]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation
from app.modules.inventory.infrastructure.minimax_service import MinimaxService
import oracledb
from fastapi import HTTPException
OUT=Path('runtime/test-evidence/tradecase/2026-10-26/T12');FILE=OUT/'empty-polling-after.json'
WARE=223240710
class Cursor:
 def __init__(self,cursor,gateway):self.cursor,self.gateway=cursor,gateway
 def execute(self,sql,*args,**kwargs):
  if 'RRL_STOCK_METADATA_TX.BEGIN_CHANGE'in sql.upper():self.gateway.metadata_entries+=1
  return self.cursor.execute(sql,*args,**kwargs)
 def __getattr__(self,name):return getattr(self.cursor,name)
class Gateway:
 def __init__(self):self.metadata_entries=0
 @contextmanager
 def transaction(self,name):
  with oracle_connection()as c:
   c.call_timeout=10000;q=c.cursor()
   try:yield Cursor(q,self)
   finally:c.rollback();q.callproc('RRL_STOCK_METADATA_TX.end_change')
def stock():
 with oracle_connection()as c:
  q=c.cursor();q.execute('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=WARE);return q.fetchone()
def main():
 assert not FILE.exists(),'Read the existing proof; do not create another actor'
 actor='CE26'+uuid4().hex[:9];r=dict(actor=actor,before=stock())
 def save():FILE.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
 save();created=False
 try:
  with oracle_connection()as c:
   q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own continuation scope check',:a,:w,0,0)",a=actor,p=secrets.token_hex(24),w=WARE)
   q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:a,'pick_wave_launch')",a=actor);c.commit();created=True
  gateway=Gateway();minimax=MinimaxService(gateway,lambda *_:None);service=ReplenishmentContinuation(gateway,lambda *_:(_ for _ in()).throw(AssertionError('Unexpected task synchronization')))
  with oracle_connection()as held:
   q=held.cursor();q.execute("select LOCK_ID from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE')");lock=q.fetchone()[0]
   result=q.var(oracledb.DB_TYPE_NUMBER);q.execute('begin :o:=sys.dbms_lock.request(:i,4,1,true);end;',o=result,i=lock);assert result.getvalue()==0
   try:
    for user in ['admin',actor]:
     t=time.perf_counter();answer=service.reconcile(WARE,user);elapsed=round((time.perf_counter()-t)*1000,2)
     assert answer==dict(warehouse=WARE,processed=0,wave_ids=[])and elapsed<1500
     t=time.perf_counter();mini=minimax.reconcile(WARE,user);mini_ms=round((time.perf_counter()-t)*1000,2)
     assert mini==dict(warehouse=WARE,created=0,wave_id=None,faces=[])and mini_ms<1500
     r[user]=dict(result=answer,elapsed_ms=elapsed,minimax_result=mini,minimax_ms=mini_ms);save()
    try:service.reconcile(1,actor)
    except HTTPException as exc:assert exc.status_code==403;r['foreign_warehouse']=403
    else:raise AssertionError('Foreign empty warehouse was accepted')
    try:service.reconcile(WARE,actor+'.missing')
    except oracledb.DatabaseError as exc:assert exc.args[0].code==20882;r['missing_permission']=20882
    else:raise AssertionError('Missing permission was accepted')
    try:minimax.reconcile(WARE,actor+'.missing')
    except oracledb.DatabaseError as exc:assert exc.args[0].code==20882;r['minimax_missing_permission']=20882
    else:raise AssertionError('Minimax missing permission was accepted')
    assert gateway.metadata_entries==0;r['empty_metadata_entries']=gateway.metadata_entries
   finally:held.rollback()
  # A stale positive hint must still enter and revalidate the original native writer.
  service._has_pending=lambda *_:True
  r['stale_positive_hint']=service.reconcile(WARE,'admin');assert r['stale_positive_hint']['processed']==0 and gateway.metadata_entries==1
  minimax._has_configuration=lambda *_:True
  r['minimax_stale_positive_hint']=minimax.reconcile(WARE,'admin');assert r['minimax_stale_positive_hint']['created']==0 and gateway.metadata_entries==2
  r['after']=stock();assert r['after']==r['before']==(0,0)
  r['status']='PASS';save()
 finally:
  if created:
   with oracle_connection()as c:
    q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a and USER_GROUP=:a',a=actor);assert q.rowcount==1;q.execute('delete from RIGHTS where USER_GROUP=:a',a=actor);c.commit()
  r['actor_closed']=created;save()
 print(json.dumps(r))
if __name__=='__main__':main()
