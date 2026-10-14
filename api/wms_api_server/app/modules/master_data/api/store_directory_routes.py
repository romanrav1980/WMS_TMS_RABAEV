from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ...platform.public import AdminUser, get_current_user
from ..contracts_store_directory import StoreDirectoryPort, store_directory_service

router = APIRouter(prefix="/api/master-data/stores", tags=["store-directory"])
READ_PERMISSIONS = ("warehouse_settings_view", "transport_dispatch_view")


def store_reader(user: AdminUser = Depends(get_current_user)) -> AdminUser:
    """Достаточно одного из прав: настройки складов или просмотр диспетчеризации."""
    if "*" not in user.permissions and not any(p in user.permissions for p in READ_PERMISSIONS):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Permission required: " + " or ".join(READ_PERMISSIONS))
    return user


@router.get("")
def search_stores(q: str | None = Query(default=None, max_length=100), after: str | None = Query(default=None, min_length=1, max_length=255),
                  limit: int = Query(default=30, ge=1, le=50), _user: AdminUser = Depends(store_reader),
                  service: StoreDirectoryPort = Depends(store_directory_service)) -> dict[str, Any]:
    return service.search(q, after, limit)


@router.get("/card")
def store_card(addr: str = Query(min_length=1, max_length=255), user: AdminUser = Depends(store_reader),
               service: StoreDirectoryPort = Depends(store_directory_service)) -> dict[str, Any]:
    card = service.card(addr, user.username)
    if card is None:
        raise HTTPException(404, {"code": "STORE_NOT_FOUND", "message": "Магазин не найден или удалён"})
    return card
