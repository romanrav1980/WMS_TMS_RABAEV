from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py");s=p.read_text(encoding="utf-8").replace('router=APIRouter','from .task_scan_routes import UnitScan\nrouter=APIRouter',1).replace("class Dispose(Operation):","class Dispose(Operation):\n    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)")
s=s.replace("body.decision_reference,user.username)","body.decision_reference,user.username,[item.model_dump()for item in body.scans])",1);out[str(p)]=s
for name in["contracts_disposal.py","infrastructure/return_disposal.py"]:
 p=Path("api/wms_api_server/app/modules/inventory")/name;s=p.read_text(encoding="utf-8").replace("reference: str,actor: str) -> dict[str,Any]:","reference: str,actor: str,scans: list[dict[str,str]]|None=None) -> dict[str,Any]:",1)
 if name.startswith("infrastructure"):
  s=s.replace("from ..contracts_stock import StockCommand","from ..contracts_stock import StockCommand\nfrom ..domain.mark_identity import normalize_unit_scan_codes")
  needle='        return self.posting.post(StockCommand(operation_id=operation_id'
  s=s.replace(needle,'        scan_metadata={"unit_scans":normalize_unit_scan_codes(scans)}if scans else {}\n'+needle,1)
  s=s.replace('"decision_reference":reference}))','"decision_reference":reference,**scan_metadata}))',1)
  s=s.replace('        return self.gateway.fetch_all("""select r.','        rows=self.gateway.fetch_all("""select r.')
  s=s.replace('req.OPERATION_ID REQUEST_OPERATION_ID,','(select json_object(\'supported\'value case when min(p.SCAN_MODE)=\'UNIT\'and max(p.SCAN_MODE)=\'UNIT\'then \'true\'else \'false\'end format json,\'physical_unit_count\'value(select count(*)from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=r.UID_PALLET and u.CURRENT_CELL=x.CELL and u.STOCK_STATUS=\'AVAILABLE\'),\'expected_scan_count\'value count(*)*(select count(*)from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=r.UID_PALLET and u.CURRENT_CELL=x.CELL and u.STOCK_STATUS=\'AVAILABLE\'),\'profiles\'value json_arrayagg(json_object(\'system_code\'value p.SYSTEM_CODE,\'profile_code\'value p.PROFILE_CODE,\'profile_version\'value p.PROFILE_VERSION,\'scan_mode\'value p.SCAN_MODE)order by p.SYSTEM_CODE,p.PROFILE_CODE returning clob) format json returning clob)from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=r.ARTICLE having count(*)>0) MARKED_UNIT_CONTROL,\n        req.OPERATION_ID REQUEST_OPERATION_ID,',1)
  s+='\n'if not s.endswith('\n')else''
  s=s.replace('fetch first 100 rows only""",{"ware":ware_id})','fetch first 100 rows only""",{"ware":ware_id})\n        for row in rows:row["marked_unit_control"]=read_oracle_json(row.get("marked_unit_control"))if row.get("marked_unit_control")else None\n        return rows')
 out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
