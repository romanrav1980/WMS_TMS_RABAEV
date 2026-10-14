exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from urllib.parse import urlencode
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'");actor,password=q.fetchone()
address=ctx["loading_ui"][1]["body"]["physical_load"]["destinations"][0]["address"]
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=20)as client:
 result=[]
 for url in ["/api/delivery/store-receipts/trips/33571/places?"+urlencode({"store_address":address}),"/api/delivery/store-receipts/preview?"+urlencode({"load_operation_id":ctx["loading_ui"][1]["body"]["operation_id"],"store_address":address})]:
  r=client.get(url);result.append({"url":url,"status":r.status_code,"body":r.json()})
ctx["store_read"]=result;ctx["store_address"]=address;Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8");print(json.dumps(result))
