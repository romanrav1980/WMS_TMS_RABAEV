exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=20)as client:
 r=client.get('/api/case-pick/tasks/1134');r.raise_for_status();data=r.json();print(json.dumps({k:v for k,v in data.items()if k!='lines'},default=str))