"""Supported entry points for transport rules; legacy callers use this facade."""
from .domain.transport_type import normalize_transport_type
from .infrastructure.st_assignment import assign_sts

__all__ = ["normalize_transport_type", "assign_sts"]
