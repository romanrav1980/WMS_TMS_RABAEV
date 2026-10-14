exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"));address=ctx["store_address"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
 for sql in ["select ADDR from RRL_ADDR where ADDR=:addr","select STORE_ADDR,RECEIPT_MODE,POLICY_VERSION from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:addr"]:
  q.execute(sql,addr=address);print(q.fetchall())
r=httpx.put("http://127.0.0.1:8088/api/delivery/store-receipts/policy",auth=("admin",password),json={"store_address":address,"mode":"BARCODE","expected_version":0})
print(r.status_code,r.text)
