"""180 original file-gateway XML contract to native weighted pallet receipt."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:8];article="QW180"+tag.upper();ware=30000000+int(tag[:6],16);receive="Q180R"+tag;pick="Q180P"+tag;storage="Q180S"+tag
prefix=str(50000000000000000+int(tag,16));sscc=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
digits="0401234567890";gtin=digits+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(digits))%10)%10)
scan="(01)"+gtin+"(3103)009800(21)"+tag
api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088";born=False;task=None;revision=None
def call(method,path,body=None,status=200,raw=None):
 r=api.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}))
 assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
def fields(node,values):
 for key,value in values.items():ET.SubElement(node,key).text=str(value)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 idoc=ET.Element("ARTMAS10");doc=ET.SubElement(idoc,"IDOC");control=ET.SubElement(doc,"EDI_DC40")
 fields(control,{"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","DOCNUM":str(2000000000000000+int(tag,16)),"SNDPRN":"OWN.QA.SAP","CREDAT":"20261011","CRETIM":"020000"})
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",{"BASE_UOM":"KG","EAN_UPC":gtin}),("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":"Own weighted box "+tag}),("E1BPE1MARMRT",{"ALT_UNIT":"KG","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":gtin})]:
  fields(ET.SubElement(doc,segment),{"MATERIAL":article,**values})
 call("POST","/api/integrations/sap/artmas",status=202,raw=ET.tostring(idoc,encoding="utf-8"))
 meta("update RRL_ARTICULS set TYPE_W=3 where ACTICUL=:p_a",p_a=article)
 call("PUT",f"/api/finished-goods/skus/{article}/receiving-policy",{"expected_version":0,"marking_required":False,"serialized_weight_boxes":True,"profiles":[]})
 meta("insert into RRL_WARES(ID,NAME,PREFIX,DEFAULT_RECEIVE_CELL)values(:p_ware,:p_name,'QW',:p_receive)",p_ware=ware,p_name="Own180 "+tag,p_receive=receive)
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:p_ware,'NONE',0)",p_ware=ware)
 for cell,is_pick in [(receive,0),(pick,1),(storage,0)]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:p_cell,:p_ware,0,0,0,:p_pick,0,0,0)",p_cell=cell,p_ware=ware,p_pick=is_pick)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p_cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p_cell=cell)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX)values(:p_ware,:p_a,:p_pick,0,0)",p_ware=ware,p_a=article,p_pick=pick)
 supply=ET.Element("WarehouseSupplyOrder",version="1")
 fields(supply,{"Sender":"OWN.QA.SAP","MessageId":"WEIGHT180.SUPPLY:"+tag,"OrderNumber":"W180:"+tag,"Revision":1,"WarehouseId":ware,"ReceiveCell":receive,"Supplier":"Own180 software fixture"})
 line=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line,{"LineNumber":"1","Material":article});ET.SubElement(line,"Quantity",unit="KG").text="9.8"
 imported=call("POST","/api/integrations/sap/supply-orders",status=202,raw=ET.tostring(supply,encoding="utf-8"))
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 body={"operation_id":"WEIGHT180.RECEIVE:"+tag,"line_number":"1","sscc":sscc,"quantity":"9.8","supplier_batch":"WB:"+tag,"expiry_date":"2030-01-01","gross_weight":"12","capture_mode":"WEIGHTED_BOXES","policy_version":1,"weighted_boxes":[{"barcode":scan,"codes":[]}]}
 try:
  result=call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201);born=True
  task=result["task_id"];assert result["physical_boxes"]==1 and result["marking_units"]==0 and result["regulatory_validation"]=="NOT_APPLICABLE"
  assert call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201)==result
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);p,h=q.fetchone();assert Decimal(str(p))==Decimal("9.8")and h==0
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=sscc);n,mass=q.fetchone();assert n==1 and Decimal(str(mass))==Decimal("9.8")
  print("PASS180 actual ARTMAS10+gateway supply XML/recipient warehouse -> native P9.8KG/unit1/box1/marking0/no legal ACK/replay/putaway task",article,body["operation_id"],flush=True)
 finally:
  if born:
   from app.modules.inventory.contracts_stock import StockCommand
   from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
   from app.modules.inventory.infrastructure.receiving import Receiving
   from app.oracle_gateway import OracleGateway
   Receiving(OracleGateway()).cancel(task,"Owned180 fixture cleanup","admin")
   q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);v=q.fetchone()[0]
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=sscc);keys=[r[0]for r in q.fetchall()]
   StockPosting().post(StockCommand(operation_id="WEIGHT180.CLEAN:"+tag,command_type="INVENTORY_COUNT",actor="admin",source={"revision_id":revision},metadata={"reason":"Native own180 cleanup","counts":[{"uid":sscc,"cell":receive,"article":article,"unit":"KG","quantity":"0","expected_stock_version":int(v),"unit_keys":keys}]},lines=()))
 print("Own180 native cleanup complete",flush=True)
