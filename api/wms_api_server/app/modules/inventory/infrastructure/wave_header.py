from typing import Any


def read_wave_header(gateway: Any, pick_wave_id: int) -> dict[str, Any] | None:
    rows = gateway.fetch_all(
        """
        select w.PICK_WAVE_ID,
               w.WAVE_CODE,
               w.WAVE_NAME,
               w.WARE_ID,
               wa.NAME WARE_NAME,
               w.ROUTE_ID,
               r.ROUTE_CODE,
               w.DOCK_ID,
               w.STATUS,
               w.WAVE_KIND,
               w.PLANNED_START_AT,
               w.PLANNED_FINISH_AT,
               w.MAX_CUSTOMERS,
               w.CUSTOMER_COUNT,
               (select count(*) from RRL_PICK_WAVE_ORDER wo where wo.PICK_WAVE_ID=w.PICK_WAVE_ID) ORDER_COUNT,
               w.PLAN_COUNT,
               (select count(*) from RRL_PICK_WAVE_TASK wt where wt.PICK_WAVE_ID=w.PICK_WAVE_ID) TASK_COUNT,
               w.HARD_RESERVE_QTY,
               w.COMMENT_TEXT,
               w.CREATED_AT,
               w.CREATED_BY,
               w.LAUNCHED_AT,
               w.LAUNCHED_BY,
               w.CANCELLED_AT,
               w.CANCELLED_BY,
               w.UPDATED_AT,
               w.UPDATED_BY
          from RRL_PICK_WAVE w
          left join RRL_WARES wa
            on wa.ID = w.WARE_ID
          left join RRL_PICK_ROUTE r
            on r.PICK_ROUTE_ID = w.ROUTE_ID
         where w.PICK_WAVE_ID = :pick_wave_id
        """,
        {"pick_wave_id": pick_wave_id},
    )
    if not rows:
        return None
    return rows[0]
