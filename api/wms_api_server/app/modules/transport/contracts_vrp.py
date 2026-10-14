"""Existing planner HTTP contracts, preserved for schema imports."""
from datetime import date
from typing import Any
from pydantic import BaseModel, Field

class VrpRouteStop(BaseModel):
    st_number: str
    addr: str | None
    lat: float | None
    lon: float | None
    pallets: int
    weight_kg: float
    ware_id: int
    unload_norm_min: int
    tw_from: int
    tw_to: int
    tw_strict: bool
    arrival_min: int | None = None
    departure_min: int | None = None
    tw_violation_min: int = 0
    distance_from_prev_km: float | None = None
    duration_from_prev_min: int | None = None
    duration_from_prev_basis: str = "UNRECORDED"
    constraint_notes: list[str] = Field(default_factory=list)


class VrpRouteItem(BaseModel):
    vehicle_id: int
    vehicle_num: str
    vehicle_type: str
    max_pallets: int
    total_pallets: int
    total_kg: float
    total_km: float
    total_duration_min: int
    utilization_pct: float
    stops: list[VrpRouteStop]
    depot_basis: str = "UNRECORDED"
    road_profile_legs: int = 0
    schedule_status: str = "UNAVAILABLE"
    schedule_start_min: int | None = None
    schedule_end_min: int | None = None
    schedule_assumptions: list[str] = Field(default_factory=list)
    operational_admission: bool = False
    capacity_status: str = "ok"
    tw_violation_count: int = 0
    strict_tw_count: int = 0
    vehicle_constraints_ok: bool = True
    hydro_board_required_count: int = 0
    explain_notes: list[str] = Field(default_factory=list)


class VrpPlanResponse(BaseModel):
    plan_id: int | None = None
    routes: list[VrpRouteItem]
    unassigned_sts: list[str]
    total_km: float
    fleet_utilization_pct: float
    tw_violations: int
    score: float
    solver_used: str
    solve_time_ms: int
    explain: dict[str, Any] | None = None


class VrpSolveRequest(BaseModel):
    plan_date: date = Field(..., description="Дата СТ для планирования")
    ware_ids: list[int] | None = None
    transport_type: str | None = None
    time_limit_s: int = Field(default=30, ge=5, le=120)
    source: str = Field(default="auto", description="Провайдер матрицы: auto|haversine|osrm|valhalla")
    solver: str = Field(default="auto", description="Решатель: auto|ortools|cluster|savings")


class VrpApplyRequest(BaseModel):
    plan_id: int = Field(..., strict=True,gt=0,description="ID плана из RRL_PLANNER_PLANS для применения")
    shipment_date: date = Field(..., description="Дата отгрузки создаваемых рейсов")
    dock: str | None = Field(default=None,max_length=100)


