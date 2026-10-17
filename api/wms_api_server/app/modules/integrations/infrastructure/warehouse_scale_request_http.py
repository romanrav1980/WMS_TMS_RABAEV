"""Actual warehouse request/claim routes; read-only equipment evidence transport."""
import json
from typing import Any
from urllib.parse import quote, urlencode
from .warehouse_scale_http import HttpWarehouseScaleGateway
from .scale_evidence_http import HttpScaleEvidenceGateway
from .scale_outbox import _unique_object
from ..contracts_scales import ScaleGatewayError


class HttpWarehouseScaleRequests(HttpWarehouseScaleGateway, HttpScaleEvidenceGateway):
    def requests(self, device_id: str) -> list[dict[str, Any]]:
        raw = self._request('/api/inventory/warehouse-scales/gateway/requests?'+urlencode(dict(device_id=device_id)))
        try:
            result = json.loads(raw, object_pairs_hook=_unique_object)
            items = result['items']
            if result['device_id'] != device_id or not isinstance(items, list) or len(items) > 20:
                raise ValueError()
            for item in items:
                if not isinstance(item, dict) or item.get('device_id') != device_id or item.get('state') not in {'REQUESTED', 'CLAIMED'}:
                    raise ValueError()
                if not isinstance(item.get('request_id'), str) or not 1 <= len(item['request_id']) <= 100:
                    raise ValueError()
            return items
        except (ValueError, TypeError, KeyError):
            raise ScaleGatewayError('WAREHOUSE_REQUEST_LIST_INVALID') from None

    def claim_request(self, request_id: str, body: bytes) -> bytes:
        return self._request('/api/inventory/warehouse-scales/gateway/requests/'+quote(request_id, safe='')+'/claim', body)

    def confirm_zero(self, request_id: str, body: bytes) -> bytes:
        return self._request('/api/inventory/warehouse-scales/gateway/requests/'+quote(request_id, safe='')+'/zero-confirmed', body)
