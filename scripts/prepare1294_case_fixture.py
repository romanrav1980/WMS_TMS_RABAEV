"""180 original file-gateway XML contract to native weighted pallet receipt."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag="1294ab01";article="QPB1294"+tag.upper();ware=30000000+int(tag[:6],16);receive="B94R"+tag;pick="B94P"+tag;storage="B94S"+tag
prefix=str(50000000000000000+int(tag,16));sscc=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
digits="0401234567890";gtin=digits+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(digits))%10)%10)
scan="(01)"+gtin+"(3103)009800(21)"+tag
api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088";born=False;task=None;revision=None
def call(method,path,body=None,status=200,raw=None):
 r=api.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}))
 assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
def fields(node,values):
 for key,value in values.items():ET.SubElement(node,key).text=str(value)
if Path("tmp/context1294.json").exists():raise SystemExit("Retained fixture exists; resume it")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 idoc=ET.Element("ARTMAS10");doc=ET.SubElement(idoc,"IDOC");control=ET.SubElement(doc,"EDI_DC40")
 fields(control,{"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","DOCNUM":str(2000000000000000+int(tag,16)),"SNDPRN":"OWN.QA.SAP","CREDAT":"20261011","CRETIM":"020000"})
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",{"BASE_UOM":"EA","EAN_UPC":gtin}),("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":"Own weighted box "+tag}),("E1BPE1MARMRT",{"ALT_UNIT":"EA","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":gtin})]:
  fields(ET.SubElement(doc,segment),{"MATERIAL":article,**values})
 call("POST","/api/integrations/sap/artmas",status=202,raw=ET.tostring(idoc,encoding="utf-8"))
 meta("update RRL_ARTICULS set TYPE_W=0 where ACTICUL=:p_a",p_a=article)
 call("PUT",f"/api/finished-goods/skus/{article}/receiving-policy",{"expected_version":0,"marking_required":True,"serialized_weight_boxes":False,"profiles":[{"system_code":"CRPT","profile_code":"TOBACCO","profile_version":"DIR1","scan_mode":"UNIT"},{"system_code":"EGAIS","profile_code":"ALCOHOL","profile_version":"DIR1","scan_mode":"UNIT"}]})
 meta("insert into RRL_WARES(ID,NAME,PREFIX,DEFAULT_RECEIVE_CELL)values(:p_ware,:p_name,'QW',:p_receive)",p_ware=ware,p_name="Own180 "+tag,p_receive=receive)
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:p_ware,'NONE',0)",p_ware=ware)
 for cell,is_pick in [(receive,0),(pick,1),(storage,0),("CPT_"+str(ware),0)]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:p_cell,:p_ware,0,0,0,:p_pick,:p_system,0,0)",p_cell=cell,p_ware=ware,p_pick=is_pick,p_system=int(cell.startswith("CPT_")))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p_cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p_cell=cell)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:p_ware,:p_a,:p_pick,0,0,'DIRECT')",p_ware=ware,p_a=article,p_pick=pick)
 supply=ET.Element("WarehouseSupplyOrder",version="2")
 fields(supply,{"Sender":"OWN.QA.SAP","MessageId":"DIRECT1294.SUPPLY:"+tag,"OrderNumber":"D1294:"+tag,"Revision":1,"WarehouseId":ware,"ReceiveCell":receive,"Supplier":"Own180 software fixture"})
 line=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line,{"LineNumber":"1","Material":article});ET.SubElement(line,"Quantity",unit="EA").text="12"
 imported=call("POST","/api/integrations/sap/supply-orders",status=202,raw=ET.tostring(supply,encoding="utf-8"))
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 body={"operation_id":"DIRECT1294.RECEIVE:"+tag,"line_number":"1","sscc":sscc,"quantity":"12","product_barcode":gtin,"supplier_batch":"PB:"+tag,"expiry_date":"2030-01-01","gross_weight":"12"}
 units=[{"unit_id":str(i),"quantity":"1","codes":[
   {"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},
   {"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]}for i in range(1,13)]
 body["units"]=units;body.pop("product_barcode",None)
 from app.services.picking_service import PickingService
 from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
 from app.modules.inventory.contracts_stock import StockCommand
 from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
 from app.modules.platform.public import read_oracle_json
 from app.oracle_gateway import OracleGateway
 picking=PickingService();orders=[];plans=[];wave=None;bookings=[];case_types=set()
 def post(kind,source,metadata,op=None):
  return StockPosting().post(StockCommand(operation_id=op or "DIRECT1294:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0]
 ctx={"stage":"METADATA","tag":tag,"warehouse":ware,"article":article,"source":sscc,"cell":receive,"gtin":gtin,"supply":imported,"revision":revision,"units":units}
 def save():Path("tmp/context1294.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 save()
 result=call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201);ctx["receipt"]=result;save()
 order=seq("RRL_CUSTOMER_ORDER_SQ")
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,:n,:customer,:ware)",id=order,n="B02.1294:"+tag,customer=customer,ware=ware)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,5,'EA')",o=order,a=article)
 ctx["order"]=order;save()
 plan=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));ctx["plan"]=plan;save()
 wave=picking.create_wave(PickWaveCreateRequest(wave_code="B02.1294:"+tag,ware_id=ware,created_by="admin"));ctx["wave"]=wave;save()
 picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
 picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
 picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="B02.LAUNCH1294:"+tag))
 post("WAVE_PICK_RELEASE",{"wave_id":wave},{},op="B02.RELEASE1294:"+tag)
 q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE,l.PLANNED_QTY,t.PALLET_TYPE_ID from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:w",w=wave)
 case,line,carrier,cell,quantity,case_type=q.fetchone()
 ctx.update(case=int(case),line=int(line),carrier=carrier,cell=cell,quantity=str(quantity),case_type=int(case_type));save()
 tare="/api/inventory/tare"
 availability=call("GET",tare+f"/warehouses/{ware}/availability");current=next(x for x in availability if x["pallet_type_id"]==case_type)
 call("POST",tare+"/count",{"operation_id":"B02.TARE.COUNT1294:"+tag,"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"1","expected_version":current["balance_version"]or 0,"reason":"Own dev B02 UI fixture","decision_reference":"B02.1294:"+tag})
 call("POST",tare+"/book",{"operation_id":"B02.TARE.BOOK1294:"+tag,"place_kind":"CASE","place_id":str(case)})
 call("POST",f"/api/case-pick/tasks/{case}/claim",{});call("POST",f"/api/case-pick/tasks/{case}/start",{})
 q.execute("select u.UNIT_ID,u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=:w and r.SOURCE_LINE_ID=(select PICK_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:l)and r.BASE_QTY>0 order by u.PHYSICAL_UNIT_KEY",w=wave,l=line)
 selected=q.fetchall();assert len(selected)==5
 ctx["scans"]=[code for unit_id,_ in selected for code in units[int(unit_id)-1]["codes"]];ctx["stage"]="READY_FOR_UI";save()
 print(json.dumps({k:v for k,v in ctx.items()if k not in("scans","units","supply")}))
