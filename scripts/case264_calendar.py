"""Explicit future exception on owned warehouse; retained SAP demand, no physical stock."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.fulfillment.application.ports import StoreOrderConflict
from app.modules.fulfillment.domain.store_order import calendar
from app.modules.platform.public import read_oracle_json
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import httpx,xml.etree.ElementTree as ET
g=OracleGateway();svc=StoreOrders(g);tag=uuid4().hex[:10];ware=5265051;day="2026-11-03";actor="CAL264"+tag;group=actor.upper();secret=uuid4().hex
p=Path("tmp/context264.json");assert not p.exists(),"Resume own context264; no new demand births"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select CUSTOMER_ID,CUSTOMER_CODE from RRL_CUSTOMER where ACTIVE=1 order by CUSTOMER_ID fetch first 1 rows only");customer_id,customer=q.fetchone()
 q.execute("select ARTICUL,BASE_UOM,SENDER from RRL_SAP_ARTICLE_META where BASE_UOM in('EA','PCE','ST')order by ARTICUL fetch first 1 rows only");article,uom,sender=q.fetchone()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select RRL_CUSTOMER_STORE_MAP_SQ.nextval from dual");map_id=int(q.fetchone()[0]);store="QCAL264"+tag
 meta("insert into RRL_CUSTOMER_STORE_MAP(CUSTOMER_STORE_MAP_ID,CUSTOMER_ID,LEGACY_ADDR,LEGACY_ADDR_KEY,STORE_CODE,STORE_NAME,ADDRESS_TEXT,ACTIVE,CREATED_AT,CREATED_BY)values(:id,:customer,:addr,RRL_CUSTOMER_ORDER_API.normalize_key(:addr),:store_code,:addr,:addr,1,to_date('2026-10-01','YYYY-MM-DD'),'QA264')",id=map_id,customer=customer_id,addr="Own264 synthetic registered store "+tag,store_code=store)
 meta("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own264 store calendar editor',:g,:w,0,0)",a=actor,p=secret,g=group,w=ware)
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'customer_rule_edit')",g=group)
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'wms_admin_login')",g=group)
 data={"tag":tag,"ware":ware,"store":store,"map_id":map_id,"customer":customer,"article":article,"uom":uom,"sender":sender,"actor":actor,"day":day}
 p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 initial=svc.calendar_context(ware,store,day,actor)
 if not initial["configured"]:svc.configure(ware,store,{"utc_offset_minutes":240,"delivery_weekdays":[1,2,3,4,5,6,7],"allow_same_day":False},actor)
 body={"warehouse_id":ware,"store_code":store,"delivery_date":day,"expected_version":0,"day_state":"CLOSED",
       "source_reference":"Own264 controlled future store closure fixture","reason":"Own264 retained source demand and explicit later admission"}
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB);payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":")))
 q.callproc("RRL_STORE_CALENDAR_API.set_exception",["CAL264.ROLL:"+tag,actor,payload,out]);assert read_oracle_json(out.getvalue())["version"]==1;c.rollback()
 assert svc.calendar_context(ware,store,day,actor)["version"]==0
 def publish(suffix):
  with httpx.Client(auth=(actor,secret),timeout=30)as h:
   r=h.post("http://127.0.0.1:8088/api/integrations/sap/store-orders/calendar-exceptions",json={"operation_id":"CAL264.CLOSE:"+tag+"."+suffix,**body})
   return r.status_code,r.json()
 with ThreadPoolExecutor(2)as pool:responses=list(pool.map(publish,["A","B"]))
 assert sorted(x[0]for x in responses)==[200,409],responses
 closed=next(b for status,b in responses if status==200);data["closed"]=closed;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 assert svc.set_calendar_exception(closed["operation_id"],body,actor)==closed
 try:svc.set_calendar_exception(closed["operation_id"],{**body,"day_state":"OPEN"},actor)
 except ValueError:pass
 else:raise AssertionError("Calendar payload conflict")
 def raw(suffix):
  r=ET.Element("WarehouseCustomerOrder",version="1")
  fields={"Sender":sender,"MessageId":"CAL264.MSG:"+tag+suffix,"OrderNumber":"CAL264.ORDER:"+tag+suffix,
   "CustomerCode":customer,"StoreCode":store,"WarehouseId":str(ware),"OrderDate":"2026-10-11",
   "OperationalDate":"2026-11-02","DeliveryDate":day,"PickingStartAt":"2026-11-02T08:00:00+04:00",
   "PickingFinishAt":"2026-11-02T18:00:00+04:00","ShipmentAt":"2026-11-03T06:00:00+04:00"}
  for name,value in fields.items():ET.SubElement(r,name).text=value
  l=ET.SubElement(ET.SubElement(r,"Lines"),"Line")
  ET.SubElement(l,"LineNumber").text="1";ET.SubElement(l,"Material").text=article;ET.SubElement(l,"Quantity",unit=uom).text="1"
  return ET.tostring(r,encoding="utf-8")
 xml=raw(".CLOSED");data["raw_closed"]=xml.decode("utf-8");p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 held=svc.receive(xml,"admin");data["held"]=held;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 assert held["admission_status"]=="PENDING_CALENDAR"and not held["calendar_allowed"]and not held["late"]
 assert svc.receive(xml,"admin")["customer_order_id"]==held["customer_order_id"]
 try:LegacyPreparation(g).prepare(held["customer_order_id"],{},"admin")
 except StoreOrderConflict:pass
 else:raise AssertionError("Calendar hold preparation bypass")
 opened=svc.set_calendar_exception("CAL264.OPEN:"+tag,{**body,"expected_version":1,"day_state":"OPEN"},actor)
 data["opened"]=opened;xml2=raw(".OPEN");data["raw_open"]=xml2.decode("utf-8");p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 accepted=svc.receive(xml2,"admin");data["accepted"]=accepted;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 assert accepted["admission_status"]=="ACCEPTED"and accepted["calendar_allowed"]
 q.execute("select ADMISSION_STATUS from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:id",id=held["customer_order_id"]);assert q.fetchone()==("PENDING_CALENDAR",)
 meta("update RUSERS set WARE_ID=6667491 where ID=:a",a=actor)
 try:svc.set_calendar_exception(closed["operation_id"],body,actor)
 except PermissionError:pass
 else:raise AssertionError("Cached foreign calendar replay")
 meta("update RUSERS set WARE_ID=:w where ID=:a",w=ware,a=actor)
 try:q.execute("delete from RRL_SAP_STORE_CAL_EXCEPTION where WARE_ID=:w and CUSTOMER_STORE_MAP_ID=:store_id and DELIVERY_DATE=to_date(:day,'YYYY-MM-DD')",w=ware,store_id=map_id,day=day)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("Exception history deletion")
 c.rollback()
 try:q.execute("update RRL_SAP_STORE_CALENDAR set ALLOW_SAME_DAY=1 where WARE_ID=:w and CUSTOMER_STORE_MAP_ID=:store_id",w=ware,store_id=map_id)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("Legacy calendar bypass")
 c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 meta("update RUSERS set DELETED=1 where ID=:a",a=actor)
print("PASS264 explicitownMap registrationagefixture/existingcustomer-SAParticle-sender/ownedWARE5265051/futureNov3/sourcebook native/currentware/outerrollback/concurrentHTTP200-409/replay/conflict/retainedPENDING_CALENDAR qty1/no preparation/OPEN neworder accepted/oldheld unchanged/cachedchangedware403/history-configguard/protected20-20/no physicalstock")
