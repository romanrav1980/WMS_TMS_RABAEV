"""Extra stop outside the main route: evaluation on the native recalculation, decisions and the per-trip ban on new points."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, require_permission
from ..contracts_extra_stop import ExtraStopCommand, ExtraStopError, ExtraStopPort, Zone, extra_stop_service

router = APIRouter(prefix="/api/transport/preflight/trips/{trip_id}/extra-stops", tags=["transport-preflight"])


def _call(run: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return run()
    except ExtraStopError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "outcome_confirmed": exc.status != 503,
                                         "retry_same_operation_id": exc.status == 503}) from exc


@router.get("")
def evaluate(trip_id: int = Path(gt=0), address: str = Query(min_length=1, max_length=255), zone: Zone = Query(default="UTC"),
             user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
             service: ExtraStopPort = Depends(extra_stop_service)) -> dict[str, Any]:
    return _call(lambda: service.evaluate(trip_id, address.strip(), zone, user.username))


@router.get("/decisions")
def decisions(trip_id: int = Path(gt=0), user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
              service: ExtraStopPort = Depends(extra_stop_service)) -> dict[str, Any]:
    return _call(lambda: service.decisions(trip_id, user.username))


@router.post("")
def command(body: ExtraStopCommand, trip_id: int = Path(gt=0), user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
            service: ExtraStopPort = Depends(extra_stop_service)) -> dict[str, Any]:
    return _call(lambda: service.command(trip_id, body, user.username))
