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


def pallet_composition(pallet: str, after: str = "", limit: int = 50) -> dict:
    return ReceivingQueries(OracleGateway()).composition(pallet, after, min(max(limit, 1), 100))


def build_query_service() -> ReceivingQueries:
    return ReceivingQueries(OracleGateway())


def complete_existing_warehouse_task(gateway, task_id: int, request, actor: str) -> None:
    from .infrastructure.task_completion import complete_existing_task
    return complete_existing_task(gateway, task_id, request, actor)


def lock_warehouse_task_domain(gateway, task: dict) -> None:
    from .infrastructure.task_completion import lock_domain
    lock_domain(gateway, task)


def apply_warehouse_task_stock_move(gateway, task: dict, actor: str) -> bool:
    from .infrastructure.task_stock_move import apply_task_stock_move
    return apply_task_stock_move(gateway, task, actor)


def apply_warehouse_replenishment_reservation(gateway, task: dict, finished: bool, fresh: bool, actor: str) -> None:
    from .infrastructure.task_reservation import apply_replenishment_reservation
    apply_replenishment_reservation(gateway, task, finished, fresh, actor)


def run_existing_warehouse_task_action(gateway, task_id: int, action: str, request) -> None:
    from .infrastructure.task_completion import run_existing_task_action
    run_existing_task_action(gateway, task_id, action, request)


__all__ = ['router', 'receiving_service', 'build_receiving_service', 'build_label_service',
           'build_configuration_service', 'build_reconciliation_service', 'build_query_service',
           'label_service', 'configuration_service', 'reconciliation_service', 'query_service',
           'pallet_composition']


# Stock posting v2 boundary; installation and activation are separate.
from .contracts_stock import StockCommand, StockLine
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


def inventory_configuration_transaction(gateway, label: str, actor: str, permission: str):
    from .infrastructure.configuration_uow import configuration_transaction
    return configuration_transaction(gateway, label, actor, permission)


def reserve_existing_wave_sources(gateway, wave_id: int, actor: str) -> bool:
    from .infrastructure.wave_commands import reserve_wave_sources
    return reserve_wave_sources(gateway, wave_id, actor)


def release_existing_document_reservations(gateway, document_type: str, document_id: int, actor: str, reason: str, **scope) -> bool:
    from .infrastructure.document_reservation_commands import release_document_reservations
    return release_document_reservations(gateway, document_type, document_id, actor, reason, **scope)


def post_existing_mes_task(gateway, action: str, task: dict, request):
    from .infrastructure.mes_task_commands import post_mes_task
    return post_mes_task(gateway, action, task, request)


def calculate_existing_mes_supply(gateway, order_id: int, request):
    from .infrastructure.mes_supply_commands import calculate_supply
    return calculate_supply(gateway, order_id, request)

from .api.inventory_count_routes import router as inventory_count_router
__all__.append("inventory_count_router")


from .application.stock_commands import ReceiptReverse
from .api.stock_command_routes import receipt_reverse_service


def build_receipt_reverse_service() -> ReceiptReverse:
    return ReceiptReverse(build_stock_posting_service())


__all__.extend(["receipt_reverse_service", "build_receipt_reverse_service"])


def post_existing_case_pick(gateway, task_id: int, line_id: int, request):
    from .infrastructure.case_pick_commands import post_case_pick
    return post_case_pick(gateway, task_id, line_id, request)


def warehouse_metadata_transaction(gateway, purpose: str, actor: str, permission: str):
    from .infrastructure.metadata_transactions import receipt_task_metadata
    return receipt_task_metadata(gateway, purpose, actor, permission)


def existing_case_pick_policy(gateway, task_id: int, line_id: int):
    from .infrastructure.case_pick_policy import case_pick_policy
    return case_pick_policy(gateway, task_id, line_id)


def build_case_carrier_move_service():
    from .application.case_carrier_move import CaseCarrierMove
    return CaseCarrierMove(build_stock_posting_service())


def post_existing_case_short_approval(gateway, short_id: int, request):
    from .infrastructure.case_short_commands import post_short_approval
    return post_short_approval(gateway, short_id, request)


from .api.error_handlers import install_stock_error_handlers

def post_existing_terminal_quality(gateway, pallet: str, request):
    from .infrastructure.terminal_quality_commands import post_terminal_quality
    return post_terminal_quality(gateway, pallet, request)


def bind_existing_case_shipment(gateway, task_id: int, pallet_identifier: str,
                               scan_container: str, expected_version: int, actor: str):
    from .infrastructure.case_shipment_binding import bind_case_shipment
    return bind_case_shipment(gateway, task_id, pallet_identifier, scan_container, expected_version, actor)


def return_existing_case_carrier(task_id:int,request,actor:str):
    from .infrastructure.stock_posting_uow import StockPosting
    from .contracts_stock import StockCommand
    if not 1 <= len(request.destinations) <= 200 or any(not k or not v or len(v)>60 for k,v in request.destinations.items()):
        raise ValueError("Bounded scanned destinations required")
    return StockPosting().post(StockCommand(operation_id=request.operation_id,command_type="CASE_CARRIER_RETURN",
        actor=actor,lines=(),source={"case_task_id":task_id},
        metadata=request.model_dump(mode="json",exclude={"operation_id"})))
