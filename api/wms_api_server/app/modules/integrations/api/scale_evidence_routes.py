"""OPC provenance is separate from capture acceptance and stock effects."""
from typing import Any, Literal
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_scale_evidence import (EvidenceKind, ScaleEvidencePayload, ScaleEvidenceError,
                                       ScaleEvidencePort, scale_evidence_service)

router = APIRouter(prefix="/api/integrations/scale-evidence", tags=["scale-evidence"])


@router.post("")
def archive(body: ScaleEvidencePayload, user: AdminUser = Depends(get_current_user),
            protocol: Literal["1.0", "1.1", "1.2"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
            service: ScaleEvidencePort = Depends(scale_evidence_service)) -> dict[str, Any]:
    if protocol != body.protocol_version:
        raise HTTPException(422, {"code": "OPC_EVIDENCE_HEADER_BODY_VERSION_MISMATCH"})
    try:
        return service.archive(body, user.username)
    except ScaleEvidenceError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "device_id": body.device_id,
                            "capture_id": body.capture_id, "evidence_sha256": body.digest(),
                            "outcome_confirmed": False, "read_before_retry": True}) from exc


@router.get("")
def read(capture_kind: EvidenceKind, device_id: str = Query(min_length=1, max_length=100),
         capture_id: str = Query(min_length=1, max_length=100),
         user: AdminUser = Depends(get_current_user),
         protocol: Literal["1.0", "1.1", "1.2"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
         service: ScaleEvidencePort = Depends(scale_evidence_service)) -> dict[str, Any]:
    expected = "1.2" if capture_kind == "WAREHOUSE_ASSEMBLY_RECON" else "1.1" if capture_kind == "WAREHOUSE_ASSEMBLY" else "1.0"
    if protocol != expected:
        raise HTTPException(422, {"code": "OPC_EVIDENCE_HEADER_KIND_VERSION_MISMATCH"})
    try:
        return service.read(capture_kind, device_id, capture_id, user.username)
    except ScaleEvidenceError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc
