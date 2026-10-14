exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select p.ID,p.ADDR,a.TRANSPORT_TYPE,a.STOL,a.MAX_VEHICLE_TONS from RRL_SBORKA_PALLETS p left join RRL_ADDR a on a.ADDR=p.ADDR where p.ID in(641360,641361)");print(json.dumps(q.fetchall(),default=str,ensure_ascii=True))
 q.execute("select v.ID,v.TR_TYPE,v.GIDROBORT,v.MAX_WEIGHT_KG,v.PALLETS from RRL_TR_VEHICLE v join RRL_TRANSPORT_TASK t on t.TRANSPORT=v.NUM where t.ID=33541");print(json.dumps(q.fetchall(),default=str))
