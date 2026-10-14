exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from concurrent.futures import ThreadPoolExecutor
p=Path("tmp/context574.json")
if p.exists():raise SystemExit("Completed574 retained; exact saved replay only")
old=json.loads(Path("tmp/context532.json").read_text(encoding="utf-8"))
svc=LogisticsCosts(OracleGateway())
assert svc.publish_transport_norm(old["request"],"admin")==old["result"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select VERSION_NO from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:id",id=old["source_price_id"]);version=int(q.fetchone()[0])
 body={**old["request"],"operation_id":"NORM574:"+old["tag"],"expected_version":version,"unload_charge_basis":"PLACE","pallet_unload_rate":"4.125","reason":"Isolated explicit charge basis case"}
 trial={**body,"operation_id":body["operation_id"]+".ROLLBACK"}
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TRANSPORT_NORM_API.publish",[json.dumps(trial),"admin",out]);c.rollback()
 q.execute("select VERSION_NO from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:id",id=old["source_price_id"]);assert q.fetchone()[0]==version
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:svc.publish_transport_norm(body,"admin"),range(2)))
 assert results[0]==results[1]and results[0]["version"]==version+1
 assert results[0]["unload_charge_basis"]=="PLACE"and results[0]["pallet_unload_rate"]=="4.125"
 assert svc.publish_transport_norm(old["request"],"admin")==old["result"]
 p.write_text(json.dumps(dict(request=body,result=results[0]),indent=2),encoding="utf-8")
 print("PASS574 explicit PLACE/pallet4.125; sameOP concurrent one version; rollback restores head; old14 exact replay preserved; no money or stock posting.")
