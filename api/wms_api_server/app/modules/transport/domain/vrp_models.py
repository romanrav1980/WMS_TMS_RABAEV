"""Passive models of the existing solver; relative time is not dispatch admission."""
from dataclasses import dataclass, field
from typing import Any

@dataclass
class VrpOrder:
    st_number: str
    addr: str
    lat: float
    lon: float
    pallets: int
    weight_kg: float
    ware_id: int
    transport_type: str | None
    tw_from: int = 0       # minutes from shift start (06:00)
    tw_to:   int = 1080    # minutes from shift start (06:00+18h=24:00)
    tw_strict: bool = False
    unload_norm_min: int = 30
    verify_perc: float | None = None


@dataclass
class VrpVehicle:
    id: int
    num: str          # гос. номер
    tr_type: str      # тип ТС
    max_pallets: int
    max_tons: float
    gidrobort: bool = False


@dataclass
class VrpRoute:
    vehicle: VrpVehicle
    stops: list[VrpOrder] = field(default_factory=list)
    total_km: float = 0.0
    total_pallets: int = 0
    total_kg: float = 0.0
    total_duration_min: int = 0
    schedule: list[dict[str, Any]] = field(default_factory=list)
    depot_basis: str = "VIRTUAL_CENTROID"
    road_profile_legs: int = 0
    schedule_status: str = "UNAVAILABLE"
    schedule_start_min: int | None = None
    schedule_end_min: int | None = None

    @property
    def utilization_pct(self) -> float:
        if self.vehicle.max_pallets == 0:
            return 0.0
        return round(self.total_pallets / self.vehicle.max_pallets * 100, 1)


@dataclass
class VrpPlan:
    routes: list[VrpRoute] = field(default_factory=list)
    unassigned: list[VrpOrder] = field(default_factory=list)
    total_km: float = 0.0
    fleet_utilization_pct: float = 0.0
    tw_violations: int = 0
    score: float = 0.0
    solver_used: str = "none"
    solve_time_ms: int = 0
