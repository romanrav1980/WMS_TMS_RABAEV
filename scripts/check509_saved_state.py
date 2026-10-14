exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
ctx=json.loads(Path("tmp/context483.json").read_text(encoding="utf-8"))
base="http://127.0.0.1:8088"
with httpx.Client(auth=("admin","admin123"),timeout=10)as h:
 for attempt in range(20):
  try:
   r=h.get(base+"/openapi.json")
   if r.status_code==200:break
  except httpx.HTTPError:pass
  time.sleep(1)
 else:raise AssertionError("API not ready")
 for basis in ["REFUSED","DAMAGED"]:
  r=h.post(base+"/api/inventory/store-returns/receive",json=ctx[basis]["receipt_body"])
  assert r.status_code==200 and r.json()==ctx[basis]["receipt"],r.text
 r=h.get(base+"/api/delivery/store-returns/"+ctx["receipt"]);assert r.status_code==200,r.text
 line=r.json()["lines"][0];assert line["accepted_quantity"]=="3"and line["available_for_approval"]=="3"and line["refused_available"]=="0"and line["damaged_available"]=="0",line
 source=json.loads(Path("tmp/context499.json").read_text(encoding="utf-8"))
 r=h.get(base+f'/api/finance/logistics-costs/trips/{source["trip"]}');assert r.status_code==200,r.text
 assert r.json()["summary"]["currency_totals"]==[dict(currency="GEL",original_amount="3.00")],r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 for basis in ["REFUSED","DAMAGED"]:
  q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx[basis]["receipt"]["pallet_identifier"]);assert q.fetchone()==(0,0)
plan=json.loads(Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json").read_text(encoding="utf-8"))
print("PASS509 latest HTTP trip summary3GEL/saved warehouse receipts after supplier-disposal replay/buyer3/caps preserved/liveVALID/protected20")
print(json.dumps({"revision":plan["planRevision"],"increments":[dict(id=x["id"],status=x["status"])for x in plan["increments"]]}))
