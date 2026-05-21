"""
transport.py — FastAPI роутер диспетчера отгрузки.

Эндпоинты:
  GET    /api/admin/transport/tasks                       — список рейсов на дату
  POST   /api/admin/transport/tasks                       — создать рейс
  GET    /api/admin/transport/tasks/{id}                  — один рейс
  PATCH  /api/admin/transport/tasks/{id}                  — обновить реквизиты рейса
  POST   /api/admin/transport/tasks/{id}/close            — закрыть рейс (Отгружен)
  POST   /api/admin/transport/tasks/{id}/cancel           — отменить рейс (Deleted)
  GET    /api/admin/transport/tasks/{id}/sts              — СТ в рейсе
  POST   /api/admin/transport/tasks/{id}/sts              — назначить СТ в рейс
  DELETE /api/admin/transport/tasks/{id}/sts/{st}         — снять СТ с рейса
  PATCH  /api/admin/transport/tasks/{id}/sts/{st}/load-type — изменить тип погрузки
  PATCH  /api/admin/transport/tasks/{id}/sts/{st}/order   — изменить порядок адреса
  GET    /api/admin/transport/available-sts               — свободные СТ (с фильтрами)
  GET    /api/admin/transport/vehicles                    — справочник ТС
  GET    /api/admin/transport/drivers                     — справочник водителей
  GET    /api/admin/transport/types                       — справочник типов транспорта
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..auth import (
    AdminUser,
    TRANSPORT_DISPATCH_CLOSE_PERMISSION,
    TRANSPORT_DISPATCH_EDIT_PERMISSION,
    TRANSPORT_DISPATCH_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    TransportStAssignRequest,
    TransportStLoadTypeRequest,
    TransportStOrderRequest,
    TransportTaskCreateRequest,
    TransportTaskUpdateRequest,
)
from ..services.transport_service import TransportService

router = APIRouter(prefix="/api/admin/transport", tags=["transport-dispatch"])


# ------------------------------------------------------------------
# Справочники
# ------------------------------------------------------------------

@router.get("/vehicles")
def list_vehicles(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_vehicles()


@router.get("/drivers")
def list_drivers(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_drivers()


@router.get("/types")
def list_transport_types(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_transport_types()


# ------------------------------------------------------------------
# Свободные СТ
# ------------------------------------------------------------------

@router.get("/available-sts")
def list_available_sts(
    stdate: date | None = None,
    unassigned_only: bool = True,
    ware_id: int | None = None,
    ware_ids: Annotated[list[int] | None, Query()] = None,
    addr_mask: str | None = None,
    st_mask: str | None = None,
    assembled_only: bool = False,
    max_weight_kg: float | None = None,
    max_volume_m3: float | None = None,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_available_sts(
        stdate=stdate,
        unassigned_only=unassigned_only,
        ware_id=ware_id,
        ware_ids=ware_ids,
        addr_mask=addr_mask,
        st_mask=st_mask,
        assembled_only=assembled_only,
        max_weight_kg=max_weight_kg,
        max_volume_m3=max_volume_m3,
    )


# ------------------------------------------------------------------
# Рейсы
# ------------------------------------------------------------------

@router.get("/tasks")
def list_tasks(
    shipment_date: date | None = None,
    condition: str | None = None,
    include_readiness: bool = False,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_tasks(
        shipment_date=shipment_date,
        condition=condition,
        include_readiness=include_readiness,
    )


@router.post("/tasks")
def create_task(
    req: TransportTaskCreateRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    task_id = TransportService().create_task(req, user.username)
    return {"task_id": task_id}


@router.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    return TransportService().get_task(task_id)


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    req: TransportTaskUpdateRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    TransportService().update_task(task_id, req, user.username)
    return {"task_id": task_id}


@router.post("/tasks/{task_id}/close")
def close_task(
    task_id: int,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_CLOSE_PERMISSION)),
) -> dict:
    TransportService().close_task(task_id, user.username)
    return {"task_id": task_id, "condition": "Отгружен"}


@router.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: int,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    TransportService().cancel_task(task_id, user.username)
    return {"task_id": task_id, "deleted": True}


# ------------------------------------------------------------------
# СТ в рейсе
# ------------------------------------------------------------------

@router.get("/tasks/{task_id}/sts")
def get_task_sts(
    task_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().get_task_sts(task_id)


@router.post("/tasks/{task_id}/sts")
def assign_sts(
    task_id: int,
    req: TransportStAssignRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    return TransportService().assign_sts(task_id, req.st_numbers, user.username)


@router.delete("/tasks/{task_id}/sts/{st_number}")
def unassign_st(
    task_id: int,
    st_number: str,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    TransportService().unassign_st(task_id, st_number, user.username)
    return {"task_id": task_id, "st_number": st_number, "unassigned": True}


@router.patch("/tasks/{task_id}/sts/{st_number}/load-type")
def set_st_load_type(
    task_id: int,
    st_number: str,
    req: TransportStLoadTypeRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    TransportService().set_st_load_type(task_id, st_number, req.load_type, user.username)
    return {"task_id": task_id, "st_number": st_number, "load_type": req.load_type}


@router.patch("/tasks/{task_id}/sts/{st_number}/order")
def set_st_order(
    task_id: int,
    st_number: str,
    req: TransportStOrderRequest,
    user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    TransportService().set_st_order(task_id, st_number, req.ord, user.username)
    return {"task_id": task_id, "st_number": st_number, "ord": req.ord}
