exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 q.execute("""select e.PARENT_UID,max(e.HU_LINK_ID) from RRL_WMS_HU_LINK e join RRL_PALLETS p on p.UID_PALLET=e.PARENT_UID where e.ACTIVE_FLAG=1 and p.HU_SHIPPED_OPERATION is null group by e.PARENT_UID order by max(e.HU_LINK_ID)desc fetch first 3 rows only""");candidates=[r[0]for r in q]
 q.execute("select UID_PALLET from RRL_PALLETS where HU_KIND='CONTAINER'and HU_SHIPPED_OPERATION is not null order by UID_PALLET desc fetch first 1 rows only");candidates.extend(r[0]for r in q)
result={}
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",secret),timeout=20)as client:
 for identifier in candidates:
  r=client.get("/api/warehouse-hus/composition",params={"identifier":identifier});print(identifier,r.status_code)
  if r.status_code==200:
   data=r.json();result[identifier]=data;print(json.dumps({"root":data["root"],"nodes":len(data["nodes"]),"links":data.get("links"),"historical":data.get("historical_composition",False)},default=str))
  else:print(r.text[:300])
Path("tmp/read1365.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
