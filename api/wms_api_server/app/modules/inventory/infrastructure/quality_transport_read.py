"""Existing ST assignment for navigation from the current QC snapshot."""
from typing import Any


def quality_transport_read(cur: Any, identifier: str, actor: str) -> dict[str, Any]:
    cur.execute("""select s.ID,s.TRANSTASK_ID from RRL_SBORKA_PALLETS s
        where s.PALLET_UID=:identifier
        and RRL_HAS_WRIGHT(:actor,'transport_dispatch_view')=1
        order by s.ID fetch first 2 rows only""", identifier=identifier, actor=actor)
    rows = cur.fetchall()
    if len(rows) != 1:
        return {"state": "UNAVAILABLE"}
    row = rows[0]
    return {"state": "ASSIGNED" if row[1] is not None else "UNASSIGNED",
            "shipment_id": int(row[0]), "transport_task_id": int(row[1]) if row[1] is not None else None}
