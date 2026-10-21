"""A qualified reach-truck session moves/binds a real full pallet with warehouse role only."""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path
import re
import secrets
import sys
from urllib.parse import urlencode
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import live_full_pallet as prep
from full_pallet_fixture import prepare_shipment
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06';FILE=OUT/'scoped-full-pallet.json'
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(history=[])


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def password():
    with oracle_connection()as c:
        q=c.cursor();q.execute("select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0",a=s['actor']);row=q.fetchone();assert row,'Do not reactivate retired QA identity';return row[0]


def step(key,path,body=None,method='POST',own=False):
    if key not in s:
        s[key]=expect(200,http(method,path,body,s['actor']if own else None,password()if own else None));save()
    return s[key]


def initialize():
    prep.FILE=OUT/'scoped-full-preparation.json';prep.s=json.loads(prep.FILE.read_text(encoding='utf-8'))if prep.FILE.exists()else dict(history=[])
    try:prep.prepare(attempt_rejected=False)
    finally:
        if 'fixture'in prep.s:
            f=prep.s['fixture']
            with oracle_connection()as c:
                q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=f['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=f['role']);c.commit()
        prep.s['history']+=CALLS;prep.save()
    f=prep.s['fixture'];s.update(warehouse_id=f['warehouse_id'],task=prep.s['task'][0]);save()
    with oracle_connection()as c:
        q=c.cursor();q.execute('select FROM_WARE_ID,TO_WARE_ID,STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t',t=s['task']);row=q.fetchone();assert row[:2]==(s['warehouse_id'],s['warehouse_id']);s['warehouses_at_creation']=list(row);save()
        if 'actor'not in s:
            actor='FPR21'+uuid4().hex[:9];pwd=secrets.token_hex(24)
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Scoped full pallet QA','TC03QA',:w,0,1)",a=actor,p=pwd,w=s['warehouse_id'])
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Scoped full pallet QA',1,1)",a=actor)
            for permission in ['warehouse_task_execute','warehouse_task_view','resource_gantt_view','resource_management_view','resource_session_view']:
                q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=permission)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '4'hour,'admin','Reach truck whole pallet scope proof',1)",a=actor,w=str(s['warehouse_id']));c.commit();s['actor']=actor;save()
        q.execute("select RRL_HAS_WRIGHT(:a,'warehouse_task_execute'),RRL_ACCESS_API.allowed(:a,'warehouse_task_execute','WAREHOUSE',:w)from dual",a=s['actor'],w=str(s['warehouse_id']));s['authority']=list(q.fetchone());assert s['authority']==[0,1];save()
    now=datetime.now(ZoneInfo('Europe/Moscow'));tag='FPR21.'+str(s['warehouse_id'])
    shift=step('shift','/api/resources/shifts',dict(shift_code=tag,shift_date=now.date().isoformat(),start_at=(now-timedelta(hours=1)).isoformat(),finish_at=(now+timedelta(hours=3)).isoformat(),ware_id=s['warehouse_id'],status='OPEN'))['id']
    equipment=step('equipment','/api/resources/equipment',dict(equipment_code=tag,equipment_type='REACHTRUCK',equipment_name='Synthetic reach truck QA',ware_id=s['warehouse_id']))['id']
    resource=step('resource','/api/resources',dict(resource_code=tag,resource_name='Synthetic reach truck QA',resource_type='REACHTRUCK',resource_class='WAREHOUSE_EQUIPMENT',equipment_id=equipment,ware_id=s['warehouse_id']))['id']
    step('qualification',f'/api/resources/{resource}/qualifications',dict(task_type='PICKING_MOVE',active=True),'PUT')
    session=step('session','/api/resources/sessions/login',dict(shift_id=shift,resource_id=resource,equipment_id=equipment,operator_user_id=s['actor'],terminal_id='QA_NOT_HARDWARE'))['id']
    s.update(resource_id=resource,equipment_id=equipment,session_id=session);save()


def grant(version,operate,key):
    return step(key,f"/api/tradecase/warehouses/{s['warehouse_id']}/stock/owner-grants",dict(operation_id=s['actor']+'.'+key,expected_version=version,username=s['actor'],owner_id='SNS',can_view=True,can_operate=operate,reason='Qualified full pallet current owner scope'),'PUT')


def move():
    task=s['task'];actor=s['actor'];base=f'/api/warehouse-tasks/{task}';tag='FPR21.'+str(s['warehouse_id'])
    grant(0,True,'owner')
    for action in ['ASSIGN','START']:
        if action not in s:
            if action+'_body'not in s:
                context=expect(200,http('GET',base+'/resource-context?'+urlencode(dict(target=actor)),actor=actor if action=='START'else None,password=password()if action=='START'else None))
                s[action+'_body']=dict(operation_id=tag+'.'+action,action=action,target=actor,expected_assignment_version=context['assignment_version'],expected_task_signature=context['task_signature'],resource_session_id=s['session_id'],resource_id=s['resource_id'],equipment_id=s['equipment_id']);save()
            body=s[action+'_body']
            step(action,base+'/resource-commands',body,own=action=='START')
    if 'complete_body'not in s:
        detail=expect(200,http('GET',base,actor=actor,password=password()))
        s['complete_body']=dict(prep.s['complete_body'],operation_id=tag+'.complete',expected_task_signature=detail['task_signature'],resource_id=s['resource_id'],resource_session_id=s['session_id'],equipment_id=s['equipment_id']);save()
    step('completed',base+'/complete',s['complete_body'],own=True)
    assert expect(200,http('POST',base+'/complete',s['complete_body'],actor,password()))==s['completed']
    if 'shipment_identifier'not in s:s.update(prepare_shipment(prep.s));save()
    if 'bind_body'not in s:
        view=expect(200,http('GET',base+'/full-pallet-shipment',actor=actor,password=password()))
        s['bind_body']=dict(operation_id=tag+'.bind',shipment_identifier=s['shipment_identifier'],scanned_pallet=view['pallet_identifier'],expected_stock_version=view['stock_version']);save()
    if '--before-migration'in sys.argv:
        denied=http('POST',base+'/full-pallet-shipment',dict(s['bind_body'],operation_id=tag+'.bind.before'),actor,password());s['bind_before']=denied;save();assert denied[0]in(403,409),denied
        return
    step('bound',base+'/full-pallet-shipment',s['bind_body'],own=True)
    assert expect(200,http('POST',base+'/full-pallet-shipment',s['bind_body'],actor,password()))==s['bound']


def cleanup():
    actor=s['actor'];w=s['warehouse_id'];url=f'/api/tradecase/warehouses/{w}/stock/owner-grants'
    if 'revoked_replay'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where USERNAME=:a and REVOKED_AT is null',a=actor);c.commit()
        denied=http('POST',f"/api/warehouse-tasks/{s['task']}/full-pallet-shipment",s['bind_body'],actor,password());s['revoked_replay']=denied;save()
        assert denied[0]==403 and denied[1]['detail']['outcome_confirmed']is False and denied[1]['detail']['retry_same_operation_id']is True,denied
    if 'restored_replay'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select count(*)from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:a',a=actor+'.RESTORE')
            if not q.fetchone()[0]:
                q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:id,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Restore current scope for original replay proof',1)",id=actor+'.RESTORE',a=actor,w=str(w));c.commit()
        value=expect(200,http('POST',f"/api/warehouse-tasks/{s['task']}/full-pallet-shipment",s['bind_body'],actor,password()));assert value==s['bound'];s['restored_replay']=value;save()
    step('owner_revoked',url,dict(operation_id=actor+'.cleanup',expected_version=1,username=actor,owner_id='SNS',can_view=False,can_operate=False,reason='Retire full pallet QA owner scope'),'PUT')
    step('logout',f"/api/resources/sessions/{s['session_id']}/logout",dict(reason='Full pallet verification complete'))
    step('qualification_revoked',f"/api/resources/{s['resource_id']}/qualifications",dict(task_type='PICKING_MOVE',active=False),'PUT')
    with oracle_connection()as c:
        q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where USERNAME=:a and REVOKED_AT is null',a=actor);c.commit()
        q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS l on l.CELL=r.CELL where l.WARE_ID=:w',w=w);s['stock']=list(q.fetchone());assert s['stock']==[10,10]
    s['status']='PASS';save()


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        if 'session_id'not in s:initialize()
        else:
            prep.FILE=OUT/'scoped-full-preparation.json';prep.s=json.loads(prep.FILE.read_text(encoding='utf-8'))
        if 'bound'not in s:move()
        if '--before-migration'not in sys.argv:cleanup()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
    print(json.dumps({k:s.get(k)for k in ['warehouse_id','task','actor','authority','stock','status','bind_before']}))
