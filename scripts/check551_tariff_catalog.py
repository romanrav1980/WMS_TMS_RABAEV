exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.routers.transport_tariffs import list_tariffs,get_tariff_table_info
ctx=json.loads(Path("tmp/context532.json").read_text(encoding="utf-8"))
rows=list_tariffs(region=None,transport_type=None)
row=next(r for r in rows if r["ID"]==ctx["source_price_id"])
assert row["PRICE"]=="120" and row["PRICE_FOR_HOURS"]=="2" and row["PRICE_FOR_ADDR"]=="5",row
assert all("error"not in r for r in rows)
assert list_tariffs(region=row["PRICE_NAME"],transport_type=str(row["TYPE_TR"]))==[row]
assert list_tariffs(region="NO.SUCH.REGION551",transport_type=None)==[]
info=get_tariff_table_info()
assert info["table"]=="RABAEV.RRL_TRANSPORT_PRICE" and info["rate_basis"]["PRICE"]=="VEHICLE"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select VERSION_NO from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:price_id",price_id=ctx["source_price_id"]);assert q.fetchone()==(3,)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)like '%FROM RRL_TRANSPORT_PRICE%'
 and upper(SQL_TEXT)like '%PRICE_NAME=:REGION_KEY%'and upper(SQL_TEXT)not like '%V$SQL%'order by LAST_ACTIVE_TIME desc fetch first 2 rows only""")
 print("SQL551",json.dumps(q.fetchall()))
print("PASS551 actual legacy catalog price120/hour2/point5, exact region/type filters, no fake error rows or native mutation, published head3 unchanged. Direct read; not browser/permission acceptance.")
