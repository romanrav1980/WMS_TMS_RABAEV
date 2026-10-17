"""Warehouse DTO selects its own archive path; store DTOs are never retargeted."""
from .scale_http import HttpScaleGateway
from ..application.warehouse_scale_ack import warehouse_packet


class HttpWarehouseScaleGateway(HttpScaleGateway):
    def post_capture(self, body: bytes) -> bytes:
        source = warehouse_packet(body)
        path = "/api/inventory/warehouse-scales/" + ("final-captures" if "purpose" in source else "captures")
        return self._request(path, body)
