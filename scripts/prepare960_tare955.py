exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.contracts_stock import StockCommand
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"));service=build_stock_posting_service()
def post(op,kind,source,metadata):
 return service.post(StockCommand(operation_id=op,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CASE_PICK_TASK_ID,PALLET_TYPE_ID from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w order by CASE_PICK_TASK_ID",w=ctx["wave"]);cases=q.fetchall()
 assert len(cases)==2 and cases[0][1]==cases[1][1]
 result=post("TARE955.COUNT:"+ctx["tag"],"TARE_COUNT",{},{"owner_ware_id":ctx["ware"],"pallet_type_id":int(cases[0][1]),"condition":"GOOD","observed_quantity":"2","expected_version":0,"reason":"Own software scenario opening observation two empty CASE supports","decision_reference":"SOURCE955:"+ctx["tag"]})
 ctx["tare_count"]=result;ctx["tare_books"]=[]
 for caseid,pallet_type in cases:
  op="TARE955.BOOK:"+ctx["tag"]+":"+str(caseid)
  result=post(op,"TARE_BOOK",{"place_kind":"CASE","place_id":str(caseid)},{"pallet_type_id":None})
  ctx["tare_books"].append({"operation":op,"result":result})
 Path("tmp/context955.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("CASE own tare observation/booked through original root; goods unchanged")
