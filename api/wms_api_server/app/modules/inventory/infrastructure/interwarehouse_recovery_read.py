"""Recovery selection without losing aggregate history on the existing RO snapshot."""
from typing import Any
from ..contracts_store_returns import StoreReturnReceiveError
from .interwarehouse_recovery_records import recovery_records


def read_recovery(cur: Any,claim: tuple|None,selected_request: str|None=None) -> tuple:
    records=recovery_records(cur,claim[4])if claim and claim[4]else []
    if selected_request:
        selected=next((r for r in records if r["request_operation_id"]==selected_request),None)
        if selected is None:raise StoreReturnReceiveError("RECOVERY_REQUEST_SCOPE_REQUIRED","Восстановление не относится к выбранной приёмке",404)
    else:selected=next((r for r in records if not r['cancel_operation_id']),records[0]if records else None)
    if selected is None:return None,None,None,None,records
    recovery=(selected["request_operation_id"],selected["reporter"],selected["approval_operation_id"],selected["approver"],
              selected["receipt_operation_id"],selected["pallet_identifier"],selected["recovered_quantity"])
    plan=(selected["task_id"],selected["task_status"],selected["target_cell"],selected["placement_operation_id"])if selected["task_id"]else None
    placement=plan if plan and plan[3]else None
    onward=(selected["binding_operation_id"],selected["st_id"],selected["st_identifier"],selected["st_number"],selected["target_tt_id"],
            selected["dispatch_operation_id"],selected["final_receipt_operation_id"],selected["final_receipt_state"])if selected["binding_operation_id"]else None
    return recovery,plan,placement,onward,records
