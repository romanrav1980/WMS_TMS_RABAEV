exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();ctx=json.loads(Path("tmp/context241a.json").read_text(encoding="utf-8"));trip=ctx["target_trip"]
 # Completed real trip cannot mutate its loaded assignments.
 q.execute("select ST_NUMBER from RRL_SBORKA_PALLETS where ID=641384");number=q.fetchone()[0];out=q.var(oracledb.DB_TYPE_CLOB)
 try:q.callproc("RRL_TRANSPORT_PLAN_API.assign_sts",[trip,json.dumps([number]),"admin",out]);raise AssertionError("departed trip reassigned")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,str(exc)
 finally:c.rollback()
 q.execute("select ID from RUSERS where ID like 'WR234%'and nvl(DELETED,0)=0 fetch first 1 row only");actor=q.fetchone()[0]
 # Native dedicated reader shares current scope; invoke service without exposing local user's secret.
 from app.oracle_gateway import OracleGateway
 from app.modules.inventory.infrastructure.interwarehouse_incoming import InterwarehouseIncoming
 from app.modules.inventory.contracts_store_returns import StoreReturnReceiveError
 try:InterwarehouseIncoming(OracleGateway()).read(trip,actor);raise AssertionError("foreign warehouse read escaped")
 except StoreReturnReceiveError as exc:assert exc.status==403
 q.execute("select TRANSPORT from RRL_TRANSPORT_TASK where ID=33541");plate=q.fetchone()[0]
 q.execute("select MAX_WEIGHT_KG,PALLETS from RRL_TR_VEHICLE where NUM=:p",p=plate);capacity=q.fetchone()
 q.execute("select ST_NUMBER,CONDITION from RRL_SBORKA_PALLETS where TRANSTASK_ID=33541 order by ID");members=q.fetchall()
 if len(members)==2 and any(x[1]==2 for x in members):
  number=next(x[0]for x in members if x[1]!=2)
  try:q.callproc("RRL_TRANSPORT_PLAN_API.assign_sts",[33541,json.dumps([number]),"admin",out]);raise AssertionError("overfull route admitted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20886 and "PLAN_PALLET_CAPACITY_EXCEEDED"in str(exc),str(exc)
  finally:c.rollback()
  print("PASS241 existing own219 vehicle capacity",capacity,"loaded first retained/extra planned capacity refusal/no changes")
 else:print("CAPACITY219_NOT_REUSED",members,capacity)
 for ctx in[json.loads(Path("tmp/context241a.json").read_text(encoding="utf-8")),json.loads(Path("tmp/context241b.json").read_text(encoding="utf-8"))]:
  q.execute("select count(*),sum(BASE_QTY),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'",u=ctx["uid"]);assert q.fetchone()==(3,3,10,10)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u",u=ctx["uid"]);assert q.fetchone()[0]==6
  q.execute("select STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o",o=ctx["order"]);assert q.fetchone()==("SHIPPED",3)
 print("PASS241 native departed modification denied/current incoming reader foreign403/original each3units6codes/customerFF3 unchanged")
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,150)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like 'with candidates as(%'or SQL_TEXT like 'SELECT NVL(SUM(L.PHYSICAL_PLACES)%'or SQL_TEXT like 'SELECT COUNT(*),NVL(SUM(L.GROSS_WEIGHT_KG)%'or SQL_TEXT like 'SELECT COUNT(DISTINCT P.PALLET_UID),SUM(R.ORDER_WEIGHT)%')order by LAST_ACTIVE_TIME desc fetch first 6 rows only")
 for row in q:print(json.dumps(row,ensure_ascii=True))
