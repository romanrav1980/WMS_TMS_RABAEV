"""Bounded recovery cases on the original shortage reader transaction."""
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError


def recovery_records(cur: Any,loss_id: str) -> list[dict[str,Any]]:
    cur.execute("""select req.OPERATION_ID REQUEST_OPERATION_ID,req.ACTOR REPORTER,
        RRL_STOCK_PLAN_HELPER.decimal_text(req.BASE_QTY)REQUEST_QUANTITY,req.SOURCE_JSON,cancelled.OPERATION_ID CANCEL_OPERATION_ID,cancelled.REASON_TEXT CANCEL_REASON,
        approval.OPERATION_ID APPROVAL_OPERATION_ID,approval.ACTOR APPROVER,
        received.OPERATION_ID RECEIPT_OPERATION_ID,received.ROOT_UID PALLET_IDENTIFIER,
        RRL_STOCK_PLAN_HELPER.decimal_text(received.BASE_QTY)RECOVERED_QUANTITY,
        pp.TASK_ID,task.STATUS TASK_STATUS,pp.TARGET_CELL,placed.OPERATION_ID PLACEMENT_OPERATION_ID,
        binding.OPERATION_ID BINDING_OPERATION_ID,binding.ST_ID,binding.ST_IDENTIFIER,st.ST_NUMBER,binding.TARGET_TT_ID,
        dispatch.OPERATION_ID DISPATCH_OPERATION_ID,final_receipt.OPERATION_ID FINAL_RECEIPT_OPERATION_ID,final_receipt.RECEIPT_STATE FINAL_RECEIPT_STATE
        from RRL_INTERWARE_RECOVERY_REQUEST req
        left join RRL_IW_RECOVERY_CANCEL cancelled on cancelled.REQUEST_OPERATION_ID=req.OPERATION_ID
        left join RRL_INTERWARE_RECOVERY_APPROVAL approval on approval.REQUEST_OPERATION_ID=req.OPERATION_ID
        left join RRL_INTERWARE_RECOVERY_RECEIPT received on received.APPROVAL_OPERATION_ID=approval.OPERATION_ID
        left join RRL_IW_RECOVERY_PUT_PLAN pp on pp.RECOVERY_OPERATION_ID=received.OPERATION_ID
        left join RRL_WAREHOUSE_TASK task on task.TASK_ID=pp.TASK_ID
        left join RRL_IW_RECOVERY_PLACEMENT placed on placed.TASK_ID=pp.TASK_ID
        left join RRL_IW_RECOVERY_ST_BIND binding on binding.RECOVERY_OPERATION_ID=received.OPERATION_ID
        left join RRL_SBORKA_PALLETS st on st.ID=binding.ST_ID
        left join RRL_IW_RECOVERY_DISPATCH dispatch on dispatch.BIND_OPERATION_ID=binding.OPERATION_ID
        left join RRL_STORE_RECEIPT_FACT final_receipt on final_receipt.LOAD_OPERATION_ID=dispatch.OPERATION_ID
        where req.LOSS_OPERATION_ID=:loss_id and(task.TASK_ID is null or task.STATUS!='CANCELLED')
        order by case when cancelled.OPERATION_ID is not null then 2 when received.OPERATION_ID is null then 0 else 1 end,req.CREATED_AT desc,req.OPERATION_ID
        fetch first 1001 rows only""",loss_id=loss_id)
    names=[column[0].lower()for column in cur.description]
    records=[dict(zip(names,row))for row in cur.fetchall()]
    if len(records)>1000:raise StoreReturnReceiveError("RECOVERY_HISTORY_BOUND_1000","Количество восстановлений превышает допустимый размер",409)
    seen=set()
    for record in records:
        if record["request_operation_id"]in seen:raise StoreReturnReceiveError("RECOVERY_CURRENT_TASK_AMBIGUOUS","Несколько действующих заданий одной найденной части",409)
        seen.add(record["request_operation_id"])
        source=read_oracle_json(record.pop("source_json"))
        record["unit_keys"]=[u["key"]for u in source["source_units"]]
    return records
