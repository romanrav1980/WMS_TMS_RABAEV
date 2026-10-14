exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
ctx=json.loads(Path("tmp/context532.json").read_text(encoding="utf-8"))
with httpx.Client(auth=("admin","admin123"),timeout=35)as api:
 r=api.post("http://127.0.0.1:8088/api/finance/logistics-costs/transport-norms",json=ctx["request"])
 assert r.status_code==200 and r.json()==ctx["result"],r.text
 r=api.get(f'http://127.0.0.1:8088/api/finance/logistics-costs/warehouses/{ctx["warehouse"]}/transport-norms/{ctx["source_price_id"]}/history',params={"limit":1})
 assert r.status_code==200 and len(r.json()["items"])==1 and r.json()["has_more"],r.text
 before=r.json()["next_before_version"]
 r=api.get(f'http://127.0.0.1:8088/api/finance/logistics-costs/warehouses/{ctx["warehouse"]}/transport-norms/{ctx["source_price_id"]}/history',params={"limit":1,"before_version":before})
 assert r.status_code==200 and r.json()["items"][0]["version"]<before,r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),
 round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,130)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_TRANSPORT_NORM_HISTORY%'or upper(SQL_TEXT)like '%FROM RRL_TRANSPORT_PRICE%FOR UPDATE%')
 order by ELAPSED_TIME desc fetch first 5 rows only""")
 print("SQL538",json.dumps(q.fetchall()))
print("PASS538 HTTP original norm exact replay; bounded descending keyset history; source current fees not changed; publication independent of recognition.")
