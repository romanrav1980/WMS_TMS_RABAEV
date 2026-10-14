"""Read current weighted whole boxes before using the existing pick planner."""
from fastapi import APIRouter, Depends, Path
from ...platform.public import AdminUser, require_permission
from ..contracts_weighted_plan import WeightedPlanPort, WeightedBoxChoiceRequest, WeightedChoiceCancelRequest, weighted_plan_service

router = APIRouter(prefix="/api/picking", tags=["weighted-planning"])


@router.get("/order-rows/{row}/weighted-box-options")
def weighted_box_options(row: int = Path(ge=1),
                         user: AdminUser = Depends(require_permission("pick_plan_create")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.options(row, user.username)

@router.get("/order-rows/{row}/weighted-box-approval-preview")
def weighted_box_approval_preview(row: int = Path(ge=1),
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.approval_options(row, user.username)


@router.post("/weighted-box-choices")
def approve_weighted_box(body: WeightedBoxChoiceRequest,
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.approve(body, user.username)


@router.post("/weighted-box-choices/{choice}/cancel")
def cancel_weighted_box(choice: str, body: WeightedChoiceCancelRequest,
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.cancel(choice, body.reason, user.username)
