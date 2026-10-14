"""179 own weighted SKU, one physical box, exact KG, native replay and cleanup."""
import sys,json
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.contracts_stock import StockCommand, StockPostingError
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.master_data.infrastructure.receipt_policy import ReceiptPolicyRepository
from app.modules.master_data.contracts import ReceiptPolicyUpdate
from app.oracle_gateway import OracleGateway
s=get_settings();tag=uuid4().hex[:8];article="QW183"+tag.upper();uid="WEIGHT183:"+tag;cell="Q167S00cdc0ef51";gtin="04012345678901"
# Generate a genuine check digit for the owned synthetic GTIN.
gtin=gtin[:13]+str((10-sum(int(x)*(3 if i%2==0 else 1)for i,x in enumerate(gtin[:13]))%10)%10)
scan="(01)"+gtin+"(3103)004250(21)"+tag
posting=StockPosting();born=False
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 meta("declare r RRL_ARTICULS%rowtype;begin select *into r from RRL_ARTICULS where ACTICUL='QC16700CDC0EF51';r.ACTICUL:=:p_a;r.TYPE_W:=3;r.UNIT_TYPE:='KG';r.BARCODE_SHT:=:p_gtin;r.BARCODE_KOR:=:p_gtin;r.BARCODE_BL:=null;insert into RRL_ARTICULS values r;end;",p_a=article,p_gtin=gtin)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)values(:p_a,'KG','KG',1,1,1,6,'Own179 exact net weight')",p_a=article)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:p_a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p_a=article)
 policy=ReceiptPolicyRepository(OracleGateway()).replace(article,ReceiptPolicyUpdate(expected_version=0,marking_required=True,serialized_weight_boxes=True,profiles=[{"system_code":"CRPT","profile_code":"DAIRY","profile_version":"WB1","scan_mode":"UNIT"}]),"admin")
 assert policy["serialized_weight_boxes"]and policy["marking_required"]
 capture={"capture_mode":"WEIGHTED_BOXES","policy_version":1,"weighted_boxes":[{"barcode":scan,"codes":[{"system_code":"CRPT","profile_code":"DAIRY","code":"(01)"+gtin+"(21)"+tag+"(91)TESTKEY(92)TESTSIGNATURE"}],"gross_weight_kg":"4.500","volume_m3":"0.030","measurement_reference":"OWN183:manual software fixture"}]}
 def command(lot=uid,mass="4.25",cap=capture,op=None):
  return StockCommand(operation_id=op or "WEIGHT183.BIRTH:"+uuid4().hex,command_type="INVENTORY_REGISTER_LOT",actor="admin",source={"revision_id":233},metadata={"uid":lot,"cell":cell,"article":article,"quantity":mass,"expiry_date":"2030-01-01","price":"0","reason":"Own179 physical GS1 box","birth_captures":{lot:cap}},lines=())
 cmd=command(op="WEIGHT183.BIRTH:"+tag)
 try:
  result=posting.post(cmd);born=True
  assert posting.post(cmd)==result
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell)
  p,h=q.fetchone();assert Decimal(str(p))==Decimal("4.25")and h==0
  q.execute("select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM,CURRENT_UID,CURRENT_CELL,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p_uid",p_uid=uid)
  units=q.fetchall();assert len(units)==1,units
  assert Decimal(str(units[0][1]))==Decimal("4.25")and units[0][2]=="KG"
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=uid);assert q.fetchone()[0]==1
  q.execute("select GROSS_WEIGHT_KG,BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p_uid",p_uid=uid);gross,volume,reference,raw=q.fetchone();assert Decimal(str(gross))==Decimal("4.5")and Decimal(str(volume))==Decimal(".03")and reference and raw==scan
  for candidate in [command(lot=uid+":DUP"),command(lot=uid+":BAD",mass="4.24")]:
   try:posting.post(candidate);raise AssertionError("Invalid duplicate/mass accepted")
   except (ValueError,oracledb.DatabaseError,StockPostingError)as exc:print("Expected refusal",type(exc).__name__,str(exc)[:180],flush=True)
   q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:p_uid",p_uid=candidate.metadata["uid"]);assert q.fetchone()[0]==0
  print("PASS183 born one physical box/P4.25KG/H0/one applicable CRPT code/no legal ACK/exact replay/duplicate and mismatched mass refused",article,cmd.operation_id,flush=True)
 finally:
  if born:
   q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);version=int(q.fetchone()[0])
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:p_cell and STOCK_STATUS='AVAILABLE'",p_uid=uid,p_cell=cell);keys=[r[0]for r in q.fetchall()]
   posting.post(StockCommand(operation_id="WEIGHT183.CLEAN:"+tag,command_type="INVENTORY_COUNT",actor="admin",source={"revision_id":233},metadata={"reason":"Native owned179 fixture cleanup","counts":[{"uid":uid,"cell":cell,"article":article,"unit":"KG","quantity":"0","expected_stock_version":version,"unit_keys":keys}]},lines=()))
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 print("PASS183 native count cleanup, original135 P20H20 unchanged",flush=True)
