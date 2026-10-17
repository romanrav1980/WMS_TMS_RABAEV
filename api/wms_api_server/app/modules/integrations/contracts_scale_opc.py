"""Ports for real OPC observations, separate from delivery and hardware effects."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol


@dataclass(frozen=True)
class OpcWeightObservation:
    gross: Decimal
    net: Decimal
    tare: Decimal
    stable: bool
    center_zero: bool
    observed_at: datetime
    evidence: dict[str, Any]


class OpcWeightReader(Protocol):
    async def read(self) -> OpcWeightObservation: ...


class ScaleDeviceLease(Protocol):
    def acquire(self, device: str, now: float, seconds: int) -> str: ...
    def renew(self, device: str, token: str, now: float, seconds: int) -> None: ...
    def release(self, device: str, token: str) -> None: ...


class ScaleBundleJournal(Protocol):
    def stage(self, body: bytes, raw: bytes) -> None: ...
    def get(self, kind: str, device: str, capture: str) -> tuple[bytes, bytes] | None: ...
