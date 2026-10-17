"""Actual assembly API endpoints, not a retargeted store packet producer."""
import json
from typing import Any
from urllib.parse import urlencode
from ..contracts_scales import ScaleGatewayError
from .scale_evidence_http import HttpScaleEvidenceGateway


class HttpAssemblyScaleGateway(HttpScaleEvidenceGateway):
    def requests(self, device_id: str) -> list[dict[str, Any]]:
        raw = self._request("/api/inventory/assembly-scale/gateway/requests?"+urlencode({"device_id":device_id}))
        try:
            items = json.loads(raw)["items"]
            if not isinstance(items,list) or len(items)>1 or any(not isinstance(item,dict) for item in items):
                raise ValueError()
            return items
        except (ValueError,TypeError,KeyError):
            raise ScaleGatewayError("ASSEMBLY_REQUEST_LIST_INVALID") from None

    def post_capture(self, body: bytes) -> bytes:
        return self._request("/api/inventory/assembly-scale/captures",body)
