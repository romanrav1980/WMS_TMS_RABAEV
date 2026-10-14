"""Use the original HU task; grouped receipt supplies its immutable origin."""
from typing import Any
from ..contracts_stock import StockCommand
from ..contracts_store_returns import StoreReturnReceiveError
from .stock_posting_uow import StockPosting


class InterwarehouseGroupPlacement:
    def __init__(self,gateway: Any,posting: StockPosting)->None:
        self.gateway=gateway
        self.posting=posting

    def plan(self,operation: str,receipt: str,metadata: dict[str,Any],actor: str)->dict[str,Any]:
        with self.gateway.transaction("Immutable grouped placement origin")as q:
            q.execute("set transaction read only")
            q.execute("""select r.ROOT_UID,r.RECEIVE_CELL,p.OUTBOUND_DOCK,r.WARE_ID from RRL_IW_GROUP_RECEIPT r
                join RRL_IW_GROUP_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID where r.OPERATION_ID=:receipt_id""",receipt_id=receipt)
            row=q.fetchone()
            if row is None:
                raise StoreReturnReceiveError("INTERWARE_GROUP_RECEIPT_NOT_FOUND","Actual grouped receipt required",404)
            q.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
                and RRL_HAS_WRIGHT(ID,'warehouse_task_execute')=1
                and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')""",actor=actor,ware=row[3])
            if q.fetchone()[0]!=1:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PUT_FORBIDDEN","Current warehouse operator required",403)
        body=dict(metadata,target_cell=row[2],group_receipt_operation_id=receipt)
        if body["scan_container"]!=row[0]or body["scanned_from_cell"]!=row[1]or body["scanned_to_cell"]!=row[2]:
            raise StoreReturnReceiveError("INTERWARE_GROUP_PUT_SCANS_REQUIRED","Scan original whole place and its planned cells")
        return self.posting.post(StockCommand(operation_id=operation,command_type="HU_PLAN_MOVE",actor=actor,
                                              source=dict(uid=row[0]),lines=(),metadata=body))
