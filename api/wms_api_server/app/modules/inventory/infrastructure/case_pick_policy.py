from typing import Any
"""Read the existing SKU marking card through the CASE line scope."""
def case_pick_policy(gateway: Any, task_id: int, line_id: int) -> dict:
    rows = gateway.fetch_all("""
        select l.ARTICUL,
          case when exists(select 1 from RRL_ARTICULS a where a.ACTICUL=l.ARTICUL and a.TYPE_W in(2,3,5,6,7))
            and exists(select 1 from RRL_STOCK_UOM_CONVERSION c where c.ARTICUL=l.ARTICUL and c.INPUT_UOM='KG'and c.BASE_UOM='KG'and c.NUMERATOR=1 and c.DENOMINATOR=1)then 1 else 0 end WEIGHTED_KG,
          nvl((select SERIALIZED_WEIGHT_BOXES from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=l.ARTICUL),0) SERIALIZED_WEIGHT_BOXES,
          greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=l.ARTICUL),0),
            nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU g where g.ARTICUL=l.ARTICUL),0),
            case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=l.ARTICUL) then 1 else 0 end) MARKING_REQUIRED
          from RRL_CASE_PICK_LINE l where l.CASE_PICK_TASK_ID=:task and l.CASE_PICK_LINE_ID=:line
    """, {"task": task_id, "line": line_id})
    if not rows:
        raise LookupError("Case line not found")
    profiles = gateway.fetch_all("""
        select SYSTEM_CODE,PROFILE_CODE from RRL_SKU_RECEIPT_PROFILE
         where ARTICUL=:article order by SYSTEM_CODE,PROFILE_CODE fetch first 51 rows only
    """, {"article": rows[0]["articul"]})
    if len(profiles) > 50:
        raise ValueError("Marking profile bound exceeded")
    return {"article": rows[0]["articul"], "marking_required": bool(rows[0]["marking_required"]), "profiles": profiles, "serialized_weight_boxes": bool(rows[0]["serialized_weight_boxes"]),
            "loose_weight_kg": bool(rows[0]["weighted_kg"]) and not bool(rows[0]["marking_required"]) and not bool(rows[0]["serialized_weight_boxes"])}
