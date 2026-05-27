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
  GET    /api/admin/transport/planner/history            — история применённых планов + Score (Sprint 10)
  GET    /api/admin/transport/planner/demand-forecast    — прогноз числа СТ на дату (Sprint 10)
  POST   /api/admin/transport/tasks/{id}/plan-operations — рассчитать операции ARM (Sprint 11)
  GET    /api/admin/transport/tasks/{id}/operations      — список операций рейса (Sprint 11)
  PATCH  /api/admin/transport/operations/{op_id}/fact    — зафиксировать fact_start/fact_end (Sprint 11)
  GET    /api/admin/transport/vehicles/gantt             — Ганта-данные всех машин на день (Sprint 11)
  GET    /api/admin/transport/vehicles/available         — доступность машин к времени отгрузки (Sprint 13)
  GET    /api/admin/transport/plan-fact                  — сводный план-фактный отчёт (Sprint 13/14)
  GET    /api/admin/transport/billing/orders             — список биллинг-заказов (Sprint 15)
  POST   /api/admin/transport/billing/orders             — создать биллинг-заказ (Sprint 15)
  GET    /api/admin/transport/billing/orders/{id}        — один заказ (Sprint 16)
  PATCH  /api/admin/transport/billing/orders/{id}/close  — закрыть заказ (Sprint 16)
  PATCH  /api/admin/transport/billing/orders/{id}/pay    — отметить оплаченным (Sprint 16)
  POST   /api/admin/transport/billing/orders/{id}/tasks — привязать рейсы к заказу (Sprint 15)
  GET    /api/admin/transport/billing/orders/{id}/tasks — рейсы в заказе (Sprint 15)
  GET    /api/admin/transport/tasks/{id}/billing        — биллинг-данные рейса (Sprint 15)
  POST   /api/admin/transport/tasks/{id}/billing/open   — создать счёт для рейса (Sprint 15)
  DELETE /api/admin/transport/billing/orders/{id}/tasks/{tt_id} — отвязать рейс от заказа (Sprint 18)
  POST   /api/admin/transport/tasks/{id}/recalculate-price — пересчёт цены через RRL_UPDATE_PRICE (Sprint 18)
  PATCH  /api/admin/transport/tasks/{id}/price          — ручная установка цены (Sprint 18)
  GET    /api/admin/transport/billing/companies         — справочник транспортных компаний (Sprint 22)
  GET    /api/admin/transport/billing/orders/{id}/export.xlsx — экспорт счёта в Excel (Sprint 26)
  GET    /api/admin/transport/billing/orders/export.xlsx     — экспорт реестра счетов в Excel (Sprint 27)
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from ..auth import (
    AdminUser,
    BILLING_CALC_PRICE_PERMISSION,
    BILLING_CREATE_PRICE_PERMISSION,
    BILLING_EDIT_PERMISSION,
    TRANSPORT_DISPATCH_CLOSE_PERMISSION,
    TRANSPORT_DISPATCH_EDIT_PERMISSION,
    TRANSPORT_DISPATCH_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    BillingAddTasksRequest,
    BillingOrderCreate,
    OperationFactUpdate,
    PriceUpdateRequest,
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
    svc = TransportService()
    task_id = svc.create_task(req, user.username)
    # Авто-пересчёт цепочки операций ARM после создания рейса
    try:
        svc.plan_operations(task_id)
    except Exception:
        pass  # Не блокируем создание рейса при ошибке ARM (таблицы могут не существовать в dev)
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


@router.get("/planner/history")
def get_planner_history(
    date_from: date = Query(default=..., description="Начало периода"),
    date_to: date = Query(default=..., description="Конец периода"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """История применённых планов с метриками (Score, утилизация, пробег)."""
    return TransportService().get_plan_history(date_from=date_from, date_to=date_to)


@router.get("/planner/demand-forecast")
def get_demand_forecast(
    target_date: date = Query(default=..., description="Дата для прогноза"),
    lookback_weeks: int = Query(default=8, ge=2, le=52),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Прогноз числа СТ на целевую дату на основе истории аналогичных дней недели."""
    return TransportService().get_demand_forecast(
        target_date=target_date, lookback_weeks=lookback_weeks
    )


# ---------------------------------------------------------------------------
# Sprint 11 — ARM: операции и нормативы
# ---------------------------------------------------------------------------

@router.post("/tasks/{task_id}/plan-operations")
def plan_operations(
    task_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> list[dict]:
    """Рассчитывает и сохраняет цепочку плановых операций рейса по нормативам."""
    return TransportService().plan_operations(task_id)


@router.get("/tasks/{task_id}/operations")
def get_operations(
    task_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Список операций рейса с плановыми и фактическими временами."""
    return TransportService().get_operations(task_id)


@router.patch("/operations/{op_id}/fact")
def update_operation_fact(
    op_id: int,
    data: OperationFactUpdate,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)),
) -> dict:
    """Фиксирует fact_start / fact_end операции (ввод диспетчера или мобильного водителя)."""
    return TransportService().update_operation_fact(op_id, data)


@router.get("/vehicles/gantt")
def get_vehicles_gantt(
    gantt_date: date = Query(default=..., description="Дата для Ганта"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Данные диаграммы Ганта для всех машин на день."""
    return TransportService().get_vehicles_gantt(gantt_date)


# ---------------------------------------------------------------------------
# Sprint 13 — Умный подбор машины и план-факт
# ---------------------------------------------------------------------------

@router.get("/vehicles/available")
def get_vehicles_available(
    shipment_time: str = Query(default=..., description="Плановое время отгрузки YYYY-MM-DD HH:MM"),
    pallets: int = Query(default=0, ge=0, description="Требуемое число паллет"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Список машин с индикатором доступности (green/yellow/red) к времени отгрузки."""
    return TransportService().get_vehicles_available(shipment_time, pallets)


@router.get("/plan-fact")
def get_plan_fact(
    date_from: date = Query(default=..., description="Начало периода"),
    date_to:   date = Query(default=..., description="Конец периода"),
    vehicle:   str | None = Query(default=None, description="Фильтр по гос. номеру"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Сводный план-фактный отчёт по всем рейсам периода."""
    return TransportService().get_plan_fact(date_from, date_to, vehicle)


# ---------------------------------------------------------------------------
# Sprint 15 — Биллинг: создание счёта
# ---------------------------------------------------------------------------

@router.get("/billing/orders")
def list_billing_orders(
    company:   str | None = Query(default=None, description="Фильтр по компании"),
    date_from: date | None = Query(default=None, description="Начало периода"),
    date_to:   date | None = Query(default=None, description="Конец периода"),
    closed:    int | None = Query(default=None, description="0=открыт, 1=закрыт"),
    payed:     int | None = Query(default=None, description="0=не оплачен, 1=оплачен"),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Список биллинг-заказов с суммой и числом рейсов."""
    return TransportService().list_billing_orders(company, date_from, date_to, closed, payed)


@router.get("/billing/orders/export.xlsx")
def export_billing_registry_xlsx(
    company:   str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to:   date | None = Query(default=None),
    closed:    int | None = Query(default=None),
    payed:     int | None = Query(default=None),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
):
    """Экспорт реестра биллинг-заказов в Excel — Sprint 27."""
    import io
    data = TransportService().export_billing_registry_xlsx(company, date_from, date_to, closed, payed)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="billing_registry.xlsx"'},
    )


@router.post("/billing/orders")
def create_billing_order(
    req: BillingOrderCreate,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> dict:
    """Создать новый биллинг-заказ."""
    svc = TransportService()
    order_id = svc.create_billing_order(req.company, req.date_from, req.date_to)
    orders = svc.list_billing_orders()
    order = next((o for o in orders if o["order_id"] == order_id), {"order_id": order_id})
    return order


@router.get("/billing/orders/{order_id}", response_model=None)
def get_billing_order(
    order_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Один биллинг-заказ по ID."""
    data = TransportService().get_billing_order(order_id)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
    return data


@router.patch("/billing/orders/{order_id}/close")
def close_billing_order(
    order_id: int,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> dict:
    """Закрыть биллинг-заказ (вызывает RRL_CLOSE_BILLINGORDER)."""
    return TransportService().close_billing_order(order_id)


@router.patch("/billing/orders/{order_id}/pay")
def pay_billing_order(
    order_id: int,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> dict:
    """Отметить биллинг-заказ как оплаченный (вызывает RRL_PAY_BILLINGORDER)."""
    return TransportService().pay_billing_order(order_id)


@router.get("/billing/orders/{order_id}/tasks")
def get_billing_order_tasks(
    order_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Рейсы, привязанные к биллинг-заказу."""
    return TransportService().get_billing_order_tasks(order_id)


@router.get("/billing/orders/{order_id}/export.xlsx")
def export_billing_order_xlsx(
    order_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
):
    """Экспорт счёта в Excel (.xlsx) — Sprint 26, DoD §12 #7."""
    import io
    data = TransportService().export_billing_order_xlsx(order_id)
    filename = f"billing_order_{order_id}.xlsx"
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/billing/orders/{order_id}/tasks")
def add_tasks_to_billing_order(
    order_id: int,
    req: BillingAddTasksRequest,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> dict:
    """Привязать рейсы к биллинг-заказу."""
    TransportService().add_tasks_to_order(order_id, req.tt_ids)
    return {"order_id": order_id, "added": len(req.tt_ids)}


@router.get("/tasks/{task_id}/billing")
def get_task_billing(
    task_id: int,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Биллинг-данные рейса (заказ, к которому привязан)."""
    data = TransportService().get_task_billing(task_id)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Рейс не привязан к биллинг-заказу")
    return data


@router.post("/tasks/{task_id}/billing/open")
def open_billing_for_task(
    task_id: int,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> dict:
    """Создать биллинг-заказ для рейса и привязать к нему."""
    return TransportService().open_billing_for_task(task_id)


@router.delete("/billing/orders/{order_id}/tasks/{tt_id}")
def remove_task_from_billing_order(
    order_id: int,
    tt_id: int,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> dict:
    """Отвязать рейс от биллинг-заказа (обнулить PAY_ORDER_ID)."""
    return TransportService().remove_task_from_billing_order(order_id, tt_id)


@router.post("/tasks/{task_id}/recalculate-price")
def recalculate_task_price(
    task_id: int,
    _user: AdminUser = Depends(require_permission(BILLING_CALC_PRICE_PERMISSION)),
) -> dict:
    """Пересчитать стоимость рейса через Oracle-функцию TRANSPORT_TASK.stoim_tt."""
    return TransportService().recalculate_price(task_id)


@router.patch("/tasks/{task_id}/price")
def set_task_price(
    task_id: int,
    req: PriceUpdateRequest,
    _user: AdminUser = Depends(require_permission(BILLING_CREATE_PRICE_PERMISSION)),
) -> dict:
    """Ручная установка стоимости рейса (право CREATE_TT_PRICE)."""
    return TransportService().set_task_price(task_id, req.price)


@router.get("/billing/companies")
def list_billing_companies(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[str]:
    """Справочник транспортных компаний из RRL_BILL_COMPANY (Sprint 22)."""
    return TransportService().list_billing_companies()
