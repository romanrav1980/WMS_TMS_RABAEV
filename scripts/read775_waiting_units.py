exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CURRENT_CELL,STOCK_STATUS,count(*),count(distinct PHYSICAL_UNIT_KEY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid group by CURRENT_CELL,STOCK_STATUS",p_uid=ctx["lot"]);print(q.fetchall())
 q.execute("select TABLE_NAME,COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME like 'RRL%UNIT%'and(COLUMN_NAME like '%CODE%'or COLUMN_NAME like '%KEY%')order by TABLE_NAME,COLUMN_ID");print(q.fetchall())
