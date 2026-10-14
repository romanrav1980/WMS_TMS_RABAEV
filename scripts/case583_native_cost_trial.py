exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
def preview_transport_cost(q,trip,ware,price,actor):
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TRANSPORT_COST_API.preview",[trip,ware,price,actor,out])
 return read_oracle_json(out.getvalue())
ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"))
source=ctx["source"];trip=ctx["trip"];ware=ctx["warehouse"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(max(ID),0)+1 from RRL_TRANSPORT_PRICE");price=int(q.fetchone()[0])
 q.execute("insert into RRL_TRANSPORT_PRICE(ID,PRICE_NAME,COMPANY,TYPE_TR,PRICE,PRICE_FOR_HOURS,PRICE_FOR_ADDR,NORM_HOURS,PRICE_FOLDER,RANGE1)values(:id,:name,'DEFAULT',:vehicle_type,100,0,5,0,0,20)",
           id=price,name="["+str(source["task_vehicle_type"])+"]",vehicle_type=source["task_vehicle_type"])
 body=dict(operation_id="NORM583.TRIAL:"+ctx["tag"],source_price_id=price,warehouse_id=ware,currency="GEL",
           effective_from="2026-10-12",timezone_region="UTC",vehicle_type=source["task_vehicle_type"],
           vehicle_size_class=source["vehicle_profile"]["profile"]["vehicle_size_class"],
           rolling_unload_rate="1.5",manual_unload_rate="2.25",loader_rate="3",pallet_unload_rate="4.125",
           unload_charge_basis="PLACE",expected_version=0,reason="Rollback-only synthetic rate, not a commercial tariff",
           decision_reference="DEV583:"+ctx["tag"])
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
  request=dict(operation_id="COST583.TRIAL:"+ctx["tag"],trip_id=trip,warehouse_id=ware,source_price_id=price,currency="GEL",expected_norm_version=2)
  q.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps(request),"admin",out])
  recognized=read_oracle_json(out.getvalue());assert recognized["cost_posted"]and recognized["total"]=="107.25"
  q.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps(request),"admin",out]);assert read_oracle_json(out.getvalue())==recognized
  try:q.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps({**request,"currency":"USD"}),"admin",out]);raise AssertionError("Changed payload accepted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20867
  q.execute("select count(*),sum(AMOUNT)from RRL_TRANSPORT_COST_DETAIL where OPERATION_ID=:op",op=request["operation_id"])
  assert q.fetchone()==(3,107.25)
  q.execute("select count(*)from RRL_TRANSPORT_COST_CLAIM where OPERATION_ID=:op",op=request["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=request["operation_id"]);assert q.fetchone()[0]==1

 finally:c.rollback()
 q.execute("select count(*)from RRL_TRANSPORT_PRICE where ID=:id",id=price);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",op="COST583.TRIAL:"+ctx["tag"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_TRANSPORT_COST_CLAIM where OPERATION_ID=:op",op="COST583.TRIAL:"+ctx["tag"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.operation_id')=:op",op="COST583.TRIAL:"+ctx["tag"]);assert q.fetchone()[0]==0

 q.execute("select count(*)from RRL_TRANSPORT_NORM_HISTORY where SOURCE_PRICE_ID=:id",id=price);assert q.fetchone()[0]==0
 print("PASS583 actual departure/unload + rollback-only explicit norm: vehicle100 + address5 + manual2.25 =107.25; legacy hourly rate does not add an unapproved Q26 charge; same native preview/conduct107.25, exact repeat one header/claim/3 lines/outbox1, changed body refused; outer rollback removes all monetary facts/tariff/history, stock unchanged.")
