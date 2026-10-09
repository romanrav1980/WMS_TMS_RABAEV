from ...oracle_gateway import OracleGateway
from .api.routes import router, artmas_service
from .application.ingestion import ArtmasIngestion
from .infrastructure.artmas_inbox import ArtmasInbox
from .infrastructure.article_master import ArticleMasterApply
from .infrastructure.supply_orders import SupplyOrders
from .api.supply_routes import router as supply_router, supply_service
from .infrastructure.receipt_outbox import ReceiptOutbox
from .infrastructure.file_gateway import receive_files as receive_gateway_files
from .infrastructure.receipt_acknowledgements import ReceiptAcknowledgements
from .api.receipt_event_routes import router as receipt_event_router, acknowledgement_service


def build_artmas_service() -> ArtmasIngestion:
    gateway = OracleGateway()
    return ArtmasIngestion(ArtmasInbox(gateway), ArticleMasterApply(gateway))


def build_supply_service() -> SupplyOrders:
    return SupplyOrders(OracleGateway())


def build_receipt_exporter() -> ReceiptOutbox:
    return ReceiptOutbox(OracleGateway())


def build_acknowledgements() -> ReceiptAcknowledgements:
    return ReceiptAcknowledgements(OracleGateway())


__all__ = ["router", "artmas_service", "build_artmas_service", "supply_router", "supply_service", "build_supply_service",
           "build_receipt_exporter", "build_acknowledgements", "receive_gateway_files", "receipt_event_router", "acknowledgement_service"]
