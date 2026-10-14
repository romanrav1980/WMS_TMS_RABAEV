from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from ...platform.public import AdminUser, require_permission
from ..contracts_store_profile import StoreProfileError, StoreProfileInput, StoreProfilePort, store_profile_service
from .store_directory_routes import store_reader

router = APIRouter(prefix="/api/master-data/stores/profile", tags=["store-profile"])


@router.get("")
def read_profile(addr: str = Query(min_length=1, max_length=255), _user: AdminUser = Depends(store_reader),
                 service: StoreProfilePort = Depends(store_profile_service)) -> dict[str, Any]:
    return service.read(addr)


@router.put("")
def save_profile(body: StoreProfileInput, user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
                 service: StoreProfilePort = Depends(store_profile_service)) -> dict[str, Any]:
    try:
        return service.save(user.username, body.model_dump(mode="json"))
    except StoreProfileError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc), "operation_id": body.operation_id,
                                         "outcome_confirmed": exc.status in (409, 422)}) from exc
