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

from collections.abc import Callable
from typing import Any
from .contracts_returns import SapStoreReturnsPort,sap_store_returns_service
from .api.store_return_routes import router as sap_store_return_router
from .infrastructure.store_returns import SapStoreReturns

def build_sap_store_returns(post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> SapStoreReturnsPort:
    return SapStoreReturns(post)

from .contracts_regulatory import RegulatoryAdapter,RegulatoryResponse
from .infrastructure.regulatory_runtime import build_regulatory_adapter,MockRegulatoryAdapter,regulatory_runtime_status
from .api.regulatory_runtime_routes import router as regulatory_runtime_router,regulatory_runtime_service

from .domain.adapter_evidence import adapter_request_evidence

from .domain.regulatory_delivery import regulatory_delivery_decision

from .infrastructure.outbox_delivery import OutboxDelivery

from .infrastructure.outbox_response_journal import OutboxResponseJournal

from .domain.scale_sma import SmaObservation, parse_sma_gross_kg
from .infrastructure.scale_outbox import SqliteScaleOutbox
from .infrastructure.scale_http import HttpScaleGateway
from .application.scale_gateway import ScaleGatewayWorker
from .contracts_scales import ScaleGatewayError

from .contracts_warehouse_gateway import WarehouseGatewayProfile

from .infrastructure.warehouse_scale_http import HttpWarehouseScaleGateway

from .application.warehouse_scale_gateway import WarehouseScaleGatewayWorker

from .application.warehouse_scale_ack import validate_warehouse_ack

from .contracts_scale_evidence import ScaleEvidence, scale_evidence_service
from .api.scale_evidence_routes import router as scale_evidence_router
from .infrastructure.scale_evidence import ScaleEvidenceArchive


def build_scale_evidence() -> ScaleEvidenceArchive:
    return ScaleEvidenceArchive(OracleGateway())
