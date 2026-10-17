"""SMA SCP-0499 section 5.1, normal-resolution KG/GROSS profile only.

This parses device evidence; native RRL_SCALE_PACKET_READ decides packet stability.
No zero/tare/calibration command is emitted by this adapter.
"""
from dataclasses import dataclass
from decimal import Decimal
import re


@dataclass(frozen=True)
class SmaObservation:
    gross_weight_kg: Decimal
    stable: bool
    center_zero: bool
    range_id: str


def parse_sma_gross_kg(frame: bytes) -> SmaObservation:
    """Consume exactly one complete 20-byte frame, never search through garbage."""
    if len(frame) != 20 or frame[:1] != b"\n" or frame[-1:] != b"\r":
        raise ValueError("SMA_FRAME_INVALID")
    try:
        text = frame.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("SMA_ASCII_REQUIRED") from exc
    status, range_id, basis, motion, future = text[1:6]
    if status not in {" ", "Z"}:
        raise ValueError("SMA_SCALE_FAULT:" + status)
    if range_id not in "123456789" or future != " ":
        raise ValueError("SMA_PROFILE_UNSUPPORTED")
    if basis != "G" or text[16:19] != "kg ":
        raise ValueError("SMA_GROSS_KG_REQUIRED")
    if motion not in {" ", "M"}:
        raise ValueError("SMA_MOTION_INVALID")
    weight = text[6:16].lstrip(" ")
    if not re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", weight):
        raise ValueError("SMA_WEIGHT_INVALID")
    value = Decimal(weight)
    if value < 0 or (status == "Z" and value != 0):
        raise ValueError("SMA_WEIGHT_STATUS_CONFLICT")
    return SmaObservation(value, motion == " ", status == "Z", range_id)
