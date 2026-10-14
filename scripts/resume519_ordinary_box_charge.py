exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
from app.modules.platform.public import read_oracle_json
tag="dc223cc37e";trip=33622;ware=14526684;load="FULL.HU.SHIP:"+tag;box="HU.FULL.BOX:"+tag
p=Path("tmp/context519.json");ctx=json.loads(p.read_text(encoding="utf-8"))if p.exists()else dict(tag=tag,trip=trip,warehouse=ware,load=load,box=box)
def save():p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
loading=build_transport_loading()
state=loading.status(trip,"admin")
if "departure"not in ctx:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor()
  q.execute("select ID,PALLET_UID from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip",trip=trip)
  bound=q.fetchall();pending=[st for st,uid in bound if uid=="TT.PENDING:"+tag]
  assert all(st in pending or uid=="FULL.ST:"+tag for st,uid in bound),bound
  if pending:
   assert state["pending_st_ids"]==pending,state
   q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
   try:q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=0 where ID=:st and PALLET_UID=:p_uid",st=pending[0],p_uid="TT.PENDING:"+tag);c.commit()
   finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 ctx["departure"]=loading.depart("TT519.DEPART:"+tag,trip,"admin");save()
finance=LogisticsCosts(OracleGateway())
if "policy"not in ctx:
 ctx["policy"]=finance.configure_period("POLICY519:"+tag,ware,"CASE_ASSEMBLY","UTC",0,"Own519 first actual BOX packing date","DEV519.UTC","admin");save()
preview=finance.assembly_period(trip,ware,"UTC","admin")
assert preview["complete"]and preview["lines"][0]["source_kind"]=="BOX_PACKING",preview
day=preview["business_dates"][0]
if "rate"not in ctx:ctx["rate"]=finance.rate(ware,"GEL","2.25",day,0,"Own519 physical BOX source","DEV519.RATE","admin");save()
charge=finance.calculate("COST519:"+tag,trip,ware,"GEL","admin")
assert charge["amount"]=="2.25"and charge["lines"][0]["rate_date"]==day,charge
assert finance.calculate("COST519:"+tag,trip,ware,"GEL","admin")==charge
ctx.update(preview=preview,charge=charge);save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",load_id=load)
 tree=read_oracle_json(q.fetchone()[0]);node=next(n for n in tree["nodes"]if n["uid"]==box)
 assert node["packing_start"]["operation_id"]==preview["lines"][0]["start_operation_id"]
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);assert q.fetchone()==(0,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS519 retained actual ordinary BOX3 goods/first scanned packing/frozen LOAD ->real DEPART ->native assembly source ->BOX1 charge2.25/exact replay; original fixture cleanup P0/protected20-20; source not rerun.")
