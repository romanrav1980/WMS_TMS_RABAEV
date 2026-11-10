"""Internal physical-stock fixture payloads; no SAP, SCM, or device adapter."""
from __future__ import annotations

from typing import Iterable


def build_manifest(*, tag: str, warehouse_id: int, article: str, gtin: str,
                   policy_version: int, profiles: Iterable[dict[str, str]], quantity: int = 250) -> dict:
    """Build a WmsTraceManifest.v1 payload for one internally created pallet.

    The caller persists the manifest through the trace-manifest API, then uses its
    operation identifier as the capture provenance for the native inventory birth.
    """
    if not tag.isalnum() or not 1 <= len(tag) <= 4:
        raise ValueError("tag must contain one to four alphanumeric characters")
    if quantity < 1 or quantity > 10000:
        raise ValueError("quantity must be within trace-manifest bounds")
    if len(gtin) != 14 or not gtin.isdigit():
        raise ValueError("GTIN-14 required")
    profile_rows = [dict(row) for row in profiles]
    if not profile_rows:
        raise ValueError("at least one marking profile is required")
    for row in profile_rows:
        if set(row) != {"system_code", "profile_code", "version"}:
            raise ValueError("exact profile fields required")
    units = []
    for index in range(1, quantity + 1):
        serial = f"{tag}{index:03d}".ljust(7, "X")
        codes = []
        for profile in profile_rows:
            if profile["system_code"] == "CRPT" and profile["profile_code"].upper() in {"TOBACCO", "CRPT_TOBACCO", "TOBACCO_PACK"}:
                code = gtin + serial
            elif profile["system_code"] == "EGAIS":
                code = (f"QA{tag}{index:05d}").ljust(68, "X")
            else:
                code = f"QA-{tag}-{profile['system_code']}-{index:05d}"
            codes.append({"system_code": profile["system_code"], "profile_code": profile["profile_code"], "code": code})
        units.append({"unit_id": str(index), "quantity": "1", "codes": codes})
    first = profile_rows[0]
    return {
        "contract_version": "WmsTraceManifest.v1",
        "source_kind": "INVENTORY",
        "source_document_id": warehouse_id,
        "warehouse_id": warehouse_id,
        "pallet_identifier": f"INT.{tag}.PAL",
        "article": article,
        "base_uom": "EA",
        "policy_version": policy_version,
        "profile_versions": profile_rows,
        "units": units,
        "aggregations": [{
            "aggregation_id": f"INT.{tag}.ROOT",
            "system_code": first["system_code"],
            "profile_code": first["profile_code"],
            "level": "PALLET",
            "code": f"INT.{tag}.ROOT",
            "unit_ids": [str(index) for index in range(1, quantity + 1)],
            "children": [],
        }],
        "document_reference": f"Internal WMS fixture {tag}",
    }
