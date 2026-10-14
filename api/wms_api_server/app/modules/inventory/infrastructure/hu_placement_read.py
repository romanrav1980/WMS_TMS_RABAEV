"""Read the recorded physical placement inside the authorised HU snapshot."""
from typing import Any
from fastapi import HTTPException


def recorded_placement(cur: Any, composition: dict) -> dict | None:
    if composition.get("historical_composition") or not composition.get("nodes"):
        return None
    cur.execute("""
        select cl.TASK_ID,cl.CELL_SLOT_ID,sl.SLOT_CODE,cl.HU_COMPOSITION_VERSION,
               to_char(cl.HU_GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
               to_char(cl.HU_BOUNDING_VOLUME_M3,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),sl.ACTIVE,wt.STATUS,
               case when exists(select 1 from RRL_WAREHOUSE_TASK_SYNC sy
                    where sy.TASK_ID=cl.TASK_ID and sy.SYNC_STATUS='SYNCED') then 1 else 0 end
          from RRL_RECEIPT_SLOT_CLAIM cl
          join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=cl.CELL_SLOT_ID
          join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=cl.TASK_ID
         where cl.UID_PALLET=:p_uid and cl.CELL=:p_cell and cl.STATUS='OCCUPIED'
           and wt.TO_WARE_ID=:p_ware
         order by cl.TASK_ID fetch first 2 rows only
    """, p_uid=composition["root"], p_cell=composition["cell"], p_ware=composition["warehouse"])
    rows = cur.fetchall()
    if len(rows) > 1:
        raise HTTPException(409, "HU_CURRENT_PLACEMENT_AMBIGUOUS")
    if not rows:
        return None
    task, slot, code, version, mass, volume, active, status, synced = rows[0]
    current_version = composition["nodes"][0].get("version")
    return {
        "task_id": int(task), "slot_id": int(slot), "slot_code": code,
        "content_version": int(version) if version is not None else None,
        "version_matches": version is not None and version == current_version,
        "gross_weight_kg": mass,
        "bounding_volume_m3": volume,
        "slot_active": active == 1, "task_status": status, "synced": synced == 1,
        "measurement_source": "RECORDED_PLACEMENT",
    }
