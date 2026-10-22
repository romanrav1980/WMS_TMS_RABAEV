"""TRADECASE exceptions of one warehouse: quarantine, quality cases (decision, posted write-off) and count discrepancies."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from ...platform.public import AdminUser, get_current_user
from ..contracts_quality_case import QualityCaseCommand, QualityCaseError, QualityCasePort, QualityWriteOff, QuarantineMove, quality_case_service

router = APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/exceptions", tags=["tradecase-exceptions"])


def _call(run: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return run()
    except QualityCaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "outcome_confirmed": exc.status != 503,
                                         "retry_same_operation_id": exc.status == 503}) from exc


@router.get("")
def overview(warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
             service: QualityCasePort = Depends(quality_case_service)) -> dict[str, Any]:
    return _call(lambda: service.overview(warehouse, user.username))


@router.get("/cases/{case}")
def detail(warehouse: int = Path(gt=0), case: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
           service: QualityCasePort = Depends(quality_case_service)) -> dict[str, Any]:
    return _call(lambda: service.detail(warehouse, case, user.username))


@router.post("/cases")
def command(body: QualityCaseCommand, warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
            service: QualityCasePort = Depends(quality_case_service)) -> dict[str, Any]:
    return _call(lambda: service.command(warehouse, body, user.username))


@router.post("/quarantine-moves")
def quarantine_move(body: QuarantineMove, warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
                    service: QualityCasePort = Depends(quality_case_service)) -> dict[str, Any]:
    return _call(lambda: service.quarantine_move(warehouse, body, user.username))


@router.post("/write-offs")
def write_off(body: QualityWriteOff, warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
              service: QualityCasePort = Depends(quality_case_service)) -> dict[str, Any]:
    return _call(lambda: service.write_off(warehouse, body, user.username))
