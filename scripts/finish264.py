exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.domain.store_order import calendar
from datetime import datetime,timezone
import httpx
data=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));svc=StoreOrders(OracleGateway())
assert data["held"]["admission_status"]=="PENDING_CALENDAR"and data["accepted"]["admission_status"]=="ACCEPTED"
for state,expected in [(None,False),(True,True),(False,False)]:
 fields={"PickingStartAt":"2026-11-02T08:00:00+04:00","PickingFinishAt":"2026-11-02T18:00:00+04:00","ShipmentAt":"2026-11-03T06:00:00+04:00",
  "OperationalDate":"2026-11-02","DeliveryDate":"2026-11-03","OrderDate":"2026-10-11"}
 result=calendar(fields,240,"1",False,datetime(2026,10,11,tzinfo=timezone.utc),state)
 assert result["calendar_allowed"]==expected
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 url=f"http://127.0.0.1:8088/api/integrations/sap/store-orders/warehouses/{data['ware']}/stores/{data['store']}/calendar-context"
 r=client.get(url,params={"delivery_date":data["day"]});assert r.status_code==200 and r.json()["exception_status"]=="OPEN"
 # Exact alreadyimported raw message repeat: no new demand.
 r=client.post("http://127.0.0.1:8088/api/integrations/sap/store-orders",content=data["raw_closed"].encode("utf-8"),headers={"Content-Type":"application/xml"})
 assert r.status_code==202,(r.status_code,r.text[:500]);assert r.json()["customer_order_id"]==data["held"]["customer_order_id"]and r.json()["admission_status"]=="PENDING_CALENDAR"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CUSTOMER_ORDER_ID,sum(ORDER_QTY)from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID in(:held,:accepted)group by CUSTOMER_ORDER_ID",held=data["held"]["customer_order_id"],accepted=data["accepted"]["customer_order_id"])
 assert sorted(q.fetchall())==sorted([(data["held"]["customer_order_id"],1),(data["accepted"]["customer_order_id"],1)])
 q.execute("select count(*)from RRL_PICK_PLAN where CUSTOMER_ORDER_ID in(:held,:accepted)",held=data["held"]["customer_order_id"],accepted=data["accepted"]["customer_order_id"]);assert q.fetchone()==(0,)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%FROM RRL_SAP_STORE_CAL_EXCEPTION WHERE WARE_ID=%'or sql_text like 'select cal.UTC_OFFSET_MINUTES,cal.DELIVERY_WEEKDAYS,%'order by last_active_time desc fetch first 6 rows only");print("SQL_MS",q.fetchall())
print("PASS264 actualHTTP contextOPEN/rawsource sameMessage202returnsoldheld/notautoaccept/immutable2 original qty1/pickplans0/weeklyclosed OPENoverride/domain sourcefixed offsets; ownMaptestregistration Oct1 syntheticnotrealstore")
