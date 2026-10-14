exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.fulfillment.public import build_customer_order_read_service
reader=build_customer_order_read_service()
first=reader.list("admin",limit=3)
second=reader.list("admin",limit=3,before_id=first[-1]["customer_order_id"])
ids1=[x["customer_order_id"] for x in first];ids2=[x["customer_order_id"] for x in second]
assert len(first)==len(second)==3 and not set(ids1)&set(ids2)
assert max(ids2)<min(ids1)
assert reader.list("admin",limit=3)==first
filtered=reader.list("admin",order_no="FULL.QA:4bb85f1f15",limit=1)
after=reader.list("admin",order_no="FULL.QA:4bb85f1f15",limit=1,before_id=filtered[0]["customer_order_id"])
assert filtered[0]["customer_order_id"]==2134 and after[0]["customer_order_id"]==2133
assert reader.list("admin",order_no="FULL.QA:4bb85f1f15",before_id=2133,limit=3)==[]
legacy=reader.get(-980711,"admin");assert legacy["customer_order_id"]==-980711
negative=reader.list("admin",before_id=-980711,limit=3);assert all(x["customer_order_id"] < -980711 for x in negative)
try:reader.list("admin",before_id=0);raise AssertionError("Invalid cursor accepted")
except ValueError:pass
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),
 round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,240)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0
 and SQL_TEXT not like '%V$SQL%' and SQL_TEXT like '%ORDER_UOM_COUNT%'
 order by LAST_ACTIVE_TIME desc fetch first 6 rows only""")
 sql=[list(x) for x in q.fetchall()]
Path("tmp/read1046_order_paging.json").write_text(json.dumps({"first_ids":ids1,"second_ids":ids2,"filtered_first":filtered,"filtered_second":after,"empty_tail":True,"invalid_rejected":True,"sql":sql},indent=2,default=str),encoding="utf-8")
print("PASS1046 actual Oracle bounded header-first/keyset/nooverlap/returnfirst/search preserved/empty/invalid; no writes")
