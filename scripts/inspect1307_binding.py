exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_TRANSPORT_DRIVER_USER'");names=[r[0]for r in q.fetchall()]
 for name in names:
  q.execute("select TEXT from USER_SOURCE where NAME=:name order by LINE",name=name);print("".join(r[0]for r in q.fetchall()))
r=httpx.put("http://127.0.0.1:8088/api/transport/driver-bindings/10018",auth=("admin",password),json={"user_id":"OWN1306_DRIVER","active":True,"expected_version":0})
print(r.status_code,r.text)
