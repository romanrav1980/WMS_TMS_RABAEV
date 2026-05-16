from fastapi import APIRouter, HTTPException

from ..schemas import (
    AggregationCreateRequest,
    CrptCodeRequest,
    IdResponse,
    MercuryBatchRequest,
    PalletAttachRequest,
    ProductionBatchCreate,
    RawUsageRequest,
)
from ..services.production_service import ProductionService

router = APIRouter(prefix="/api", tags=["production"])


@router.post("/production-batches", response_model=IdResponse)
def create_production_batch(request: ProductionBatchCreate) -> IdResponse:
    batch_id = ProductionService().create_batch(request)
    return IdResponse(id=batch_id)


@router.get("/production-batches/{prod_batch_id}/status")
def get_production_batch_status(prod_batch_id: int) -> dict:
    status = ProductionService().get_batch_status(prod_batch_id)
    if not status:
        raise HTTPException(status_code=404, detail="Production batch not found.")
    return status


@router.post("/production-batches/{prod_batch_id}/pallets")
def attach_pallet(prod_batch_id: int, request: PalletAttachRequest) -> dict[str, str]:
    ProductionService().attach_pallet(prod_batch_id, request)
    return {"status": "ok"}


@router.post("/production-batches/{prod_batch_id}/raw-usage", response_model=IdResponse)
def add_raw_usage(prod_batch_id: int, request: RawUsageRequest) -> IdResponse:
    usage_id = ProductionService().add_raw_usage(prod_batch_id, request)
    return IdResponse(id=usage_id)


@router.post("/production-batches/{prod_batch_id}/crpt-codes", response_model=IdResponse)
def add_crpt_code(prod_batch_id: int, request: CrptCodeRequest) -> IdResponse:
    code_id = ProductionService().add_crpt_code(prod_batch_id, request)
    return IdResponse(id=code_id)


@router.post("/production-batches/{prod_batch_id}/aggregations", response_model=IdResponse)
def create_aggregation(prod_batch_id: int, request: AggregationCreateRequest) -> IdResponse:
    aggregation_id = ProductionService().create_aggregation(prod_batch_id, request)
    return IdResponse(id=aggregation_id)


@router.post("/production-batches/{prod_batch_id}/mercury")
def set_mercury_batch(prod_batch_id: int, request: MercuryBatchRequest) -> dict[str, str]:
    ProductionService().set_mercury_batch(prod_batch_id, request)
    return {"status": "ok"}
