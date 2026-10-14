"""Weighted box scanning feeds the existing CASE posting command."""
from fastapi import APIRouter, Depends, HTTPException
from ...platform.public import AdminUser, require_permission
from ..contracts_weighted_case import WeightedCaseRequest, WeighedLineRequest, WeightedCasePort, weighted_case_service

router = APIRouter(prefix="/api/case-pick", tags=["case-pick"])


@router.post("/tasks/{task}/lines/{line}/weighted-box")
def confirm_weighted_box(task: int, line: int, body: WeightedCaseRequest,
                         user: AdminUser = Depends(require_permission("case_pick_execute")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    try:
        return {"case_pick_task_id": task, "case_pick_line_id": line,
                **service.confirm(task, line, body, user.username)}
    except ValueError as exc:
        raise HTTPException(409, {"code": "WEIGHTED_BOX_SCAN_REJECTED", "message": str(exc), "outcome_confirmed": True, "retry_same_operation_id": False}) from exc


@router.post("/tasks/{task}/lines/{line}/weigh-line")
def confirm_weighed_line(task: int, line: int, body: WeighedLineRequest,
                         user: AdminUser = Depends(require_permission("case_pick_execute")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    try:
        return {"case_pick_task_id": task, "case_pick_line_id": line,
                **service.weigh_line(task, line, body, user.username)}
    except ValueError as exc:
        raise HTTPException(409, {"code": "WEIGHED_CASE_SOURCE_REJECTED", "message": str(exc),
                                 "outcome_confirmed": True, "retry_same_operation_id": False}) from exc


@router.get("/tasks/{task}/lines/{line}/order-weight-preview")
def order_weight_preview(task: int, line: int,
                         user: AdminUser = Depends(require_permission("case_pick_execute")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    return service.weight_preview(task, line, user.username)


@router.get("/shorts/{short}/weight-preview")
def short_weight_preview(short: int,
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    return service.short_weight_preview(short, user.username)
