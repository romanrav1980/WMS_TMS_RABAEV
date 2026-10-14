from typing import Any, Protocol
from fastapi import APIRouter, Depends, Query
from ...platform.public import AdminUser, require_permission


class WarehouseOptionsPort(Protocol):
    def list(self, query: str | None, after: int | None, limit: int) -> dict[str, Any]: ...


def warehouse_options_service() -> WarehouseOptionsPort:
    raise RuntimeError("Warehouse options service not wired")


router = APIRouter(prefix="/api/master-data/warehouses", tags=["warehouse-options"])


# То же право, что у полного справочника /api/admin/warehouses; состав складов прежний (без отбора по складу пользователя).
@router.get("/options")
def warehouse_options(q: str | None = Query(default=None, max_length=100), after: int | None = Query(default=None, gt=0),
                      limit: int = Query(default=100, ge=1, le=100),
                      _user: AdminUser = Depends(require_permission("warehouse_settings_view")),
                      service: WarehouseOptionsPort = Depends(warehouse_options_service)) -> dict[str, Any]:
    return service.list(q, after, limit)
