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
  GET    /api/admin/transport/clusters                    — свободные СТ, сгруппированные по RAION (Phase 2.1)
  GET    /api/admin/transport/vehicles                    — справочник ТС
  GET    /api/admin/transport/drivers                     — справочник водителей
  GET    /api/admin/transport/types                       — справочник типов транспорта
  GET    /api/admin/transport/sts/{st_number}/pallets     — паллеты СТ (Sprint 6)
  GET    /api/admin/transport/planner/orders             — СТ с координатами для карты (Sprint 7)
  GET    /api/admin/transport/routing/status             — статус геокодирования (Sprint 7)
  POST   /api/admin/transport/distance-matrix/rebuild    — пересчитать матрицу расстояний (Sprint 8)
  POST   /api/admin/transport/planner/solve              — запустить VRP-оптимизатор (Sprint 8)
  POST   /api/admin/transport/planner/apply              — применить план (создать рейсы) (Sprint 8)
  GET    /api/admin/transport/planner/metrics            — метрики последнего плана (Sprint 8)
  GET    /api/admin/transport/planner/templates          — похожие исторические планы (Sprint 9)
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
    VrpSolveRequest,
    VrpApplyRequest,
    VrpPlanResponse,
)
from ..services.transport_service import TransportService
from ..services.distance_matrix_service import DistanceMatrixService

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
    date_to: date | None = None,
    unassigned_only: bool = True,
    ware_id: int | None = None,
    ware_ids: Annotated[list[int] | None, Query()] = None,
    addr_mask: str | None = None,
    st_mask: str | None = None,
    st_mask_exclude: bool = False,
    transport_type: str | None = None,
    assembled_only: bool = False,
    not_assembled_only: bool = False,
    max_weight_kg: float | None = None,
    max_volume_m3: float | None = None,
    articul: str | None = None,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_available_sts(
        stdate=stdate,
        date_to=date_to,
        unassigned_only=unassigned_only,
        ware_id=ware_id,
        ware_ids=ware_ids,
        addr_mask=addr_mask,
        st_mask=st_mask,
        st_mask_exclude=st_mask_exclude,
        transport_type=transport_type,
        assembled_only=assembled_only,
        not_assembled_only=not_assembled_only,
        max_weight_kg=max_weight_kg,
        max_volume_m3=max_volume_m3,
        articul=articul,
    )


# ------------------------------------------------------------------
# Кластеры (Phase 2.1)
# ------------------------------------------------------------------

@router.get("/clusters")
def list_clusters(
    stdate: date | None = None,
    ware_ids: Annotated[list[int] | None, Query()] = None,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_clusters(stdate=stdate, ware_ids=ware_ids)


# ------------------------------------------------------------------
# Рейсы
# ------------------------------------------------------------------

@router.get("/tasks")
def list_tasks(
    shipment_date: date | None = None,
    condition: str | None = None,
    include_readiness: bool = False,
    task_id: int | None = None,
    transport_mask: str | None = None,
    company_mask: str | None = None,
    date_to: date | None = None,
    no_payments_only: bool = False,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_tasks(
        shipment_date=shipment_date,
        condition=condition,
        include_readiness=include_readiness,
        task_id=task_id,
        transport_mask=transport_mask,
        company_mask=company_mask,
        date_to=date_to,
        no_payments_only=no_payments_only,
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


# ------------------------------------------------------------------
# Паллеты СТ (Sprint 6)
# ------------------------------------------------------------------

@router.get("/sts/{st_number}/pallets")
def list_st_pallets(
    st_number: str,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().list_st_pallets(st_number)


# ------------------------------------------------------------------
# Планировщик / карта заказов (Sprint 7)
# ------------------------------------------------------------------

@router.get("/planner/orders")
def get_planner_orders(
    date: date | None = None,
    ware_ids: Annotated[list[int] | None, Query()] = None,
    transport_type: str | None = None,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return TransportService().get_planner_orders(
        plan_date=date,
        ware_ids=ware_ids,
        transport_type=transport_type,
    )


@router.get("/routing/status")
def get_routing_status(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    return TransportService().get_routing_status()


# ---------------------------------------------------------------------------
# Sprint 8 — Матрица расстояний + VRP-оптимизатор
# ---------------------------------------------------------------------------

@router.post("/distance-matrix/rebuild")
def rebuild_distance_matrix(
    source: str = Query(default="auto", description="auto|haversine|osrm|valhalla"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    """Пересчитывает матрицу расстояний RRL_ADDR_DISTANCE_MATRIX."""
    return DistanceMatrixService().rebuild(source=source)


@router.post("/planner/solve")
def solve_vrp(
    body: VrpSolveRequest,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> VrpPlanResponse:
    """
    Запускает VRP-оптимизатор (OR-Tools CVRPTW или Clarke-Wright fallback).
    Сохраняет план в RRL_PLANNER_PLANS и возвращает структуру плана.
    """
    svc = TransportService()
    return svc.solve_vrp(
        plan_date=body.plan_date,
        ware_ids=body.ware_ids,
        transport_type=body.transport_type,
        time_limit_s=body.time_limit_s,
        source=body.source,
        solver=body.solver,
    )


@router.post("/planner/apply")
def apply_vrp_plan(
    body: VrpApplyRequest,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    """
    Создаёт рейсы (TRANSPORT_TASK) по сохранённому плану через Oracle-пакеты.
    Возвращает {"tasks_created": int, "plan_id": int}.
    """
    svc = TransportService()
    return svc.apply_vrp_plan(
        plan_id=body.plan_id,
        shipment_date=body.shipment_date,
        dock=body.dock,
    )


@router.get("/planner/metrics")
def get_planner_metrics(
    plan_id: int | None = Query(default=None, description="ID плана; null = последний"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Возвращает агрегированные метрики плана."""
    return TransportService().get_plan_metrics(plan_id=plan_id)


@router.get("/planner/templates")
def get_planner_templates(
    plan_date: date = Query(default=..., description="Дата СТ для поиска похожих планов"),
    lookback_days: int = Query(default=90, ge=7, le=365),
    min_jaccard: float = Query(default=0.7, ge=0.1, le=1.0),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Возвращает исторические планы с Jaccard ≥ min_jaccard за последние lookback_days дней."""
    return TransportService().get_plan_templates(
        plan_date=plan_date,
        lookback_days=lookback_days,
        min_jaccard=min_jaccard,
    )
