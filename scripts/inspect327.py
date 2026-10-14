exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select c.TABLE_NAME,c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE,listagg(cc.COLUMN_NAME,',')within group(order by cc.POSITION)from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME in('RRL_INTERWARE_ONWARD_DISPATCH','RRL_IW_RECOVERY_DISPATCH')group by c.TABLE_NAME,c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE")
 print(json.dumps(q.fetchall()))
 for name in ["RRL_STOCK_HU_SHIP_CMD","RRL_STOCK_INTERWARE_NEXT","RRL_STOCK_IW_RECOVERY_NEXT","RRL_INTERWARE_DEPART_GATE"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name);wire="create or replace "+"".join(r[0]for r in q).replace("\r","").strip()+"\n/\n"
  Path("tmp/327_"+name.lower()+".sql").write_text(wire,encoding="utf-8")
