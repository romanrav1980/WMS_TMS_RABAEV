"""Live scoped read of committed shipment queue summaries; never claim or send an outbox event."""
import json
import os
import re
import secrets
import sys
from uuid import uuid4
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import live_shipment_events as p
qa=p.qa;s=p.s


def main():
    assert s['phase']=='CLOSED'
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[\x60,)\s]',(qa.ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    w=s['fixture']['warehouse_id'];base=f'/api/tradecase/warehouses/{w}/trips/'
    actor='SD26'+uuid4().hex[:10];password=secrets.token_hex(24);r=dict(status='STARTED',actor=actor)
    def read(trip,qty,user=None,pwd=None):
        result=qa.expect(200,qa.http('GET',base+trip+'/execution',actor=user,password=pwd))
        items=result['shipment_messages'];assert len(items)==2 and not result['shipment_messages_has_more']
        assert {x['system_code']for x in items}=={'SAP','SKM'}and all(x['quantity']==str(qty)for x in items)
        assert all('units'not in x and 'payload'not in x for x in items)
        return result
    before=qa.stock()
    try:
        r['admin']={trip:read(trip,qty)for trip,qty in [('T60',600),('T20',200)]}
        with qa.oracle_connection()as c:
            q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Shipment summary viewer','SD26QA',1,0,1)",a=actor,p=password)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Shipment summary viewer',1,1)",a=actor)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_view')",a=actor);c.commit()
        r['unassigned']=qa.expect(403,qa.http('GET',base+'T60/execution',actor=actor,password=password))
        with qa.oracle_connection()as c:
            q=c.cursor();q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Owned shipment summary read',1)",a=actor,w=str(w));c.commit()
        r['scoped']={trip:read(trip,qty,actor,password)for trip,qty in [('T60',600),('T20',200)]}
        for trip in r['admin']:assert r['admin'][trip]['shipment_messages']==r['scoped'][trip]['shipment_messages']
        r['foreign']=qa.expect(403,qa.http('GET',(base+'T60/execution').replace(str(w),str(w+1)),actor=actor,password=password))
        with qa.oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        r['revoked']=qa.expect(403,qa.http('GET',base+'T60/execution',actor=actor,password=password))
        for denial in ['unassigned','foreign','revoked']:assert 'shipment_messages'not in r[denial]
        for _ in range(4):read('T60',600)
        assert qa.stock()==before==(0,0,0)
        r['status']='PASS';print('Actual HTTP shipment summaries, warehouse assignment, foreign scope and revoke: PASS')
    except Exception as exc:r['status']='FAIL';r['error']=str(exc);raise
    finally:
        with qa.oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a and REVOKED_AT is null',a=actor)
            q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='SD26QA'",a=actor);c.commit()
        r['actor_retired']=True;r['http']=qa.CALLS;(qa.OUT/'delivery-read-http.json').write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')


if __name__=='__main__':main()
