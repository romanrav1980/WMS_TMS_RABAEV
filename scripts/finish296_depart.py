exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
loading=build_transport_loading()
for number in[291,292]:
 p=Path("tmp/context296_"+str(number)+".json");saved=json.loads(p.read_text());ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text())
 if "departure_result"not in saved:
  saved["departure_operation_id"]="IW296.DEPART:"+str(number)+":"+ctx["tag"]
  saved["departure_result"]=loading.depart(saved["departure_operation_id"],ctx["target_trip"],"admin");p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 assert loading.depart(saved["departure_operation_id"],ctx["target_trip"],"admin")==saved["departure_result"]
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select STATUS,ROOT_UID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op_id",op_id=saved["load_operation_id"]);assert q.fetchone()==("DEPARTED",ctx["receipt_result"]["pallet_identifier"])
  q.execute("select count(*)from RRL_INTERWARE_SHORTAGE_UNIT where FACT_OPERATION_ID=:op_id",op_id=json.loads(Path("tmp/context295_"+str(number)+".json").read_text())["confirmation_operation_id"]);assert q.fetchone()==(2 if number==292 else 0,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS296 actual existing native departure both accepted1 fragments; shortage2 history retained/no full receipt/no extra stock/protected20-20")
