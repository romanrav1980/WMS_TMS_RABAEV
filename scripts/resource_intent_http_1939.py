"""Root-run bounded N1939 HTTP metadata proof; default plan never connects. No quantity command."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/retailcase/2026-10-15/resource-metadata-intents/http-1939.json'
PREFIX='N1939.RMI.'
ACTOR='N1939.OP'
TASK=1139
BASE='http://127.0.0.1:8088'
INTENTS='/api/resources/metadata-intents'
COMMAND=f'/api/case-pick/tasks/{TASK}/resource-commands'


def save(value:dict[str,Any])->None:
    OUT.parent.mkdir(parents=True,exist_ok=True)
    temporary=OUT.with_suffix('.tmp')
    with temporary.open('w',encoding='utf-8')as stream:
        json.dump(value,stream,indent=2,default=str);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,OUT)


def plan()->dict[str,Any]:
    from app.modules.resources.contracts_case_resource import CaseResourceCommand
    from app.modules.resources.infrastructure.case_resource_commands import canonical
    from app.modules.resources.contracts_resource_intents import ResourceIntentAbandon
    result={}
    for name,action,version in [('ABSENT','CLAIM',0),('CLAIM','CLAIM',0),('START','START',1)]:
        body=CaseResourceCommand(operation_id=PREFIX+name,action=action,expected_assignment_version=version,
            resource_session_id=59,resource_id=63,reason='SIMULATED_TEST_LABEL_NOT_PHYSICAL N1939 metadata acceptance only')
        result[name]=dict(body=body.model_dump(),wire=canonical(body))
    for name,original in [('ABANDON','ABSENT'),('RECORDED','CLAIM')]:
        result[name]=ResourceIntentAbandon(operation_id=PREFIX+name,domain='CASE',task_id=TASK,
            reason='TEST explicit never-recorded proof, not physical cancellation',original_wire=result[original]['wire']).model_dump()
    return result


def snapshot(g:Any)->dict[str,Any]:
    value=dict(stock=g.fetch_all('select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u order by CELL',{'u':'REUSE.RETURN:e6c16d0bbd'}),
        task=g.fetch_all('select STATUS,PICKED_QTY,CONTENT_VERSION,ASSIGNMENT_VERSION,ASSIGNED_TO,RESOURCE_SESSION_ID,ASSIGNED_RESOURCE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':TASK}),
        events=g.fetch_all('select CASE_PICK_EVENT_ID,EVENT_TYPE,OFFLINE_EVENT_ID from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:t order by CASE_PICK_EVENT_ID fetch first 201 rows only',{'t':TASK}),
        lineage=g.fetch_all('select p.UID_PALLET,p.STOCK_ORIGIN_UID,p.CREATED_BY_STOCK_OP,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION from RRL_PALLETS p join RRL_REMAINS r on r.UID_POLETA=p.UID_PALLET where p.UID_PALLET in(:p,:c)order by p.UID_PALLET,r.CELL',{'p':'REUSE.RETURN:e6c16d0bbd','c':'CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1'}),
        child=g.fetch_all('select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t',{'t':TASK}))
    assert len(value['events'])<=200
    assert all(r['stock_origin_uid']=='300000034518661218'for r in value['lineage'])
    assert sum(r['remain']for r in value['lineage'])==24 and sum(r['hard_reserved_base']for r in value['lineage'])==1
    assert len(value['task'])==1 and value['task'][0]['picked_qty']==0 and not value['child']
    assert sum(r['remain']for r in value['stock'])==23 and sum(r['hard_reserved_base']for r in value['stock'])==1
    return json.loads(json.dumps(value,default=str))


def checked(response:Any,status:int)->dict[str,Any]:
    assert response.status_code==status,(response.status_code,response.text[:600])
    return response.json()


def resolve(client:Any,original:dict[str,Any],status:int=200)->dict[str,Any]:
    body=original['body']
    return checked(client.get(INTENTS+'/resolution',params=dict(domain='CASE',task_id=TASK,
        original_operation_id=body['operation_id'],action=body['action'],target=ACTOR,
        original_request_sha256=hashlib.sha256(original['wire'].encode()).hexdigest().upper())),status)


def abandoned(data:dict[str,Any],control:dict[str,Any])->None:
    from app.modules.resources.contracts_resource_intents import ResourceIntentAbandoned,ResourceIntentAbandon
    from app.modules.resources.infrastructure.resource_intent_commands import control_wire,digest
    ack=ResourceIntentAbandoned.model_validate(data)
    assert(ack.operation_id,ack.domain,ack.task_id,ack.actor,ack.target,ack.original_wire)==(control['operation_id'],'CASE',TASK,ACTOR,ACTOR,control['original_wire'])
    assert ack.original_request_sha256==digest(control['original_wire'])
    assert ack.control_request_sha256==digest(control_wire(ResourceIntentAbandon(**control)))


def original_ack(response:Any,original:dict[str,Any])->dict[str,Any]:
    from app.modules.resources.contracts_case_resource import CaseResourceAck
    data=checked(response,200);ack=CaseResourceAck.model_validate(data);body=original['body']
    assert(ack.operation_id,ack.actor,ack.task_id,ack.action,ack.resource_session_id,ack.resource_id)==(body['operation_id'],ACTOR,TASK,body['action'],59,63)
    assert ack.request_sha256==hashlib.sha256(original['wire'].encode()).hexdigest().upper()
    assert ack.outcome=='APPLIED'and ack.changed and not ack.stock_posted
    return data


def role_command(g:Any,body:dict[str,Any])->dict[str,Any]:
    from app.modules.platform.public import AccessMetadataService
    from app.modules.platform.api.metadata_inputs import Command,normalize
    return AccessMetadataService(g).command('admin',normalize(Command(**body),'ACCESS'))


def restore_role(g:Any,report:dict[str,Any])->None:
    from app.modules.platform.api.metadata_inputs import Command,normalize
    off,on=report['role_commands']
    assert off['operation_id']==PREFIX+'ROLE.OFF'and on['operation_id']==PREFIX+'ROLE.ON'
    assert off['payload']==dict(on['payload'],active=False,expected_version=1)
    assert on['payload']['role_id']=='N1939.CASE.EXEC'and on['payload']['active']is True and on['payload']['expected_version']==2
    normalized=normalize(Command(**off),'ACCESS')
    digest=hashlib.sha256(json.dumps(normalized,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    current=g.fetch_all('select ACTIVE,VERSION_NO,TITLE from RRL_ACCESS_ROLE where ROLE_ID=:r',{'r':on['payload']['role_id']})
    if current==[{'active':1,'version_no':1,'title':on['payload']['title']}]:return
    if current==[{'active':1,'version_no':3,'title':on['payload']['title']}]:
        normalized_on=normalize(Command(**on),'ACCESS')
        on_digest=hashlib.sha256(json.dumps(normalized_on,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        own=g.fetch_all("select ACTOR,PAYLOAD_HASH from RRL_PLATFORM_COMMAND where DOMAIN='ACCESS'and OPERATION_ID=:o",{'o':on['operation_id']})
        assert own==[{'actor':'admin','payload_hash':on_digest}],own
        return
    rights=g.fetch_all('select PERMISSION from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:r order by PERMISSION',{'r':on['payload']['role_id']})
    assert rights==[{'permission':value}for value in on['payload']['permissions']]
    assert current==[{'active':0,'version_no':2,'title':on['payload']['title']}],current
    receipt=g.fetch_all("select ACTOR,PAYLOAD_HASH from RRL_PLATFORM_COMMAND where DOMAIN='ACCESS'and OPERATION_ID=:o",{'o':off['operation_id']})
    assert receipt==[{'actor':'admin','payload_hash':digest}],receipt
    report['role_on']=role_command(g,on)
    save(report)


def revoke_trial(g:Any,client:Any,control:dict[str,Any],report:dict[str,Any])->None:
    role='N1939.CASE.EXEC'
    rows=g.fetch_all('select ACTIVE,VERSION_NO,TITLE from RRL_ACCESS_ROLE where ROLE_ID=:r',{'r':role})
    assert len(rows)==1 and rows[0]['active']==1 and rows[0]['version_no']==1
    rights=g.fetch_all('select PERMISSION from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:r order by PERMISSION',{'r':role})
    assert rights==[{'permission':'case_pick_execute'}],rights
    payload=dict(role_id=role,title=rows[0]['title'],permissions=[r['permission']for r in rights])
    off=dict(operation_id=PREFIX+'ROLE.OFF',command_type='ROLE_SAVE',payload=dict(payload,active=False,expected_version=1))
    on=dict(operation_id=PREFIX+'ROLE.ON',command_type='ROLE_SAVE',payload=dict(payload,active=True,expected_version=2))
    report['role_commands']=[off,on];save(report)
    try:
        report['role_off']=role_command(g,off);save(report)
        checked(client.get(INTENTS+'/abandonments/'+control['operation_id']),403)
        checked(client.post(INTENTS+'/abandonments',json=control),403)
        report['checks'].append('current_role_revocation_denies_read_and_exact_replay')
    finally:restore_role(g,report)


def absence(client:Any,secret:str,p:dict[str,Any],report:dict[str,Any])->None:
    import httpx
    resolve(client,p['ABSENT'],404)
    def race(_:int)->dict[str,Any]:
        with httpx.Client(base_url=BASE,auth=(ACTOR,secret),timeout=15)as parallel:
            ack=checked(parallel.post(INTENTS+'/abandonments',json=p['ABANDON']),200)
            abandoned(ack,p['ABANDON']);return ack
    with ThreadPoolExecutor(max_workers=2)as pool:acks=list(pool.map(race,[1,2]))
    assert acks[0]==acks[1];report['abandonment']=acks[0];save(report)
    assert checked(client.get(INTENTS+'/abandonments/'+p['ABANDON']['operation_id']),200)==acks[0]
    assert checked(client.post(INTENTS+'/abandonments',json=p['ABANDON']),200)==acks[0]
    assert resolve(client,p['ABSENT'])['abandonment']==acks[0]
    denial=checked(client.post(COMMAND,json=p['ABSENT']['body']),409)['detail']
    assert 'RESOURCE_INTENT_ABANDONED_READ_PROOF'in denial['code']and denial['operation_id']==p['ABSENT']['body']['operation_id']and denial['outcome_confirmed']is False
    checked(client.get('/api/case-pick/resource-commands/'+p['ABSENT']['body']['operation_id']),404)
    report['checks'].append('same_control_race_exact_receipt_resolution_late_original_fenced_no_receipt')
    wrong=dict(p['ABANDON'],original_wire=p['ABANDON']['original_wire'].replace('acceptance only','changed intent'))
    checked(client.post(INTENTS+'/abandonments',json=wrong),409)
    checked(client.get(INTENTS+'/resolution',params=dict(domain='CASE',task_id=TASK,original_operation_id=p['ABSENT']['body']['operation_id'],action='CLAIM',target=ACTOR,original_request_sha256='0'*64)),409)
    checked(client.post(INTENTS+'/abandonments',json=dict(p['ABANDON'],actor='admin')),422)
    with httpx.Client(base_url=BASE,auth=('admin','admin123'),timeout=15)as foreign:
        checked(foreign.get(INTENTS+'/abandonments/'+p['ABANDON']['operation_id']),403)
    report['checks'].append('changed_body_wrong_hash_browser_actor_foreign_actor_denied')


def execute()->None:
    import httpx
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.oracle_gateway import OracleGateway
    g=OracleGateway();before=snapshot(g)
    assert before['task'][0]['status']=='NEW'and before['task'][0]['assignment_version']==0
    for table,key in [('RRL_RESOURCE_INTENT_ABANDON','CONTROL_OPERATION_ID'),('RRL_CASE_RESOURCE_COMMAND','OPERATION_ID')]:
        assert not g.fetch_all('select '+key+' from '+table+' where '+key+' like :p',{'p':PREFIX+'%'})
    secret=json.loads((ROOT/'runtime/n1939-qa-secrets.json').read_text(encoding='utf-8-sig'))[ACTOR]
    p=plan();report=dict(status='IN_PROGRESS',before=before,commands=p,checks=[],hardware=False,goods_commands=0);save(report)
    with httpx.Client(base_url=BASE,auth=(ACTOR,secret),timeout=15)as client:
        absence(client,secret,p,report)
        revoke_trial(g,client,p['ABANDON'],report)
        abandoned(checked(client.get(INTENTS+'/abandonments/'+p['ABANDON']['operation_id']),200),p['ABANDON'])
        claim=original_ack(client.post(COMMAND,json=p['CLAIM']['body']),p['CLAIM'])
        assert claim['assignment_version']==1 and claim['status']=='ASSIGNED'
        assert checked(client.post(COMMAND,json=p['CLAIM']['body']),200)==claim
        checked(client.post(INTENTS+'/abandonments',json=p['RECORDED']),409)
        assert resolve(client,p['CLAIM'])['original_receipt']==claim
        report['claim']=claim;save(report)
        start=original_ack(client.post(COMMAND,json=p['START']['body']),p['START'])
        assert start['assignment_version']==2 and start['status']=='IN_PROGRESS'and start['started_at_instant']
        assert checked(client.post(COMMAND,json=p['START']['body']),200)==start
        report['start']=start;report['checks'].append('CLAIM_APPLIED_replay_RECORDED_not_ABANDONED_START_APPLIED_replay')
    after=snapshot(g)
    assert after['lineage']==before['lineage']
    assert after['events'][:len(before['events'])]==before['events'] and len(after['events'])==len(before['events'])+2
    assert after['stock']==before['stock']and after['task'][0]['content_version']==before['task'][0]['content_version']
    assert not g.fetch_all('select OPERATION_ID from RRL_STOCK_OPERATION where ACTOR=:a',{'a':ACTOR})
    receipts=g.fetch_all('select OPERATION_ID,OUTCOME from RRL_CASE_RESOURCE_COMMAND where OPERATION_ID like :p order by OPERATION_ID',{'p':PREFIX+'%'})
    assert receipts==[{'operation_id':PREFIX+'CLAIM','outcome':'APPLIED'},{'operation_id':PREFIX+'START','outcome':'APPLIED'}],receipts
    tombstones=g.fetch_all('select CONTROL_OPERATION_ID from RRL_RESOURCE_INTENT_ABANDON where CONTROL_OPERATION_ID like :p',{'p':PREFIX+'%'})
    assert tombstones==[{'control_operation_id':PREFIX+'ABANDON'}],tombstones
    report.update(status='PASS',after=after,goods_stock_unchanged=True,role_restored_version=3);save(report)
    print(json.dumps(dict(status='PASS',checks=len(report['checks']),goods_commands=0)))


def main()->None:
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group();mode.add_argument('--execute',action='store_true');mode.add_argument('--restore-role-only',action='store_true');args=parser.parse_args()
    if not args.execute and not args.restore_role_only:
        print(json.dumps(dict(status='PREPARED_NOT_EXECUTED',task=TASK,actor=ACTOR,goods_commands=0)));return
    assert os.environ.get('RESOURCE_INTENT_HTTP_ROOT_RELEASE')=='1','Root release required'
    sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
    if args.restore_role_only:
        from stock_posting_environment import load_local_oracle_environment
        load_local_oracle_environment()
        from app.oracle_gateway import OracleGateway
        restore_role(OracleGateway(),json.loads(OUT.read_text(encoding='utf-8')))
        return
    assert not OUT.exists(),'Existing evidence: inspect exact original journal; never fork or rerun blindly'
    execute()


if __name__=='__main__':main()
