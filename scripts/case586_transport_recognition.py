exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from app.modules.finance.contracts import LogisticsCostError
from concurrent.futures import ThreadPoolExecutor
ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"));source=ctx["source"]
p=Path("tmp/context586.json")
if p.exists():raise SystemExit("586 fixture retained; resume exact saved commands only")
svc=LogisticsCosts(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_TRANSPORT_COST_CLAIM where DEPARTURE_OPERATION_ID=:op",op=source["departure_operation_id"]);assert q.fetchone()[0]==0
 q.execute("select PRICE from RRL_TRANSPORT_TASK where ID=:id",id=ctx["trip"]);original_price=q.fetchone()[0]
 q.execute("select nvl(max(ID),0)+1 from RRL_TRANSPORT_PRICE");price=int(q.fetchone()[0])
 q.execute("insert into RRL_TRANSPORT_PRICE(ID,PRICE_NAME,COMPANY,TYPE_TR,PRICE,PRICE_FOR_HOURS,PRICE_FOR_ADDR,NORM_HOURS,PRICE_FOLDER,RANGE1)values(:id,:name,'DEFAULT',:vehicle_type,100,2,5,0,0,20)",
           id=price,name=source["legacy_region_key"],vehicle_type=source["task_vehicle_type"])
 norm=dict(operation_id="NORM586:"+ctx["tag"],source_price_id=price,warehouse_id=ctx["warehouse"],currency="GEL",
           effective_from="2026-10-12",timezone_region="UTC",vehicle_type=source["task_vehicle_type"],
           vehicle_size_class=source["vehicle_profile"]["profile"]["vehicle_size_class"],
           rolling_unload_rate="1.5",manual_unload_rate="2.25",loader_rate="3",pallet_unload_rate="4.125",
           unload_charge_basis="PLACE",expected_version=0,reason="Dedicated dev software fixture, synthetic rates; not an actual carrier contract",
           decision_reference="DEV586:"+ctx["tag"])
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TRANSPORT_NORM_API.publish",[json.dumps(norm),"admin",out]);c.commit()
 saved=dict(norm_request=norm,trip=ctx["trip"],warehouse=ctx["warehouse"],source_price_id=price,original_price=str(original_price))
 saved["requests"]=[dict(operation_id="COST586."+str(i)+":"+ctx["tag"],trip_id=ctx["trip"],warehouse_id=ctx["warehouse"],source_price_id=price,currency="GEL",expected_norm_version=1)for i in range(2)]
 p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 try:svc.conduct_transport_cost({**saved["requests"][0],"expected_norm_version":2},"admin");raise AssertionError("Stale version accepted")
 except LogisticsCostError as exc:assert exc.status==409 and "VERSION_CONFLICT"in str(exc)
 def conduct(body):
  try:return dict(result=svc.conduct_transport_cost(body,"admin"),body=body)
  except LogisticsCostError as exc:return dict(error=exc.code,body=body)
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(conduct,saved["requests"]))
 winners=[r for r in results if "result"in r];losers=[r for r in results if "error"in r]
 assert len(winners)==len(losers)==1,results
 winner=winners[0];assert winner["result"]["total"]=="107.25"and winner["result"]["cost_posted"]
 assert losers[0]["error"]=="TRANSPORT_COST_SOURCE_ALREADY_RECOGNIZED",losers
 assert svc.conduct_transport_cost(winner["body"],"admin")==winner["result"]
 read=svc.transport_costs(ctx["trip"],ctx["warehouse"],"admin");assert read["recognized"]==winner["result"]
 q.execute("select count(*)from RRL_TRANSPORT_COST_CLAIM where DEPARTURE_OPERATION_ID=:op",op=source["departure_operation_id"]);assert q.fetchone()[0]==1
 q.execute("select count(*),sum(AMOUNT)from RRL_TRANSPORT_COST_DETAIL where OPERATION_ID=:op",op=winner["body"]["operation_id"]);assert q.fetchone()==(3,107.25)
 q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=winner["body"]["operation_id"]);assert q.fetchone()[0]==1
 q.execute("select PRICE from RRL_TRANSPORT_TASK where ID=:id",id=ctx["trip"]);assert q.fetchone()[0]==original_price
 saved.update(results=results,winner=winner,done=True);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 print("PASS586 two distinct OP compete for original departure: one107.25 winner, other source-claim refusal; stale norm rejected; exact replay/immutable read one header+claim+3 detail/outbox1; legacy carrier PRICE unchanged. Dedicated dev synthetic norm retained, no commercial/ACK claim.")
