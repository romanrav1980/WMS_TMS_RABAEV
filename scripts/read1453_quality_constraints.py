exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select c.TABLE_NAME,c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE,k.COLUMN_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS k on k.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME in('RRL_WARES','RRL_SBORKA_PALLETS','RRL_STOCK_OPERATION') and c.CONSTRAINT_TYPE in('P','U') order by c.TABLE_NAME,k.POSITION");print(json.dumps(q.fetchall()))
