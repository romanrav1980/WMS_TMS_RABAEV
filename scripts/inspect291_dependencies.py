exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select distinct NAME,TYPE from USER_SOURCE where upper(TEXT)like '%RRL_INTERWARE_RECEIPT%'order by NAME,TYPE");print("DEPENDANTS291",q.fetchall())
 q.execute("select c.CONSTRAINT_NAME,listagg(cc.COLUMN_NAME,',')within group(order by cc.POSITION)from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME='RRL_INTERWARE_RECEIPT'and c.CONSTRAINT_TYPE='U'group by c.CONSTRAINT_NAME");print("UNIQUES291",q.fetchall())
 q.execute("select count(*)from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.REMAIN>0 and r.HARD_RESERVED_BASE=0 and p.ARTICUL='REUSE.QA:cdbf4c0962'");print("OWN_REUSE_STOCK_AVAILABLE291",q.fetchone()[0])
