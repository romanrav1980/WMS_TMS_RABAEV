from typing import Any
from collections.abc import Callable
from .oracle_gateway import OracleGateway
from .modules.inventory.public import StockCommand,StockPostingError,build_stock_posting_service
from .modules.inventory.public import StoreReturnReceivePort,StoreReturnReceiveError,build_store_return_receiving


def _return_poster() -> Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]:
    posting=build_stock_posting_service()

    def post(kind: str,operation_id: str,source: dict[str,Any],metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        try:
            return posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source=source,lines=(),metadata=metadata))
        except StockPostingError as exc:
            uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","LOCK_RETRY_EXHAUSTED","CONNECTION_UNUSABLE","STOCK_RELEASE_NOT_ACTIVE"}
            raise StoreReturnReceiveError(exc.code,exc.rule_reason or str(exc),503 if uncertain else 403 if abs(exc.oracle_code or 0)==20882 else 409,operation_id) from exc
        except ValueError as exc:
            raise StoreReturnReceiveError("STORE_RETURN_INPUT_INVALID",str(exc),422,operation_id) from exc

    return post

def build_return_receiving() -> StoreReturnReceivePort:
    return build_store_return_receiving(OracleGateway(),_return_poster())

from .modules.inventory.public import ReturnPutawayPort,build_return_putaway

def build_store_return_putaway() -> ReturnPutawayPort:
    return build_return_putaway(OracleGateway(),_return_poster())
