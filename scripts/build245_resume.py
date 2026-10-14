from pathlib import Path
import json
s=Path("scripts/case245_cancel_resource.py").read_text(encoding="utf-8")
start=s.index(' meta("insert into RUSERS')
end=s.index(' # Outer rollback includes')
s=s[:start]+''' q.execute("select ID,USER_GROUP from RUSERS where NAME='Own task cancellation manager'and nvl(DELETED,0)=0 order by ROWID desc fetch first 1 row only");actor,group=q.fetchone()
 meta("update RUSERS set PASS=:p where ID=:a",p=secret,a=actor)
 h=httpx.Client(auth=(actor,secret),timeout=35)
 q.execute("select TASK_ID from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='OWN245'and CREATED_BY=:a order by TASK_ID",a=actor);tasks=[int(x[0])for x in q.fetchall()];assert len(tasks)==3,tasks
 first,other,stale=tasks
 q.execute("select CURRENT_TASK_ID,CURRENT_INVENTORY_TASK_ID,STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);assert q.fetchone()==(first,None,"ACTIVE")
'''+s[end:]
s=s.replace('assert initial==(None,None,"ACTIVE"),initial','assert initial[1:]==(None,"ACTIVE"),initial;initial=(None,None,"ACTIVE")',1)
print(json.dumps({"scripts/resume245.py":s},ensure_ascii=True))
