"""Hold only an owned carrier's native resource mutex; verify bounded HTTP refusal and exact-operation recovery."""
import json,os,re,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import live_topup_physical_660 as qa
FILE=qa.OUT/'lock-budget-contention.json'
def main():
 assert not FILE.exists(),'Read the recorded contention proof instead of starting another operation'
 qa.s.update(json.loads(qa.STATE.read_text(encoding='utf-8')));s=qa.s
 assert s['fixture']['warehouse_id']==223214750 and s['phase']=='UNLOADED'
 os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',Path('AGENTS.md').read_text(encoding='utf-8'))[1]
 uid=s['shipments'][sorted(s['shipments'])[0]]['pallet'];path='/api/inventory/pallet-floor-types'
 p=qa.expect(200,qa.http('GET',path+'?identifier='+uid))
 body=dict(operation_id=qa.tag()+'.contention.floor',identifier=uid,pallet_type_id=1,expected_version=p['version'],scan_pallet=uid,scan_cell=p['cell'],evidence_reference='OWN_SYNTHETIC_MUTEX_CONTENTION')
 r=dict(body=body,before=qa.stock(),phase='INTENT_SAVED')
 def save():FILE.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
 save()
 try:
  with qa.oracle_connection()as conn:
   q=conn.cursor()
   q.execute("select RRL_STOCK_LOCK_API.resource_lock_id(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PALLET_FLOOR_TYPE',:p))from dual",p=uid);lock=q.fetchone()[0]
   import oracledb
   result=q.var(oracledb.DB_TYPE_NUMBER);q.execute('begin :o:=sys.dbms_lock.request(:i,6,0,true);end;',o=result,i=lock);assert result.getvalue()==0
   r['native_mutex']=lock;save()
   try:
    start=time.perf_counter();response=qa.http('POST',path,body);r['blocked_elapsed_ms']=round((time.perf_counter()-start)*1000,2);r['blocked']=response;save()
    assert response[0]==503 and response[1]['detail']['code']in('LOCK_RETRY_EXHAUSTED','REQUEST_DEADLINE'),response
    assert 5000<=r['blocked_elapsed_ms']<=33000,r['blocked_elapsed_ms']
    assert qa.expect(200,qa.http('GET',path+'?identifier='+uid))['version']==p['version']
    assert tuple(qa.stock())==(6600,6600,33)
   finally:conn.rollback()
  r['recovered']=qa.expect(200,qa.http('POST',path,body));save()
  assert qa.expect(200,qa.http('POST',path,body))==r['recovered']
  r['current']=qa.expect(200,qa.http('GET',path+'?identifier='+uid));assert r['current']['version']==p['version']+1
  r['after']=qa.stock();assert tuple(r['after'])==(6600,6600,33)
  r['status']='PASS';r['phase']='CLOSED';save();print(json.dumps(dict(status=r['status'],blocked_ms=r['blocked_elapsed_ms'],after=r['after'])))
 finally:r['http']=qa.CALLS;save()
if __name__=='__main__':main()
