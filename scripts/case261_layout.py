exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import propose_receipt_layout
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.oracle_gateway import OracleGateway
from decimal import Decimal
import httpx
normal=propose_receipt_layout("10","EA","4",None,None);assert normal["quantities"]==["4","4","2"]
more=propose_receipt_layout("10","EA","4",4,None);assert more["quantities"]==["3","3","2","2"]
less=propose_receipt_layout("10","EA","4",2,None);assert less["quantities"]==["5","5"]and less["above_norm_pallets"]==[1,2]
partial=propose_receipt_layout("10","EA","4",None,["4","3"]);assert partial["unplanned_quantity"]=="3"
weighted=propose_receipt_layout("1.000001","KG","0.5",3,None);assert sum(map(Decimal,weighted["quantities"]))==Decimal("1.000001")
for args in [("1","EA","1",2,None),("10","EA","4",None,["11"]),("10","EA","4",None,["0"]),("10","EA","4",None,["0.5"])]:
 try:propose_receipt_layout(*args)
 except ValueError:pass
 else:raise AssertionError("Impossible layout")
svc=SupplyOrders(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select l.ORDER_ID,l.LINE_NUMBER from RRL_SAP_SUPPLY_LINE l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID
 where l.PLANNED_QTY>nvl((select sum(UNIT_COUNT)from RRL_PALLETS where PRIHOD_NAKLAD_ID=o.NAKLAD_ID and ARTICUL=l.ARTICUL),0)
 order by l.ORDER_ID,l.LINE_NUMBER fetch first 1 rows only""");order,line=q.fetchone()
request={"line_number":line,"pallet_count":1};actual=svc.pallet_plan(order,request,"admin")
assert actual["read_only"]and not actual["stock_changed"]and actual["unplanned_quantity"]=="0"
assert sum(map(Decimal,actual["quantities"]))==Decimal(actual["remaining_quantity"])
try:svc.pallet_plan(order,{**request,"expected_source_signature":"0"*64},"admin")
except ValueError as e:assert str(e)=="RECEIPT_LAYOUT_SOURCE_CHANGED"
else:raise AssertionError("Stale layout")
Path("tmp/context261.json").write_text(json.dumps({"order":order,"line":line,"proposal":actual},ensure_ascii=True),encoding="utf-8")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.post("http://127.0.0.1:8088/api/integrations/sap/supply-orders/"+order+"/pallet-plan",json=request)
 assert r.status_code==200,(r.status_code,r.text[:500]);assert r.json()==actual
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS261 norm/more-less/manualpartial/exactweighted/min1piece/overcurrentrefusal/stalesource/realremaining order oneREADONLY/HTTP200/no goods/label/task/reservation/protected20-20")
