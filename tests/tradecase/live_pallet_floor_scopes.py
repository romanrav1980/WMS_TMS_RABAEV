"""Declare the retained stock pallet type with a warehouse role; retire QA access."""
import json
import os
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
import oracledb

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T11';OUT.mkdir(parents=True,exist_ok=True)
FILE=OUT/'pallet-floor-scope.json';s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(history=[])


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def password():
    with oracle_connection()as c:
        q=c.cursor();q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=s['actor']);row=q.fetchone();assert row,'Never reactivate QA';return row[0]


def own(method,body=None,uid=None):
    return http(method,'/api/inventory/pallet-floor-types'+('?identifier='+(uid or s['uid'])if method=='GET'else''),body,s['actor'],password())


def grant(key,version,view,operate):
    if key not in s:
        s[key]=expect(200,http('PUT',f"/api/tradecase/warehouses/{s['warehouse_id']}/stock/owner-grants",dict(operation_id=s['actor']+'.'+key,expected_version=version,username=s['actor'],owner_id='SNS',can_view=view,can_operate=operate,reason='Warehouse role physical carrier declaration proof')));save()


def prepare():
    assert 'actor'not in s,'Review retained fixture'
    f=json.loads((ROOT/'runtime/test-evidence/tradecase/2026-10-21/T03/factory-box-219023232.json').read_text(encoding='utf-8'))['fixture']
    with oracle_connection()as c:
        q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=f['warehouse_id']);assert q.fetchone()==('TRADECASE QA 89af0087',)
        q.execute('select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and REMAIN>0',p=f['pallet']);rows=q.fetchall();assert len(rows)==1 and rows[0][1:]==(5,0),rows
        actor='PF22'+uuid4().hex[:10];pwd=secrets.token_hex(24)
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Scoped carrier QA','TC03QA',222823304,0,1)",a=actor,p=pwd)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Scoped carrier QA',1,1)",a=actor)
        q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'stock_posting_shipping')",a=actor)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '4'hour,'admin','Physical carrier role proof',1)",a=actor,w=str(f['warehouse_id']));c.commit()
        s.update(actor=actor,warehouse_id=f['warehouse_id'],uid=f['pallet'],cell=rows[0][0]);save()
        q.execute("select RRL_HAS_WRIGHT(:a,'stock_posting_shipping'),RRL_ACCESS_API.allowed(:a,'stock_posting_shipping','WAREHOUSE',:w)from dual",a=actor,w=str(s['warehouse_id']));s['authority']=list(q.fetchone());assert s['authority']==[0,1];save()
    grant('owner',0,True,True)
    with oracle_connection()as c:
        q=c.cursor()
        try:q.callfunc('RRL_PALLET_FLOOR_READ.scope_warehouse',int,[s['uid'],s['actor']]);raise AssertionError('Before migration role accepted')
        except oracledb.DatabaseError as exc:assert exc.args[0].code==20882;s['before']=str(exc).split('\n')[0];save()


def verify():
    if 'declared'not in s:
        v=expect(200,own('GET'));s['preview']=v
        s.setdefault('body',dict(operation_id=s['actor']+'.floor',identifier=s['uid'],pallet_type_id=1,expected_version=v['version'],scan_pallet=s['uid'],scan_cell=s['cell'],evidence_reference='SYNTHETIC_QA_PHYSICAL_CARRIER_TYPE'));save()
        s['declared']=expect(200,own('POST',s['body']));save()
    assert expect(200,own('POST',s['body']))==s['declared']
    expect(409,own('POST',dict(s['body'],pallet_type_id=2)))
    expect(409,own('POST',dict(s['body'],operation_id=s['actor']+'.stale')))
    expect(403,own('GET',uid='690000000237860173'))
    grant('owner_read_only',1,True,False)
    denied=own('POST',s['body']);s['owner_denied']=denied;save();assert denied[0]==403 and denied[1]['detail']['outcome_confirmed']is False
    expect(403,own('GET'))
    grant('owner_restored',2,True,True)
    assert expect(200,own('POST',s['body']))==s['declared']
    if 'warehouse_denied'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=s['actor']);c.commit()
        s['warehouse_denied']=own('POST',s['body']);save();assert s['warehouse_denied'][0]==403
    if 'warehouse_restored'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:id,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Restore original receipt verification',1)",id=s['actor']+'.RESTORE',a=s['actor'],w=str(s['warehouse_id']));c.commit()
        s['warehouse_restored']=True;save()
    assert expect(200,own('POST',s['body']))==s['declared']
    grant('owner_retired',3,False,False)
    with oracle_connection()as c:
        q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=s['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where USERNAME=:a and REVOKED_AT is null',a=s['actor']);c.commit()
        q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse_id']);s['stock']=list(q.fetchone());assert s['stock']==[10,0]
    s['status']='PASS';save()


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:prepare()if '--prepare'in sys.argv else verify()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
    print(json.dumps({k:s.get(k)for k in ['actor','authority','before','stock','status']}))
