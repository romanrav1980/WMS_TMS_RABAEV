"""PREPARED ONLY: root-reviewed GROUP-only CASE1138 caller-rollback quantity proof.
Default --plan does not import Oracle. No StockPosting.post and no quantity commit exists.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'reports/retailcase/2026-10-15/case-resource-commands'
JOURNAL=FOLDER/'group-quantity-journal.json'
ACTOR='CRES15.OP';ROLE='CRES15.CASE.EXEC';GROUP='CRES15.GQP.WARE'
GROUP_ASSIGN='CRES15.GQP.ASSIGN';OPERATION='CRES15.GQP.PICK.ROLLBACK'
PARENT='REUSE.RETURN:e6c16d0bbd';CHILD='CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1'
DEADLINE=datetime(2026,10,15,15,25,tzinfo=timezone.utc)
SQL_CONTEXT={"case":1138,"line":1140,"wave":569,"resource":59,"session":55,"warehouse":13583852}


def save(journal:dict[str,Any])->None:
    FOLDER.mkdir(parents=True,exist_ok=True);temporary=JOURNAL.with_suffix('.json.next')
    with temporary.open('w',encoding='utf-8',newline='\n')as stream:
        json.dump(journal,stream,indent=2,ensure_ascii=False,default=str);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,JOURNAL)


def normalized(value:Any)->Any:
    return json.loads(json.dumps(value,default=str,sort_keys=True))


def grants(g:Any)->list[dict[str,Any]]:
    return g.fetch_all("""select a.ASSIGNMENT_ID,a.USERNAME,a.ROLE_ID,a.SCOPE_KIND,a.SCOPE_ID,a.MEMBERSHIP,a.SNAPSHOT_VERSION,a.VERSION_NO,
      to_char(a.VALID_FROM at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')VALID_FROM,
      to_char(a.VALID_UNTIL at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')VALID_UNTIL
      from RRL_ACCESS_ASSIGNMENT a join RRL_ACCESS_ROLE r on r.ROLE_ID=a.ROLE_ID
      where a.USERNAME=:a and a.REVOKED_AT is null and a.VALID_FROM<=systimestamp
      and(a.VALID_UNTIL is null or a.VALID_UNTIL>systimestamp)and r.ACTIVE=1 order by a.ASSIGNMENT_ID""",{'a':ACTOR})


def role(g:Any)->dict[str,Any]:
    rows=g.fetch_all('select ROLE_ID,TITLE,ACTIVE,VERSION_NO from RRL_ACCESS_ROLE where ROLE_ID=:r',{'r':ROLE})
    assert len(rows)==1 and rows[0]['active']==1 and rows[0]['version_no']==3,'Role changed/retired: never edit/reactivate it'
    return dict(row=rows[0],permissions=g.fetch_all('select PERMISSION from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:r order by PERMISSION',{'r':ROLE}))


def fixture(g:Any,strict:bool=True)->dict[str,Any]:
    users=g.fetch_all('select ID,DELETED,USER_GROUP,WARE_ID from RUSERS where ID=:a',{'a':ACTOR})
    assert len(users)==1 and(users[0]['deleted']or 0)==0,'CRES actor retired: stop, never reactivate'
    current=role(g)
    task=g.fetch_all('select STATUS,ASSIGNED_TO,ASSIGNED_RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,CONTENT_VERSION,ASSIGNMENT_VERSION,PICKED_QTY,SSCC,STARTED_AT_INSTANT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1138')
    assert len(task)==1 and task[0]['status']not in('CANCELLED','DONE','CLOSED'),'CRES CASE retired/closed'
    if strict:
        t=task[0];assert t['assigned_to']==ACTOR and t['assigned_resource_id']==59 and t['resource_session_id']==55 and t['picked_qty']==0
        assert t['status']=='IN_PROGRESS' and t['sscc']=='090000000000009028'
        assert g.fetch_all("select STATUS,OPERATOR_USER_ID,RESOURCE_ID from RRL_RESOURCE_SESSION where SESSION_ID=55")==[{'status':'ACTIVE','operator_user_id':ACTOR,'resource_id':59}]
        assert not g.fetch_all("select SESSION_ID from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=1138 and STATE in('OPEN','BLOCKED','HOLD')")
    return dict(user=users,role=current,task=task)


def snapshot(g:Any)->dict[str,Any]:
    result=dict(fixture=fixture(g),line=g.fetch_all('select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,STATUS,CELL_CODE,ARTICUL,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=1140'),
      lineage=g.fetch_all('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,p.STOCK_ORIGIN_UID,p.CREATED_BY_STOCK_OP from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.UID_POLETA in(:p,:c)order by r.UID_POLETA,r.CELL',{'p':PARENT,'c':CHILD}),
      reservations=g.fetch_all("select RESERVATION_ID,UID_PALLET,CELL,BASE_QTY,STATUS from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=569 order by RESERVATION_ID fetch first 21 rows only"),
      events=g.fetch_all('select CASE_PICK_EVENT_ID,EVENT_TYPE,CREATED_BY from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=1138 order by CASE_PICK_EVENT_ID fetch first 201 rows only'),
      carrier=g.fetch_all('select LOT_UID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,CREATED_OPERATION from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1138 order by LOT_UID fetch first 21 rows only'),
      resource_events=g.fetch_all('select EVENT_ID,EVENT_TYPE,EVENT_BY from RRL_RESOURCE_FACT_EVENT where TASK_ID=1138 order by EVENT_ID fetch first 201 rows only'),
      resource_receipts=g.fetch_all('select OPERATION_ID,SOURCE_SHA256,OUTCOME from RRL_CASE_RESOURCE_COMMAND where CASE_PICK_TASK_ID=1138 order by OPERATION_ID fetch first 101 rows only'),
      warehouse_object=g.fetch_all("select KIND,OBJECT_ID,TITLE,PARENT_KIND,PARENT_ID,ACTIVE,VERSION_NO from RRL_ACCESS_OBJECT where KIND='WAREHOUSE'and OBJECT_ID='13583852'"))
    assert len(result['line'])==1 and len(result['lineage'])<=10 and len(result['reservations'])<=20 and len(result['events'])<=200 and len(result['carrier'])<=20 and len(result['resource_events'])<=200 and len(result['resource_receipts'])<=100
    assert result['line'][0]['case_pick_task_id']==1138 and result['line'][0]['planned_qty']==1 and result['line'][0]['picked_qty']==0
    assert sum(x['remain']for x in result['lineage'])==24 and sum(x['hard_reserved_base']for x in result['lineage'])==1
    assert all(x['stock_origin_uid']=='300000034518661218'for x in result['lineage'])
    assert not result['carrier'];return normalized(result)


def no_orphans(g:Any)->None:
    checks=[('RRL_STOCK_OPERATION','OPERATION_ID',OPERATION),('RRL_STOCK_OP_CLOCK','OPERATION_ID',OPERATION),
      ('RRL_EVENT_OUTBOX','IDEMPOTENCY_KEY','STOCK:'+hashlib.sha256(OPERATION.encode()).hexdigest().upper()),
      ('RRL_PALLETS','CREATED_BY_STOCK_OP',OPERATION),('RRL_CASE_CARRIER_LOT','CREATED_OPERATION',OPERATION),
      ('RRL_ASSEMBLY_STEP_USE','STOCK_OPERATION_ID',OPERATION)]
    for table,key,value in checks:assert not g.fetch_all('select '+key+' from '+table+' where '+key+'=:v fetch first 1 rows only',{'v':value}),('Unexpected durable proof history',table)


def frozen_acl(name:str,kind:str,payload:dict[str,Any])->dict[str,Any]:
    from app.modules.platform.api.metadata_inputs import Command,normalize
    command=normalize(Command(operation_id='CRES15.GQP.'+name,command_type=kind,payload=payload),'ACCESS')
    wire=json.dumps(command,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return dict(command=command,wire=wire,sha256=hashlib.sha256(wire.encode()).hexdigest())


def command_plan(original:list[dict[str,Any]],now:datetime)->dict[str,Any]:
    commands={};members=[dict(kind='WAREHOUSE',object_id='13583852')]
    commands['group_create']=frozen_acl('GROUP.CREATE','GROUP_SAVE',dict(group_id=GROUP,title='Private GROUP quantity caller-rollback proof',member_kind='WAREHOUSE',members=members,active=True,expected_version=0))
    until=min(now+timedelta(minutes=15),DEADLINE)
    commands['group_assign']=frozen_acl('GROUP.ASSIGN','ASSIGN',dict(assignment_id=GROUP_ASSIGN,username=ACTOR,role_id=ROLE,scope_kind='GROUP',scope_id=GROUP,membership='CURRENT',snapshot_version=None,valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=until.isoformat(),reason='Root-reviewed private CASE GROUP quantity proof; physical effects caller rollback',expected_version=0))
    for item in original:
        suffix='SELF'if item['scope_kind']=='SELF'else'WARE'
        commands['revoke_'+suffix]=frozen_acl('ORIG.REVOKE.'+suffix,'REVOKE',dict(assignment_id=item['assignment_id'],expected_version=int(item['version_no']),reason='Isolate GROUP-only authority; restore equivalent scope through a NEW assignment'))
        payload={k:item[k]for k in('role_id','scope_kind','scope_id','membership','snapshot_version','valid_from','valid_until')}
        payload.update(assignment_id='CRES15.GQP.RESTORE.'+suffix,username=ACTOR,expected_version=0,reason='Restore exact original effective scope and validity; revoked IDs remain revoked')
        commands['restore_'+suffix]=frozen_acl('RESTORE.'+suffix,'ASSIGN',payload)
    commands['group_revoke']=frozen_acl('GROUP.REVOKE','REVOKE',dict(assignment_id=GROUP_ASSIGN,expected_version=1,reason='Retire only private GROUP proof assignment; preserve history'))
    commands['group_retire']=frozen_acl('GROUP.RETIRE','GROUP_SAVE',dict(group_id=GROUP,title='Retired private GROUP quantity proof',member_kind='WAREHOUSE',members=[],active=False,expected_version=1))
    return commands


def prepare(g:Any)->dict[str,Any]:
    assert not JOURNAL.exists(),'Existing journal: use --restore-only; never fork/rebuild frozen operations'
    assert datetime.now(timezone.utc)<DEADLINE-timedelta(minutes=2),'Too late for an isolated ACL window'
    baseline=snapshot(g);no_orphans(g);original=grants(g)
    assert len(original)==2 and {x['assignment_id']for x in original}=={'CRES15.SELF','CRES15.WARE'} and {x['scope_kind']for x in original}=={'SELF','WAREHOUSE'} and all(x['role_id']==ROLE and x['version_no']==1 and x['membership']=='CURRENT'and x['snapshot_version']is None for x in original)
    assert next(x for x in original if x['scope_kind']=='WAREHOUSE')['scope_id']=='13583852'
    assert not g.fetch_all("select GROUP_ID from RRL_ACCESS_GROUP where GROUP_ID=:i",{'i':GROUP})
    assert not g.fetch_all('select ASSIGNMENT_ID from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:i',{'i':GROUP_ASSIGN})
    assert not g.fetch_all("select OPERATION_ID from RRL_PLATFORM_COMMAND where DOMAIN='ACCESS'and OPERATION_ID like 'CRES15.GQP.%'fetch first 1 rows only")
    now=datetime.now(timezone.utc);commands=command_plan(original,now)
    for identity in('CRES15.GQP.RESTORE.SELF','CRES15.GQP.RESTORE.WARE'):
        assert not g.fetch_all('select ASSIGNMENT_ID from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:i',{'i':identity})
    line=baseline['line'][0];sscc=baseline['fixture']['task'][0]['sscc']
    from app.modules.inventory.contracts_stock import StockCommand
    stock=StockCommand(OPERATION,'CASE_PICK_CONFIRM',ACTOR,(),{'case_task_id':1138,'case_line_id':1140},metadata={'fact_qty':'1','scan_cell':line['cell_code'],'scan_product':line['articul'],'scan_container':sscc,'offline_event_id':None}).canonical_json()
    journal=dict(prepared_at=now.isoformat(),status='FROZEN_BEFORE_ANY_ACL_MUTATION',prepared_only=False,baseline=baseline,original_grants=normalized(original),commands=commands,stock_wire=stock,stock_sha256=hashlib.sha256(stock.encode()).hexdigest(),steps={},history=[],stock_committed=False)
    validate_journal(journal);save(journal);return journal


def validate_journal(journal:dict[str,Any])->None:
    stamp=datetime.fromisoformat(journal['prepared_at']);assert stamp.utcoffset()is not None
    assert datetime(2026,10,15,14,55,tzinfo=timezone.utc)<=stamp<DEADLINE-timedelta(minutes=2)
    original=journal['original_grants'];assert len(original)==2
    assert {x['assignment_id']for x in original}=={'CRES15.WARE','CRES15.SELF'}
    for item in original:
        suffix='SELF'if item['assignment_id']=='CRES15.SELF'else'WAREHOUSE'
        assert item['username']==ACTOR and item['role_id']==ROLE and item['scope_kind']==suffix
        assert item['scope_id']==(None if suffix=='SELF'else'13583852')
        assert item['membership']=='CURRENT'and item['snapshot_version']is None and item['version_no']==1
        begins=datetime.fromisoformat(item['valid_from']);ends=datetime.fromisoformat(item['valid_until'])
        assert begins.utcoffset()is not None and ends.utcoffset()is not None and begins<=stamp<ends
    assert journal['commands']==command_plan(original,stamp),'Frozen ACL commands retargeted or changed'
    baseline=journal['baseline'];assert baseline['fixture']['role']['row']['role_id']==ROLE
    assert baseline['fixture']['role']['row']['version_no']==3 and baseline['fixture']['role']['row']['active']==1
    task=baseline['fixture']['task'][0];line=baseline['line'][0]
    assert task['assigned_to']==ACTOR and task['assigned_resource_id']==59 and task['resource_session_id']==55 and task['picked_qty']==0
    assert task['sscc']=='090000000000009028'and line['case_pick_task_id']==1138 and line['case_pick_line_id']==1140
    assert line['cell_code']=='QIPcdbf4c0962'and line['articul']=='REUSE.QA:cdbf4c0962'and line['planned_qty']==1 and line['picked_qty']==0
    from app.modules.inventory.contracts_stock import StockCommand
    expected=StockCommand(OPERATION,'CASE_PICK_CONFIRM',ACTOR,(),{'case_task_id':1138,'case_line_id':1140},metadata={'fact_qty':'1','scan_cell':'QIPcdbf4c0962','scan_product':'REUSE.QA:cdbf4c0962','scan_container':'090000000000009028','offline_event_id':None}).canonical_json()
    assert journal['stock_wire']==expected and journal['stock_sha256']==hashlib.sha256(expected.encode()).hexdigest(),'Frozen Stock request retargeted'


def isolated_cursor(cursor:Any)->None:
    cursor.execute("""select a.ASSIGNMENT_ID,a.SCOPE_KIND,a.SCOPE_ID from RRL_ACCESS_ASSIGNMENT a join RRL_ACCESS_ROLE r on r.ROLE_ID=a.ROLE_ID
     where a.USERNAME=:a and a.REVOKED_AT is null and a.VALID_FROM<=systimestamp and(a.VALID_UNTIL is null or a.VALID_UNTIL>systimestamp)and r.ACTIVE=1 order by a.ASSIGNMENT_ID""",a=ACTOR)
    assert cursor.fetchall()==[(GROUP_ASSIGN,'GROUP',GROUP)],'Physical transaction is not GROUP-only'
    cursor.execute("select RRL_HAS_WRIGHT(:a,'case_pick_execute'),RRL_CASE_TASK_ACCESS.has_current_scoped_execute(1138,:a),RRL_CASE_TASK_ACCESS.scoped_executor(1138,:a)from dual",a=ACTOR)
    assert cursor.fetchone()==(0,1,1),'GROUP execution admission or legacy-flat isolation changed'


def persist(journal:dict[str,Any],strict:bool)->None:
    try:save(journal)
    except OSError as error:
        if strict:raise
        journal.setdefault('logging_errors',[]).append(str(error)[:300])


def run_acl(g:Any,journal:dict[str,Any],name:str,compensation:bool=False)->None:
    from app.modules.platform.public import AccessMetadataService
    frozen=journal['commands'][name]
    journal['history'].append(dict(step=name,state='ATTEMPT',at=datetime.now(timezone.utc).isoformat()));persist(journal,not compensation)
    result=AccessMetadataService(g).command('admin',frozen['command'])
    journal['steps'][name]=normalized(result);journal['history'].append(dict(step=name,state='RECEIPT_CONFIRMED',at=datetime.now(timezone.utc).isoformat()));persist(journal,not compensation)


def isolated(g:Any)->None:
    active=grants(g);assert len(active)==1 and active[0]['assignment_id']==GROUP_ASSIGN and active[0]['scope_kind']=='GROUP'and active[0]['scope_id']==GROUP
    rows=g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute')FLAT,RRL_CASE_TASK_ACCESS.has_current_scoped_execute(1138,:a)CURRENT_SCOPE,RRL_CASE_TASK_ACCESS.scoped_executor(1138,:a)EXECUTOR from dual",{'a':ACTOR})
    assert rows==[{'flat':0,'current_scope':1,'executor':1}],rows
    assert role(g)['row']['version_no']==3


def stock_trial(g:Any,journal:dict[str,Any])->None:
    import oracledb
    from app.db import oracle_connection
    from app.modules.platform.public import read_oracle_json
    assert snapshot(g)==journal['baseline'];no_orphans(g);isolated(g)
    wire=journal['stock_wire'];assert hashlib.sha256(wire.encode()).hexdigest()==journal['stock_sha256']
    assert json.loads(wire)['operation_id']==OPERATION and json.loads(wire)['actor']==ACTOR
    with oracle_connection()as connection:
        cursor=connection.cursor()
        try:
            cursor.execute("select dbms_transaction.local_transaction_id(false)from dual");assert cursor.fetchone()[0]is None,'Fresh clean physical transaction required'
            output=cursor.var(oracledb.DB_TYPE_CLOB);cursor.callproc('RRL_STOCK_POSTING_API.prepare_command',[wire,ACTOR,output])
            assert output.getvalue()is None,'Orphan/historical APPLIED receipt must not satisfy a fresh execution proof'
            isolated_cursor(cursor)
            cursor.callproc('RRL_STOCK_POSTING_API.execute_prepared',[output]);result=read_oracle_json(output.getvalue())
            isolated_cursor(cursor)
            cursor.execute("select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:o",o=OPERATION);assert cursor.fetchone()==('APPLIED',)
            cursor.execute('select PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1138');assert cursor.fetchone()==(1,)
            cursor.execute('select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=1140');assert cursor.fetchone()==(1,)
            cursor.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u',u=PARENT);assert cursor.fetchone()==(22,0)
            cursor.execute('select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1138 and CREATED_OPERATION=:o',o=OPERATION);assert cursor.fetchone()[0]>0
            cursor.execute('select count(*)from RRL_STOCK_OP_CLOCK where OPERATION_ID=:o',o=OPERATION);assert cursor.fetchone()==(1,)
            cursor.execute('select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:k',k='STOCK:'+hashlib.sha256(OPERATION.encode()).hexdigest().upper());assert cursor.fetchone()==(1,)
            journal['inside_rolledback_stock_result']=normalized(result)
        finally:
            try:connection.rollback()
            finally:cursor.callproc('RRL_STOCK_POSTING_API.reset_connection')
    assert snapshot(g)==journal['baseline'];no_orphans(g)
    journal['quantity_rollback']='PASS exact CASE/line/both UID lineage/reservations/events/resource receipts; no op/clock/outbox/newlots/carrier/STEP_USE';save(journal)


def effective(rows:list[dict[str,Any]])->list[str]:
    keys=('role_id','scope_kind','scope_id','membership','snapshot_version','valid_from','valid_until')
    return sorted(json.dumps({k:row[k]for k in keys},sort_keys=True,default=str)for row in rows)


def original_source(g:Any,item:dict[str,Any])->dict[str,Any]:
    row=g.fetch_all("""select ASSIGNMENT_ID,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,SNAPSHOT_VERSION,VERSION_NO,REVOKED_AT,
     to_char(VALID_FROM at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')VALID_FROM,
     to_char(VALID_UNTIL at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')VALID_UNTIL
     from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:i and USERNAME=:a""",{'i':item['assignment_id'],'a':ACTOR})
    assert len(row)==1 and effective(row)==effective([item]),'Original assignment identity/scope/validity changed'
    return row[0]


def restore(g:Any,journal:dict[str,Any])->None:
    validate_journal(journal);errors=[];restore_allowed=False
    try:fixture(g,strict=False);restore_allowed=True
    except Exception as error:errors.append(dict(step='fixture_restore_guard',error=str(error)[:700]))
    if restore_allowed:
        for item in journal['original_grants']:
            suffix='SELF'if item['scope_kind']=='SELF'else'WARE'
            try:
                row=original_source(g,item)
                if row['revoked_at']is not None:
                    assert row['version_no']==item['version_no']+1,'Concurrent original revoke/version change: manual reconciliation'
                    command=journal['commands']['revoke_'+suffix]
                    receipt=g.fetch_all("select ACTOR,PAYLOAD_HASH from RRL_PLATFORM_COMMAND where DOMAIN='ACCESS'and OPERATION_ID=:o",{'o':command['command']['operation_id']})
                    assert receipt==[{'actor':'admin','payload_hash':command['sha256']}],'Original revoke was not this proof command'
                    run_acl(g,journal,'restore_'+suffix,True)
            except Exception as error:errors.append(dict(step='restore_'+suffix,error=str(error)[:700]))
    # Always attempt private cleanup, including when actor/task/role was retired or logging failed.
    for name,table,column,identity in [('group_revoke','RRL_ACCESS_ASSIGNMENT','ASSIGNMENT_ID',GROUP_ASSIGN),('group_retire','RRL_ACCESS_GROUP','GROUP_ID',GROUP)]:
        try:
            try:exists=bool(g.fetch_all('select '+column+' from '+table+' where '+column+'=:i',{'i':identity}))
            except Exception:exists=True  # Unknown state still attempts the already-fsynced bounded canonical compensation.
            if exists:run_acl(g,journal,name,True)
        except Exception as error:errors.append(dict(step=name,error=str(error)[:700]))
    if errors:
        journal.update(status='RESTORE_REQUIRED_STOP',restore_errors=errors);persist(journal,False);raise RuntimeError('ACL restoration incomplete; same --restore-only journal, no new IDs or reactivation')
    assert effective(grants(g))==effective(journal['original_grants']),'Original effective scope/validity not restored'
    assert normalized(role(g))==journal['baseline']['fixture']['role'],'Role version/rights changed: never edit them'
    journal['acl_restored']='PASS equivalent WARE/SELF through new IDs; private GROUP retired; history retained';persist(journal,False)


def main()->None:
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group();mode.add_argument('--plan',action='store_true');mode.add_argument('--execute-reviewed',action='store_true');mode.add_argument('--restore-only',action='store_true');args=parser.parse_args()
    if not args.execute_reviewed and not args.restore_only:
        print(json.dumps(dict(status='PREPARED_NOT_EXECUTED',fixture=SQL_CONTEXT,group=GROUP,stock_operation=OPERATION,requires='Root review and exclusive UI ACL window; all physical effects caller rollback',journal=str(JOURNAL),quantity_commit=False)));return
    assert os.environ.get('CRES15_GROUP_QUANTITY_ROOT_REVIEWED')=='1'and os.environ.get('CRES15_UI_ACL_WINDOW_RELEASED')=='1','Explicit root review and exclusive UI/cleanup window required'
    sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.oracle_gateway import OracleGateway
    g=OracleGateway()
    if args.restore_only:
        journal=json.loads(JOURNAL.read_text(encoding='utf-8'));validate_journal(journal);restore(g,journal);no_orphans(g);journal['status']='ACL_RESTORED_ONLY';save(journal);return
    journal=prepare(g);failure=None
    try:
        for name in('group_create','group_assign','revoke_SELF','revoke_WARE'):run_acl(g,journal,name)
        isolated(g);stock_trial(g,journal)
    except Exception as error:failure=str(error)[:1000];journal['proof_error']=failure;save(journal)
    finally:restore(g,journal)
    assert snapshot(g)==journal['baseline'];no_orphans(g)
    journal['status']='PASS'if failure is None else'FAILED_PROOF_ACL_RESTORED';save(journal)
    if failure:raise RuntimeError(failure)
    print('GROUP_ONLY_CASE_PICK_CALLER_ROLLBACK_PASS_METADATA_HISTORY_RETAINED')


if __name__=='__main__':main()
