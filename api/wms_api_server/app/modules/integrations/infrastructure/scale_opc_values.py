"""Strict real DataValue interpretation, without a second sample-spread algorithm."""
from datetime import datetime, timezone
from decimal import Decimal
import math
from typing import Any
from ..contracts_scale_opc import OpcWeightObservation
from ..contracts_scales import ScaleGatewayError


def checked_values(values: dict[str, Any], profile: dict[str, Any]) -> OpcWeightObservation:
    now = datetime.now(timezone.utc)
    evidence: dict[str, Any] = {}
    decoded: dict[str, Any] = {}
    for field, dv in values.items():
        if dv.StatusCode.value != 0 or dv.Value is None or dv.Value.Value is None:
            raise ScaleGatewayError("OPC_VALUE_QUALITY_REJECTED")
        source, server = dv.SourceTimestamp, dv.ServerTimestamp
        if source is None or server is None or source.tzinfo is None or server.tzinfo is None:
            raise ScaleGatewayError("OPC_TIMESTAMP_REQUIRED")
        # Source may be older for a constant value; never rewrite it as observation time.
        if not -1 <= (now-server).total_seconds() <= 3 or source > server:
            raise ScaleGatewayError("OPC_SERVER_TIME_STALE_OR_INCONSISTENT")
        value = dv.Value.Value
        decoded[field] = value
        evidence[field] = dict(value=None, status_code=dv.StatusCode.value, source_timestamp=source.isoformat(timespec="microseconds"),
                               server_timestamp=server.isoformat(timespec="microseconds"), variant_type=dv.Value.VariantType.name)
    for field in ("stable", "center_zero", "overload", "underload"):
        if type(decoded[field]) is not bool:
            raise ScaleGatewayError("OPC_BOOLEAN_MAPPING_INVALID")
    if decoded["overload"] or decoded["underload"]:
        raise ScaleGatewayError("OPC_SCALE_RANGE_REJECTED")
    if type(decoded["tare_mode"]) is bool or not isinstance(decoded["tare_mode"], int) or decoded["tare_mode"] != profile["no_tare_mode"]:
        raise ScaleGatewayError("OPC_PRESET_OR_TARE_MODE_REJECTED")
    unit = decoded["engineering_units"]
    if unit.UnitId != profile["kg_unit_id"] or unit.NamespaceUri != profile["unit_namespace_uri"]:
        raise ScaleGatewayError("OPC_KG_UNIT_REQUIRED")
    weight = decoded["current_weight"]
    mass = []
    for field in ("Gross", "Net", "Tare"):
        value = getattr(weight, field, None)
        if type(value) not in {float, int} or not math.isfinite(value) or value < 0:
            raise ScaleGatewayError("OPC_WEIGHT_VALUE_REJECTED")
        mass.append(Decimal(str(value)))
    if mass[2] != 0:
        raise ScaleGatewayError("OPC_NONZERO_DEVICE_TARE_REJECTED")
    for field in ("stable", "center_zero", "overload", "underload", "tare_mode"):
        evidence[field]["value"] = decoded[field]
    evidence["current_weight"]["value"] = {field: repr(getattr(weight, field)) for field in ("Gross", "Net", "Tare")}
    evidence["engineering_units"]["value"] = dict(namespace_uri=unit.NamespaceUri, unit_id=unit.UnitId)
    return OpcWeightObservation(*mass, decoded["stable"], decoded["center_zero"], now,
                               dict(observed_at=now.isoformat(timespec="microseconds"), values=evidence))
