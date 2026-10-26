"""Read the saved 80/80/60/20 case with scoped document permission; retire the fresh reader afterwards."""
import json
import os
import re
import secrets
import sys
from uuid import uuid4
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import live_program_partial_80 as p

FILE=p.qa.OUT/'order-execution-http.json'
r=dict(status='STARTED',http=[])


def main():
    assert p.s['phase']=='PARTIAL_DEPARTED','This reader verifies the saved partial departure stage; do not rerun after dispatching the remainder'
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[\x60,)\s]',Path('AGENTS.md').read_text(encoding='utf-8'))[1]
    w=p.s['fixture']['warehouse_id'];path=f'/api/tradecase/warehouses/{w}/documents/ORDER/O80'
    actor='OP80'+uuid4().hex[:10];password=secrets.token_hex(24)
    expected=dict(ordered='80',picked='80',loaded='60',shipped='60',retained='20')
    before=p.qa.stock()
    try:
        r['admin']=p.qa.expect(200,p.qa.http('GET',path));assert r['admin']['execution']['items'][0]['boxes']==expected
        with p.qa.oracle_connection()as c:
            q=c.cursor()
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Order progress isolated viewer','OP80QA',1,0,1)",a=actor,p=password)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Order progress isolated viewer',1,1)",a=actor)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_view')",a=actor);c.commit()
        r['no_assignment']=p.qa.expect(403,p.qa.http('GET',path,actor=actor,password=password));assert 'execution'not in r['no_assignment']
        with p.qa.oracle_connection()as c:
            q=c.cursor();q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Owned document quantity read proof',1)",a=actor,w=str(w));c.commit()
        r['scoped']=p.qa.expect(200,p.qa.http('GET',path,actor=actor,password=password));assert r['scoped']['execution']==r['admin']['execution']
        r['foreign']=p.qa.expect(403,p.qa.http('GET',path.replace(str(w),str(w+1)),actor=actor,password=password));assert 'execution'not in r['foreign']
        with p.qa.oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        r['revoked']=p.qa.expect(403,p.qa.http('GET',path,actor=actor,password=password));assert 'execution'not in r['revoked']
        for _ in range(5):assert p.qa.expect(200,p.qa.http('GET',path))['execution']==r['admin']['execution']
        assert p.qa.stock()==before==(200,200,1)
        r['status']='PASS';print(json.dumps(dict(status=r['status'],boxes=expected)))
    except Exception as exc:
        r['status']='FAIL';r['error']=str(exc);raise
    finally:
        with p.qa.oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a and REVOKED_AT is null',a=actor)
            q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='OP80QA'",a=actor);c.commit()
        r['actor']=actor;r['actor_retired']=True;r['http']=p.qa.CALLS
        FILE.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')


if __name__=='__main__':main()
