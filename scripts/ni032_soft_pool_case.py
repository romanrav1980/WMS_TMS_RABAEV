"""One isolated stock pool: 40/30/30, repeated calculations and cancellation."""
import json,sys,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.pool_service import PoolService
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.services.picking_service import PickingService
from app.schemas import PickWaveCreateRequest,PickWaveAddPlanRequest
from app.modules.master_data.infrastructure.allocation_policy import AllocationPolicy
from app.modules.master_data.api.allocation_routes import AllocationPolicyInput
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_stock import StockCommand
from fastapi import HTTPException
cfg=get_settings();tag=uuid4().hex[:10];article="QPOOL"+tag;cell="QL"+tag;lot="QPOOL-"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor();conn.call_timeout=15000
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):
  q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def post(kind,source,body):
  return StockPosting().post(StockCommand(operation_id="POOL.QA:"+uuid4().hex,command_type=kind,actor="admin",lines=(),source=source,metadata=body))
 meta("declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL='DS-BASE-D10';r.ACTICUL:=:a;r.BARCODE_SHT:=:bc;insert into RRL_ARTICULS values r;end;",a=article,bc="QP"+tag)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'SOFT pool QA' from RRL_STOCK_UOM_CONVERSION where ARTICUL='DS-BASE-D10'",a=article)
 meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,1,0,0,0,0,0)",c=cell)
 for kind,value in (("SKU",article),("CELL",cell)):
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key(:kind,:key),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",kind=kind,key=value)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));conn.commit()
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 orders=[];lines=[]
 for n,qty in enumerate((40,30,30)):
  oid,lid=seq("RRL_CUSTOMER_ORDER_SQ"),seq("RRL_CUSTOMER_ORDER_ROW_SQ");orders.append(oid);lines.append(lid)
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,STATUS,SHIPMENT_DATE) values(:id,:no,:customer,1,'OPEN',trunc(sysdate)+1)",id=oid,no=lot+str(n),customer=customer)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS) values(:id,:o,1,:a,'EA',:qty,1,'OPEN')",id=lid,o=oid,a=article,qty=qty)
 gateway=OracleGateway();policy=AllocationPolicy(gateway);service=PoolService(gateway);wave=None
 q.execute("select CELL from RRL_CELLS where WARE_ID=1 and OTBOR=1 and rownum=1");pick_cell=q.fetchone()[0]
 try:
  ReceiptConfiguration(gateway).sku_rule(1,article,{"pick_cell":pick_cell,"temp_min":None,"temp_max":None,"min_shelf_days":0},"admin")
  policy.set(1,article,AllocationPolicyInput(expected_version=1,stock_class="DRY_RACK",ship_from_stock=None,pick_step="1"),"admin")
  post("INVENTORY_REGISTER_LOT",{"revision_id":revision},{"uid":lot,"cell":cell,"article":article,"quantity":"100","expiry_date":"2030-01-01","price":0,"reason":"Bounded SOFT pool case"})
  started=time.perf_counter();preview=service.preview(1,article);elapsed_ms=round((time.perf_counter()-started)*1000,2);assert preview["available_quantity"]=="100",preview
  operation="POOL.QA.CALCULATE:"+tag
  result=service.allocate(1,article,operation,"admin")
  assert result["allocated_quantity"]=="100" and [x["quantity"] for x in result["allocations"]]==["40","30","30"],result
  assert service.allocate(1,article,operation,"admin")==result
  with ThreadPoolExecutor(max_workers=2) as executor:
   futures=[executor.submit(service.allocate,1,article,"POOL.QA.PARALLEL:"+tag+str(n),"admin") for n in range(2)]
   assert all(f.result()["allocated_quantity"]=="100" for f in futures)

  q.execute("select count(*),sum(QTY),sum(nvl(BASE_QTY,0)),sum(case when WARE_ID is not null or UID_PALLET is not null or PICK_WAVE_ID is not null then 1 else 0 end) from RRL_STOCK_RESERVATION where POOL_WARE_ID=1 and ARTICUL=:a and STATUS='ACTIVE'",a=article)
  assert q.fetchone()==(3,100,0,0),"Duplicate or physical SOFT binding"
  meta("update RRL_CUSTOMER_ORDER set STATUS='CANCELLED' where CUSTOMER_ORDER_ID=:id",id=orders[1])
  after=service.allocate(1,article,"POOL.QA.CANCEL:"+tag,"admin");assert after["allocated_quantity"]=="70",after
  q.execute("select SOURCE_LINE_ID,QTY from RRL_STOCK_RESERVATION where POOL_WARE_ID=1 and ARTICUL=:a and STATUS='ACTIVE' order by SOURCE_LINE_ID",a=article)
  assert q.fetchall()==[(lines[0],40),(lines[2],30)]
  current=policy.get(1,article)
  policy.set(1,article,AllocationPolicyInput(expected_version=current["policy_version"],stock_class="FRESH",ship_from_stock=None,pick_step="1"),"admin")
  fresh=service.allocate(1,article,"POOL.QA.FRESH:"+tag,"admin");assert fresh["allocated_quantity"]=="0" and fresh["from_stock"] is False,fresh
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot and CELL=:c",lot=lot,c=cell);assert q.fetchone()==(100,0)
  current=policy.get(1,article)
  policy.set(1,article,AllocationPolicyInput(expected_version=current["policy_version"],stock_class="DRY_RACK",ship_from_stock=None,pick_step="1"),"admin")
  service.allocate(1,article,"POOL.QA.WAVE.PREP:"+tag,"admin")
  plan,pl,pt,pr=[seq(name) for name in ("RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_RESERVATION_SQ")]
  meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS,TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY) values(:id,:o,:customer,1,'PLANNED_FULL',40,40)",id=plan,o=orders[0],customer=customer)
  meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,CASE_PICK_QTY,STATUS) values(:id,:p,:line,:a,40,40,40,'PLANNED_FULL')",id=pl,p=plan,line=lines[0],a=article)
  meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,TASK_TYPE,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,QTY) values(:id,:p,:pl,:o,'CASE_PICK',:a,:lot,:c,40)",id=pt,p=plan,pl=pl,o=orders[0],a=article,lot=lot,c=cell)
  meta("insert into RRL_PICK_RESERVATION(PICK_RESERVATION_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_TASK_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,RESERVATION_SCOPE,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,RESERVED_QTY) values(:id,:p,:pl,:pt,:o,:customer,'CASE',:a,:lot,:c,40)",id=pr,p=plan,pl=pl,pt=pt,o=orders[0],customer=customer,a=article,lot=lot,c=cell)
  picking=PickingService(gateway)
  wave=picking.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=1,created_by="admin"))
  picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  command=StockCommand(operation_id="POOL.QA.WAVE.LAUNCH:"+tag,command_type="WAVE_LAUNCH",actor="admin",lines=(),source={"wave_id":wave},metadata={})
  launched=StockPosting().post(command);assert StockPosting().post(command)==launched
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot and CELL=:c",lot=lot,c=cell);assert q.fetchone()==(100,40)
  q.execute("select QTY,STATUS from RRL_STOCK_RESERVATION where POOL_WARE_ID=1 and ARTICUL=:a and SOURCE_LINE_ID=:line and STATUS='CONSUMED'",a=article,line=lines[0]);assert q.fetchone()==(0,"CONSUMED")
  remaining=service.allocate(1,article,"POOL.QA.WAVE.AFTER:"+tag,"admin");assert remaining["allocated_quantity"]=="30",remaining
  print(json.dumps({"passed":True,"article":article,"orders":orders,"lines":lines,"operation":operation,"wave":wave,"preview_ms":elapsed_ms,"case":"40/30/30 + replay + concurrent calculations + unique pool + cancellation + FRESH no physical reserve"}),flush=True)
 finally:
  if wave is not None:
   post("WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":wave},{"reason":"Close own pool-wave case","only_cancelled_replenishment":0,"reservation_kind":None})
  for oid in orders:meta("update RRL_CUSTOMER_ORDER set STATUS='CANCELLED' where CUSTOMER_ORDER_ID=:id",id=oid)
  service.allocate(1,article,"POOL.QA.CLEAN:"+tag,"admin")
  q.execute("select REMAIN,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot and CELL=:c",lot=lot,c=cell);stock=q.fetchone()
  if stock and stock[0]>0:
   post("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Close own SOFT fixture","counts":[{"uid":lot,"cell":cell,"article":article,"unit":stock[1],"quantity":"0","expected_stock_version":int(stock[2]),"unit_keys":[]}]})
  print("Own stock restored through root, demand/reservation/operation history retained",flush=True)
