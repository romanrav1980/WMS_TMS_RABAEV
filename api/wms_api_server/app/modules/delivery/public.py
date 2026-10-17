"""Destination receipt boundary and injectable infrastructure factory."""
from collections.abc import Callable
from typing import Any
from .contracts import StoreReceiptError,StoreReceiptPort,store_receipt_service
from .api.store_receipt_routes import router as store_receipt_router
from .infrastructure.store_receipt import StoreReceipt


def build_store_receipt(gateway: Any, post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> StoreReceiptPort:
    return StoreReceipt(gateway,post)

from .contracts_delivery_time import DeliveryTimePort, delivery_time_service
from .api.delivery_time_routes import router as delivery_time_router
from .infrastructure.delivery_time import DeliveryTime


def build_delivery_time(gateway: Any) -> DeliveryTimePort:
    return DeliveryTime(gateway)

from .contracts_evidence import StoreEvidencePort,store_evidence_service
from .api.store_evidence_routes import router as store_evidence_router
from .infrastructure.store_evidence import StoreEvidence

def build_store_evidence(gateway: Any) -> StoreEvidencePort:
    return StoreEvidence(gateway)


from .contracts_scales import StoreScalesPort,store_scales_service
from .api.store_scale_routes import router as store_scales_router
from .infrastructure.store_scales import StoreScales

def build_store_scales(gateway: Any) -> StoreScalesPort:
    return StoreScales(gateway)


from .contracts_orders import OrderDeliveryPort,order_delivery_service
from .api.order_delivery_routes import router as order_delivery_router
from .infrastructure.order_delivery import OrderDelivery

def build_order_delivery(gateway: Any) -> OrderDeliveryPort:
    return OrderDelivery(gateway)


from .contracts_case_work import CaseWorkPort,case_work_service
from .api.case_work_routes import router as case_work_router
from .infrastructure.case_work import CaseWork

def build_case_work(gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> CaseWorkPort:
    return CaseWork(gateway,post)

from .contracts_returns import StoreReturnsPort,store_returns_service
from .api.store_return_routes import router as store_return_router
from .infrastructure.store_returns import StoreReturns

def build_store_returns(gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> StoreReturnsPort:
    return StoreReturns(gateway,post)

from .contracts_return_transport import ReturnTransportPort,return_transport_service
from .api.return_transport_routes import router as return_transport_router
from .infrastructure.return_transport import ReturnTransport

def build_return_transport(gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> ReturnTransportPort:
    return ReturnTransport(gateway,post)

from .contracts_return_custody import ReturnCustodyPort,return_custody_service
from .api.return_custody_routes import router as return_custody_router
from .infrastructure.return_custody import ReturnCustody

def build_return_custody(gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> ReturnCustodyPort:
    return ReturnCustody(gateway,post)
from .contracts_store_app import StoreAppPort,store_app_service
from .api.store_app_routes import router as store_app_router
from .infrastructure.store_app_reads import StoreAppReads

from .contracts_scale_requests import StoreScaleRequestsPort, store_scale_requests_service
from .api.store_scale_request_routes import router as store_scale_requests_router
from .infrastructure.store_scale_requests import StoreScaleRequests


def build_store_scale_requests(gateway: Any) -> StoreScaleRequestsPort:
    return StoreScaleRequests(gateway)
