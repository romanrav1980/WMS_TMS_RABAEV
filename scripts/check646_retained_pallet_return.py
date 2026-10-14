exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context643.json").read_text())
origin=ctx["source"]["source"];uid=ctx["returned_uid"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=uid);assert q.fetchone()==(3,0)
 q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=uid);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot",lot=origin["lot"]);assert q.fetchone()[0]==6
 q.execute("select count(*)from RUSERS where ID=:actor and DELETED=1",actor="QD643"+ctx["tag"]);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_STORE_RETURN_HANDOVER where OPERATION_ID=:op",op="REUSE643.HAND:"+ctx["tag"]);assert q.fetchone()[0]==1
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,130)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'and(upper(SQL_TEXT)like '%RRL_STORE_RETURN_UNIT_CORE%'or upper(SQL_TEXT)like '%RRL_WMS_RECEIPT_AGG%')order by LAST_ACTIVE_TIME desc fetch first 5 rows only")
 print("SQL646",json.dumps(q.fetchall()))
print("PASS646 retained preserved PALLET/BOX-only return P3H0/3originalunits6codes/actor retired/one handover; no source recreation")
