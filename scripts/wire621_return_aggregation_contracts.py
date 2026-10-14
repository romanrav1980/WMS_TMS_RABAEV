from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/public.py");v=p.read_text(encoding="utf-8")
v+='\nfrom .contracts_aggregation_scans import AggregationCodeScan\nfrom .domain.interwarehouse_scans import normalize_interwarehouse_scans\n';p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/delivery/api/return_custody_routes.py");v=p.read_text(encoding="utf-8")
v='from ...inventory.public import AggregationCodeScan\n'+v
v=v.replace("class CustodyCommand(BaseModel):","class CustodyCommand(BaseModel):\n    aggregation_scans: list[AggregationCodeScan]=Field(default_factory=list,max_length=1000)")
p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py");v=p.read_text(encoding="utf-8")
v='from ..contracts_aggregation_scans import AggregationCodeScan\n'+v
v=v.replace("class ReceiveStoreReturn(BaseModel):","class ReceiveStoreReturn(BaseModel):\n    aggregation_scans: list[AggregationCodeScan]=Field(default_factory=list,max_length=1000)")
p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py");v=p.read_text(encoding="utf-8")
v=v.replace("from ...inventory.public import normalize_unit_scan_codes","from ...inventory.public import normalize_interwarehouse_scans")
a='''        metadata=dict(metadata)
        scans=metadata.pop("scans",None)
        if scans:metadata["unit_scans"]=normalize_unit_scan_codes(scans)'''
assert v.count(a)==2
v=v.replace(a,'''        try:metadata=normalize_interwarehouse_scans(metadata)
        except (ValueError,KeyError,TypeError)as exc:raise StoreReceiptError("RETURN_SCAN_INPUT_INVALID",str(exc),422,operation_id)from exc''')
p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py");v=p.read_text(encoding="utf-8")
v=v.replace("from ..domain.mark_identity import normalize_unit_scan_codes","from ..domain.interwarehouse_scans import normalize_interwarehouse_scans")
a='''        metadata=dict(metadata)
        scans=metadata.pop("scans",None)
        if scans:metadata["unit_scans"]=normalize_unit_scan_codes(scans)'''
assert a in v
v=v.replace(a,'''        try:metadata=normalize_interwarehouse_scans(metadata)
        except (ValueError,KeyError,TypeError)as exc:raise StoreReturnReceiveError("RETURN_SCAN_INPUT_INVALID",str(exc),422,operation_id)from exc''')
p.write_text(v,encoding="utf-8")
print("621 shared registered aggregation scanner DTO/normalizer wired into original store handover/driver pickup/warehouse receipt; empty field omitted preserves old exact payload.")
