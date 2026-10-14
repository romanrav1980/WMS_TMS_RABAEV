"""Scoped paginated history; all source and current route facts share one snapshot."""
from typing import Any
from ..contracts_store_returns import StoreReturnReceiveError

class InterwarehouseDecisions:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def read(self,plan_id: str,actor: str,after_revision: int=0) -> dict[str,Any]:
        with self.gateway.transaction("Interwarehouse immutable decisions history") as cur:
            cur.execute("set transaction read only")
            cur.execute("""select p.TARGET_TT_ID,RRL_INTERWARE_ROUTING.target_trip(p.OPERATION_ID)
                from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=:actor
                where p.OPERATION_ID=:plan and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
                and(u.WARE_ID in(p.SOURCE_WARE_ID,p.TARGET_WARE_ID)or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",actor=actor,plan=plan_id)
            scope=cur.fetchone()
            if scope is None:
                raise StoreReturnReceiveError("INTERWARE_DECISIONS_SCOPE_REQUIRED","Текущий диспетчер склада источника или приёмки обязателен",403)
            cur.execute("""select d.OPERATION_ID,d.REVISION_NO,d.DECISION_KIND,d.PREVIOUS_TT_ID,d.TARGET_TT_ID,d.OUTBOUND_DOCK,
                to_char(EXPECTED_ARRIVAL,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') EXPECTED_ARRIVAL,
                to_char(READY_DUE,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') READY_DUE,
                d.REASON_TEXT,d.DECISION_REFERENCE,d.ACTOR,d.INCIDENT_KIND,d.INCIDENT_DETAIL,d.EVIDENCE_REFERENCE,case when d.INCIDENT_KIND is not null and r.CREATED_AT>d.CREATED_AT then r.OPERATION_ID end FOLLOWUP_RECEIPT_OPERATION_ID,
                closed.OPERATION_ID INCIDENT_CLOSE_OPERATION_ID,closed.REASON_TEXT INCIDENT_CLOSE_REASON,closed.EVIDENCE_REFERENCE INCIDENT_CLOSE_EVIDENCE,
                to_char(closed.CLOSED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')INCIDENT_CLOSED_AT,
                to_char(d.CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') CREATED_AT
                from RRL_INTERWARE_DECISION d left join RRL_INTERWARE_RECEIPT r on r.PLAN_OPERATION_ID=d.PLAN_OPERATION_ID left join RRL_INTERWARE_INCIDENT_CLOSE closed on closed.INCIDENT_OPERATION_ID=d.OPERATION_ID where d.PLAN_OPERATION_ID=:plan and d.REVISION_NO>:after_revision
                order by REVISION_NO fetch first 51 rows only""",plan=plan_id,after_revision=after_revision)
            columns=[column[0].lower() for column in cur.description]
            rows=[dict(zip(columns,values)) for values in cur.fetchall()]
            has_more=len(rows)>50
            rows=rows[:50]
            return {"plan_operation_id":plan_id,"original_target_trip_id":int(scope[0]),"target_trip_id":int(scope[1]),
                    "decisions":rows,"has_more":has_more,"next_after_revision":rows[-1]["revision_no"] if has_more else None}
