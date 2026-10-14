import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .slotting_demand_reader import SlottingDemand","from .slotting_demand_reader import SlottingDemand\nfrom .range_command import range_command\nfrom .range_apply import RangeApply")
s=s.replace("self.reader = SlottingDemand(gateway)","self.reader = SlottingDemand(gateway)\n        self.apply = RangeApply(gateway, self.reader)")
start=s.index('        request = json.dumps(body');end=s.index("        except oracledb.DatabaseError",start)
s=s[:start]+'''        try:
            with self.gateway.transaction("Native immutable slotting proposal command") as cur:
                return range_command(cur, ware, article, operation, action, actor, body, source)
''' +s[end:]
s=s.replace("    def get(self, ware:",'''    def approve(self, ware: int, article: str, proposal: str, operation: str, reason: str,
                geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]:
        return self.apply.approve(ware, article, proposal, operation, reason, geometry, compatibility, actor)

    def close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]:
        return self.apply.close(ware, article, mapping, operation, reason, actor)

    def get(self, ware:''')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_range_proposal.py");s=p.read_text(encoding="utf-8").replace("    def get(self, ware:",'''    def approve(self, ware: int, article: str, proposal: str, operation: str, reason: str,
                geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]: ...
    def close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]: ...
    def get(self, ware:''')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("router=APIRouter(",'''class ApproveRangeProposalInput(CancelRangeProposalInput):
    geometry_checked: bool
    product_compatibility_checked: bool

class CloseRangeDrainInput(CancelRangeProposalInput):
    pick_face_articul_id: int=Field(gt=0)

router=APIRouter(''')
s+="""
@router.post("/{proposal_id}/approve")
def approve(request: ApproveRangeProposalInput,proposal_id: str=Path(min_length=8,max_length=100),
            ware_id: int=Path(gt=0),article: str=Path(min_length=1,max_length=40),
            user: AdminUser=Depends(require_permission("pick_topology_edit")),
            service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str,Any]:
    try:return service.approve(ware_id,article.strip().upper(),proposal_id,request.operation_id,request.reason,
        request.geometry_checked,request.product_compatibility_checked,user.username)
    except SlottingError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("/actions/close-drain")
def close_drain(request: CloseRangeDrainInput,ware_id: int=Path(gt=0),article: str=Path(min_length=1,max_length=40),
                user: AdminUser=Depends(require_permission("pick_topology_edit")),
                service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str,Any]:
    try:return service.close(ware_id,article.strip().upper(),request.pick_face_articul_id,request.operation_id,request.reason,user.username)
    except SlottingError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
"""
out[str(p)]=s
print(json.dumps(out))
