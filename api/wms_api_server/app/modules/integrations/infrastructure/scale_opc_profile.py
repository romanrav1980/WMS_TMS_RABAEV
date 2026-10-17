"""Explicit commissioning passport; no invented vendor NodeIds or discovery."""
from dataclasses import dataclass
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SCALES_V2 = "http://opcfoundation.org/UA/Scales/V2/"
FIELDS = ("current_weight", "stable", "center_zero", "overload", "underload", "tare_mode", "engineering_units")


@dataclass(frozen=True)
class OpcScaleProfile:
    data: dict[str, Any]
    root: Path
    digest: str

    @classmethod
    def load(cls, path: Path) -> "OpcScaleProfile":
        raw = path.read_bytes()
        data = json.loads(raw)
        if data.get("model_namespace_uri") != SCALES_V2 or data.get("model_version") != "2.00":
            raise ValueError("OPC40200_V2_PROFILE_REQUIRED")
        endpoint = urlsplit(data["endpoint"])
        if endpoint.scheme != "opc.tcp" or not endpoint.hostname or not endpoint.port or endpoint.username or endpoint.password:
            raise ValueError("OPC_ENDPOINT_INVALID")
        if set(data["nodes"]) != set(FIELDS):
            raise ValueError("OPC_REQUIRED_NODE_MAPPING_MISSING")
        for field in FIELDS:
            node = data["nodes"][field]
            if not isinstance(node.get("namespace_uri"), str) or not 1 <= len(node["namespace_uri"]) <= 512 or node.get("identifier_type") not in {"s", "i"}:
                raise ValueError("OPC_NODE_MAPPING_INVALID")
            if node["identifier_type"] == "i" and (type(node["identifier"]) is not int or not 0 <= node["identifier"] <= 4294967295):
                raise ValueError("OPC_NODE_MAPPING_INVALID")
            if node["identifier_type"] == "s" and (not isinstance(node["identifier"], str) or not 1 <= len(node["identifier"]) <= 1024):
                raise ValueError("OPC_NODE_MAPPING_INVALID")
        for field in ("device_id", "station_id", "application_uri", "server_application_uri", "unit_namespace_uri"):
            if not isinstance(data.get(field), str) or not 1 <= len(data[field]) <= (100 if field in {"device_id", "station_id"} else 512):
                raise ValueError("OPC_PROFILE_IDENTITY_REQUIRED")
        if type(data.get("kg_unit_id")) is not int or type(data.get("no_tare_mode")) is not int:
            raise ValueError("OPC_UNIT_TARE_MAPPING_REQUIRED")
        security = data.get("security", {})
        if not re.fullmatch(r"[a-fA-F0-9]{64}", security.get("server_sha256", "")):
            raise ValueError("OPC_SERVER_CERTIFICATE_PIN_REQUIRED")
        return cls(data, path.resolve().parent, hashlib.sha256(raw).hexdigest())

    def certificate_path(self, key: str) -> Path:
        path = self.root / self.data["security"][key]
        if not path.is_file():
            raise ValueError("OPC_CERTIFICATE_FILE_REQUIRED")
        return path
