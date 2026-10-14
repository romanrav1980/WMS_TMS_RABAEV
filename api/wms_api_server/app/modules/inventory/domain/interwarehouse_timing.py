"""Derived phase timing; physical placement does not imply QC or dispatch approval."""
from datetime import datetime
from decimal import Decimal
from typing import Any


def phase_timing(due: str, actual: str | None, observed: str, reached: str) -> dict[str, str]:
    deadline = datetime.fromisoformat(due)
    fact = datetime.fromisoformat(actual) if actual else datetime.fromisoformat(observed)
    if deadline.utcoffset() is None or fact.utcoffset() is None:
        raise ValueError("Interwarehouse phase timing requires explicit UTC offsets")
    elapsed = fact - deadline
    seconds = max(Decimal(0), Decimal(elapsed.days * 86400 + elapsed.seconds) +
                  Decimal(elapsed.microseconds) / Decimal(1000000))
    state = reached + ("_LATE" if seconds else "_ON_TIME") if actual else ("OVERDUE" if seconds else "EXPECTED")
    return {"state": state, "delay_seconds": format(seconds, "f")}


def annotate_timing(row: dict[str, Any]) -> dict[str, Any]:
    row["arrival_timing"] = phase_timing(row["arrival_due"], row["unloaded_at"], row["observed_at"], "UNLOADED")
    row["gate_timing"] = phase_timing(row["ready_due"], row["placed_at"], row["observed_at"], "AT_GATE")
    return row
