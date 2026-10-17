"""Versioned gateway-reported OPC provenance; never an inventory command."""
import hashlib
import json
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

DIGEST = r"^[A-F0-9]{64}$"
UTC = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00$"
EvidenceKind = Literal["STORE_RECEIPT", "WAREHOUSE_PICK", "WAREHOUSE_FINAL", "WAREHOUSE_ASSEMBLY", "WAREHOUSE_ASSEMBLY_RECON"]


class EvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class OpcValue(EvidenceModel):
    variant_type: str = Field(min_length=1, max_length=40)
    value: Any
    status_code: int = Field(ge=0, le=4294967295)
    source_timestamp: str | None = Field(pattern=UTC)
    server_timestamp: str | None = Field(pattern=UTC)


class OpcValues(EvidenceModel):
    current_weight: OpcValue
    stable: OpcValue
    center_zero: OpcValue
    overload: OpcValue
    underload: OpcValue
    tare_mode: OpcValue
    engineering_units: OpcValue


class OpcObservation(EvidenceModel):
    observed_at: str = Field(pattern=UTC)
    values: OpcValues


class OpcSample(OpcObservation):
    offset_ms: int = Field(ge=0, le=10000)


class OpcNode(EvidenceModel):
    namespace_uri: str = Field(min_length=1, max_length=512)
    identifier_type: Literal["Numeric", "String", "Guid", "ByteString"]
    identifier: str = Field(min_length=1, max_length=1024)


class OpcServer(EvidenceModel):
    application_uri: str = Field(min_length=1, max_length=512)
    certificate_sha256: str = Field(pattern=DIGEST)


class ScaleEvidenceBase(EvidenceModel):
    protocol_version: str
    device_id: str = Field(min_length=1, max_length=100)
    capture_id: str = Field(min_length=1, max_length=100)
    capture_kind: str
    capture_sha256: str = Field(pattern=DIGEST)
    profile_sha256: str = Field(pattern=DIGEST)
    station_id: str = Field(min_length=1, max_length=100)
    model_namespace_uri: Literal["http://opcfoundation.org/UA/Scales/V2/"]
    opc_server: OpcServer
    nodes: dict[str, OpcNode] = Field(min_length=7, max_length=7)
    observations: list[OpcSample] = Field(min_length=5, max_length=25)

    @model_validator(mode="after")
    def exact_nodes_and_bound(self) -> "ScaleEvidenceBase":
        if set(self.nodes) != set(OpcValues.model_fields):
            raise ValueError("Exactly the seven observed OPC fields need node provenance")
        canonical = self.canonical_bytes()
        if len(canonical) > 131072:
            raise ValueError("Evidence exceeds 128 KiB")
        return self

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.model_dump(), ensure_ascii=True, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest().upper()


class ScaleEvidence(ScaleEvidenceBase):
    protocol_version: Literal["1.0"]
    capture_kind: Literal["STORE_RECEIPT", "WAREHOUSE_PICK", "WAREHOUSE_FINAL"]
    zero_observation: OpcObservation


class AssemblyZeroReference(EvidenceModel):
    session_id: str = Field(min_length=1, max_length=100)
    step_id: str = Field(min_length=1, max_length=100)
    phase: Literal["BEFORE", "AFTER"]
    tare_capture_key: str = Field(pattern=DIGEST)


class AssemblyScaleEvidence(ScaleEvidenceBase):
    protocol_version: Literal["1.1"]
    capture_kind: Literal["WAREHOUSE_ASSEMBLY"]
    zero_reference: AssemblyZeroReference


class AssemblyReconciliationReference(EvidenceModel):
    session_id: str = Field(min_length=1, max_length=100)
    step_id: str = Field(min_length=1, max_length=100)
    phase: Literal["RECONCILE"]
    tare_capture_key: str = Field(pattern=DIGEST)
    reconciliation_id: str = Field(min_length=1, max_length=100)


class AssemblyReconciliationEvidence(ScaleEvidenceBase):
    protocol_version: Literal["1.2"]
    capture_kind: Literal["WAREHOUSE_ASSEMBLY_RECON"]
    zero_reference: AssemblyReconciliationReference


ScaleEvidencePayload = ScaleEvidence | AssemblyScaleEvidence | AssemblyReconciliationEvidence


class ScaleEvidenceError(RuntimeError):
    def __init__(self, code: str, status: int = 409) -> None:
        super().__init__(code)
        self.code, self.status = code, status


class ScaleEvidencePort(Protocol):
    def archive(self, body: ScaleEvidencePayload, actor: str) -> dict[str, Any]: ...
    def read(self, kind: str, device: str, capture: str, actor: str) -> dict[str, Any]: ...


def scale_evidence_service() -> ScaleEvidencePort:
    raise RuntimeError("Scale provenance archive is not wired")
