exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from datetime import datetime,timedelta,timezone
ctx=json.loads(Path("tmp/context239.json").read_text(encoding="utf-8"));tag=ctx["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID from RUSERS where ID like 'WR234%'and nvl(DELETED,0)=0 fetch first 1 row only");actor=q.fetchone()[0]
 q.execute("select CANONICAL_REQUEST from RRL_INTERWARE_DECISION where OPERATION_ID=:op",op=ctx["decision_operation"]);raw=q.fetchone()[0];payload=json.dumps(raw,sort_keys=True,separators=(",",":")) if isinstance(raw,dict) else raw.read()if hasattr(raw,"read")else raw
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:q.callproc("RRL_INTERWARE_ROUTING.record_decision",[payload,actor,out]);raise AssertionError("foreign replay escaped")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20882,str(exc)
  c.rollback()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,170)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%FROM( SELECT OPERATION_ID FROM RRL_INTERWARE_PLAN WHERE TARGET_TT_ID%'or SQL_TEXT like 'select p.OPERATION_ID,p.SOURCE_LOAD_OPERATION_ID,p.SOURCE_ST_ID%'or SQL_TEXT like 'INSERT INTO RRL_INTERWARE_DECISION%'or SQL_TEXT like 'SELECT TARGET_TT_ID,OUTBOUND_DOCK,READY_DUE%')order by LAST_ACTIVE_TIME desc fetch first 10 rows only")
 for row in q:print(json.dumps(row,ensure_ascii=True))
 print("PASS239 native foreign actor replay denied before saved result/current table state")
