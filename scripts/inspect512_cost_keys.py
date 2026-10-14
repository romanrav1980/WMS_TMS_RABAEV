exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for sql in [
 "select sys_context('USERENV','CURRENT_SCHEMA'),sys_context('USERENV','SERVICE_NAME') from dual",
 "select c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE,listagg(k.COLUMN_NAME,',')within group(order by k.POSITION) from USER_CONSTRAINTS c join USER_CONS_COLUMNS k on k.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME='RRL_LOGISTICS_COST_LINE'group by c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE order by c.CONSTRAINT_TYPE",
 "select OWNER,TABLE_NAME,CONSTRAINT_NAME from ALL_CONSTRAINTS where CONSTRAINT_TYPE='R'and R_OWNER=user and R_CONSTRAINT_NAME in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_LOGISTICS_COST_LINE'and CONSTRAINT_TYPE in('P','U'))",
 "select count(*),sum(case when RATE_DATE is null then 1 else 0 end),sum(AMOUNT)from RRL_LOGISTICS_COST_LINE",
 "select distinct NAME,TYPE from USER_DEPENDENCIES where REFERENCED_NAME='RRL_LOGISTICS_COST_LINE'order by NAME"]:
  q.execute(sql);print(json.dumps(q.fetchall(),default=str))
