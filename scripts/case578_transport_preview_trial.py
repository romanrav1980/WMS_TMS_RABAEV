exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.transport_cost_preview import preview_transport_cost
ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"))
source=ctx["source"];trip=ctx["trip"];ware=ctx["warehouse"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(max(ID),0)+1 from RRL_TRANSPORT_PRICE");price=int(q.fetchone()[0])
 q.execute("insert into RRL_TRANSPORT_PRICE(ID,PRICE_NAME,COMPANY,TYPE_TR,PRICE,PRICE_FOR_HOURS,PRICE_FOR_ADDR,NORM_HOURS,PRICE_FOLDER,RANGE1)values(:id,:name,'DEFAULT',:vehicle_type,100,0,5,0,0,20)",
           id=price,name="["+str(source["task_vehicle_type"])+"]",vehicle_type=source["task_vehicle_type"])
 body=dict(operation_id="NORM578.TRIAL:"+ctx["tag"],source_price_id=price,warehouse_id=ware,currency="GEL",
           effective_from="2026-10-12",timezone_region="UTC",vehicle_type=source["task_vehicle_type"],
           vehicle_size_class=source["vehicle_profile"]["profile"]["vehicle_size_class"],
           rolling_unload_rate="1.5",manual_unload_rate="2.25",loader_rate="3",pallet_unload_rate="4.125",
           unload_charge_basis="PLACE",expected_version=0,reason="Rollback-only synthetic rate, not a commercial tariff",
           decision_reference="DEV578:"+ctx["tag"])
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_TRANSPORT_NORM_API.publish",[json.dumps(body),"admin",out])
  result=preview_transport_cost(q,trip,ware,price,"admin")
  assert result["complete"]and result["total"]=="107.25",result
  assert len(result["lines"])==3 and not result["cost_posted"]and not result["stock_changed"]
  q.execute("update RRL_TRANSPORT_PRICE set PRICE_FOR_HOURS=2 where ID=:id",id=price)
  q.callproc("RRL_TRANSPORT_NORM_API.publish",[json.dumps({**body,"operation_id":body["operation_id"]+".HOURS","expected_version":1}),"admin",out])
  blocked=preview_transport_cost(q,trip,ware,price,"admin")
  assert blocked["complete"]and blocked["total"]=="107.25"
  assert blocked["missing"]==[]
 finally:c.rollback()
 q.execute("select count(*)from RRL_TRANSPORT_PRICE where ID=:id",id=price);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_TRANSPORT_NORM_HISTORY where SOURCE_PRICE_ID=:id",id=price);assert q.fetchone()[0]==0
 print("PASS578 actual departure/unload + rollback-only explicit norm: vehicle100 + address5 + manual2.25 =107.25; legacy hourly rate does not add an unapproved Q26 charge; all synthetic tariff/history rolled back, no money or stock posting.")
