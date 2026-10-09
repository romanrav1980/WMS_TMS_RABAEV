"""Versioned typed boundary for the Oracle stock command."""
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from .domain.stock_quantity import quantity_text


class StockPostingError(RuntimeError):
    def __init__(self, code: str, operation_id: str, oracle_code: int | None = None) -> None:
        self.code = code
        self.operation_id = operation_id
        self.oracle_code = oracle_code
        super().__init__(f"{code}: {operation_id}")


@dataclass(frozen=True)
class StockLine:
    line_number: int
    uid: str
    article: str
    quantity: str | Decimal
    unit: str
    source_cell: str | None = None
    target_cell: str | None = None
    reservation_id: int | None = None
    reservation_action: str = "NONE"
    expected_stock_version: int | None = None
    target_uid: str | None = None

    def wire(self) -> dict[str, Any]:
        if (isinstance(self.line_number, bool) or not isinstance(self.line_number, int) or self.line_number < 1
            or not self.uid or len(self.uid) > 200 or not self.article or len(self.article) > 160
            or not self.unit or len(self.unit) > 20):
            raise ValueError("Stock line requires identity, article, unit and line number")
        if any(value is not None and (not value or len(value) > 60 or "\x00" in value)
               for value in (self.source_cell, self.target_cell)):
            raise ValueError("Invalid cell identity")
        if self.expected_stock_version is not None and (isinstance(self.expected_stock_version, bool)
                or not isinstance(self.expected_stock_version, int) or self.expected_stock_version < 0):
            raise ValueError("Invalid stock version")
        if self.reservation_action not in {"NONE", "RELOCATE", "CONSUME", "RELEASE", "CREATE"}:
            raise ValueError("Unknown reservation action")
        return {"line_number": self.line_number, "uid": self.uid, "article": self.article,
                "quantity": quantity_text(self.quantity), "unit": self.unit,
                "source_cell": self.source_cell, "target_cell": self.target_cell,
                "target_uid": self.target_uid or self.uid, "reservation_id": self.reservation_id,
                "reservation_action": self.reservation_action,
                "expected_stock_version": self.expected_stock_version}


@dataclass(frozen=True)
class StockCommand:
    operation_id: str
    command_type: str
    actor: str
    lines: tuple[StockLine, ...]
    source: dict[str, Any]
    units: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def canonical_json(self) -> str:
        if not self.operation_id or len(self.operation_id) > 100 or not self.actor or len(self.actor) > 50:
            raise ValueError("Operation ID and authenticated actor required")
        if not self.command_type or len(self.command_type) > 80:
            raise ValueError("Command type required")
        if not (0 if self.command_type in {"CASE_CARRIER_RETURN", "CASE_CARRIER_MOVE", "OUTGOING_PALLET_CHECK", "CASE_SHORT_APPROVE", "CASE_PICK_CONFIRM", "RECEIPT_REVERSE", "INVENTORY_REGISTER_LOT", "PICK_PLAN_CANCEL", "WAVE_CANCEL", "WAVE_RELEASE", "WAVE_LAUNCH", "INVENTORY_COUNT", "MES_RAW_TASK_CANCEL", "MES_RELEASE_TO_PRODUCTION", "MES_CALCULATE_SUPPLY", "TASK_COMPLETE", "SAP_RECEIPT", "MES_MOVEMENTS", "INTERNAL_MOVE", "MOVE_QUARANTINE", "WAVE_RESERVE_SOURCES", "DOCUMENT_RELEASE_RESERVATIONS", "SHIP_DOCUMENT", "SHIP_PALLET"} or self.command_type.startswith("RESERVATION_") else 1) <= len(self.lines) <= 200 or len(self.units) > 10000:
            raise ValueError("Stock command exceeds the line/unit contract")
        numbers = [line.line_number for line in self.lines]
        if len(set(numbers)) != len(numbers) or len(set(self.units)) != len(self.units):
            raise ValueError("Duplicate stock line or physical unit")
        payload = {"contract_version": 2, "operation_id": self.operation_id,
                   "command_type": self.command_type, "actor": self.actor,
                   "source": self.source, "lines": [line.wire() for line in sorted(self.lines, key=lambda x: x.line_number)],
                   "units": sorted(self.units), "metadata": self.metadata}
        result = json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
        if len(result.encode("utf-8")) > 4 * 1024 * 1024:
            raise ValueError("Stock command exceeds 4 MiB")
        return result
