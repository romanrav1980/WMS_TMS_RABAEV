exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.interwarehouse_scans import normalize_interwarehouse_scans
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.oracle_gateway import OracleGateway
import httpx
source=json.loads(Path("tmp/context316.json").read_text(encoding="utf-8"));p=Path("tmp/context314_received.json")
if p.exists():raise SystemExit("314 actual receipt exists; retained exact replay only")
cell="IR314"+source["tag"];op="IW314.RECEIVE:"+source["tag"];root=source["physical_root"]
client=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088/api/inventory/interwarehouse"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=cell)
  if not q.fetchone()[0]:
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell_code,:ware_no,0,0,0,0,0,0,0,0,1,1)",cell_code=cell,ware_no=source["target_warehouse"])
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=cell)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 r=client.post(base+"/unload",json=dict(operation_id="IW314.UNLOAD:"+source["tag"],plan_operation_id=source["plan_operation_id"],scan_pallet=root,scan_vehicle="QL"+source["tag"],scan_dock=source["inbound"]));assert r.status_code==200,r.text
 body=dict(operation_id=op,plan_operation_id=source["plan_operation_id"],scan_pallet=root,scan_cell=cell,scan_article=source["barcode"],article=source["article"],quantity="3",base_uom="EA",aggregation_scans=source["aggregations"])
 metadata=normalize_interwarehouse_scans({k:v for k,v in body.items()if k not in["operation_id","plan_operation_id"]})
 def native(meta,operation):
  req=dict(contract_version=2,operation_id=operation,command_type="INTERWARE_RECEIVE",actor="admin",source=dict(plan_operation_id=source["plan_operation_id"]),lines=[],units=[],metadata=meta);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 try:native(dict(metadata,scan_pallet=source["lot"]),"IW314.BAD.SCAN:"+source["tag"])
 except oracledb.DatabaseError as e:assert e.args[0].code==20886,str(e)
 else:raise AssertionError("Stock leaf scan bypassed physical upper place")
 finally:c.rollback()
 trial=native(metadata,op);assert trial["physical_tree_restored"]and trial["physical_unit_count"]==3
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_WMS_HU_LINK where PARENT_UID in(:top_id,:inner_id)and ACTIVE_FLAG=1",top_id=root,inner_id=source["inner_root"]);assert q.fetchone()[0]==2
 c.rollback()
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_WMS_HU_LINK where PARENT_UID in(:top_id,:inner_id)and ACTIVE_FLAG=1",top_id=root,inner_id=source["inner_root"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_INTERWARE_RECEIPT where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==0;c.rollback()
 r=client.post(base+"/receive",json=body);assert r.status_code==200,r.text;result=r.json()
 repeat=client.post(base+"/receive",json=body);assert repeat.status_code==200 and repeat.json()==result,repeat.text
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=source["lot"]);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_PALLETS where UID_PALLET in(:top_id,:inner_id)and HU_CURRENT_CELL=:cell_code and HU_SHIPPED_OPERATION is null",top_id=root,inner_id=source["inner_root"],cell_code=cell);assert q.fetchone()[0]==2
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
tree=WarehouseHu(OracleGateway()).preview(root,"admin");assert tree["warehouse"]==source["target_warehouse"]and len(tree["nodes"])==3 and tree["leaf_count"]==1
p.write_text(json.dumps(dict(source=source,body=body,result=result,tree=tree,cell=cell,operation_id=op),indent=2),encoding="utf-8")
print("PASS314 actual nested firstleg source316 -> whole receipt3 original physicalunits6codes; sameTOP/BOX identities/2newlinks/oldclosedhistory/P3H0; late rollback/replay/wrongleafscan denied; protected20-20")
