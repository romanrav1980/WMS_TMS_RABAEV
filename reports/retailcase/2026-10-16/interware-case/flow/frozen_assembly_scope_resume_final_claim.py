from pathlib import Path
source=(Path(__file__).parent/'assembly_scope_finalize.py').read_text(encoding='utf-8')
exec(compile(source.split("x=json.loads",1)[0],'<final imports>','exec'))
x=json.loads((f.BASE/'fixture.json').read_text());g=f.OracleGateway();out=f.BASE/'finalize.json';report=json.loads(out.read_text())
assert 'claim'in report and'capture'not in report
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
report['rejected_pre_claim_window_packet']=report['packet'];save()
requests=WarehouseWeighRequests(g)
if'expired_attempt'not in report:
 report['expired_attempt']=dict(request=report['request'],claim=report['claim'],packet=report['packet'],status=requests.status(x['prefix']+'.FINAL.REQUEST',x['actor']))
assert not g.fetch_all('select CAPTURE_KEY from RRL_WH_SCALE_CAPTURE where DEVICE_ID=:d and CAPTURE_ID=:id',{'d':x['device'],'id':report['claim_body']['claim_id']})
request_id=x['prefix']+'.FINAL.REQUEST2'
report['request_body']={**report['request_body'],'request_id':request_id};save()
report['request']=requests.request(report['request_body'],x['actor']);save()
report.setdefault('prior_claims',[]).append(dict(claim=report['claim'],packet=report['packet']));save()
report['claim_body']=dict(claim_id=x['prefix']+'.FINAL.CLAIM3',device_id=x['device']);save()
report['claim']=requests.claim(request_id,report['claim_body'],x['sender']);save()
time.sleep(3.1)
exec(compile('now=datetime.now(timezone.utc);stamp='+source.split('now=datetime.now(timezone.utc);stamp=',1)[1],'<final remainder>','exec'))
