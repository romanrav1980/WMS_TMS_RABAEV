"""Separate evidence HTTP transport; old v1.0 and assembly v1.1 are explicit."""
import json
from ..contracts_scales import ScaleGatewayError
from .scale_http import HttpScaleGateway


class HttpScaleEvidenceGateway(HttpScaleGateway):
    def post_evidence(self, body: bytes) -> bytes:
        try:
            version = json.loads(body)["protocol_version"]
        except (ValueError, TypeError, KeyError):
            raise ScaleGatewayError("OPC_EVIDENCE_VERSION_REQUIRED") from None
        return self._request("/api/integrations/scale-evidence", body, protocol_version=version)
