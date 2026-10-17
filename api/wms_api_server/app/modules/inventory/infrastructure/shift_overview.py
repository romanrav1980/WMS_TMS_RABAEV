"""Existing source readers share one READ ONLY lease; no duplicate readiness rules."""
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Iterator
import oracledb
from ....transaction_gateway import TransactionGateway
from ..contracts_shift_overview import ShiftOverviewError

SectionReader = Callable[[Any, int, str], Any]


class BoundOverviewRead(TransactionGateway):
    @contextmanager
    def transaction(self, label: str) -> Iterator[Any]:
        # This adapter is used only for the four fixed read sources below in a READ ONLY transaction.
        yield self.cursor


class ShiftOverview:
    def __init__(self, gateway: Any, readers: dict[str, SectionReader]) -> None:
        if set(readers) != {"readiness", "pick", "time", "replenishment"}:
            raise ValueError("Explicit source readers required")
        self.gateway, self.readers = gateway, readers

    def read(self, actor: str, warehouse: int, waves: list[int]) -> dict[str, Any]:
        if not 1 <= len(waves) <= 50 or len(set(waves)) != len(waves) or any(wave < 1 for wave in waves):
            raise ShiftOverviewError("SHIFT_OVERVIEW_BATCH_BOUND_50", 422)
        try:
            with self.gateway.transaction("Bounded shift overview single READ ONLY snapshot") as cur:
                cur.execute("set transaction read only")
                cur.execute("select RRL_ACCESS_API.allowed(:actor,'pick_wave_view','WAREHOUSE',:ware) from dual",
                            actor=actor, ware=str(warehouse))
                if cur.fetchone()[0] != 1:
                    raise ShiftOverviewError("SHIFT_OVERVIEW_WAREHOUSE_DENIED")
                placeholders = ",".join(":wave" + str(index) for index in range(len(waves)))
                cur.execute("select PICK_WAVE_ID,WARE_ID from RRL_PICK_WAVE where PICK_WAVE_ID in(" + placeholders + ")",
                            {"wave" + str(index): wave for index, wave in enumerate(waves)})
                identities = dict(cur.fetchall())
                if set(identities) != set(waves) or any(ware != warehouse for ware in identities.values()):
                    raise ShiftOverviewError("SHIFT_OVERVIEW_WAVE_NOT_IN_SCOPE", 404)
                bound = BoundOverviewRead(cur)
                result = [{"wave_id": wave, **{name: self._part(reader, bound, wave, actor)
                           for name, reader in self.readers.items()}} for wave in waves]
        except oracledb.DatabaseError as error:
            raise ShiftOverviewError("SHIFT_OVERVIEW_UNAVAILABLE", 503) from error
        return {"warehouse_id": warehouse, "wave_ids": waves, "waves": result, "limit": 50,
                "observed_at": datetime.now(timezone.utc).isoformat(), "snapshot": "ORACLE_READ_ONLY",
                "all_sources_available": all(part["status"] == "READY" for row in result for name, part in row.items() if name != "wave_id"),
                "commands_executed": False, "stock_changed": False}

    @staticmethod
    def _part(reader: SectionReader, gateway: Any, wave: int, actor: str) -> dict[str, Any]:
        try:
            data = reader(gateway, wave, actor)
            return {"status": "READY", "data": data, "error": ""}
        except Exception as error:
            status = getattr(error, "status_code", getattr(error, "status", 503))
            return {"status": "FORBIDDEN" if status == 403 else "ERROR", "data": None,
                    "error": "SOURCE_ACCESS_DENIED" if status == 403 else "SOURCE_UNAVAILABLE"}
