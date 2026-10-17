"""Authenticated actor; current native CASE manage authority decides admission."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from ...platform.public import AdminUser, get_current_user
from ..contracts_case_empty import CaseEmptyInput, CaseEmptyPort, case_empty_service
from ..contracts_stock import StockPostingError

router = APIRouter(prefix="/api/case-pick", tags=["case-empty-disposition"])


@router.post("/tasks/{task_id}/empty-disposition")
def dispose(body: CaseEmptyInput, task_id: int = Path(gt=0),
            user: AdminUser = Depends(get_current_user),
            service: CaseEmptyPort = Depends(case_empty_service)) -> dict[str, Any]:
    try:
        return service.dispose(task_id, body, user.username)
    except StockPostingError as exc:
        status = 403 if exc.oracle_code == 20882 else 409 if (
            exc.oracle_code and 20800 <= exc.oracle_code <= 20999) else 503
        raise HTTPException(status, dict(code=exc.code, message=exc.rule_reason,
            operation_id=body.operation_id, outcome_confirmed=False,
            retry_same_operation_id=True)) from exc
