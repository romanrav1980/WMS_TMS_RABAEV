"""Resolve current physical CASE continuation without reopening its picking task."""
from typing import Any


def resolve_hu_rows(gateway: Any, code: str, normalized: str, case_id: int | None) -> list[dict[str, Any]]:
    return gateway.fetch_all(
        """select p.UID_PALLET,cast(null as number) CASE_TASK_ID,p.HU_SHIPPED_OPERATION from RRL_PALLETS p
          where p.UID_PALLET in(:p_code,:p_normal) or p.SSCC=:p_normal
           or exists(select 1 from RRL_IW_CASE_CARRIER m where m.CARRIER_UID=p.UID_PALLET and m.CASE_TASK_ID=:p_case_id)
          union all select cast(null as varchar2(200)),c.CASE_PICK_TASK_ID,cast(null as varchar2(100))
          from RRL_CASE_PICK_TASK c where (c.SSCC in(:p_code,:p_normal) or c.CASE_PICK_TASK_ID=:p_case_id)
           and not exists(select 1 from RRL_IW_CASE_CARRIER m where m.CASE_TASK_ID=c.CASE_PICK_TASK_ID)
          fetch first 3 rows only""",
        {"p_code": code, "p_normal": normalized, "p_case_id": case_id})
