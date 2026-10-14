exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from hashlib import sha256
ctx=json.loads(Path("tmp/context292.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select UNIT_ID,SYSTEM_CODE,CODE_HASH from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"])
 actual=set(q.fetchall());expected={(u["unit_id"],x["system_code"],sha256(x["code"].encode()).hexdigest())for u in ctx["units"]for x in u["codes"]}
 assert actual==expected
print("PASS292 all six original code hashes byte-identical after selected receive and PUT")
