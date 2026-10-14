exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
proof=json.loads(Path("tmp/result1349.json").read_text(encoding="utf-8"));op=next(f["request"]["operation_id"]for f in proof["facts"]if f["action"]=="accept-lost")
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9807 and PALLET_TYPE_ID=1 and CONDITION_CODE='GOOD'");result["balances"]=dict(q.fetchall());assert result["balances"]=={"WAREHOUSE":4,"VEHICLE":0,"STORE":2}
 q.execute("select count(*)from RRL_TARE_ACCEPT where OPERATION_ID=:op",op=op);result["one_accept"]=q.fetchone()[0];assert result["one_accept"]==1
 q.execute("select count(*)from RRL_TARE_JOURNAL where OPERATION_ID=:op",op=op);result["one_journal"]=q.fetchone()[0];assert result["one_journal"]==1
 ids=[f["request"]["operation_id"]for f in proof["facts"]if "request"in f]
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID in(select V from json_table(:ids,'$[*]'columns(V varchar2(100)path '$')))",ids=json.dumps(ids));result["goods_events"]=q.fetchone()[0];assert result["goods_events"]==0
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,140)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%from RRL_TARE_OFFER o left join%'or SQL_TEXT like '%from RRL_TARE_BALANCE b join RRL_PALLET_TYPE%'or SQL_TEXT like '%INSERT INTO RRL_TARE_ACCEPT%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 6 rows only""");result["sql"]=q.fetchall()
print(json.dumps(result,default=str))
Path("tmp/verify1351.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
