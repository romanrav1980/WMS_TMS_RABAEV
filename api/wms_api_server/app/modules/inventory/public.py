from __future__ import annotations
from .domain.pallet_identifiers import normalize_incoming_sscc as normalize_pallet_scan_identifier
from typing import Any
from contextlib import AbstractContextManager
import oracledb
from ...transaction_gateway import TransactionGateway
from ...schemas import (PickingPlanCreateRequest, WarehouseTaskStatusRequest, MesRawTransferTaskConfirmRequest, MesRawTransferTaskCancelRequest,
    MesRawSupplyCalculateRequest, CasePickLineConfirmRequest, CasePickShortDecisionRequest, LotCheckRequest)
from .contracts_task_actions import TaskActionHandler
from .contracts_case_return import CaseCarrierReturnRequest
from .application.case_carrier_move import CaseCarrierMove
from collections.abc import Callable
from ...oracle_gateway import OracleGateway
from .api.receiving_routes import router, receiving_service, label_service, configuration_service, reconciliation_service, query_service
from .infrastructure.receiving import Receiving
from .infrastructure.labels import ReceiptLabels
from .infrastructure.configuration import ReceiptConfiguration
from .infrastructure.reconciliation import ReceiptReconciliation
from .infrastructure.receiving_queries import ReceivingQueries

def build_receiving_service() -> Receiving:
    return Receiving(OracleGateway())

def build_label_service() -> ReceiptLabels:
    return ReceiptLabels(OracleGateway())

def build_configuration_service() -> ReceiptConfiguration:
    return ReceiptConfiguration(OracleGateway())

def build_reconciliation_service() -> ReceiptReconciliation:
    return ReceiptReconciliation(OracleGateway())

def pallet_composition(pallet: str, after: str = "", limit: int = 50, expected_signature: str|None=None) -> dict:
    return ReceivingQueries(OracleGateway()).composition(pallet, after, min(max(limit, 1), 100),expected_signature)

def build_query_service() -> ReceivingQueries:
    return ReceivingQueries(OracleGateway())

def complete_existing_warehouse_task(gateway: OracleGateway | TransactionGateway, task_id: int, request: WarehouseTaskStatusRequest, actor: str) -> dict[str, Any]:
    from .infrastructure.task_completion import complete_existing_task
    return complete_existing_task(gateway, task_id, request, actor)

def run_existing_warehouse_task_action(gateway: OracleGateway | TransactionGateway, task_id: int, action: str, request: WarehouseTaskStatusRequest, service_factory: Callable[[TransactionGateway], TaskActionHandler]) -> None:
    from .infrastructure.task_completion import run_existing_task_action
    run_existing_task_action(gateway, task_id, action, request, service_factory)

__all__ = ['router', 'receiving_service', 'build_receiving_service', 'build_label_service',
           'build_configuration_service', 'build_reconciliation_service', 'build_query_service',
           'label_service', 'configuration_service', 'reconciliation_service', 'query_service',
           'pallet_composition', 'normalize_pallet_scan_identifier']

# Stock posting v2 boundary; installation and activation are separate.
from .contracts_stock import StockCommand, StockLine, StockPostingError
from .api.stock_routes import router as stock_router, stock_queries_service
from .infrastructure.stock_posting_queries import StockPostingQueries
from .infrastructure.stock_posting_uow import StockPosting

def build_stock_queries_service() -> StockPostingQueries:
    return StockPostingQueries(OracleGateway())

def build_stock_posting_service() -> StockPosting:
    return StockPosting()

__all__.extend(["StockCommand", "StockLine", "stock_router", "stock_queries_service", "build_stock_queries_service", "build_stock_posting_service"])

from .application.stock_commands import ManualStockMove
from .api.stock_command_routes import router as stock_command_router, manual_stock_move_service

def build_manual_stock_move_service() -> ManualStockMove:
    return ManualStockMove(build_stock_posting_service())

__all__.extend(["stock_command_router", "manual_stock_move_service", "build_manual_stock_move_service"])

def inventory_configuration_transaction(gateway: OracleGateway | TransactionGateway, label: str, actor: str, permission: str) -> AbstractContextManager[oracledb.Cursor]:
    from .infrastructure.configuration_uow import configuration_transaction
    return configuration_transaction(gateway, label, actor, permission)

def reserve_existing_wave_sources(gateway: OracleGateway | TransactionGateway, wave_id: int, actor: str) -> bool:
    from .infrastructure.wave_commands import reserve_wave_sources
    return reserve_wave_sources(gateway, wave_id, actor)

def release_existing_document_reservations(gateway: OracleGateway | TransactionGateway, document_type: str, document_id: int, actor: str, reason: str, **scope: bool | str | None) -> bool:
    from .infrastructure.document_reservation_commands import release_document_reservations
    return release_document_reservations(gateway, document_type, document_id, actor, reason, **scope)

def post_existing_mes_task(gateway: OracleGateway | TransactionGateway, action: str, task: dict, request: MesRawTransferTaskConfirmRequest | MesRawTransferTaskCancelRequest) -> dict[str, Any]:
    from .infrastructure.mes_task_commands import post_mes_task
    return post_mes_task(gateway, action, task, request)

def calculate_existing_mes_supply(gateway: OracleGateway | TransactionGateway, order_id: int, request: MesRawSupplyCalculateRequest) -> dict[str, Any]:
    from .infrastructure.mes_supply_commands import calculate_supply
    return calculate_supply(gateway, order_id, request)

from .api.inventory_count_routes import router as inventory_count_router
__all__.append("inventory_count_router")

from .application.stock_commands import ReceiptReverse
from .api.stock_command_routes import receipt_reverse_service

def build_receipt_reverse_service() -> ReceiptReverse:
    return ReceiptReverse(build_stock_posting_service())

__all__.extend(["receipt_reverse_service", "build_receipt_reverse_service"])

def post_existing_case_pick(gateway: OracleGateway | TransactionGateway, task_id: int, line_id: int, request: CasePickLineConfirmRequest) -> dict[str, Any]:
    from .infrastructure.case_pick_commands import post_case_pick
    return post_case_pick(gateway, task_id, line_id, request)

def warehouse_metadata_transaction(gateway: OracleGateway | TransactionGateway, purpose: str, actor: str, permission: str) -> AbstractContextManager[oracledb.Cursor]:
    from .infrastructure.metadata_transactions import receipt_task_metadata
    return receipt_task_metadata(gateway, purpose, actor, permission)

def existing_case_pick_policy(gateway: OracleGateway | TransactionGateway, task_id: int, line_id: int) -> dict[str, Any]:
    from .infrastructure.case_pick_policy import case_pick_policy
    return case_pick_policy(gateway, task_id, line_id)

def build_case_carrier_move_service() -> CaseCarrierMove:
    from .application.case_carrier_move import CaseCarrierMove
    return CaseCarrierMove(build_stock_posting_service())

def post_existing_case_short_approval(gateway: OracleGateway | TransactionGateway, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]:
    from .infrastructure.case_short_commands import post_short_approval
    return post_short_approval(gateway, short_id, request)

from .api.error_handlers import install_stock_error_handlers

def post_existing_terminal_quality(gateway: OracleGateway | TransactionGateway, pallet: str, request: LotCheckRequest) -> dict[str, Any]:
    from .infrastructure.terminal_quality_commands import post_terminal_quality
    return post_terminal_quality(gateway, pallet, request)

def bind_existing_case_shipment(gateway: OracleGateway | TransactionGateway, task_id: int, pallet_identifier: str,
                               scan_container: str, expected_version: int, actor: str) -> dict[str, Any]:
    from .infrastructure.case_shipment_binding import bind_case_shipment
    return bind_case_shipment(gateway, task_id, pallet_identifier, scan_container, expected_version, actor)

def return_existing_case_carrier(task_id:int,request: CaseCarrierReturnRequest,actor:str) -> dict[str, Any]:
    from .infrastructure.stock_posting_uow import StockPosting
    from .contracts_stock import StockCommand
    if not (0 if request.allow_empty else 1) <= len(request.destinations) <= 200 or any(not k or not v or len(v)>60 for k,v in request.destinations.items()):
        raise ValueError("Bounded scanned destinations required")
    return StockPosting().post(StockCommand(operation_id=request.operation_id,command_type="CASE_CARRIER_RETURN",
        actor=actor,lines=(),source={"case_task_id":task_id},
        metadata={**request.model_dump(mode="json",exclude={"operation_id","allow_empty","reason"}),
                  **({"allow_empty":True,"reason":request.reason} if request.allow_empty else {})}))

from .api.source_routes import router as source_router, source_availability_service, source_view_permission
from .infrastructure.source_availability import SourceAvailability

def build_source_availability_service() -> SourceAvailability:
    return SourceAvailability(OracleGateway())

__all__.extend(["source_router", "source_availability_service", "source_view_permission", "build_source_availability_service"] )

from typing import Any as _Any

def get_existing_task_progress(gateway: _Any, task_id: int) -> dict[str, _Any]:
    from .infrastructure.task_progress import task_progress
    return task_progress(gateway, task_id)
from .api.recovery_routes import router as recovery_router, inventory_task_view, inventory_task_execute, recovery_view, recovery_tasks_service
from .infrastructure.recovery_tasks import RecoveryTasks

def build_recovery_tasks_service() -> RecoveryTasks:
    return RecoveryTasks(OracleGateway())
from .infrastructure.short_report_replay import short_report_replay
from .api.task_scan_routes import router as task_scan_router, scan_view, scan_execute, scan_draft_service
from .infrastructure.task_scan_drafts import TaskScanDrafts

def build_task_scan_drafts() -> TaskScanDrafts:
    return TaskScanDrafts(OracleGateway())

from .api.replenishment_progress_routes import (router as replenishment_progress_router,
    replenishment_view,replenishment_progress_service)
from .infrastructure.replenishment_progress import ReplenishmentProgress

def build_replenishment_progress() -> ReplenishmentProgress:
    return ReplenishmentProgress(OracleGateway())

from .contracts_stock import StockPostingError
from .infrastructure.case_events import write_case_event as write_existing_case_event

from .infrastructure.configuration_uow import configuration_transaction as stock_configuration_transaction
from .api.pool_routes import router as pool_router,pool_view,pool_edit,pool_service
from .infrastructure.pool_service import PoolService

def build_pool_service() -> PoolService:
    return PoolService(OracleGateway())

from .infrastructure.minimax_service import MinimaxService
from .api.minimax_routes import router as minimax_router,minimax_view,minimax_edit,minimax_service

from .api.investigation_routes import router as investigation_router,investigation_view,investigation_edit,camera_edit,investigation_service
from .infrastructure.short_investigation import ShortInvestigation

def build_short_investigation() -> ShortInvestigation:
    return ShortInvestigation(OracleGateway())

from .infrastructure.replenishment_continuation import ReplenishmentContinuation

from .api.partial_shipment_routes import router as partial_layout_router, partial_layout_service
from .infrastructure.partial_shipment_layout import PartialShipmentLayout

def build_partial_layout_service() -> PartialShipmentLayout:
    return PartialShipmentLayout(OracleGateway())

from .api.wave_pick_routes import router as wave_pick_router, wave_pick_service
from .infrastructure.wave_pick_release import WavePickRelease

def build_wave_pick_service() -> WavePickRelease:
    return WavePickRelease(OracleGateway())

from .infrastructure.alternative_pick_faces import AlternativePickFaces

def route_existing_alternative_pick_faces(gateway: OracleGateway | TransactionGateway, wave_id: int, actor: str) -> int:
    return AlternativePickFaces(gateway).route_wave(wave_id, actor)

from .api.fullpal_shipment_routes import router as fullpal_shipment_router, fullpal_shipment_service
from .infrastructure.fullpal_shipment import FullPalletShipment

def build_fullpal_shipment_service() -> FullPalletShipment:
    return FullPalletShipment(OracleGateway())

from .infrastructure.replenishment_capacity_hold import hold_unissued_capacity as hold_existing_replenishment_capacity

from .api.wave_execution_routes import router as wave_execution_router, wave_execution_service
from .infrastructure.wave_execution import WaveExecution

def build_wave_execution_service() -> WaveExecution:
    return WaveExecution(OracleGateway())

from .api.warehouse_hu_routes import router as warehouse_hu_router, warehouse_hu_service
from .infrastructure.warehouse_hu import WarehouseHu

def build_warehouse_hu_service() -> WarehouseHu:
    return WarehouseHu(OracleGateway())

from .api.outgoing_quality_routes import router as outgoing_quality_router, outgoing_quality_service
from .infrastructure.outgoing_quality import OutgoingQuality

def build_outgoing_quality_service() -> OutgoingQuality:
    return OutgoingQuality(OracleGateway())

from typing import Any
from .contracts_observations import InventoryObservationsPort, inventory_observations_service
from .infrastructure.inventory_observations import InventoryObservations

def build_inventory_observations_service() -> InventoryObservationsPort:
    return InventoryObservations(OracleGateway(),build_stock_posting_service())

from .contracts_store_returns import StoreReturnReceivePort,StoreReturnReceiveError,store_return_receive_service
from .api.store_return_receiving_routes import router as store_return_receiving_router
from .infrastructure.store_return_receiving import StoreReturnReceiving

def build_store_return_receiving(gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> StoreReturnReceivePort:
    return StoreReturnReceiving(gateway,post)

from .contracts_return_putaway import ReturnPutawayPort,return_putaway_service
from .api.return_putaway_routes import router as return_putaway_router
from .infrastructure.return_putaway import ReturnPutaway

def build_return_putaway(gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> ReturnPutawayPort:
    return ReturnPutaway(gateway,post)

from .contracts_tare import TarePort,TareError,tare_service
from .api.tare_routes import router as tare_router
from .infrastructure.tare import Tare

def build_tare(gateway: Any,post: Callable[...,dict[str,Any]]) -> TarePort:
    return Tare(gateway,post)

from .contracts_tare_policy import TarePolicyPort,tare_policy_service
from .api.tare_policy_routes import router as tare_policy_router
from .infrastructure.tare_policy import TarePolicy

def build_tare_policy(gateway: Any) -> TarePolicyPort:
    return TarePolicy(gateway)

from .api.tare_resolution_routes import router as tare_resolution_router

from .contracts_tare_assembly import TareAssemblyPort,tare_assembly_service
from .api.tare_assembly_routes import router as tare_assembly_router
from .infrastructure.tare_assembly import TareAssembly,case_snapshot as existing_case_tare_snapshot

def build_tare_assembly(gateway: Any) -> TareAssemblyPort:
    return TareAssembly(gateway)

from .api.tare_loss_routes import router as tare_loss_router

from .contracts_supplier_return import SupplierReturnPort,supplier_return_service
from .api.supplier_return_routes import router as supplier_return_router
from .infrastructure.supplier_return import SupplierReturn

def build_supplier_return(gateway: Any) -> SupplierReturnPort:
    return SupplierReturn(gateway)

from .contracts_supplier_handover import SupplierHandoverPort,supplier_handover_service
from .api.supplier_handover_routes import router as supplier_handover_router
from .infrastructure.supplier_handover import SupplierHandover

def build_supplier_handover(gateway: Any) -> SupplierHandoverPort:
    return SupplierHandover(gateway)

from .contracts_disposal import ReturnDisposalPort,return_disposal_service
from .api.return_disposal_routes import router as return_disposal_router
from .infrastructure.return_disposal import ReturnDisposal

def build_return_disposal(gateway: Any) -> ReturnDisposalPort:
    return ReturnDisposal(gateway,StockPosting())

from .contracts_interwarehouse import InterwarehousePort,interwarehouse_service
from .api.interwarehouse_routes import router as interwarehouse_router
from .infrastructure.interwarehouse import Interwarehouse

def build_interwarehouse(gateway: Any) -> InterwarehousePort:
    return Interwarehouse(gateway,StockPosting())

from .contracts_trace_manifest import TraceManifestPort,trace_manifest_service
from .api.trace_manifest_routes import router as trace_manifest_router
from .infrastructure.trace_sender_manifest import TraceSenderManifest

def build_trace_manifest(gateway: Any) -> TraceManifestPort:
    return TraceSenderManifest(gateway)

from .contracts_stock_settings import StockCompatibilityPort,stock_compatibility_service
from .infrastructure.stock_settings import StockCompatibility

def build_stock_compatibility(gateway: Any) -> StockCompatibilityPort:
    return StockCompatibility(gateway)

from .infrastructure.pickface_configuration import configure_existing_pick_face_article

from .contracts_slotting import SlottingDemandPort,slotting_demand_service
from .api.slotting_routes import router as slotting_router
from .infrastructure.slotting_demand_reader import SlottingDemand

def build_slotting_demand(gateway: Any) -> SlottingDemandPort:
    return SlottingDemand(gateway)

from .infrastructure.release_boundary import require_active_release as require_active_stock_release
from .infrastructure.mes_commands import apply_mes_movements as apply_existing_mes_movements
from .infrastructure.mes_release_commands import release_supply as release_existing_mes_supply
from .infrastructure.reservation_commands import post_reservation as post_existing_reservation

from .infrastructure.case_task_services import CaseTaskServices

def build_case_task_services() -> CaseTaskServices:
    return CaseTaskServices(OracleGateway())

from .contracts_range_proposal import RangeProposalPort,range_proposal_service
from .api.range_proposal_routes import router as range_proposal_router
from .infrastructure.range_proposal import RangeProposal

def build_range_proposal(gateway: Any) -> RangeProposalPort:
    return RangeProposal(gateway)

from .contracts_case_close import CaseCarrierCloseRequest
from .infrastructure.case_carrier_close import close_case_carrier as close_existing_case_carrier

def create_existing_pick_plan(gateway: OracleGateway, request: PickingPlanCreateRequest) -> int:
    from .infrastructure.picking_plan import create_existing_plan
    return create_existing_plan(gateway, request)

from .api.warehouse_hu_repack_routes import router as warehouse_hu_repack_router

from .contracts_weighted_case import WeightedCasePort, weighted_case_service
from .api.weighted_case_routes import router as weighted_case_router
from .infrastructure.weighted_case_pick import WeightedCasePick

def build_weighted_case() -> WeightedCasePort:
    return WeightedCasePick(OracleGateway())

from .contracts_warehouse_scale import WarehouseScalePort, warehouse_scale_service
from .api.warehouse_scale_routes import router as warehouse_scale_router
from .infrastructure.warehouse_scales import WarehouseScales

def build_warehouse_scales() -> WarehouseScalePort:
    return WarehouseScales(OracleGateway())

from .contracts_weighted_plan import WeightedPlanPort, weighted_plan_service
from .api.weighted_plan_routes import router as weighted_plan_router
from .infrastructure.weighted_planning import WeightedPlanning

def build_weighted_plan() -> WeightedPlanPort:
    return WeightedPlanning(OracleGateway())

from .contracts_pallet_types import PalletTypeUpsertRequest

def upsert_existing_pallet_type(gateway: OracleGateway,request: PalletTypeUpsertRequest)->int:
    from .infrastructure.pallet_types import upsert_pallet_type
    return upsert_pallet_type(gateway,request)

from .api.case_label_routes import router as case_label_router,labels as case_label_dependency

from .contracts_case_labels import CaseLabelPort
from .infrastructure.case_labels import CaseLabels
def case_label_service()->CaseLabelPort:return CaseLabels(OracleGateway())

def normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]:
    from .domain.mark_identity import normalize_unit_scan_codes as normalize
    return normalize(scans)

__all__.append("normalize_unit_scan_codes")


from .contracts_task_read import TaskReadError,TaskViewScope
from .infrastructure.task_read_scope import read_task_snapshot,read_task_progress_snapshot
from .infrastructure.task_scoped_view import scoped_task_queue,scoped_task_detail
__all__ += ["TaskReadError","TaskViewScope","read_task_snapshot","read_task_progress_snapshot"]

from .infrastructure.interwarehouse_incoming import read_incoming_snapshot as read_interwarehouse_incoming_snapshot

from .domain.receipt_layout import propose_receipt_layout

from .infrastructure.sap_quantity import convert_sap_source_quantity

from .infrastructure.interwarehouse_incoming import read_optional_incoming_snapshot as read_optional_interwarehouse_incoming_snapshot

from .contracts_aggregation_scans import AggregationCodeScan
from .domain.interwarehouse_scans import normalize_interwarehouse_scans

from .api.waiting_task_routes import router as waiting_task_router
from .contracts_waiting_tasks import waiting_task_dependency,WaitingTaskPort
from .infrastructure.st_defer_waiting import StDeferWaiting

def waiting_task_service() -> WaitingTaskPort:
    return StDeferWaiting(OracleGateway())

from .infrastructure.shared_arrival_reconciliation import reconcile_arrived_sources as reconcile_existing_shared_arrival

from .infrastructure.wave_queue_reads import WaveQueueReads

from .contracts_shift_overview import ShiftOverviewPort, shift_overview_service
from .api.shift_overview_routes import router as shift_overview_router
from .infrastructure.shift_overview import ShiftOverview, SectionReader


def build_shift_overview(gateway: Any, readers: dict[str, SectionReader]) -> ShiftOverviewPort:
    return ShiftOverview(gateway, readers)

def build_wave_queue_reads() -> WaveQueueReads:
    return WaveQueueReads(OracleGateway())

from .infrastructure.wave_header import read_wave_header as existing_wave_header


from .infrastructure.task_queue_read import TaskQueueRead


def build_task_queue_read(gateway: Any) -> TaskQueueRead:
    return TaskQueueRead(gateway)

from .infrastructure.shipping_temperature_read import read_shipping_temperature_requirements


from .contracts_pallet_floor import PalletFloorPort,pallet_floor_service
from .api.pallet_floor_routes import router as pallet_floor_router
from .infrastructure.pallet_floor_type import PalletFloorType

def build_pallet_floor_type(gateway: Any,posting: Any)->PalletFloorPort:
    return PalletFloorType(gateway,posting)

from .contracts_case_type import CaseTypePort,case_type_service
from .api.case_type_routes import router as case_type_router
from .infrastructure.case_type import CaseType

def build_case_type(gateway: Any,posting: Any)->CaseTypePort:
    return CaseType(gateway,posting)

from .infrastructure.wave_planning import create_wave as create_existing_wave, add_plan as add_existing_wave_plan

from .contracts_wave_planning import WavePlanningError

from .infrastructure.wave_staging import release_staging as release_existing_wave_staging

from .contracts_quality_scope import QualityScopePort,quality_scope_service
from .contracts_wave_launch import WaveLaunchContinuationError
from .application.wave_launch import continue_launched_wave
from .infrastructure.metadata_transactions import begin_wave_metadata
from .api.quality_scope_routes import router as quality_scope_router
from .infrastructure.quality_scope import QualityScope

def build_quality_scope(gateway: Any) -> QualityScopePort:
    return QualityScope(gateway)

from .contracts_warehouse_scale import WarehouseScalePacket, WarehouseFinalScalePacket
from .contracts_task_completion import TaskCompletionAccessError
from .infrastructure.task_completion_scope import authorize_task_completion

from .contracts_assembly_scale import AssemblyScalePort, assembly_scale_service
from .api.assembly_scale_routes import router as assembly_scale_router
from .infrastructure.assembly_scale import AssemblyScales


def build_assembly_scale(gateway: OracleGateway) -> AssemblyScalePort:
    return AssemblyScales(gateway, StockPosting().post)

from .contracts_assembly_close import AssemblyClosePort, assembly_close_service
from .infrastructure.assembly_close import AssemblyClose
from .api.assembly_close_routes import router as assembly_close_router

from .api.assembly_recovery_routes import router as assembly_recovery_router

from .contracts_warehouse_scale_requests import WarehouseWeighRequestsPort, warehouse_weigh_requests_service
from .api.warehouse_scale_request_routes import router as warehouse_weigh_requests_router
from .infrastructure.warehouse_scale_requests import WarehouseWeighRequests


def build_warehouse_weigh_requests(gateway: OracleGateway) -> WarehouseWeighRequestsPort:
    return WarehouseWeighRequests(gateway)

from .infrastructure.case_confirmation_scope import authorize_existing_case_confirmation
from .contracts_case_confirmation import CaseConfirmationAccessError

from .contracts_assembly_intents import AssemblyIntentPort, assembly_intent_service
from .infrastructure.assembly_intents import AssemblyIntents
from .api.assembly_intent_routes import router as assembly_intent_router

from .contracts_case_current_close import CaseCurrentClosePort, case_current_close_service
from .infrastructure.case_current_close import CaseCurrentClose
from .api.case_current_close_routes import router as case_current_close_router


def build_case_current_close() -> CaseCurrentClosePort:
    return CaseCurrentClose(OracleGateway())

from .contracts_case_empty import CaseEmptyPort, case_empty_service
from .api.case_empty_routes import router as case_empty_router
from .infrastructure.case_empty import CaseEmpty


def build_case_empty() -> CaseEmptyPort:
    return CaseEmpty()


from .api.trade_stock_routes import router as trade_stock_router, trade_stock_service
from .infrastructure.trade_stock import OracleTradeStock


def build_trade_stock() -> OracleTradeStock:
    return OracleTradeStock(OracleGateway())

from .api.trade_planning_routes import router as trade_planning_router, trade_planning_service
from .infrastructure.trade_planning import OracleTradePlanning

def build_trade_planning() -> OracleTradePlanning:
    return OracleTradePlanning(OracleGateway())

from .api.trade_buyout_routes import router as trade_buyout_router,trade_buyout_service
