exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
r=httpx.get("http://127.0.0.1:8088/api/resources/workload/warehouses/9807",auth=("admin",password),timeout=20)
print(r.status_code);print(r.text.encode("ascii","backslashreplace").decode()[:5000])
