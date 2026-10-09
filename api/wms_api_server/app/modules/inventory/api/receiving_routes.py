"""Receipt entry points kept separately from ERP master-data transport."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator, model_validator

from ....auth import AdminUser, require_permission
from ..application.ports import ReceivingPort as Receiving
from ..domain.pallet_identifiers import normalize_incoming_sscc
from ..application.ports import LabelPort as ReceiptLabels
from ..application.ports import ConfigurationPort as ReceiptConfiguration
from ..application.ports import ReconciliationPort as ReceiptReconciliation
from ..application.ports import QueriesPort as ReceivingQueries
from typing import Literal

router = APIRouter(prefix="/api/receiving", tags=["warehouse-receiving"])


class PalletReceipt(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100)
    line_number: str = Field(min_length=1, max_length=20)
    sscc: str = Field(pattern=r"^[0-9]{18}$")
    quantity: Decimal = Field(gt=0, le=999999999999, decimal_places=6)
    product_barcode: str | None = Field(default=None, min_length=1, max_length=128)
    supplier_batch: str = Field(min_length=1, max_length=100)
    expiry_date: date
    produced_date: date | None = None
    gross_weight: Decimal | None = Field(default=None, gt=0)
    pallet_height: Decimal | None = Field(default=None, gt=0)
    pallet_height_m: Decimal | None = Field(default=None, gt=0)
    volume_m3: Decimal | None = Field(default=None, gt=0)
    units: list[dict] = Field(default_factory=list, max_length=10000)
    aggregations: list[dict] = Field(default_factory=list, max_length=1000)

    @field_validator("sscc", mode="before")
    @classmethod
    def normalize_sscc(cls, value: object) -> object:
        return normalize_incoming_sscc(value)


class PutawayConfirmation(BaseModel):
    scanned_pallet: str
    scanned_from_cell: str
    scanned_to_cell: str


def receiving_service() -> Receiving:
    raise RuntimeError("Receiving service not wired")


def label_service() -> ReceiptLabels:
    raise RuntimeError("Label service not wired")


def configuration_service() -> ReceiptConfiguration:
    raise RuntimeError("Receiving configuration not wired")


def reconciliation_service() -> ReceiptReconciliation:
    raise RuntimeError("Reconciliation service not wired")


def query_service() -> ReceivingQueries:
    raise RuntimeError("Receiving query service not wired")


@router.get("/pallets/{pallet}/composition")
def pallet_composition(pallet: str, after: str = "", limit: int = Query(50, ge=1, le=100),
                        user: AdminUser = Depends(require_permission("traceability_view")),
                        service: ReceivingQueries = Depends(query_service)) -> dict:
    try:
        return service.composition(pallet, after, limit)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


class LabelIssue(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100)
    line_number: str = Field(min_length=1, max_length=20)
    quantity: Decimal = Field(gt=0, decimal_places=6)
    supplier_batch: str = Field(min_length=1, max_length=100)
    expiry_date: date


class LabelScan(BaseModel):
    scanned_sscc: str = Field(min_length=18, max_length=25)


class WarehouseReceiptSettings(BaseModel):
    company_prefix: str | None = Field(default=None, pattern=r"^[0-9]{6,12}$")
    extension_digit: int = Field(default=0, ge=0, le=9)
    coordinate_unit_m: Decimal = Field(default=1, gt=0)
    reachtruck_mps: Decimal = Field(default=1, gt=0)
    lift_mps: Decimal = Field(default="0.5", gt=0)
    placement_metric: Literal["DISTANCE", "TIME"] = "DISTANCE"


class TemperatureRule(BaseModel):
    temp_min: Decimal | None = None
    temp_max: Decimal | None = None

    @model_validator(mode="after")
    def ordered_temperature(self) -> "TemperatureRule":
        if (self.temp_min is None) != (self.temp_max is None) or (self.temp_min is not None and self.temp_min > self.temp_max):
            raise ValueError("Set both temperature limits in ascending order, or leave both empty")
        return self


class SkuPlacementRule(TemperatureRule):
    pick_cell: str = Field(min_length=1, max_length=60)
    min_shelf_days: int = Field(default=0, ge=0)


class CellPlacementRule(TemperatureRule):
    pick_cell: str | None = Field(default=None, max_length=60)
    travel_sec: Decimal | None = Field(default=None, ge=0)
    basis: Literal["MEASURED", "ROUTE_GRAPH", "NORMATIVE"] = "NORMATIVE"


class CloseSupply(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=3, max_length=1000)


class ReplanPutaway(BaseModel):
    operation_id: str = Field(min_length=1, max_length=60, pattern=r"^[A-Za-z0-9._:-]+$")
    scanned_pallet: str = Field(min_length=1, max_length=25)
    scanned_from_cell: str = Field(min_length=1, max_length=60)
    reason: str = Field(min_length=3, max_length=500)


@router.post("/putaway/{task_id}/replan")
def replan_putaway(task_id: int, body: ReplanPutaway, user: AdminUser = Depends(require_permission("warehouse_task_assign")),
                    service: Receiving = Depends(receiving_service)) -> dict:
    try:
        return service.replan(task_id, body.model_dump(), user.username)
    except (LookupError, ValueError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/supply-orders/{order_id}/labels", status_code=201)
def issue_label(order_id: str, body: LabelIssue, user: AdminUser = Depends(require_permission("warehouse_receipt_confirm")),
                service: ReceiptLabels = Depends(label_service)) -> dict:
    try:
        return service.issue(order_id, body.model_dump(mode="json"), user.username)
    except (LookupError, ValueError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/labels/{label_id}")
def read_label(label_id: str, format: Literal["html", "zpl"] = "html", dpi: int = Query(203, ge=203, le=600), user: AdminUser = Depends(require_permission("warehouse_receipt_confirm")),
               service: ReceiptLabels = Depends(label_service)) -> Response:
    try:
        return Response(service.document(label_id, format, dpi), media_type="text/html" if format == "html" else "text/plain",
                        headers={"Content-Disposition": f'inline; filename="label-{label_id}.{format}"'})
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/labels/{label_id}/confirm")
def confirm_label(label_id: str, body: LabelScan, user: AdminUser = Depends(require_permission("warehouse_receipt_confirm")),
                  service: ReceiptLabels = Depends(label_service)) -> dict:
    try:
        return service.confirm(label_id, body.scanned_sscc, user.username)
    except (LookupError, ValueError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/warehouses/{warehouse}/settings")
def get_settings(warehouse: int, user: AdminUser = Depends(require_permission("warehouse_settings_view")),
                  service: ReceiptConfiguration = Depends(configuration_service)) -> dict:
    return service.get(warehouse)


@router.put("/warehouses/{warehouse}/settings")
def save_settings(warehouse: int, body: WarehouseReceiptSettings, user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
                   service: ReceiptConfiguration = Depends(configuration_service)) -> dict:
    try:
        return service.save(warehouse, body.model_dump(), user.username)
    except (ValueError, LookupError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.put("/warehouses/{warehouse}/skus/{articul}/placement-rule")
def save_sku_rule(warehouse: int, articul: str, body: SkuPlacementRule, user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
                  service: ReceiptConfiguration = Depends(configuration_service)) -> dict:
    try:
        return service.sku_rule(warehouse, articul, body.model_dump(), user.username)
    except (ValueError, LookupError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/warehouses/{warehouse}/skus/{articul}/placement-rule")
def read_sku_rule(warehouse: int, articul: str, user: AdminUser = Depends(require_permission("warehouse_settings_view")),
                  service: ReceiptConfiguration = Depends(configuration_service)) -> dict:
    return service.read_rule(warehouse, articul, "sku")


@router.get("/warehouses/{warehouse}/cells/{cell}/placement-rule")
def read_cell_rule(warehouse: int, cell: str, user: AdminUser = Depends(require_permission("warehouse_settings_view")),
                   service: ReceiptConfiguration = Depends(configuration_service)) -> dict:
    return service.read_rule(warehouse, cell, "cell")


@router.put("/warehouses/{warehouse}/cells/{cell}/placement-rule")
def save_cell_rule(warehouse: int, cell: str, body: CellPlacementRule, user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
                   service: ReceiptConfiguration = Depends(configuration_service)) -> dict:
    try:
        return service.cell_rule(warehouse, cell, body.model_dump(), user.username)
    except (ValueError, LookupError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/supply-orders/{order_id}/close")
def close_supply(order_id: str, body: CloseSupply, user: AdminUser = Depends(require_permission("warehouse_receipt_reconcile")),
                  service: ReceiptReconciliation = Depends(reconciliation_service)) -> dict:
    try:
        return service.close(order_id, body.operation_id, body.reason, user.username)
    except (ValueError, LookupError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/supply-orders/{order_id}/reopen")
def reopen_supply(order_id: str, body: CloseSupply, user: AdminUser = Depends(require_permission("warehouse_receipt_reconcile")),
                    service: ReceiptReconciliation = Depends(reconciliation_service)) -> dict:
    try:
        return service.reopen(order_id, body.operation_id, body.reason, user.username)
    except (ValueError, LookupError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/supply-orders/{order_id}/pallets", status_code=201)
def receive_pallet(order_id: str, request: PalletReceipt,
                   user: AdminUser = Depends(require_permission("warehouse_receipt_confirm")),
                   service: Receiving = Depends(receiving_service)) -> dict:
    try:
        return service.receive(order_id, request.model_dump(mode="json"), user.username)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/putaway/{task_id}/complete")
def complete_putaway(task_id: int, request: PutawayConfirmation,
                      user: AdminUser = Depends(require_permission("warehouse_task_execute")),
                      service: Receiving = Depends(receiving_service)) -> dict:
    try:
        return service.complete(task_id, request.model_dump(), user.username)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
