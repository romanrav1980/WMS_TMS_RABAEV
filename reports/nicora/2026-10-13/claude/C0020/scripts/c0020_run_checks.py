# C-0020: запуск адресных проверок без записи; пароли читаются в памяти и передаются через stdin.
import json, subprocess, sys
from pathlib import Path
ROOT = Path("C:/projects/TMS")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.config import get_settings
s = get_settings(); creds = {}
with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
    q = c.cursor()
    for role, user in (("store", "OWN1348_STORE"), ("driver", "OWN1306_DRIVER")):
        q.execute("select PASS from RUSERS where ID=:u", u=user); creds[role] = {"username": user, "password": q.fetchone()[0]}
run = subprocess.run(["node", str(Path(__file__).with_name("c0020_checks.cjs")), sys.argv[1]], input=json.dumps(creds), capture_output=True, text=True, encoding="utf-8")
for v in creds.values(): assert v["password"] not in run.stdout + run.stderr
print(run.stdout[-3000:], run.stderr[-1500:])
