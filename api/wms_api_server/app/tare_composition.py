from typing import Any
from .oracle_gateway import OracleGateway
from .modules.inventory.public import StockCommand,StockPostingError,build_stock_posting_service,build_tare,TarePort,TareError

def build_tare_ledger() -> TarePort:
    posting=build_stock_posting_service()
    def post(kind: str,operation_id: str,source: dict[str,Any],metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        try:return posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source=source,lines=(),metadata=metadata))
        except StockPostingError as exc:
            uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","LOCK_RETRY_EXHAUSTED","CONNECTION_UNUSABLE","STOCK_RELEASE_NOT_ACTIVE"}
            raise TareError(exc.code,exc.rule_reason or str(exc),503 if uncertain else 403 if abs(exc.oracle_code or 0)==20882 else 409,operation_id) from exc
        except ValueError as exc:raise TareError("TARE_INPUT_INVALID",str(exc),422,operation_id) from exc
    return build_tare(OracleGateway(),post)

from .modules.inventory.public import TarePolicyPort,build_tare_policy

def build_tare_return_policy() -> TarePolicyPort:
    return build_tare_policy(OracleGateway())

from .modules.inventory.public import TareAssemblyPort,build_tare_assembly

def build_tare_for_assembly() -> TareAssemblyPort:
    return build_tare_assembly(OracleGateway())
