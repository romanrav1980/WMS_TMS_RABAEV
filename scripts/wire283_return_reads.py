from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..contracts_store_returns import StoreReturnReceiveError","from ..contracts_store_returns import StoreReturnReceiveError\nfrom . import return_receiving_reads as reads")
s=s.replace(' as cursor:\n                cursor.execute(', ' as cursor:\n                reads.require_scope(cursor,ware_id,actor,"warehouse_settings_edit")\n                cursor.execute(')
s=s.replace("return self.policy(ware_id)","return self.policy(ware_id,actor)")
a=s.index("    def policy(");b=s.index("    def confirm(",a)
s=s[:a]+"""    def policy(self,ware_id: int,actor: str) -> dict[str,Any]:
        return reads.policy(self.gateway,ware_id,actor)

    def page(self,ware_id: int,after: str,limit: int,actor: str) -> dict:
        return reads.page(self.gateway,ware_id,actor,after,limit)

    def source(self,ware_id: int,pickup_id: str,actor: str) -> dict:
        return reads.source(self.gateway,ware_id,pickup_id,actor)

    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        result=reads.page(self.gateway,ware_id,actor,limit=100,proof=True)
        if result["has_more"]:raise StoreReturnReceiveError("RETURN_RECEIVING_USE_PAGED_QUEUE","Откройте очередь с продолжением списка")
        return result["items"]

"""+s[b:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_store_returns.py");s=p.read_text(encoding="utf-8")
s=s.replace("def policy(self,ware_id: int)", "def policy(self,ware_id: int,actor: str)")
s=s.replace("class StoreReturnReceivePort(Protocol):","class StoreReturnReceivePort(Protocol):\n    def page(self,ware_id: int,after: str,limit: int,actor: str) -> dict: ...\n    def source(self,ware_id: int,pickup_id: str,actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("from fastapi import APIRouter,Depends,HTTPException","from fastapi import APIRouter,Depends,HTTPException,Query")
s=s.replace("    return service.policy(ware_id)","    try:return service.policy(ware_id,user.username)\n    except StoreReturnReceiveError as exc:raise failure(exc)from exc",1)
s+="""
@router.get("/warehouses/{ware_id}/pending-page")
def pending_page(ware_id: int,after: str=Query(default="",max_length=100),limit: int=Query(default=20,ge=1,le=100),
                 user: AdminUser=Depends(require_permission("warehouse_return_receive")),
                 service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict:
    if ware_id<1:raise HTTPException(422,"Positive warehouse required")
    try:return service.page(ware_id,after,limit,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc)from exc

@router.get("/warehouses/{ware_id}/pickups/{pickup_id}/source")
def selected_source(ware_id: int,pickup_id: str,user: AdminUser=Depends(require_permission("warehouse_return_receive")),
                    service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict:
    if ware_id<1 or not 1<=len(pickup_id)<=100:raise HTTPException(422,"Positive warehouse and pickup required")
    try:return service.source(ware_id,pickup_id,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc)from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
