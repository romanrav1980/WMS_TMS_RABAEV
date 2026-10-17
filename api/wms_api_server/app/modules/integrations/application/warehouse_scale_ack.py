"""Strict warehouse native archive ACK; no receipt/stock decision is made here."""
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from typing import Any
from ...inventory.public import WarehouseScalePacket, WarehouseFinalScalePacket
from ..contracts_scales import ScaleGatewayError
from ..contracts_warehouse_gateway import WarehouseGatewayProfile


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("WAREHOUSE_JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def warehouse_packet(body: bytes) -> dict[str, Any]:
    try:
        if not isinstance(body, bytes) or len(body) > 32000:
            raise ValueError()
        source = json.loads(body.decode("utf-8"), object_pairs_hook=unique_object)
        model = WarehouseFinalScalePacket if "purpose" in source else WarehouseScalePacket
        return model.model_validate(source).model_dump(exclude_none=True)
    except (ValueError, TypeError, UnicodeError):
        raise ScaleGatewayError("WAREHOUSE_CAPTURE_PACKET_INVALID") from None


def validate_warehouse_ack(body: bytes, response: bytes, profile: WarehouseGatewayProfile) -> None:
    source = warehouse_packet(body)
    try:
        result = json.loads(response.decode("utf-8"), object_pairs_hook=unique_object)
        for field in ("device_id", "post_cell", "basis"):
            if source[field] != getattr(profile, field):
                raise ValueError()
        for field in ("device_id", "post_cell", "device_policy_version", "calibration_ref", "basis"):
            if type(result[field]) is not type(source[field]) or result[field] != source[field]:
                raise ValueError()
        for field in ("capture_id", "case_task_id", "scan_container", "measured_at"):
            if type(result[field]) is not type(source[field]) or result[field] != source[field]:
                raise ValueError()
        if type(result["warehouse_id"]) is not int or result["warehouse_id"] != profile.warehouse_id:
            raise ValueError()
        if result["device_mode"] != profile.device_mode or result["stock_posted"] is not False or result["status"] != "ARCHIVED":
            raise ValueError()
        if type(result["case_content_version"]) is not int or result["case_content_version"] != source["expected_content_version"]:
            raise ValueError()
        canonical = json.dumps(source, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
        identity = json.dumps([source["device_id"], source["capture_id"]], ensure_ascii=False, separators=(",", ":")).encode()
        if result["capture_key"] != hashlib.sha256(identity).hexdigest().upper():
            raise ValueError()
        if result["source_sha256"] != hashlib.sha256(canonical).hexdigest().upper():
            raise ValueError()
        if not isinstance(result["weight_kg"], str) or Decimal(result["weight_kg"]) != Decimal(source["samples"][-1]["weight_kg"]):
            raise ValueError()
        if source.get("purpose"):
            if result["purpose"] != source["purpose"]:
                raise ValueError()
            for field in ("pallet_type_id", "type_version"):
                if type(result[field]) is not int or result[field] < 1:
                    raise ValueError()
            if source["purpose"] == "FINAL_GROSS":
                if result["tare_capture_key"] != source["tare_capture_key"]:
                    raise ValueError()
                if not re.fullmatch(r"[A-F0-9]{64}", result["composition_signature"]):
                    raise ValueError()
                tare, net = Decimal(result["tare_weight_kg"]), Decimal(result["net_weight_kg"])
                if tare < 0 or net <= 0 or tare + net != Decimal(result["weight_kg"]):
                    raise ValueError()
        else:
            for field in ("case_line_id", "scan_source_cell", "scan_product"):
                if type(result[field]) is not type(source[field]) or result[field] != source[field]:
                    raise ValueError()
        if type(result["sample_count"]) is not int or result["sample_count"] != len(source["samples"]):
            raise ValueError()
        if type(result["span_ms"]) is not int or result["span_ms"] != source["samples"][-1]["offset_ms"] - source["samples"][0]["offset_ms"]:
            raise ValueError()
    except (ValueError, TypeError, KeyError, IndexError, InvalidOperation, UnicodeError):
        raise ScaleGatewayError("WAREHOUSE_CAPTURE_ACK_INVALID", True) from None
