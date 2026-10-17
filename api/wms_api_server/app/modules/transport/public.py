"""Supported entry points for transport rules; legacy callers use this facade."""
from .domain.transport_type import normalize_transport_type
from .infrastructure.st_assignment import assign_sts, unassign_st, cancel_trip

__all__ = ["normalize_transport_type", "assign_sts"]

from collections.abc import Callable
from typing import Any
from .contracts import TransportLoadingPort, TransportLoadingError, transport_loading_service
from .infrastructure.loading import TransportLoading
from .api.loading_routes import router as transport_loading_router


def build_loading_service(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> TransportLoadingPort:
    return TransportLoading(gateway,post)

from .contracts_driver_binding import DriverBindingPort,driver_binding_service
from .api.driver_binding_routes import router as driver_binding_router
from .infrastructure.driver_binding import DriverBinding

def build_driver_binding(gateway: Any) -> DriverBindingPort:
    return DriverBinding(gateway)

from .contracts_forecast import WarehouseForecastPort,warehouse_forecast_service
from .infrastructure.warehouse_forecast import WarehouseForecast
from .api.forecast_routes import router as warehouse_forecast_router

def build_warehouse_forecast(gateway: Any) -> WarehouseForecastPort:
    return WarehouseForecast(gateway)

from .infrastructure.plan_application import apply_existing_plan,TransportPlanError

from .infrastructure.trip_edit import create_existing_trip,update_existing_trip

from .infrastructure.cluster_creation import create_existing_cluster

from .infrastructure.operation_plan import generate_existing_operations

from .infrastructure.operation_fact import update_existing_operation_fact

from .contracts_operation_fact import OperationFactPort, operation_fact_service
from .api.operation_fact_routes import router as operation_fact_router
from .infrastructure.operation_fact_service import OperationFacts
from .contracts_preflight import TransportPreflightPort, transport_preflight_service
from .infrastructure.plan_preflight import TransportPreflight
from .api.preflight_routes import router as transport_preflight_router
from .api.unloading_routes import router as transport_unloading_router

from .api.st_deferral_routes import router as st_deferral_router
from .contracts_st_deferral import st_deferral_service,StDeferralPort
from .infrastructure.st_deferral import StDeferral

def build_st_deferral(gateway: Any) -> StDeferralPort:
    return StDeferral(gateway)

from .domain.road_matrix import osrm_costs,valhalla_costs,validate_points

from .infrastructure.distance_matrix_rows import matrix_merge_statements

from .domain.vrp_travel_time import travel_times
from .infrastructure.profile_duration_cache import profile_duration_cache,planner_cost_cache,planner_inputs

from .contracts_depot import WarehouseDepotPort,warehouse_depot_service
from .infrastructure.warehouse_depot import WarehouseDepot
from .api.warehouse_depot_routes import router as warehouse_depot_router

def build_warehouse_depot(gateway: Any) -> WarehouseDepotPort:
    return WarehouseDepot(gateway)

from .domain.vrp_distance_costs import distance_costs

from .contracts_vehicle_profile import VehicleProfilePort,vehicle_profile_service
from .infrastructure.vehicle_profile import VehicleProfiles
from .api.vehicle_profile_routes import router as vehicle_profile_router

def build_vehicle_profiles(gateway: Any)->VehicleProfilePort:
    return VehicleProfiles(gateway)

from .contracts_driver_workspace import DriverWorkspacePort,driver_workspace_service
from .api.driver_workspace_routes import router as driver_workspace_router
from .infrastructure.driver_workspace import DriverWorkspace

def build_driver_workspace(gateway: Any) -> DriverWorkspacePort:
    return DriverWorkspace(gateway)

from .infrastructure.available_sts_query import available_sts_query

from .infrastructure.geofences import list_address_geofences, update_address_geofence

from .infrastructure.gps_ingestion import ingest_gps, GpsVehicleMissing

from .infrastructure.gantt_rows import gantt_rows, MAX_GANTT_ROWS

from .contracts_dispatch_read import TripListFilter, DispatchReadError
from .infrastructure.trip_list_filters import trip_list_filters
from .infrastructure.dispatch_read_scope import guarded_trip_read, scoped_dispatch_rows

from .infrastructure.timeline_clock import current_timeline_clock
