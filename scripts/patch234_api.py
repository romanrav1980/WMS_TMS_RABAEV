from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py");s=p.read_text(encoding="utf-8").replace("router=APIRouter","from .task_scan_routes import UnitScan\n\nrouter=APIRouter",1).replace("class ReceiveStoreReturn(BaseModel):","class ReceiveStoreReturn(BaseModel):\n    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py");s=p.read_text(encoding="utf-8").replace("from ...platform.public import stock_configuration_transaction","from ...platform.public import stock_configuration_transaction,read_oracle_json\nfrom ..domain.mark_identity import normalize_unit_scan_codes")
s=s.replace('        return self.gateway.fetch_all("""\n            select p.', '        rows=self.gateway.fetch_all("""\n            select p.')
s=s.replace("                   a.ARTICLE,a.LOT_UID","                   RRL_STORE_RETURN_UNIT_CORE.approved_proof(a.OPERATION_ID) MARKED_UNIT_CONTROL,\n                   a.ARTICLE,a.LOT_UID")
s=s.replace('        """,{"ware":ware_id})\n\n    def confirm','        """,{"ware":ware_id})\n        for row in rows:row["marked_unit_control"]=read_oracle_json(row.get("marked_unit_control")) if row.get("marked_unit_control") else None\n        return rows\n\n    def confirm')
s=s.replace('        return self.post("STORE_RETURN_RECEIVE"', '        metadata=dict(metadata)\n        scans=metadata.pop("scans",None)\n        if scans:metadata["unit_scans"]=normalize_unit_scan_codes(scans)\n        return self.post("STORE_RETURN_RECEIVE"');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
