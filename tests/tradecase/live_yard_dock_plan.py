"""Live dock planning on owned metadata; no physical stock changes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import json,os,secrets,sys
from pathlib import Path
from threading import Barrier
from urllib.parse import urlencode
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.update(TRADECASE_ADMIN_USER='admin',TRADECASE_ADMIN_PASSWORD='admin123')
from live_document_acceptance import http,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
W,O=220793322,215590763
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T10/dock-plan-live.json'
s=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else dict(tag='DP23.'+uuid4().hex[:9],requests={},results={},checks=[])
TAG=s['tag']
def save():
 s['calls']=s.get('old_calls',[])+CALLS;OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def query(sql,**binds):
 with oracle_connection() as conn:
  q=conn.cursor();q.execute(sql,binds);return [tuple(x.read() if hasattr(x,'read') else x for x in r)for r in q.fetchall()]
def stock():
 return query('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322,215590763)group by c.WARE_ID order by c.WARE_ID')
def path(w,tail=''):return f'/api/tradecase/warehouses/{w}/yard/dock-plans'+tail
def step(key,url,body=None,status=200,qa=False,method='POST'):
 if key not in s['requests']:s['requests'][key]=dict(path=url,body=body,status=status,qa=qa,method=method);save()
 if key not in s['results']:
  r=s['requests'][key];args=(s['actor'],s['password']) if r['qa'] else ()
  code,result=http(r['method'],r['path'],r['body'],*args);save()
  assert code in ([r['status']] if isinstance(r['status'],int) else r['status']),(code,result)
  s['results'][key]=result;save()
 return s['results'][key]
def interval(hours=0,minutes=0):
 a=datetime.fromisoformat(s['start'])+timedelta(hours=hours,minutes=minutes)
 return dict(planned_from=a.isoformat(),planned_to=(a+timedelta(hours=1)).isoformat())
def visit(name,w=W,vehicle=None,qa=False):
 return step('visit_'+name,f'/api/tradecase/warehouses/{w}/yard/visits',dict(operation_id=TAG+'.visit.'+name,supply_ids=[TAG+'.'+name],vehicle=vehicle or TAG+'.'+name,planned_arrival_at=s['start']),qa=qa)
def grant(key,version,allow):
 return step(key,f'/api/tradecase/warehouses/{W}/stock/owner-grants',dict(operation_id=TAG+'.'+key,expected_version=version,username=s['actor'],owner_id='SNS',can_view=allow,can_operate=allow,reason='Owned dock plan proof'),method='PUT')
def setup():
 if 'before'not in s:
  s.update(before=stock(),actor='DP'+uuid4().hex[:12],password=secrets.token_hex(20),start=(datetime.now(timezone.utc).replace(microsecond=0)+timedelta(hours=3)).isoformat(),slow_marker=query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0]);save()
 if s.get('fixture_created'):return
 with oracle_connection()as conn:
  q=conn.cursor()
  for w,names in[(W,('A','B','D','E','Q')),(O,('C',))]:
   q.execute('select NAME from RRL_WARES where ID=:w',w=w);assert q.fetchone()[0].startswith('TRADECASE QA ')
   q.execute('select SOURCE_ID from RRL_TRADE_SITE where WARE_ID=:w and ENABLED=1',w=w);source=q.fetchone()[0]
   for name in names:
    body=json.dumps(dict(entity_type='SUPPLY',owner_id='SNS',pallet_identifier=TAG+'.'+name,fixture='Controlled metadata; no ERP receipt proof'))
    q.execute("insert into RRL_TRADE_DOCUMENT(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)values(:w,'SUPPLY',:id,:src,1,:h,:b,'ACCEPTED','admin')",w=w,id=TAG+'.'+name,src=source,h=sha256(body.encode()).hexdigest(),b=body)
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED)values(:a,:p,'Dock QA','QA_ONLY',:w,0)",a=s['actor'],p=s['password'],w=W)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Dock QA',1,1)",a=s['actor'])
  for r in('tradecase_view','tradecase_yard_operate'):q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:r)',a=s['actor'],r=r)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '12'hour,'admin','Owned dock proof',1)",a=s['actor'],w=str(W));conn.commit()
 s['fixture_created']=True;save()
def cleanup():
 for p,w,v in query("select PLAN_ID,WARE_ID,VERSION_NO from RRL_YARD_DOCK_PLAN where STATUS='ACTIVE'and VISIT_ID in(select VISIT_ID from RRL_YARD_VISIT_EVENT where OPERATION_ID like :tag)",tag=TAG+'%'):
  step('cancel_plan_'+str(p),path(w,f'/{p}/cancel'),dict(operation_id=TAG+'.cancel.plan.'+str(p),expected_version=v,reason='End owned planning proof'))
 for v,w,ver in query("select VISIT_ID,WARE_ID,VERSION_NO from RRL_YARD_VISIT where STATE not in('CANCELLED','DEPARTED')and VISIT_ID in(select VISIT_ID from RRL_YARD_VISIT_EVENT where OPERATION_ID like :tag)",tag=TAG+'%'):
  step('cancel_visit_'+str(v),f'/api/tradecase/warehouses/{w}/yard/visits/{v}/transitions',dict(operation_id=TAG+'.cancel.visit.'+str(v),action='CANCEL',expected_version=ver,reason='End owned planning proof'))
 with oracle_connection()as conn:
  q=conn.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=s['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=s['actor']);conn.commit()
 assert [list(x)for x in stock()]==[list(x)for x in s['before']]
 assert query("select count(*)from RRL_YARD_DOCK_PLAN where STATUS='ACTIVE'and VISIT_ID in(select VISIT_ID from RRL_YARD_VISIT_EVENT where OPERATION_ID like :t)",t=TAG+'%')==[(0,)]
 s['slow_sql']=query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 12 rows only',m=s['slow_marker']);s['status']='PASS';s.pop('error',None);save()
def run():
 if s.get('status')=='PASS':print('Already PASS; no commands');return
 if s.get('cleanup_started'):cleanup();return
 setup();grant('grant',0,True)
 a=visit('A');b=visit('B');c=visit('C',O,TAG+'.A')
 p=step('plan_A',path(W),dict(operation_id=TAG+'.plan.A',visit_id=a['visit_id'],dock='B22D1161',**interval()))
 replay=step('replay_A',path(W),s['requests']['plan_A']['body']);assert replay['replayed']and replay['plan_id']==p['plan_id']
 r=step('body_conflict',path(W),dict(s['requests']['plan_A']['body'],dock='N22DA1168'),status=409);assert r['detail']['code']=='YARD_OPERATION_CONFLICT'
 r=step('dock_conflict',path(W),dict(operation_id=TAG+'.conflict.dock',visit_id=b['visit_id'],dock='B22D1161',**interval(minutes=30)),status=409);assert r['detail']['code']=='YARD_DOCK_PLAN_CONFLICT'
 r=step('vehicle_conflict',path(O),dict(operation_id=TAG+'.conflict.vehicle',visit_id=c['visit_id'],dock='TC7D1155',**interval()),status=409);assert r['detail']['code']=='YARD_VEHICLE_PLAN_CONFLICT'
 step('touching',path(W),dict(operation_id=TAG+'.touching',visit_id=b['visit_id'],dock='B22D1161',**interval(hours=1)))
 moved=step('move_A',path(W,f"/{p['plan_id']}/move"),dict(operation_id=TAG+'.move.A',expected_version=p['version'],dock='N22DA1168',**interval()));assert moved['version']==2 and moved['fact_dock']is None and moved['arrived_at']is None
 old=step('old_receipt',path(W),s['requests']['plan_A']['body']);assert old['version']==1 and old['dock']=='B22D1161'and old['replayed']
 s['checks'].append('Replay/body conflict, dock and cross-site vehicle overlaps, touching, move with unchanged facts, immutable old receipt')
 for n in('D','E'):visit(n)
 if 'race'not in s:
  bodies=[dict(operation_id=TAG+'.race.'+n,visit_id=s['results']['visit_'+n]['visit_id'],dock='B22D1161',**interval(hours=3))for n in('D','E')];s['race_requests']=bodies;save();barrier=Barrier(2)
  def contender(body):barrier.wait(timeout=10);return http('POST',path(W),body)
  with ThreadPoolExecutor(max_workers=2)as pool:answers=list(pool.map(contender,bodies))
  s['race']=answers;save();assert sorted(r[0]for r in answers)==[200,409],answers
 qv=visit('Q',qa=True)
 qp=step('plan_Q',path(W),dict(operation_id=TAG+'.plan.Q',visit_id=qv['visit_id'],dock='B22D1161',**interval(hours=5)),qa=True)
 window='?'+urlencode({'from':s['start'],'to':(datetime.fromisoformat(s['start'])+timedelta(days=1)).isoformat()})
 visible=step('visible',path(W)+window,method='GET',qa=True);assert qp['plan_id']in[p['plan_id']for p in visible['plans']]
 grant('revoke_owner',1,False)
 hidden=step('hidden',path(W)+window,method='GET',qa=True);assert hidden['plans']==[]
 step('hidden_replay',path(W),s['requests']['plan_Q']['body'],status=[403,409],qa=True)
 with oracle_connection()as conn:
  q=conn.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=s['actor']);conn.commit()
 step('scope_replay',path(W),s['requests']['plan_Q']['body'],status=403,qa=True)
 s['checks'].append('Two parallel plans have one winner; role-only plan succeeds; owner revoke hides plans/denies receipt; WARE revoke403')
 s['cleanup_started']=True;save();cleanup()
if __name__=='__main__':
 s['old_calls']=s.get('calls',[])
 try:run()
 except Exception as exc:s['error']=str(exc);save();raise
 finally:save()
