from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py');t=p.read_text(encoding='utf-8');needle='    def decisions('
addition='''    def group_source(self,load: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_source import InterwarehouseGroupSource
        return InterwarehouseGroupSource(self.gateway).read(load,actor)

'''
if 'def group_source(' not in t:t=t.replace(needle,addition+needle,1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py');t=p.read_text(encoding='utf-8').replace('class InterwarehousePort(Protocol):','class InterwarehousePort(Protocol):\n    def group_source(self,load: str,actor: str)->dict[str,Any]: ...');out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
addition='''@router.get("/source-loads/{load_id}/group-composition")
def group_source(load_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:
        return service.group_source(load_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

'''
if 'def group_source('not in t:t=t.replace('class Plan(BaseModel):',addition+'class Plan(BaseModel):',1)
out[p.as_posix()]=t
print(json.dumps(out))
