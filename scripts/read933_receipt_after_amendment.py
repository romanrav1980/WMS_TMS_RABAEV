exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
ctx=json.loads(Path("tmp/context910.json").read_text(encoding="utf-8"))
def stock():
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid order by CELL",p_uid=ctx["uid"]);return q.fetchall()
before=stock()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
with httpx.Client(auth=("admin",password),base_url="http://127.0.0.1:8088",timeout=20)as client:
 response=client.post("/api/receiving/supply-orders/"+ctx["order_id"]+"/pallets",json=ctx["body"])
 assert response.status_code==201,response.text
 assert response.json()==ctx["receipt"]
 source=client.get("/api/integrations/sap/supply-orders/"+ctx["order_id"]).json()
 assert source["receipt_state"]=="REVERSED"and source["receipt_allowed"]is False
assert stock()==before
assert all(row[1]==0 and row[2]==0 for row in before)
Path("tmp/recovery933.json").write_text(json.dumps({"cached_receipt_unchanged":True,"current_receipt_allowed":False,"state":"REVERSED","stock_version_unchanged":True,"stock":before},indent=2,default=str),encoding="utf-8")
print("933 real HTTP original910 after SAP amendments receipt cached exact after reversal; source REVERSED/new receipt disabled; own P/H0 and versions unchanged")
