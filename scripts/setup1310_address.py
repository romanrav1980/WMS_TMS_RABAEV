exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"));address=ctx["store_address"]
assert address.startswith("Own264 synthetic registered store "),address
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_ADDR where ADDR=:addr",addr=address)
 if q.fetchone()[0]==0:q.execute("insert into RRL_ADDR(ADDR)values(:addr)",addr=address);c.commit()
print("Own B01 destination registered")
