from decimal import Decimal
from typing import Literal, Protocol
from fastapi import APIRouter, Depends, Path, Query, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from ...platform.public import AdminUser, require_permission
from .task_scan_routes import UnitScan
from ..domain.quality_label import quality_label_html


class QualityPort(Protocol):
    def status(self, identifier: str, actor: str|None=None) -> dict: ...
    def check(self, identifier: str, body: dict, actor: str) -> dict: ...
    def check_final(self, identifier: str, body: dict, actor: str) -> dict: ...
    def final_readings(self, identifier: str, actor: str) -> dict: ...


router = APIRouter(prefix="/api/outgoing-quality", tags=["outgoing-quality"])


def outgoing_quality_service() -> QualityPort:
    raise RuntimeError("Outgoing quality service not wired")


class QualityRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_composition_signature: str = Field(pattern=r"^[A-F0-9]{64}$")
    note: str | None = Field(default=None, max_length=1000)


class ItemScan(BaseModel):
    scan_id: str = Field(min_length=1,max_length=100)
    barcode: str = Field(min_length=1,max_length=128)
    quantity: Literal["1"] = "1"


class ScanRequest(QualityRequest):
    error_count: int = Field(ge=0, strict=True)
    scans: list[UnitScan] = Field(default_factory=list,max_length=20000)
    item_scans: list[ItemScan] = Field(default_factory=list,max_length=20000)


class WeightRequest(QualityRequest):
    quality_kind: Literal["WEIGHT", "WEIGHT2"]
    gross_weight: Decimal = Field(gt=0, max_digits=18, decimal_places=9)
    wood_weight: Decimal = Field(ge=0, max_digits=18, decimal_places=9)
    measurement_origin: Literal["MANUAL_CONFIRMED"] | None = None

    @model_validator(mode="before")
    @classmethod
    def exclusive_source(cls, value: object) -> object:
        if (isinstance(value, dict) and value.get("measurement_origin") == "MANUAL_CONFIRMED"
                and any(key in value for key in ("final_scale_capture", "capture_key"))):
            raise ValueError("Manual weight and electronic capture are mutually exclusive")
        return value


@router.get("/{identifier}")
def status(identifier: str = Path(min_length=1, max_length=150),
           user: AdminUser = Depends(require_permission("outgoing_pallet_check")),
           service: QualityPort = Depends(outgoing_quality_service)) -> dict:
    return service.status(identifier,user.username)


@router.get("/{identifier}/control-label")
def control_label(identifier: str = Path(min_length=1,max_length=150),
                  expected_signature: str|None = Query(default=None,pattern=r"^[A-F0-9]{64}$"),
                  user: AdminUser = Depends(require_permission("outgoing_pallet_check")),
                  service: QualityPort = Depends(outgoing_quality_service)) -> Response:
    snapshot=service.status(identifier,user.username)
    if expected_signature is not None and snapshot.get("composition_signature")!=expected_signature:
        raise HTTPException(409,"Состав изменился. Перечитайте результат контроля перед печатью.")
    if (snapshot.get("weight_exemption",{}).get("eligible") is True
            and snapshot.get("weight_exemption_recorded") is not True):
        raise HTTPException(409,"Предъявите грузовое место к контролю, чтобы сохранить основание освобождения от веса.")
    return Response(quality_label_html(snapshot,user.username),media_type="text/html",
                    headers={"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})


@router.post("/{identifier}/scan")
def scan(body: ScanRequest, identifier: str = Path(min_length=1, max_length=150),
         user: AdminUser = Depends(require_permission("outgoing_pallet_check")),
         service: QualityPort = Depends(outgoing_quality_service)) -> dict:
    return service.check(identifier, {"quality_kind": "SCAN", **body.model_dump(mode="json")}, user.username)


@router.post("/{identifier}/weight")
def weight(body: WeightRequest, identifier: str = Path(min_length=1, max_length=150),
           user: AdminUser = Depends(require_permission("outgoing_pallet_check")),
           service: QualityPort = Depends(outgoing_quality_service)) -> dict:
    payload = body.model_dump(mode="json")
    if body.measurement_origin is None:
        payload.pop("measurement_origin")
    return service.check(identifier, payload, user.username)


@router.post("/{identifier}/plan")
def assign_plan(body: QualityRequest, identifier: str = Path(min_length=1,max_length=150),
                user: AdminUser = Depends(require_permission("outgoing_pallet_check")),
                service: QualityPort = Depends(outgoing_quality_service)) -> dict:
    return service.check(identifier,{"quality_kind":"PLAN",**body.model_dump(mode="json")},user.username)


class FinalWeightRequest(QualityRequest):
    model_config=ConfigDict(extra="forbid")
    capture_key: str = Field(pattern=r"^[A-F0-9]{64}$")

@router.post("/{identifier}/final-weight")
def final_weight(body:FinalWeightRequest,identifier:str=Path(min_length=1,max_length=150),
                 user:AdminUser=Depends(require_permission("outgoing_pallet_check")),
                 service:QualityPort=Depends(outgoing_quality_service))->dict:
    return service.check_final(identifier,body.model_dump(mode="json",exclude_none=True),user.username)


@router.get("/{identifier}/final-captures")
def final_readings(identifier:str=Path(min_length=1,max_length=150),
                   user:AdminUser=Depends(require_permission("outgoing_pallet_check")),
                   service:QualityPort=Depends(outgoing_quality_service))->dict:
    return service.final_readings(identifier,user.username)
