exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select to_char(sysdate,'YYYY-MM-DD HH24:MI'),to_char(systimestamp,'YYYY-MM-DD HH24:MI TZH:TZM')from dual");print("DB_CLOCK",q.fetchone())
 q.execute("select count(*),min(CREATED_AT),max(CREATED_AT),sum(case when CREATED_AT<sysdate-8 then 1 else 0 end),sum(case when ACTIVE=1 then 1 else 0 end)from RRL_CUSTOMER_STORE_MAP");print("STORE_AGE",q.fetchone())
 q.execute("select count(*),sum(case when ACTIVE=1 then 1 else 0 end)from RRL_CUSTOMER");print("CUSTOMERS",q.fetchone())
 q.execute("select count(*)from RRL_SAP_STORE_ORDER");print("SAP_ORDERS",q.fetchone())
 q.execute("select count(*)from RRL_CUSTOMER_STORE_MAP m join RRL_CUSTOMER c on c.CUSTOMER_ID=m.CUSTOMER_ID where m.ACTIVE=1 and c.ACTIVE=1");print("ACTIVE_JOIN",q.fetchone())
