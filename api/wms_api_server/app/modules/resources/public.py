"""Public entry point for existing warehouse task resource assignment."""
from typing import Any,Callable
from .infrastructure.task_assignment import task_resource_context


def existing_task_resource_context(gateway: Any, task: dict[str, Any], action: str,
                                   request: Any, assignee: str) -> dict[str, Any]:
    return task_resource_context(gateway, task, action, request, assignee)


from .infrastructure.wave_tasks import sync_wave_tasks

def sync_existing_wave_tasks(gateway: Any, wave_id: int, actor: str) -> None:
    sync_wave_tasks(gateway, wave_id, actor)

from .api.qualification_routes import (router as qualification_router, resource_view,
    qualification_edit, resource_position_user, resource_dispatch_user, qualification_service)
from .infrastructure.qualification_service import QualificationService
from .infrastructure.qualified_candidates import QualifiedCandidates

def build_qualification_service(assign: Callable[[Any,int,Any],None]) -> QualificationService:
    from ...oracle_gateway import OracleGateway
    return QualificationService(OracleGateway(),assign)

def assign_existing_inventory_auditor(gateway: Any, short_id: int, actor: str) -> dict[str, Any]:
    return QualifiedCandidates(gateway).dispatch_inventory(short_id,actor)

from .infrastructure.case_assignment import context as case_resource_context, run_action as run_case_resource_action
from .infrastructure.case_report_metadata import case_short_report_transaction

from .infrastructure.urgent_dispatch import dispatch_urgent as dispatch_existing_urgent_replenishment

from .infrastructure.case_handoff import validate as validate_existing_case_handoff

from .infrastructure.case_actions import execute as execute_existing_case_action

from .api.reach_shift_routes import router as reach_shift_router,reach_shift_view,reach_shift_edit,reach_shift_service
from .infrastructure.reach_shifts import ReachShifts
from .infrastructure.session_lifecycle import open_session as open_existing_resource_session,close_session as close_existing_resource_session

def build_reach_shifts() -> ReachShifts:
    from ...oracle_gateway import OracleGateway
    return ReachShifts(OracleGateway())

from .contracts_workload import WorkloadConfigPort,workload_config_service
from .infrastructure.workload_config import WorkloadConfig
from .api.workload_config_routes import router as workload_config_router

def build_workload_config(gateway: Any) -> WorkloadConfigPort:
    return WorkloadConfig(gateway)

from .api.workload_monitor_routes import WorkloadMonitorPort,workload_monitor_service,router as workload_monitor_router
from .infrastructure.workload_monitor import WorkloadMonitor

def build_workload_monitor(gateway: Any) -> WorkloadMonitorPort:
    return WorkloadMonitor(gateway)

from .contracts_wave_time import WaveTimePort,wave_time_service
from .api.wave_time_routes import router as wave_time_router
from .infrastructure.wave_time import WaveTime

def build_wave_time(gateway: Any) -> WaveTimePort:
    return WaveTime(gateway)

from .contracts_workload import WorkloadHistoryPort,workload_history_service
from .api.workload_history_routes import router as workload_history_router
from .infrastructure.workload_history import WorkloadHistory

def build_workload_history(gateway: Any) -> WorkloadHistoryPort:
    return WorkloadHistory(gateway)

from .contracts_case_read import CaseReadPort, CaseReadError, case_read_service
from .infrastructure.case_scoped_reads import ScopedCaseReads
from .infrastructure.case_read_model import LegacyCaseReads


def legacy_case_reads(gateway: Any) -> LegacyCaseReads:
    return LegacyCaseReads(gateway)
from .infrastructure.case_scoped_reads import native_task_scope as assert_case_task_access

from .infrastructure.task_cancellation import release_cancelled_task as release_cancelled_warehouse_task_resource

from .infrastructure.forecast_norms import forecast_norm_basis
from .domain.forecast_labour import forecast_labour

from .contracts_timeline import ResourceTimelinePort, resource_timeline_service, TimelineClockReader
from .api.timeline_routes import router as resource_timeline_router
from .infrastructure.resource_timeline import ResourceTimeline
from .infrastructure.session_reads import list_session_rows
from .contracts_session_read import ResourceReadError


def build_resource_timeline(gateway: Any, clock_reader: TimelineClockReader | None = None) -> ResourceTimelinePort:
    return ResourceTimeline(gateway, clock_reader)

from .contracts_case_resource import CaseResourcePort, case_resource_service
from .infrastructure.case_resource_commands import CaseResourceCommands
from .api.case_resource_routes import router as case_resource_router


def build_case_resource_service(gateway: Any | None = None) -> CaseResourcePort:
    from ...oracle_gateway import OracleGateway
    return CaseResourceCommands(gateway if gateway is not None else OracleGateway())

from .contracts_task_resource import TaskResourcePort, task_resource_service
from .infrastructure.task_resource_commands import TaskResourceCommands
from .api.task_resource_routes import router as task_resource_router


def build_task_resource_service(gateway: Any | None = None) -> TaskResourcePort:
    from ...oracle_gateway import OracleGateway
    return TaskResourceCommands(gateway if gateway is not None else OracleGateway())

# Approved time basis only; a verified runtime fact adapter is still required.
from .domain.picker_time_denominators import (
    ConfirmedTimeInterval, ConfirmedTimeCoverage, TimeDenominator,
    PickerTimeDenominators, picker_time_denominators,
)

from .contracts_resource_intents import ResourceIntentPort, resource_intent_service
from .api.resource_intent_routes import router as resource_intent_router
from .infrastructure.resource_intent_commands import ResourceIntentCommands


def build_resource_intent_service() -> ResourceIntentPort:
    from ...oracle_gateway import OracleGateway
    return ResourceIntentCommands(OracleGateway())

from .contracts_picker_time import PickerTimePort, picker_time_service
from .api.picker_time_routes import router as picker_time_router
from .application.picker_time_service import PickerTimeService
from .infrastructure.picker_time_native import PickerTimeNative


def build_picker_time_service() -> PickerTimePort:
    from ...oracle_gateway import OracleGateway
    return PickerTimeService(PickerTimeNative(OracleGateway()))

from .contracts_picker_kpi import PickerKpiPort, picker_kpi_service
from .api.picker_kpi_routes import router as picker_kpi_router
from .application.picker_kpi_service import PickerKpiService
from .infrastructure.picker_kpi_read import PickerKpiRead


def build_picker_kpi_service() -> PickerKpiPort:
    from ...oracle_gateway import OracleGateway
    return PickerKpiService(PickerKpiRead(OracleGateway()))
