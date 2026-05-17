from fastapi import APIRouter, HTTPException

from ..schemas import (
    AggregationItemRequest,
    AggregationCreateRequest,
    CrptCodeStatusRequest,
    CrptCodeRequest,
    IdResponse,
    MercuryBatchRequest,
    MercuryOperationCreateRequest,
    MercuryOperationUpdateRequest,
    MercurySiteRequest,
    PalletAttachRequest,
    ProductionBatchCreate,
    RawBatchCreate,
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


@router.post("/raw-batches", response_model=IdResponse)
def create_raw_batch(request: RawBatchCreate) -> IdResponse:
    raw_batch_id = ProductionService().create_raw_batch(request)
    return IdResponse(id=raw_batch_id)


@router.get("/raw-batches/{raw_batch_id}")
def get_raw_batch(raw_batch_id: int) -> dict:
    raw_batch = ProductionService().get_raw_batch(raw_batch_id)
    if not raw_batch:
        raise HTTPException(status_code=404, detail="Raw batch not found.")
    return raw_batch


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


@router.post("/aggregations/{aggregation_id}/items")
def add_aggregation_item(aggregation_id: int, request: AggregationItemRequest) -> dict[str, str]:
    ProductionService().add_aggregation_item(aggregation_id, request)
    return {"status": "ok"}


@router.post("/production-batches/{prod_batch_id}/mercury")
def set_mercury_batch(prod_batch_id: int, request: MercuryBatchRequest) -> dict[str, str]:
    ProductionService().set_mercury_batch(prod_batch_id, request)
    return {"status": "ok"}


@router.get("/production-batches/{prod_batch_id}/regulatory-status")
def get_regulatory_status(prod_batch_id: int) -> dict:
    status = ProductionService().get_regulatory_status(prod_batch_id)
    if not status:
        raise HTTPException(status_code=404, detail="Production batch not found.")
    return status


@router.post("/regulatory/mercury-sites", response_model=IdResponse)
def upsert_mercury_site(request: MercurySiteRequest) -> IdResponse:
    site_id = ProductionService().upsert_mercury_site(request)
    return IdResponse(id=site_id)


@router.get("/regulatory/mercury-sites")
def list_mercury_sites(active: int | None = None) -> list[dict]:
    return ProductionService().list_mercury_sites(active=active)


@router.post("/production-batches/{prod_batch_id}/mercury-operations", response_model=IdResponse)
def create_batch_mercury_operation(
    prod_batch_id: int, request: MercuryOperationCreateRequest
) -> IdResponse:
    operation_id = ProductionService().create_mercury_operation(prod_batch_id, request)
    return IdResponse(id=operation_id)


@router.post("/mercury-operations", response_model=IdResponse)
def create_mercury_operation(request: MercuryOperationCreateRequest) -> IdResponse:
    operation_id = ProductionService().create_mercury_operation(None, request)
    return IdResponse(id=operation_id)


@router.patch("/mercury-operations/{operation_row_id}")
def update_mercury_operation(
    operation_row_id: int, request: MercuryOperationUpdateRequest
) -> dict[str, str]:
    ProductionService().update_mercury_operation(operation_row_id, request)
    return {"status": "ok"}


@router.post("/crpt-codes/status", response_model=IdResponse)
def set_crpt_code_status(request: CrptCodeStatusRequest) -> IdResponse:
    code_id = ProductionService().set_crpt_code_status(request)
    return IdResponse(id=code_id)


@router.get("/regulatory/journal")
def list_regulatory_journal(
    prod_batch_id: int | None = None,
    system_code: str | None = None,
    limit: int = 100,
) -> list[dict]:
    return ProductionService().list_journal(
        prod_batch_id=prod_batch_id,
        system_code=system_code,
        limit=limit,
    )


@router.get("/regulatory/outbox")
def list_regulatory_outbox(
    status: str | None = None,
    system_code: str | None = None,
    limit: int = 100,
) -> list[dict]:
    return ProductionService().list_outbox(status=status, system_code=system_code, limit=limit)
