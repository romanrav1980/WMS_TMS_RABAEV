"""C-0176: the places of one assembly on a trip and the removal of selected places (native RRL_TT_PLACE_REMOVAL_API)."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from ...platform.public import AdminUser, get_current_user
from ..contracts_place_removal import PlaceRemovalCommand, PlaceRemovalError, PlaceRemovalPort, place_removal_service

router = APIRouter(prefix="/api/transport/trips/{trip_id}", tags=["transport-place-removal"])


def _call(run: Callable[[], dict[str, Any]], command: bool = False) -> dict[str, Any]:
    try:
        return run()
    except PlaceRemovalError as exc:
        # For a command, a refusal of rights or an operation conflict does not prove that an earlier lost request of the same operation
        # did not run: the caller keeps its intent. Only a business refusal of the request itself confirms the outcome.
        unknown = exc.status == 503 or (command and (exc.status in (401, 403) or exc.code == "OPERATION_CONFLICT"))
        raise HTTPException(exc.status, {"code": exc.code, "outcome_confirmed": not unknown, "retry_same_operation_id": exc.status == 503}) from exc


@router.get("/sts/{st_number}/places")
def places(trip_id: int = Path(gt=0), st_number: str = Path(min_length=1, max_length=200), user: AdminUser = Depends(get_current_user),
           service: PlaceRemovalPort = Depends(place_removal_service)) -> dict[str, Any]:
    return _call(lambda: service.places(trip_id, st_number, user.username))


@router.post("/place-removals")
def remove(body: PlaceRemovalCommand, trip_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
           service: PlaceRemovalPort = Depends(place_removal_service)) -> dict[str, Any]:
    return _call(lambda: service.remove(trip_id, body, user.username), command=True)
