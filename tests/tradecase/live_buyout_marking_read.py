"""Read every authorized marking code after shipment; revoke the fresh viewer and preserve stock."""
import json,os,re,secrets,sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).parent))
import live_program_buyout_25 as qa
from live_document_acceptance import http,expect,CALLS
suffix=sys.argv[1]if len(sys.argv)>1 else '';assert re.fullmatch(r'[a-z0-9-]{0,30}',suffix)
label=('.'+suffix)if suffix else ''
FILE=qa.OUT/('buyout-marking-read'+('-'+suffix if suffix else '')+'.json')
r=json.loads(FILE.read_text())if FILE.exists()else dict(phase='NEW',steps={})
def save():FILE.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
def step(key,path,body,method='PUT'):
 if key not in r['steps']:r['steps'][key]=dict(path=path,body=body,method=method);save()
 v=r['steps'][key]
 if 'result'not in v:v['result']=expect(200,http(v['method'],v['path'],v['body']));save()
 return v['result']
def pages(mode,actor=None,password=None):
 result=[];after='';counts=[]
 while True:
  path=qa.base()+'/buyouts/'+qa.tag()+'.'+mode+'/units?limit=100&after='+after
  data=expect(200,http('GET',path,actor=actor,password=password));counts.append(len(data['items']));result.extend(data['items'])
  if not data['has_more']:break
  assert data['next_after'] and data['next_after']!=after;after=data['next_after']
 assert counts==[100,100,50],counts
 pairs={(u['physical_unit_key'],m['system_code'],m['code'])for u in result for m in u['marking_codes']}
 expected=set(qa.db('select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE from RRL_TRADE_BUYOUT_UNIT bu join RRL_TRADE_BUYOUT b on b.BUYOUT_ID=bu.BUYOUT_ID join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=bu.PHYSICAL_UNIT_KEY join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where b.WARE_ID=:w and b.BUYOUT_ID=:b',w=qa.s['fixture']['warehouse_id'],b=qa.tag()+'.'+mode))
 assert pairs==expected and len(pairs)==250
 assert len(result)==250 and all(u['owner_id']=='BLC'and u['outcome']=='CONFIRMED'for u in result)
 carrier=qa.db('select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=qa.s['case_after'])[0][0]if mode=='AFTER'else qa.s['transit_pallet']
 assert all(u['stock_status']=='ISSUED'and u['carrier_identifier']==carrier for u in result)
 return dict(pages=counts,units=len(result),codes=len(pairs),carrier_checked=True,issued=True)
def main():
 assert r['phase']!='CLOSED','Closed proof; no requests'
 assert qa.s['phase']=='CLOSED'and qa.s['fixture']['warehouse_id']==223240710
 os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',Path('AGENTS.md').read_text(encoding='utf-8'))[1]
 w=qa.s['fixture']['warehouse_id']
 try:
  r['before']=qa.stock();r['admin']={mode:pages(mode)for mode in ['AFTER','TRANSIT']};save()
  if 'viewer'not in r:r['viewer']=dict(username='BC25'+uuid4().hex[:9],password=secrets.token_hex(24));save()
  actor=r['viewer']['username'];password=r['viewer']['password']
  if 'created'not in r:
   with qa.oracle_connection()as c:
    q=c.cursor();q.execute('select count(*)from RUSERS where ID=:a',a=actor)
    if not q.fetchone()[0]:
     q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Scoped buyout marks viewer','TC03QA',222823304,0,1)",a=actor,p=password)
     q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Scoped buyout marks viewer',1,1)",a=actor)
     q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_view')",a=actor)
     q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Own marking read proof',1)",a=actor,w=str(w));c.commit()
   r['created']=True;save()
  path=qa.base()+'/buyouts/'+qa.tag()+'.AFTER/units?limit=100'
  if 'grant'not in r['steps']:expect(403,http('GET',path,actor=actor,password=password))
  step('grant',qa.base()+'/stock/owner-grants',dict(operation_id=qa.tag()+'.marks'+label+'.grant',expected_version=0,username=actor,owner_id='SNS',can_view=True,can_operate=False,reason='Read existing party-owned buyout codes'))
  r['assigned_view']={mode:pages(mode,actor,password)for mode in ['AFTER','TRANSIT']};save()
  expect(403,http('GET',path.replace('/223240710/','/222232016/'),actor=actor,password=password))
  step('revoke',qa.base()+'/stock/owner-grants',dict(operation_id=qa.tag()+'.marks'+label+'.revoke',expected_version=1,username=actor,owner_id='SNS',can_view=False,can_operate=False,reason='Revoke marking read proof'))
  denied=expect(403,http('GET',path,actor=actor,password=password));assert 'items'not in denied;r['denied_after_revoke']=True
  with qa.oracle_connection()as c:
   q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor);assert q.rowcount==1
   q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
  r['after']=qa.stock();assert tuple(r['after'])==tuple(r['before'])==(0,0)
  r['status']='PASS';r['phase']='CLOSED';save();print(json.dumps({k:r[k]for k in ['status','admin','assigned_view','denied_after_revoke','after']}))
 finally:r.setdefault('http',[]).extend(CALLS);save()
if __name__=='__main__':main()
