exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_STOCK_OPERATION'and DATA_TYPE in('CLOB','JSON')order by COLUMN_ID");print("OperationJSON",json.dumps(q.fetchall()))
 q.execute("""select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and NAME in('RRL_STOCK_CONFIG_API','RRL_TRACE_AGG_LIFECYCLE')
 and(upper(TEXT)like '%BEGIN_CHANGE%'or upper(TEXT)like '%ACQUIRE%'or upper(TEXT)like '%CONFIGURATION%'or upper(TEXT)like '%RESOURCE_KEY%')
 order by NAME,LINE fetch first 10 rows only""");print("LifecycleFence",json.dumps(q.fetchall()))
