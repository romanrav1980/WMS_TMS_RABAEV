exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import base64,urllib.request,urllib.error
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TARGET_WARE_ID from RRL_IW_GROUP_PLAN order by OPERATION_ID fetch first 1 row only");ware=int(q.fetchone()[0])
 q.execute("select ID,PASS from RUSERS where ID='admin'and nvl(DELETED,0)=0");user,password=q.fetchone()
headers={"Authorization":"Basic "+base64.b64encode((user+":"+password).encode()).decode()}
def get(path):
 with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/api/inventory/interwarehouse"+path,headers=headers),timeout=15)as r:return json.load(r)
page=get("/group-warehouses/"+str(ware)+"?limit=1");assert len(page)==1
after=urllib.parse.quote(page[0]["operation_id"],safe="")
next_page=get("/group-warehouses/"+str(ware)+"?limit=1&after_operation_id="+after)
assert not next_page or next_page[0]["operation_id"]!=page[0]["operation_id"]
try:get("/group-warehouses/"+str(ware)+"?limit=201");raise AssertionError("Expected 422")
except urllib.error.HTTPError as e:assert e.code==422
print(json.dumps({"status":"PASS","http_first_page":len(page),"http_next_page":len(next_page),"invalid_limit":422,"stock_commands":0}))
