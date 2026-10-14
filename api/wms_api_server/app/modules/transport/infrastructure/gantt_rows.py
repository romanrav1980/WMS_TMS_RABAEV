"""Daily Gantt rows include operations crossing midnight, using legacy wall-clock dates."""
from datetime import date, datetime, time, timedelta
from typing import Any

MAX_GANTT_ROWS = 20000


def gantt_rows(gateway: Any, gantt_date: date) -> list[dict[str, Any]]:
    start = datetime.combine(gantt_date, time.min)
    return gateway.fetch_all(
        """SELECT /* NICORA_GANTT_DAY_OVERLAP */
                   TT.ID AS TT_ID, TT.TRANSPORT AS VEHICLE_NUM, TT.TRANSTYPE AS VEHICLE_TYPE,
                   V.ID AS VEHICLE_ID,
                   OPS.ID, OPS.OPERATION_CODE, OPS.ORD, OPS.DURATION_MIN,
                   TO_CHAR(OPS.PLAN_START, 'YYYY-MM-DD HH24:MI') AS PLAN_START,
                   TO_CHAR(OPS.PLAN_END, 'YYYY-MM-DD HH24:MI') AS PLAN_END,
                   TO_CHAR(OPS.FACT_START, 'YYYY-MM-DD HH24:MI') AS FACT_START,
                   TO_CHAR(OPS.FACT_END, 'YYYY-MM-DD HH24:MI') AS FACT_END,
                   OPS.NOTE
              FROM RRL_TRANSPORT_TASK TT
              LEFT JOIN RRL_TR_VEHICLE V ON V.NUM = TT.TRANSPORT
              JOIN RRL_TT_OPERATIONS OPS ON OPS.TT_ID = TT.ID
             WHERE NVL(TT.DELETED, 0) = 0 AND (
                   (TT.SHIPMENT_DATE >= :day_start AND TT.SHIPMENT_DATE < :day_end)
                OR (OPS.PLAN_START < :day_end
                    AND (OPS.PLAN_END > :day_start OR OPS.PLAN_START >= :day_start))
                OR (OPS.FACT_START < :day_end
                    AND (OPS.FACT_END IS NULL OR OPS.FACT_END > :day_start
                         OR OPS.FACT_START >= :day_start)))
             ORDER BY NVL(TT.TRANSPORT, ' '), TT.ID, OPS.ORD, OPS.ID
             FETCH FIRST 20001 ROWS ONLY""",
        {"day_start": start, "day_end": start + timedelta(days=1)},
    )
