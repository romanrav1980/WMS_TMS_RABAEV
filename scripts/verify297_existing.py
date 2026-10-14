exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/customer-orders/2030/delivery");assert r.status_code==200,r.text
 x=r.json();assert x["quantities"][0]["shipped"]=="3"and x["quantities"][0]["accepted"]=="3"and x["quantities"][0]["unreceived"]=="0"and x["quantities"][0]["confirmed_transport_shortage"]=="0",x
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for number in[291,292]:
  ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text());final=json.loads(Path("tmp/context297_"+str(number)+".json").read_text());q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op_id",op_id=final["body"]["operation_id"]);assert q.fetchone()==(0,)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=ctx["receipt_result"]["pallet_identifier"]);assert q.fetchone()==(0,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and dbms_lob.instr(SQL_FULLTEXT,'CONFIRMED_TRANSPORT_SHORTAGE')>0 order by ELAPSED_TIME desc fetch first 4 rows only""")
 rows=q.fetchall();Path("tmp/slow297.json").write_text(json.dumps(rows,indent=2),encoding="utf-8");print(json.dumps(rows))
print("PASS297 protected20-20/noStoreStockEvents/P0, preserved original229 full3, no confirmedloss creditedasgoods")
