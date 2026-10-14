"""Inject the sole existing inventory posting owner into destination receipts."""
from typing import Any
from collections.abc import Callable
from .oracle_gateway import OracleGateway
from .modules.inventory.public import StockCommand,StockPostingError,build_stock_posting_service
from .modules.delivery.public import StoreReceiptPort,StoreReceiptError,build_store_receipt


def _delivery_post() -> Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]:
    posting=build_stock_posting_service()

    def post(kind: str, operation_id: str, source: dict[str,Any], metadata: dict[str,Any], actor: str) -> dict[str,Any]:
        try:
            return posting.post(StockCommand(operation_id=operation_id,command_type=kind,
                actor=actor,source=source,lines=(),metadata=metadata))
        except StockPostingError as exc:
            uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","LOCK_RETRY_EXHAUSTED","CONNECTION_UNUSABLE","STOCK_RELEASE_NOT_ACTIVE"}
            raise StoreReceiptError(exc.code,exc.rule_reason or str(exc),503 if uncertain else 403 if abs(exc.oracle_code or 0)==20882 else 409,operation_id) from exc
        except ValueError as exc:
            raise StoreReceiptError("COMMAND_INVALID",str(exc),422,operation_id) from exc

    return post


def build_delivery_receipt() -> StoreReceiptPort:
    return build_store_receipt(OracleGateway(),_delivery_post())

from .modules.delivery.public import StoreEvidencePort,build_store_evidence

def build_delivery_evidence() -> StoreEvidencePort:
    return build_store_evidence(OracleGateway())


from .modules.delivery.public import StoreScalesPort,build_store_scales

def build_delivery_scales() -> StoreScalesPort:
    return build_store_scales(OracleGateway())


from .modules.delivery.public import OrderDeliveryPort,build_order_delivery

def build_delivery_progress() -> OrderDeliveryPort:
    return build_order_delivery(OracleGateway())


from .modules.delivery.public import CaseWorkPort,build_case_work

def build_delivery_case_work() -> CaseWorkPort:
    return build_case_work(OracleGateway(),_delivery_post())

from .modules.delivery.public import StoreReturnsPort,build_store_returns

def build_delivery_returns() -> StoreReturnsPort:
    return build_store_returns(OracleGateway(),_delivery_post())

from .modules.integrations.public import SapStoreReturnsPort,build_sap_store_returns as compose_sap_store_returns

def build_sap_store_returns() -> SapStoreReturnsPort:
    return compose_sap_store_returns(_delivery_post())

from .modules.delivery.public import ReturnTransportPort,build_return_transport

def build_delivery_return_transport() -> ReturnTransportPort:
    return build_return_transport(OracleGateway(),_delivery_post())

from .modules.delivery.public import ReturnCustodyPort,build_return_custody

def build_delivery_return_custody() -> ReturnCustodyPort:
    return build_return_custody(OracleGateway(),_delivery_post())
