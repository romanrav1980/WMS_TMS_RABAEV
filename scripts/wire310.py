from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");t=p.read_text(encoding="utf-8")
t=t.replace("class Receive(PhysicalAction):","class AggregationScan(UnitScan):\n    level: Literal['BOX','PALLET']\n\nclass Receive(PhysicalAction):",1)
t=t.replace("    scans: list[UnitScan] = Field(default_factory=list,max_length=20000)","    scans: list[UnitScan] = Field(default_factory=list,max_length=20000)\n    aggregation_scans: list[AggregationScan] = Field(default_factory=list,max_length=1000)",1)
t=t.replace("    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)","    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)\n    aggregation_scans: list[AggregationScan]=Field(default_factory=list,max_length=1000)",1);out[p.as_posix()]=t
p=Path("api/wms_api_server/app/modules/inventory/domain/interwarehouse_scans.py")
out[p.as_posix()]='''"""Scanner evidence normalization; native Oracle resolves authoritative membership."""
from hashlib import sha256
from typing import Any
from .mark_identity import normalize_unit_scan_codes

def normalize_interwarehouse_scans(metadata: dict[str,Any]) -> dict[str,Any]:
    result=dict(metadata)
    scans=result.pop("scans",[])
    if scans:result["unit_scans"]=normalize_unit_scan_codes(scans)
    aggregations=result.get("aggregation_scans",[])
    if not aggregations:
        result.pop("aggregation_scans",None)
        return result
    normalized=[]
    if len(aggregations)>1000:raise ValueError("Maximum 1000 aggregation scans")
    for scan in aggregations:
        if set(scan)!={"system_code","profile_code","code","level"} or scan["level"]not in {"BOX","PALLET"}:
            raise ValueError("Exact aggregation scanner fields required")
        code=scan["code"]
        if not isinstance(code,str)or not code or len(code.encode("utf-8"))>4000 or "\\x00"in code:
            raise ValueError("Invalid aggregation scanner code")
        normalized.append(dict(system_code=scan["system_code"],profile_code=scan["profile_code"],
                               level=scan["level"],code_hash=sha256(code.encode("utf-8")).hexdigest()))
    result["aggregation_scans"]=normalized
    return result
'''
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");t=p.read_text(encoding="utf-8")
a=t.index("        metadata = dict(metadata)",t.index("    def receive_action("));b=t.index("        try:\n            return self.posting.post",a)
t=t[:a]+'''        from ..domain.interwarehouse_scans import normalize_interwarehouse_scans
        try:
            metadata=normalize_interwarehouse_scans(metadata)
        except ValueError as exc:
            raise StoreReturnReceiveError("INTERWARE_SCAN_INVALID",str(exc),422)from exc
'''+t[b:]
a=t.index("        from ..domain.mark_identity import normalize_unit_scan_codes",t.index("    def receive_recovery("));b=t.index("        return self.posting.post",a)
t=t[:a]+'''        from ..domain.interwarehouse_scans import normalize_interwarehouse_scans
        metadata=normalize_interwarehouse_scans(metadata)
'''+t[b:];out[p.as_posix()]=t
p=Path("scripts/source310_marked_case.py");t=Path("scripts/source305_marked_case.py").read_text(encoding="utf-8").replace("305","310")
t=t.replace("'QR1','UNIT'","'QR1','UNIT_OR_AGGREGATION'")
a=t.index('  born=api("POST","/api/inventory/stock-posting/inventory/lots"');b=t.index('\n  post("RESERVATION_CREATE"',a)
t=t[:a]+'''  sscc_prefix="100"+str(int(tag,16)).zfill(14)
  sscc=sscc_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(sscc_prefix)))%10)%10)
  aggregations=[
   dict(aggregation_id="CRPT.B1",system_code="CRPT",profile_code="TOBACCO",level="BOX",code="CRPT.B1:"+tag,unit_ids=["1"],children=[]),
   dict(aggregation_id="CRPT.B2",system_code="CRPT",profile_code="TOBACCO",level="BOX",code="CRPT.B2:"+tag,unit_ids=["2","3"],children=[]),
   dict(aggregation_id="CRPT.P",system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=sscc,unit_ids=[],children=["CRPT.B1","CRPT.B2"]),
   dict(aggregation_id="EGAIS.B",system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag,unit_ids=["1","2","3"],children=[])]
  scan_aggregations=[dict(system_code=a["system_code"],profile_code=a["profile_code"],level=a["level"],code=a["code"])for a in aggregations if a["aggregation_id"]in ["CRPT.P","EGAIS.B"]]
  manifest_op="IW310.MANIFEST:"+tag
  document=dict(contract_version="WmsTraceManifest.v1",source_kind="INVENTORY",source_document_id=revision,warehouse_id=ware,pallet_identifier=lot,article=article,base_uom="EA",policy_version=ctx["policy_version"],
   profile_versions=[dict(system_code=x["system_code"],profile_code=x["profile_code"],version=x["profile_version"])for x in ctx["profile_versions"]],units=units,aggregations=aggregations,document_reference="DEV310:physical sender")
  api("POST","/api/inventory/trace-manifests",dict(operation_id=manifest_op,manifest_json=json.dumps(document)),status=200)
  born=api("POST","/api/inventory/stock-posting/inventory/lots",{"operation_id":"IW310.BIRTH:"+tag,"revision_id":revision,"uid":lot,"cell":src,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":"0","reason":"Own310 sender aggregation exact physical units",
   "capture":{"units":[],"aggregations":scan_aggregations,"manifest_operation_id":manifest_op,"expected_policy_version":ctx["policy_version"],"expected_profile_versions":ctx["profile_versions"]}})
'''+t[b:]
t=t.replace('"source_quantity":"3","units":units}', '"source_quantity":"3","units":units,"aggregations":scan_aggregations,"manifest_operation_id":manifest_op}')
out[p.as_posix()]=t
print(json.dumps(out))
