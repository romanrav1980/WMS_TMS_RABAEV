"""Bounded logistics dossier; recorded excess is never presented as available stock."""
from typing import Any
from ..contracts import StoreReceiptError


class StoreCases:
    def __init__(self, gateway: Any) -> None:
        self.gateway=gateway

    def list(self, address: str, after: str, limit: int) -> dict[str,Any]:
        rows=self.gateway.fetch_all("""
            select CASE_ID,LOAD_OPERATION_ID,STORE_ADDR,STATUS,REASON_TEXT,REPORTED_BY,
                   CREATED_AT,ASSIGNED_TO,LAST_DECISION_OPERATION,CASE_VERSION,EXPEDITION_USER,SECURITY_USER,SEARCH_DEADLINE
              from RRL_STORE_DISCREPANCY_CASE
             where STORE_ADDR=:addr and CASE_ID>:after_key
             order by CASE_ID fetch first :row_limit rows only
        """,{"addr":address,"after_key":after or " ","row_limit":limit+1})
        more=len(rows)>limit
        rows=rows[:limit]
        return {"items":rows,"next_after":rows[-1]["case_id"] if more else None}

    def detail(self, case_id: str) -> dict[str,Any]:
        cases=self.gateway.fetch_all("""
            select CASE_ID,LOAD_OPERATION_ID,STORE_ADDR,STATUS,REASON_TEXT,REPORTED_BY,
                   CREATED_AT,ASSIGNED_TO,LAST_DECISION_OPERATION,CASE_VERSION,EXPEDITION_USER,SECURITY_USER,SEARCH_DEADLINE
              from RRL_STORE_DISCREPANCY_CASE where CASE_ID=:case_id
        """,{"case_id":case_id})
        if not cases:
            raise StoreReceiptError("STORE_CASE_NOT_FOUND","Разбирательство не найдено",404)
        lines=self.gateway.fetch_all("""
            select LINE_NO,LOT_UID,ARTICLE,BASE_UOM,
                   to_char(SHIPPED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') SHIPPED_BASE_QTY,
                   to_char(ACCEPTED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ACCEPTED_BASE_QTY,
                   to_char(MISSING_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') MISSING_BASE_QTY,
                   to_char(REFUSED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REFUSED_BASE_QTY,
                   to_char(DAMAGED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DAMAGED_BASE_QTY,
                   to_char(REPORTED_EXTRA_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REPORTED_EXTRA_BASE_QTY
              from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:case_id
             order by LINE_NO fetch first 201 rows only
        """,{"case_id":case_id})
        obligations=self.gateway.fetch_all("""
            select LINE_NO,KIND,to_char(BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') BASE_QTY,BASE_UOM,STATUS
              from RRL_STORE_DELIVERY_OBLIGATION where CASE_ID=:case_id
             order by LINE_NO,KIND fetch first 801 rows only
        """,{"case_id":case_id})
        if len(lines)>200 or len(obligations)>800:
            raise StoreReceiptError("STORE_CASE_BOUND_EXCEEDED","Состав превышает допустимую границу")
        weight=self.gateway.fetch_all("""
            select CAPTURE_KEY,
                   RRL_STOCK_PLAN_HELPER.decimal_text(SHIPPING_GROSS_KG) SHIPPING_GROSS_KG,
                   RRL_STOCK_PLAN_HELPER.decimal_text(OBSERVED_GROSS_KG) OBSERVED_GROSS_KG,
                   RRL_STOCK_PLAN_HELPER.decimal_text(TOLERANCE_KG) TOLERANCE_KG,
                   RRL_STOCK_PLAN_HELPER.decimal_text(DELTA_KG) DELTA_KG,
                   IN_TOLERANCE,ACT_CONFIRMED,PHOTOS_JSON,RECORDED_BY
              from RRL_STORE_RECEIPT_WEIGHT where OPERATION_ID=:case_id
        """,{"case_id":case_id})
        actions=self.gateway.fetch_all("select OPERATION_ID,ACTION_CODE,VERSION_BEFORE,VERSION_AFTER,ACTOR,CREATED_AT from RRL_STORE_CASE_ACTION where CASE_ID=:case_id order by VERSION_AFTER desc fetch first 201 rows only",{"case_id":case_id})
        findings=self.gateway.fetch_all("select OPERATION_ID,ROLE_CODE,REPORT_TEXT,REPORTED_BY,CREATED_AT from RRL_STORE_CASE_FINDING where CASE_ID=:case_id order by CREATED_AT desc,OPERATION_ID desc fetch first 201 rows only",{"case_id":case_id})
        losses=self.gateway.fetch_all("select OPERATION_ID,LINE_NO,LOT_UID,ARTICLE,BASE_UOM,RRL_STOCK_PLAN_HELPER.decimal_text(BASE_QTY) BASE_QTY,REASON_TEXT,CONFIRMED_BY,CREATED_AT from RRL_STORE_LOSS_RECOGNITION where CASE_ID=:case_id order by LINE_NO fetch first 201 rows only",{"case_id":case_id})
        closures=self.gateway.fetch_all("select OPERATION_ID,REASON_TEXT,DECISION_REFERENCE,ACTOR,EXPEDITION_FINDING_OP,SECURITY_FINDING_OP,CREATED_AT from RRL_STORE_CASE_CLOSURE where CASE_ID=:case_id",{"case_id":case_id})
        returns=self.gateway.fetch_all("select a.OPERATION_ID,a.LINE_NO,a.RETURN_BASIS,a.DISPOSITION,RRL_STOCK_PLAN_HELPER.decimal_text(a.BASE_QTY) BASE_QTY,a.BASE_UOM,a.APPROVED_BY,r.OPERATION_ID WAREHOUSE_RECEIPT_OPERATION_ID from RRL_STORE_RETURN_APPROVAL a left join RRL_STORE_RETURN_RECEIPT r on r.APPROVAL_OPERATION_ID=a.OPERATION_ID where a.RECEIPT_OPERATION_ID=:case_id order by a.LINE_NO,a.OPERATION_ID fetch first 201 rows only",{"case_id":case_id})
        if len(returns)>200:raise StoreReceiptError("STORE_CASE_RETURN_HISTORY_BOUND","Нужно уточнить диапазон возвратов разбирательства")
        return {**cases[0],"lines":lines,"obligations":obligations,"weight":weight[0] if weight else None,
                "actions":actions[:200],"findings":findings[:200],"losses":losses[:200],"has_older_history":len(actions)>200 or len(findings)>200,
                "return_approved":bool(returns),"warehouse_stock_restored":any(row["warehouse_receipt_operation_id"] for row in returns),"return_approvals":returns,"closure":closures[0] if closures else None}
