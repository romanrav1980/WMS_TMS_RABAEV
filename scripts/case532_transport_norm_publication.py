exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
p=Path("tmp/context532.json")
if p.exists():raise SystemExit("Own532 already committed; exact saved replay only")
tag=uuid4().hex[:8];ware=14526684;svc=LogisticsCosts(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select min(TRANSPORTTYPE)from RRL_TRANSPORT_TYPE");vehicle_type=q.fetchone()[0]
 q.execute("select nvl(max(ID),0)+1 from RRL_TRANSPORT_PRICE");price_id=int(q.fetchone()[0])
 q.execute("insert into RRL_TRANSPORT_PRICE(ID,PRICE_NAME,COMPANY,TYPE_TR,PRICE,PRICE_FOR_HOURS,PRICE_FOR_ADDR,NORM_HOURS,PRICE_FOLDER,RANGE1)values(:price_id,:name,:company,:vehicle_type,100,2,5,8,0,20)",
           price_id=price_id,name="["+vehicle_type+"]",company="OWN.NORM532."+tag,vehicle_type=vehicle_type);c.commit()
 body=dict(operation_id="NORM532:"+tag,source_price_id=price_id,warehouse_id=ware,currency="GEL",effective_from="2026-10-12",
           timezone_region="UTC",vehicle_type=vehicle_type,vehicle_size_class="DEV_SMALL",
           rolling_unload_rate="1.50",manual_unload_rate="2.25",loader_rate="3",
           expected_version=0,reason="Own532 isolated software norm publication, not actual carrier tariff",decision_reference="DEV532:"+tag)
 trial={**body,"operation_id":body["operation_id"]+".ROLLBACK"}
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TRANSPORT_NORM_API.publish",[json.dumps(trial),"admin",out])
 q.execute("select VERSION_NO from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:price_id",price_id=price_id);assert q.fetchone()==(1,)
 c.rollback()
 q.execute("select count(*)from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:price_id",price_id=price_id);assert q.fetchone()[0]==0
 def publish():return svc.publish_transport_norm(body,"admin")
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:publish(),range(2)))
 assert results[0]==results[1]and results[0]["version"]==1,results
 result=results[0]
 assert result["source"]["vehicle_rate"]=="100"and result["source"]["point_rate"]=="5"
 assert result["cost_posted"]is False and result["stock_changed"]is False
 assert svc.publish_transport_norm(body,"admin")==result
 try:svc.publish_transport_norm({**body,"loader_rate":"4"},"admin")
 except Exception as e:assert getattr(e,"code",None)=="TRANSPORT_NORM_REJECTED"and"CONFLICT"in str(e),repr(e)
 else:raise AssertionError("Changed norm operation accepted")
 # Current source can change, but the already published snapshot and saved result do not.
 q.execute("update RRL_TRANSPORT_PRICE set PRICE=120 where ID=:price_id",price_id=price_id);c.commit()
 assert svc.publish_transport_norm(body,"admin")==result
 body2={**body,"operation_id":body["operation_id"]+".V2","expected_version":1,"reason":"Own532 source rate revision"}
 second=svc.publish_transport_norm(body2,"admin")
 assert second["version"]==2 and second["source"]["vehicle_rate"]=="120"
 history=svc.transport_norm_history(ware,price_id,None,10,"admin")
 assert [r["norm"]["source"]["vehicle_rate"]for r in history["items"]]==["120","100"]
 try:q.execute("delete from RRL_TRANSPORT_NORM_HISTORY where SOURCE_PRICE_ID=:price_id",price_id=price_id);raise AssertionError("Norm history deleted")
 except oracledb.DatabaseError as e:c.rollback();assert e.args[0].code==20863
 q.execute("select count(*)from RRL_TRANSPORT_NORM_HISTORY where SOURCE_PRICE_ID=:price_id",price_id=price_id);assert q.fetchone()[0]==2
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 p.write_text(json.dumps(dict(tag=tag,warehouse=ware,source_price_id=price_id,request=body,result=result,revision=second,history=history),indent=2),encoding="utf-8")
 print("PASS532 original legacy tariff snapshot100/point5, explicit currency/period/size/unload/loader; late rollback removes head/history; concurrent sameOP returns one version; changed-body refused; original100 frozen after source120/v2; immutable history; no stock/price posting.")
