"""Dispatcher read filters; object authority is native RRL_ACCESS_API."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TripListFilter:
    shipment_date: date | None = None
    condition: str | None = None
    include_deleted: bool = False
    task_id: int | None = None
    transport_mask: str | None = None
    company_mask: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    no_payments_only: bool = False


class DispatchReadError(RuntimeError):
    def __init__(self, code: str, status: int = 403) -> None:
        super().__init__(code)
        self.code, self.status = code, status
