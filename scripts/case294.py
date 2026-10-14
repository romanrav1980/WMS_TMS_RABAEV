exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 for number,count in [(291,0),(292,2)]:
  ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
  r=client.get("http://127.0.0.1:8088/api/inventory/interwarehouse/receipts/"+ctx["receipt_operation"]+"/shortage")
  assert r.status_code==200,r.text
  x=r.json();assert x["expected_quantity"]=="3"and x["accepted_quantity"]=="1"and x["short_quantity"]=="2",x
  assert len(x["missing_units"])==count and not x["current_unit_state_conflicts"]and not x["carrier_custody_released"],x
  if count:assert all(u["current_stock_status"]=="ISSUED"and u["registered_code_count"]==2 for u in x["missing_units"]),x
  Path("tmp/case294_"+str(number)+".json").write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and SQL_TEXT not like '%V$SQL%'and EXECUTIONS>0 and dbms_lob.instr(SQL_FULLTEXT,':missing_units')>0 order by ELAPSED_TIME desc fetch first 4 rows only""");print(json.dumps(q.fetchall()))
print("PASS294 existing ordinary291 and marked292 same snapshot shortage2/current2ISSUED/4codes/custodyopen/protected20-20")
