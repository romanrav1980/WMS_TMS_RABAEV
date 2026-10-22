"""201 synthetic visits rolled back; temporary QA access retired; native filtering before page limit."""
from hashlib import sha256
import json
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb

WARE=220793322
TAG='YV23'+uuid4().hex[:10]
report=dict(status='FAIL',basis='Synthetic documents/visits rolled back; temporary QA and owner grant retired; native functions',count=201)
actor_created=False
grant_version=0

def wire(q,value):
    v=q.var(oracledb.DB_TYPE_CLOB);v.setvalue(0,json.dumps(value,sort_keys=True,separators=(',',':')));return v

def read(v):
    return json.loads(v.read()if hasattr(v,'read')else v)

with oracle_connection()as c:
    q=c.cursor()
    try:
        q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        q.execute('select NAME from RRL_WARES where ID=:w',w=WARE);assert q.fetchone()[0].startswith('TRADECASE QA ')
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Yard visibility QA','TC03QA',:w,0,1)",a=TAG,p=secrets.token_hex(24),w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Yard visibility QA',1,1)",a=TAG)
        for permission in ('tradecase_view','tradecase_yard_operate'):
            q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=TAG,p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Yard visible limit acceptance',1)",a=TAG,w=str(WARE))
        c.commit();actor_created=True
        grant=dict(operation_id=TAG+'.grant',command_type='GRANT',username=TAG,owner_id='SNS',can_view=True,can_operate=True,expected_version=0,reason='Owned rolled-back visibility fixture')
        grant['business_hash']=sha256(json.dumps(grant,sort_keys=True).encode()).hexdigest()
        grant['payload_hash']=sha256(json.dumps(grant,sort_keys=True).encode()).hexdigest()
        out=q.var(oracledb.DB_TYPE_CLOB)
        q.callproc('RRL_TRADE_STOCK_API.execute_command',[WARE,'admin',wire(q,grant),wire(q,[]),out])
        c.commit();grant_version=1
        def doc(kind,key,body):
            text=json.dumps(body)
            q.execute("insert into RRL_TRADE_DOCUMENT(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)values(:w,:k,:id,'TC03.SAP',1,:h,:body,'ACCEPTED','admin')",w=WARE,k=kind,id=key,h=sha256(text.encode()).hexdigest(),body=text)
        for owner in ('SNS','BLC'):doc('ORDER',TAG+'.'+owner,dict(lines=[dict(line_id='1',source_owner_id=owner)]))
        q.execute("select to_char(systimestamp,'YYYY-MM-DD\"T\"HH24:MI:SSTZH:TZM')from dual");planned=q.fetchone()[0]
        visible=None
        for i in range(201):
            trip=TAG+'.T'+str(i)
            doc('TRIP',trip,dict(orders=[dict(order_id=TAG+('.SNS'if i==200 else '.BLC'),line_id='1')]))
            q.callproc('RRL_YARD_VISIT_API.command',[WARE,wire(q,dict(operation_id=TAG+'.expect.'+str(i),action='EXPECT',trip_id=trip,planned_arrival_at=planned)),'admin',out])
            if i==200:visible=read(out.getvalue())['visit_id']
        start=time.perf_counter()
        visits=read(q.callfunc('RRL_YARD_VISIT_API.visits',oracledb.DB_TYPE_CLOB,[WARE,TAG,1]))
        report['visits_ms']=round((time.perf_counter()-start)*1000,2)
        assert [v['visit_id']for v in visits['visits']]==[visible],visits
        q.execute("select to_char(systimestamp-interval '1'hour,'YYYY-MM-DD\"T\"HH24:MI:SSTZH:TZM'),to_char(systimestamp+interval '1'hour,'YYYY-MM-DD\"T\"HH24:MI:SSTZH:TZM')from dual")
        a,z=q.fetchone();start=time.perf_counter()
        history=read(q.callfunc('RRL_YARD_VISIT_API.history',oracledb.DB_TYPE_CLOB,[WARE,TAG,a,z]))
        report['history_ms']=round((time.perf_counter()-start)*1000,2)
        own=[v for v in history['visits']if str(v['trip_id']).startswith(TAG)]
        assert len(own)==1 and own[0]['visit_id']==visible,own
        assert '.BLC'not in json.dumps([visits,history])
        report.update(status='PASS',visible_visit=visible,checks=['200 hidden visits cannot displace the visible 201st visit','History contains only the visible own visit'])
    finally:
        c.rollback()
        if actor_created:
            if grant_version:
                grant.update(operation_id=TAG+'.grant.retire',can_view=False,can_operate=False,expected_version=grant_version)
                grant['business_hash']=sha256(json.dumps(grant,sort_keys=True).encode()).hexdigest()
                grant['payload_hash']=sha256(json.dumps(grant,sort_keys=True).encode()).hexdigest()
                q.callproc('RRL_TRADE_STOCK_API.execute_command',[WARE,'admin',wire(q,grant),wire(q,[]),out]);c.commit()
            q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=TAG);c.commit()
        for table,column in [('RRL_TRADE_DOCUMENT','EXTERNAL_ID'),('RRL_YARD_VISIT_EVENT','OPERATION_ID')]:
            q.execute(f'select count(*)from {table} where {column} like :tag',tag=TAG+'%');assert q.fetchone()==(0,)
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
        report['rolled_back']=True
        report['qa_retired']=actor_created
        path=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T10'/f'{TAG}.json'
        path.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(dict(status=report['status'],evidence=str(path))))
