"""Composition root: inject the existing inventory posting owner into transport."""
from typing import Any
from .oracle_gateway import OracleGateway
from .modules.inventory.public import StockCommand, StockPostingError, build_stock_posting_service
from .modules.transport.public import build_loading_service, TransportLoadingPort, TransportLoadingError


def build_transport_loading() -> TransportLoadingPort:
    posting = build_stock_posting_service()

    def post(kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        try:
            return posting.post(StockCommand(operation_id=operation_id,command_type=kind,
                actor=actor,source=source,lines=(),metadata=metadata))
        except StockPostingError as exc:
            uncertain = exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","LOCK_RETRY_EXHAUSTED","CONNECTION_UNUSABLE","STOCK_RELEASE_NOT_ACTIVE"}
            raise TransportLoadingError(exc.code,exc.rule_reason or str(exc),operation_id,
                503 if uncertain else 403 if exc.oracle_code == 20882 else 409) from exc
        except ValueError as exc:
            raise TransportLoadingError("COMMAND_INVALID",str(exc),operation_id,422) from exc

    return build_loading_service(OracleGateway(),post)

from .modules.transport.public import DriverBindingPort,build_driver_binding

def build_transport_driver_binding() -> DriverBindingPort:
    return build_driver_binding(OracleGateway())
