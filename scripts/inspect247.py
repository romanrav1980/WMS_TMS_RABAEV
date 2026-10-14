exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select t.ID,t.TRANSPORT,t.VODITEL_ID,t.DELETED,count(o.ID),min(o.PLAN_START),max(o.PLAN_END)
 from RRL_TRANSPORT_TASK t left join RRL_TT_OPERATIONS o on o.TT_ID=t.ID
 where t.ID between 33529 and 33531 group by t.ID,t.TRANSPORT,t.VODITEL_ID,t.DELETED order by t.ID""")
 print(q.fetchall())
