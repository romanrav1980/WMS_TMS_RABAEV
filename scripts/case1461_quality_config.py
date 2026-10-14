exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import httpx
from uuid import uuid4
ctx=json.loads(Path('tmp/qc1460_scope.json').read_text());ware=ctx['warehouse'];url=f'/api/inventory/quality-policies/warehouses/{ware}'
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'");user,password=q.fetchone()
with httpx.Client(base_url='http://127.0.0.1:8088',auth=(user,password),timeout=30) as client:
 response=client.get(url,params={'store_addr':'*','place_category':'STOCK'});assert response.status_code==200,response.text
 before=response.json();body={'operation_id':'QC1461:'+uuid4().hex,'expected_version':before['version'],'store_addr':'*','place_category':'STOCK','active':True,'control_mode':'WEIGHT','independent':False,'sample_percent':'0','exempt_whole':True,'exempt_storage':False,'reason':'Private native whole pallet exception case'}
 response=client.post(url,json=body);assert response.status_code==200,response.text;result=response.json()
 assert client.post(url,json=body).json()==result
 conflict=client.post(url,json={**body,'exempt_whole':False});assert conflict.status_code==409,conflict.text
 stale=client.post(url,json={**body,'operation_id':'QC1461.STALE:'+uuid4().hex});assert stale.status_code==409,stale.text
 ctx.update(body=body,result=result,before=before);Path('tmp/qc1461_config.json').write_text(json.dumps(ctx,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'save':response.status_code,'replay':True,'changed_body':conflict.status_code,'stale_version':stale.status_code,'version':result['version'],'stock_changed':result['stock_changed']}))
