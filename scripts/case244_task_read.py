exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from uuid import uuid4
import httpx
tag=uuid4().hex[:10];actor="WR244"+tag;group=actor.upper();secret=uuid4().hex;ware=51702230;task=975
h=httpx.Client(auth=(actor,secret),timeout=35);admin=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
def get(client,path,status=200):
 r=client.get(base+path);assert r.status_code==status,(r.status_code,r.text[:2300]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 meta("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own scoped task reader',:g,:w,0,0)",a=actor,p=secret,g=group,w=ware)
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'warehouse_task_view')",g=group)
 row=get(h,f"/api/warehouse-tasks/{task}");assert row["task_id"]==task and row["from_ware_id"]==ware and row["status"]=="DONE",row
 rows=get(h,"/api/warehouse-tasks?limit=100");assert rows and all(ware in(x["from_ware_id"],x["to_ware_id"])for x in rows)and task in[x["task_id"]for x in rows]
 get(h,"/api/warehouse-tasks/972",403);get(h,"/api/warehouse-tasks/972/progress",403);get(h,"/api/warehouse-tasks/972/sync",403)
 own_sync=get(h,f"/api/warehouse-tasks/{task}/sync");assert own_sync["task_id"]==task and own_sync["sync_status"]=="SYNCED",own_sync
 syncs=get(h,"/api/warehouse-tasks/domain-sync?limit=100");assert syncs and all(x["task_id"] in[x["task_id"]for x in rows]for x in syncs),syncs
 filtered=get(h,f"/api/warehouse-tasks?source_doc_type=INTERWARE&source_doc_id={task}&limit=1");assert len(filtered)==1 and filtered[0]["task_id"]==task
 meta("update RUSERS set WARE_ID=6667491 where ID=:a",a=actor);get(h,f"/api/warehouse-tasks/{task}",403)
 other=get(h,"/api/warehouse-tasks?limit=100");assert all(6667491 in(x["from_ware_id"],x["to_ware_id"])for x in other)
 meta("update RUSERS set WARE_ID=:w where ID=:a",a=actor,w=ware)
 meta("delete from RIGHTS where USER_GROUP=:g and upper(RIGHT1)='WAREHOUSE_TASK_VIEW'",g=group)
 get(h,f"/api/warehouse-tasks/{task}",403)
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'warehouse_task_view')",g=group)
 # READ ONLY wrapper rejects any ordinary write from a loader and leaves data unchanged.
 from app.oracle_gateway import OracleGateway
 from app.modules.inventory.public import read_task_snapshot
 def bad_loader(tx,scope):
  tx.execute("update RRL_WAREHOUSE_TASK set LAST_ERROR=LAST_ERROR where TASK_ID=:id",{"id":task})
 try:read_task_snapshot(OracleGateway(),actor,bad_loader,task);raise AssertionError("read-only loader wrote")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==1456,str(exc)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 meta("update RUSERS set DELETED=1 where ID=:a",a=actor)
 print("PASS244 current task/detail/sync/progress foreign403/scoped bounded list-filter/sync list/warehouse change/current revoked VIEW403/loader READ ONLY write denied/protected20-20/no task effect",actor)
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,130)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%FROM_WARE_ID=:scope_ware or TO_WARE_ID=:scope_ware%'or SQL_TEXT like '%task_scope.TASK_ID=RRL_WAREHOUSE_TASK_SYNC.TASK_ID%')order by LAST_ACTIVE_TIME desc fetch first 4 rows only")
 for row in q:print(json.dumps(row,ensure_ascii=True))
