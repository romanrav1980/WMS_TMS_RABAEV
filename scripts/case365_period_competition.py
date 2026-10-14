exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from concurrent.futures import ThreadPoolExecutor
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
ware=35944973;svc=LogisticsCosts(OracleGateway())
def one(i):
 try:return ("OK",svc.configure_period(f"POLICY365.RACE:{ware}:{i}",ware,"LOADED_UTC",None,2,f"Own365 competing controller decision{i}",f"DEV365.{i}","admin"))
 except LogisticsCostError as e:return(e.code,None)
with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(one,[1,2]))
assert sorted(x[0]for x in results)==["COST_PERIOD_VERSION_CONFLICT","OK"],results
assert svc.period_policy(ware,"admin")["version"]==3
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_LOG_COST_PERIOD_HISTORY where WARE_ID=:w and VERSION_NO=3",w=ware);assert q.fetchone()[0]==1
 try:
  q.execute("""insert into RRL_LOGISTICS_COST_RUN(OPERATION_ID,PAYLOAD_HASH,TT_ID,WARE_ID,CURRENCY,ACTOR,RESULT_JSON)
   select 'COST365.FORGED',PAYLOAD_HASH,TT_ID,WARE_ID,CURRENCY,ACTOR,RESULT_JSON from RRL_LOGISTICS_COST_RUN where OPERATION_ID='COST364.LOAD:33533'""")
  q.execute("""insert into RRL_LOGISTICS_COST_LINE(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE,CURRENCY,RATE_KEY,VERSION_NO,QUANTITY,RATE_VALUE,AMOUNT,BASIS,RATE_DATE,PERIOD_MODE,PERIOD_TIME_ZONE,PERIOD_POLICY_VERSION)
   select 'COST365.FORGED',LOAD_OPERATION_ID,COST_CODE,CURRENCY,RATE_KEY,VERSION_NO,QUANTITY,RATE_VALUE,AMOUNT,BASIS,RATE_DATE+1,PERIOD_MODE,PERIOD_TIME_ZONE,3
   from RRL_LOGISTICS_COST_LINE where OPERATION_ID='COST364.LOAD:33533'""")
 except oracledb.DatabaseError as e:assert e.args[0].code==20886 and "COST_ACTUAL_PERIOD_DATE_REQUIRED"in str(e),str(e)
 else:raise AssertionError("Forged financial date admitted")
 finally:c.rollback()
 q.execute("select count(*)from RRL_LOGISTICS_COST_RUN where OPERATION_ID='COST365.FORGED'");assert q.fetchone()[0]==0
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,130)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%RRL_LOG_COST_PERIOD%'or SQL_TEXT like '%STARTED_AT_INSTANT at time zone%')
 order by ELAPSED_TIME desc fetch first 8 rows only""");slow=q.fetchall()
Path("tmp/context365.json").write_text(json.dumps({"competition":results,"slow_sql":slow},indent=2,default=str),encoding="utf-8")
print("PASS365 same warehouse/version concurrent policy one winner/one conflict/no lost decision/native forged date blocked/run rolledback")
print(json.dumps(slow,default=str))
