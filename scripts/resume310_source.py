source=__import__("pathlib").Path("scripts/source310_marked_case.py").read_text(encoding="utf-8")
source=source.replace('version=x["profile_version"]','version=x["version"]')
prefix=source[:source.index('if Path("tmp/context310.json")')]
exec(prefix)
saved=json.loads(Path("tmp/source310_progress.json").read_text(encoding="utf-8"));globals().update(saved);ware=saved["warehouse"]
if Path("tmp/context310.json").exists():raise SystemExit("Source310 complete; no repeat birth")
functions=source[source.index(" def meta("):source.index(' q.execute("select user,')]
continuation=source[source.index(' try:\n  ctx=api("POST"'):]
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 q=conn.cursor()
 exec("\n".join(line[1:]if line.startswith(" ")else line for line in functions.splitlines()))
 import httpx
 from datetime import datetime,timedelta,timezone
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(method,path,body=None,status=200):
  r=admin_api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
 exec("\n".join(line[1:]if line.startswith(" ")else line for line in continuation.splitlines()))
