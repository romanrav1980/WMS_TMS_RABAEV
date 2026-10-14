from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_range_proposal import RangeDraft,RangeProposalPort,range_proposal_service
from ..contracts_slotting import SlottingError
from .slotting_routes import SlottingScenarioInput

class SaveRangeProposalInput(SlottingScenarioInput):
    operation_id: str=Field(min_length=8,max_length=100)
    expected_source_signature: str=Field(pattern="^[0-9a-f]{64}$")
    reason: str=Field(min_length=8,max_length=2000)

class CancelRangeProposalInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=8,max_length=100)
    reason: str=Field(min_length=8,max_length=2000)

class ApproveRangeProposalInput(CancelRangeProposalInput):
    geometry_checked: bool
    product_compatibility_checked: bool

class CloseRangeDrainInput(CancelRangeProposalInput):
    pick_face_articul_id: int=Field(gt=0)

router=APIRouter(prefix="/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations",tags=["warehouse-slotting"])

@router.post("")
def save(request: SaveRangeProposalInput,ware_id: int=Path(gt=0),article: str=Path(min_length=1,max_length=40),
         user: AdminUser=Depends(require_permission("pick_topology_edit")),
         service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str,Any]:
    command=RangeDraft(request.operation_id,request.period_from,request.period_to_exclusive,
        request.declared_period_forecast,request.forecast_base_uom,request.declared_pallet_gross_weight_kg,
        [row.model_dump(mode="json")for row in request.recommendation_costs],request.expected_source_signature,request.reason,request.candidate_pick_route_id)
    try:return service.save(ware_id,article.strip().upper(),command,user.username)
    except SlottingError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.get("/{proposal_id}")
def get(proposal_id: str=Path(min_length=8,max_length=100),ware_id: int=Path(gt=0),article: str=Path(min_length=1,max_length=40),
        user: AdminUser=Depends(require_permission("pick_topology_view")),
        service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str,Any]:
    try:return service.get(ware_id,article.strip().upper(),proposal_id,user.username)
    except SlottingError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("/{proposal_id}/cancel")
def cancel(request: CancelRangeProposalInput,proposal_id: str=Path(min_length=8,max_length=100),
           ware_id: int=Path(gt=0),article: str=Path(min_length=1,max_length=40),
           user: AdminUser=Depends(require_permission("pick_topology_edit")),
           service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str,Any]:
    try:return service.cancel(ware_id,article.strip().upper(),proposal_id,request.operation_id,request.reason,user.username)
    except SlottingError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

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
