exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx
from app.transaction_gateway import TransactionGateway
from app.services.warehouse_task_service import WarehouseTaskService
from app.schemas import WarehouseTaskStatusRequest
tag=uuid4().hex[:10];actor="WR245"+tag;group=actor.upper();secret=uuid4().hex;ware=51365792;session=40
h=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select CURRENT_TASK_ID,CURRENT_INVENTORY_TASK_ID,STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);initial=q.fetchone();assert initial[1:]==(None,"ACTIVE"),initial;initial=(None,None,"ACTIVE")
 q.execute("select ID,USER_GROUP from RUSERS where NAME='Own task cancellation manager'and nvl(DELETED,0)=0 order by ROWID desc fetch first 1 row only");actor,group=q.fetchone()
 meta("update RUSERS set PASS=:p where ID=:a",p=secret,a=actor)
 h=httpx.Client(auth=(actor,secret),timeout=35)
 q.execute("select TASK_ID from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='OWN245'and CREATED_BY=:a order by TASK_ID",a=actor);tasks=[int(x[0])for x in q.fetchall()];assert len(tasks)==3,tasks
 first,other,stale=tasks
 q.execute("select CURRENT_TASK_ID,CURRENT_INVENTORY_TASK_ID,STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);assert q.fetchone()==(first,None,"ACTIVE")
 # Outer rollback includes cancellation, session and resource fact.
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",[actor,"warehouse_task_edit"])
 try:
  q.execute("select TASK_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id for update",id=first)
  q.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[first,actor,None])
  WarehouseTaskService(TransactionGateway(q)).cancel_task(first,WarehouseTaskStatusRequest(updated_by=actor,reason="Own rollback resource cancellation"))
  c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=first);assert q.fetchone()[0]=="ASSIGNED"
 q.execute("select CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);assert q.fetchone()[0]==first
 q.execute("select count(*)from RRL_RESOURCE_FACT_EVENT where TASK_ID=:id and EVENT_TYPE='CANCELLED'",id=first);assert q.fetchone()[0]==0
 def cancel(task,reason="Own manager resource cancellation"):
  return h.post(base+f"/api/warehouse-tasks/{task}/cancel",json={"updated_by":"admin","reason":reason})
 with ThreadPoolExecutor(2)as pool:responses=list(pool.map(lambda _:cancel(first),[1,2]))
 assert all(r.status_code==200 for r in responses),[(r.status_code,r.text[:1800])for r in responses]
 q.execute("select STATUS,CANCELLED_BY,CANCELLED_AT from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=first);state=q.fetchone();assert state[:2]==("CANCELLED",actor),state
 q.execute("select CURRENT_TASK_ID,CURRENT_INVENTORY_TASK_ID,STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);assert q.fetchone()==initial
 q.execute("select count(*)from RRL_RESOURCE_FACT_EVENT where TASK_ID=:id and EVENT_TYPE='CANCELLED'and EVENT_BY=:a",id=first,a=actor);assert q.fetchone()[0]==1
 assert cancel(first,"different retry reason").status_code==200
 q.execute("select STATUS,CANCELLED_BY,CANCELLED_AT from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=first);assert q.fetchone()==state
 meta("update RUSERS set WARE_ID=6667491 where ID=:a",a=actor);denied=cancel(first);assert denied.status_code==403,denied.text
 meta("update RUSERS set WARE_ID=:w where ID=:a",a=actor,w=ware)
 meta("update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=:task where SESSION_ID=:sid and CURRENT_TASK_ID is null",task=other,sid=session)
 response=cancel(stale);assert response.status_code==200,response.text
 q.execute("select CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);assert q.fetchone()[0]==other
 response=cancel(other);assert response.status_code==200,response.text
 q.execute("select CURRENT_TASK_ID,CURRENT_INVENTORY_TASK_ID,STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:sid",sid=session);assert q.fetchone()==initial
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 meta("update RUSERS set DELETED=1 where ID=:a",a=actor)
 print("PASS245 own metadata tasks",tasks,"existing own226 session40 restored/null; edit-only manager/current warehouse/server actor/concurrent repeat one event/date stable/outer rollback/stale attached task preserves other pointer/no stock/protected20-20. Synthetic association, no new qualified assignment/hardware claim.")
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,120)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like 'update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=null%'or SQL_TEXT like 'insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID%')order by LAST_ACTIVE_TIME desc fetch first 4 rows only")
 for row in q:print(json.dumps(row,ensure_ascii=True))
