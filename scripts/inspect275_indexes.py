exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TABLE_NAME,INDEX_NAME,listagg(COLUMN_NAME,',')within group(order by COLUMN_POSITION)from USER_IND_COLUMNS where TABLE_NAME in('RRL_CELLS','RRL_REMAINS','RRL_SBORKA_PALLETS','RRL_CASE_PICK_TASK')group by TABLE_NAME,INDEX_NAME order by TABLE_NAME,INDEX_NAME")
 print(json.dumps(q.fetchall(),ensure_ascii=True))
