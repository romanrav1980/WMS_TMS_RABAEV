exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from uuid import uuid4
import httpx
ctx=json.loads(Path("tmp/context532.json").read_text(encoding="utf-8"));body=ctx["request"]
svc=LogisticsCosts(OracleGateway())
assert svc.publish_transport_norm(body,"admin")==ctx["result"]
tag=uuid4().hex[:8];actor="QN535"+tag;group=actor.upper();secret=uuid4().hex
with httpx.Client(auth=("admin","admin123"),timeout=35)as api:
 r=api.post("http://127.0.0.1:8088/api/admin/rights/groups",json={"id":group,"name":"Own535 norm scope"})
 assert r.status_code==200,r.text
 for right in ["create_tt_price","transport_dispatch_view"]:
  r=api.post(f"http://127.0.0.1:8088/api/admin/rights/groups/{group}/rights",json={"right_name":right,"description":"Own535 scoped finance"})
  assert r.status_code==200,r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:actor,:secret,'Own535 norm publisher',:grp,:ware,0,0)",
                      actor=actor,secret=secret,grp=group,ware=body["warehouse_id"]);c.commit()
 try:
  q.execute("select VERSION_NO from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:price_id",price_id=body["source_price_id"]);version=q.fetchone()[0]
  own={**body,"operation_id":"NORM535:"+tag,"expected_version":version,"reason":"Own535 bound non-admin publication"}
  result=svc.publish_transport_norm(own,actor);assert result["version"]==version+1
  q.execute("update RUSERS set WARE_ID=9807 where ID=:actor",actor=actor);c.commit()
  try:svc.publish_transport_norm(own,actor)
  except Exception as e:assert getattr(e,"status",None)==403,repr(e)
  else:raise AssertionError("Saved replay bypassed current warehouse")
  q.execute("update RUSERS set WARE_ID=:ware,DELETED=1 where ID=:actor",actor=actor,ware=body["warehouse_id"]);c.commit()
  try:svc.publish_transport_norm(own,actor)
  except Exception as e:assert getattr(e,"status",None)==403,repr(e)
  else:raise AssertionError("Deleted actor replay allowed")
  Path("tmp/context535.json").write_text(json.dumps(dict(request=own,result=result,actor=actor,retired=True),indent=2),encoding="utf-8")
 finally:q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
print("PASS535 native original norm saved replay; bound non-admin publishes next version; changed WARE/deleted actor cannot replay old result; actor retired; native VALID.")
