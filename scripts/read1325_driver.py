exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='OWN1306_DRIVER'");password=q.fetchone()[0]
r=httpx.get("http://127.0.0.1:8088/api/driver/trips",params={"driver_id":10018,"trip_date":"2026-11-03"},auth=("OWN1306_DRIVER",password));print(r.status_code,r.text.encode("ascii","backslashreplace").decode());r.raise_for_status();assert r.json()[0]["loaded_weight_kg"]=="24"
