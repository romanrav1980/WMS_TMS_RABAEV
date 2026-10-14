"""Describe original aware task-clock coverage without backfilling legacy DATEs."""
from typing import Any

def task_time_coverage(cursor: Any, ware: int) -> dict[str, Any]:
    cursor.execute("""select
        nvl(sum(case when STARTED_AT is not null and STARTED_AT_INSTANT is null then 1 else 0 end),0),
        nvl(sum(case when FINISHED_AT is not null and FINISHED_AT_INSTANT is null then 1 else 0 end),0)
        from RRL_WAREHOUSE_TASK where FROM_WARE_ID=:ware or TO_WARE_ID=:ware""",ware=ware)
    starts,finishes=cursor.fetchone()
    return {"legacy_unclassified_start_count":int(starts),
            "legacy_unclassified_finish_count":int(finishes),
            "daily_counts_use_aware_instants":True,
            "legacy_wall_dates_reinterpreted":False,
            "finish_time_basis":"NATIVE_DONE_TRANSACTION_INSTANT",
            "scope":"SOURCE_OR_DESTINATION_WAREHOUSE_TASKS"}
