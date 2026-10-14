exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from uuid import uuid4
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.oracle_gateway import OracleGateway
p=Path("tmp/context744.json");base=json.loads(Path("tmp/context669.json").read_text(encoding="utf-8"));incoming=json.loads(Path("tmp/context688.json").read_text(encoding="utf-8"))
ctx=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {"tag":uuid4().hex[:10],"stage":"NEW"}
def save():p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();ware=base["warehouse"];article=base["article"];customer=json.loads(Path("tmp/source669_progress.json").read_text(encoding="utf-8"))["customer"];lot=incoming["uid"];src=incoming["receipt"]["putaway_cell"];tag=ctx["tag"];dst="DP744"+tag;st_uid="DV744."+tag
 if ctx["stage"]=="NEW":
  names=("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ","RRL_TRANSPORT_TASK_SQ","RRL_TRANSPORT_TASK_SQ")
  ids=[]
  for name in names:q.execute("select "+name+".nextval from dual");ids.append(int(q.fetchone()[0]))
  ctx.update(ids=ids,lot=lot,src=src,dst=dst,ware=ware,article=article,st_uid=st_uid);save()
  order,row,plan,pl,pt,wave,wt,task,st,ff,source_trip,target_trip=ids
  def meta(sql,**b):
   if ":ware"in sql:b["ware"]=ware
   q.execute(sql,b)
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:cell,:ware,1,1,0,0,0,0,0)",cell=dst)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=dst)
   template=Path("scripts/source669_group_agg.py").read_text(encoding="utf-8")
   a=template.index(' meta("insert into RRL_CUSTOMER_ORDER(');b=template.index(' q.execute("select TRANSPORTTYPE',a)
   exec("\n".join(line[1:]for line in template[a:b].splitlines()))
   for trip,offset in[(source_trip,1),(target_trip,2)]:
    meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate)+:offset,:driver,:dock,0)",id=trip,plate="QL"+base["tag"],typ=base["trtype"],offset=offset,driver=base["driver"],dock=base["dock"])
   meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:trip where ID=:st_id",trip=source_trip,st_id=st)
   c.commit();ctx["stage"]="METADATA";save()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 order,row,plan,pl,pt,wave,wt,task,st,ff,source_trip,target_trip=ctx["ids"]
service=build_stock_posting_service()
def post(key,kind,source,metadata):
 if key not in ctx:
  result=service.post(StockCommand(operation_id="DEF744:"+tag+":"+key,command_type=kind,actor="admin",source=source,lines=(),metadata=metadata));ctx[key]=result;save()
 return ctx[key]
post("reserve","RESERVATION_CREATE",{"type":"PICK_WAVE","id":wave},{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl})
post("release","WAVE_PICK_RELEASE",{"wave_id":wave},{})
post("picked","TASK_COMPLETE",{"task_id":task},{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst})
if "binding"not in ctx:
 preview=FullPalletShipment(OracleGateway()).preview(task);assert preview["pallet_identifier"]==lot
 post("binding","PICK_PALLET_BIND_SHIPMENT",{"task_id":task},{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])})
ctx["stage"]="PICKED_BOUND";save()
print("744 retained SAP688 internalUID47 whole3 moved+reserved by original root/bound to one new dev ST; no birth/ship/cost or other-source rebuild")
