import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py");s=p.read_text(encoding="utf-8")
s=s.replace("m.TARGET_LOCATION,m.QUANTITY,m.UNIT_CODE ","m.TARGET_LOCATION,to_char(m.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),m.UNIT_CODE ",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8")
needle='    units_by_movement: dict[str, list[str]] = Field(default_factory=dict)'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    birth_captures: dict[str, dict[str, Any]] = Field(default_factory=dict)',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py");s=p.read_text(encoding="utf-8")
s=s.replace('{"units_by_movement": request.units_by_movement}','{"units_by_movement": request.units_by_movement, **({"birth_captures": request.birth_captures} if request.birth_captures else {})}')
out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/125_inventory_birth.sql");s=p.read_text(encoding="utf-8")
s=s.replace("  if n>0 then\n   if legacy is null then raise_application_error(-20887,'INVENTORY_CELL_HAS_STOCK: count existing lots');end if;","  if n>0 and legacy is not null then",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py");s=p.read_text(encoding="utf-8")
s+='''

class InventoryLotBirthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1,max_length=100)
    revision_id: int = Field(strict=True,ge=1)
    uid: str = Field(min_length=1,max_length=150)
    cell: str = Field(min_length=1,max_length=60)
    article: str = Field(min_length=1,max_length=160)
    quantity: Decimal = Field(gt=0,max_digits=27,decimal_places=9,allow_inf_nan=False)
    expiry_date: date
    price: Decimal = Field(ge=0,max_digits=27,decimal_places=9,allow_inf_nan=False)
    reason: str = Field(min_length=1,max_length=1000)
    capture: dict[str, Any] | None = None


@router.post("/inventory/lots")
def register_inventory_lot(request: InventoryLotBirthRequest,
    user: AdminUser=Depends(require_permission("stock_inventory_count"))) -> dict:
    from ..infrastructure.stock_posting_uow import StockPosting
    metadata=request.model_dump(mode="json",exclude={"operation_id","revision_id","capture"})
    if request.capture is not None:metadata["birth_captures"]={request.uid:request.capture}
    return StockPosting().post(StockCommand(operation_id=request.operation_id,
        command_type="INVENTORY_REGISTER_LOT",actor=user.username,lines=(),
        source={"revision_id":request.revision_id},metadata=metadata))
'''
if "from datetime import date" not in s:s="from datetime import date\nfrom decimal import Decimal\n"+s
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
