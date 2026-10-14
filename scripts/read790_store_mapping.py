exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_STORE_MAP'order by COLUMN_ID");print("STORE_MAP",q.fetchall())
 q.execute("select count(*)from RRL_TRANSPORT_TASK where CONDITION=:p_condition and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0 and SHIPMENT_DATE>=to_date('2026-10-14','YYYY-MM-DD') and SHIPMENT_DATE<to_date('2026-10-22','YYYY-MM-DD')",p_condition="Спланирован");print("PLANNED_FUTURE_COUNT",q.fetchone()[0])
 q.execute("select m.CUSTOMER_STORE_MAP_ID,m.ADDRESS_ID from RRL_CUSTOMER_ORDER o join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=o.CUSTOMER_STORE_MAP_ID where o.CUSTOMER_ORDER_ID=:id",id=ctx["ids"][0]);print("SOURCE_MAP",q.fetchall())
