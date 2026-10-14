exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import subprocess
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();credentials={}
 for role,actor in [("driver","OWN1306_DRIVER"),("store","OWN1348_STORE"),("admin","admin")]:
  q.execute("select PASS from RUSERS where ID=:id",id=actor);credentials[role]={"username":actor,"password":q.fetchone()[0]}
result=subprocess.run(["node","scripts/browser1349_tare.mjs"],input=json.dumps(credentials),text=True,capture_output=True,encoding="utf-8",timeout=180)
print(result.stdout.encode("ascii","backslashreplace").decode());print(result.stderr.encode("ascii","backslashreplace").decode());sys.exit(result.returncode)
