"""Regulatory delivery is separate from a verified government acknowledgment."""
from typing import Any,Protocol

from .domain.regulatory_delivery import RegulatoryResponse

class RegulatoryAdapter(Protocol):
    mode: str
    configured: bool
    simulated: bool
    signature_status: str
    cert_alias: str|None
    cert_thumbprint: str|None
    def send(self,event: dict[str,Any]) -> RegulatoryResponse: ...
