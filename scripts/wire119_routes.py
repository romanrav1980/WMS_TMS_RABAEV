from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
if "def unload(" not in s:
 s+='''

class PhysicalAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    plan_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    scan_pallet: str = Field(strict=True,min_length=1,max_length=200)

class Unload(PhysicalAction):
    scan_vehicle: str = Field(strict=True,min_length=1,max_length=60)
    scan_dock: str = Field(strict=True,min_length=1,max_length=60)

class Receive(PhysicalAction):
    scan_cell: str = Field(strict=True,min_length=1,max_length=60)
    scan_article: str = Field(strict=True,min_length=1,max_length=128)
    article: str = Field(strict=True,min_length=1,max_length=160)
    quantity: str = Field(strict=True,min_length=1,max_length=40,pattern=r"^[0-9]+(\\.[0-9]+)?$")
    base_uom: str = Field(strict=True,min_length=1,max_length=20)

def physical(kind: str,body: PhysicalAction,user: AdminUser,service: InterwarehousePort) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.receive_action(kind,body.operation_id,body.plan_operation_id,body.model_dump(exclude={"operation_id","plan_operation_id"}),user.username)
    except StockPostingError as exc:
        confirmed = exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed}) from exc

@router.post("/unload")
def unload(body: Unload,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    return physical("INTERWARE_UNLOAD",body,user,service)

@router.post("/receive")
def receive(body: Receive,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    return physical("INTERWARE_RECEIVE",body,user,service)
'''
 p.write_text(s,encoding="utf-8")
