exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import read_task_progress_snapshot
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RUSERS set DELETED=0 where ID='WR244a0d0aaac78'");c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 result=read_task_progress_snapshot(OracleGateway(),975,"WR244a0d0aaac78");assert result["confirmed_quantity"]=="3"and result["remaining_quantity"]=="0"and result["status"]=="DONE",result
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RUSERS set DELETED=1 where ID='WR244a0d0aaac78'");c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 print("PASS244 own task975 progress3/remaining0/DONE/read-only current scoped snapshot")
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,110)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT like '%scope_ware%'order by LAST_ACTIVE_TIME desc fetch first 4 rows only")
 for row in q:print(json.dumps(row,ensure_ascii=True))
