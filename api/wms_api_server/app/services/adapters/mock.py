"""Legacy import compatibility; simulation explicitly carries no government ACK."""
from ...modules.integrations.public import MockRegulatoryAdapter,RegulatoryResponse
MockAdapterResponse=RegulatoryResponse
__all__=["MockRegulatoryAdapter","MockAdapterResponse"]
