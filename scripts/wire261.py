from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")+'\nfrom .domain.receipt_layout import propose_receipt_layout\n';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py");s=p.read_text(encoding="utf-8")+'''
def pallet_plan(gateway: Any, order: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    from hashlib import sha256
    import json
    from ...inventory.public import propose_receipt_layout
    source = supply_detail(gateway, order, None, actor)
    lines = [line for line in source["lines"] if line["line_number"] == body["line_number"]]
    if len(lines) != 1:
        raise ValueError("RECEIPT_LAYOUT_CURRENT_LINE_REQUIRED")
    line = lines[0]
    signature = sha256(json.dumps([source["order_id"], source["revision"], source["ware_id"],
        line["line_number"], line["planned_qty"], line["accepted_qty"], line["norma_ukladki"]],
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    if body.get("expected_source_signature") is not None and body["expected_source_signature"] != signature:
        raise ValueError("RECEIPT_LAYOUT_SOURCE_CHANGED")
    proposal = propose_receipt_layout(line["remaining_qty"], line["base_uom"], line["norma_ukladki"],
        body.get("pallet_count"), body.get("quantities"), body.get("quantity_step"))
    return {"order_id": order, "revision": source["revision"], "warehouse_id": source["ware_id"],
            "line_number": line["line_number"], "source_signature": signature,
            "remaining_quantity": line["remaining_qty"], "consistent_snapshot": True,
            "read_only": True, **proposal}
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py");s=p.read_text(encoding="utf-8")+'''
    def pallet_plan(self, order_id: str, body: dict[str, Any], actor: str) -> dict:
        from .supply_reads import pallet_plan
        return pallet_plan(self.gateway, order_id, body, actor)
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/application/receipt_ports.py");s=p.read_text(encoding="utf-8").replace('    def get(self, order_id: str, actor: str) -> dict: ...','    def get(self, order_id: str, actor: str) -> dict: ...\n    def pallet_plan(self, order_id: str, body: dict, actor: str) -> dict: ...');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/api/supply_routes.py");s=p.read_text(encoding="utf-8").replace('import xml.etree.ElementTree as ET','import xml.etree.ElementTree as ET\nfrom decimal import Decimal\nfrom pydantic import BaseModel, ConfigDict, Field')
s+='''

class PalletPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_number: str = Field(min_length=1, max_length=20)
    pallet_count: int | None = Field(default=None, strict=True, ge=1, le=200)
    quantities: list[Decimal] | None = Field(default=None, min_length=1, max_length=200)
    quantity_step: Decimal | None = Field(default=None, gt=0, decimal_places=6)
    expected_source_signature: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


@router.post("/{order_id}/pallet-plan")
def supply_pallet_plan(order_id: str, body: PalletPlan,
                       user: AdminUser = Depends(require_permission("sap_supply_view")),
                       service: SupplyOrders = Depends(supply_service)) -> dict:
    try:
        return service.pallet_plan(order_id, body.model_dump(mode="json", exclude_none=True), user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
