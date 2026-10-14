from collections.abc import Callable
from typing import Any
from ..contracts import StoreReceiptError


class StoreReturns:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def approve(self,operation_id: str,receipt_id: str,line_no: int,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_APPROVE",operation_id,{"receipt_operation_id":receipt_id,"line_no":line_no},metadata,actor)

    def original(self,receipt_id: str) -> dict[str,Any]:
        headers=self.gateway.fetch_all("select OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,RECEIPT_STATE,RECEIVED_AT from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:receipt",{"receipt":receipt_id})
        if len(headers)!=1:
            raise StoreReceiptError("STORE_RETURN_ORIGINAL_NOT_FOUND","Исходная приёмка не найдена",404)
        lines=self.gateway.fetch_all("""
            select l.LINE_NO,l.LOT_UID,l.ARTICLE,l.BASE_UOM,
                   to_char(l.ACCEPTED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ACCEPTED_QUANTITY,
                   to_char(nvl(a.APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') APPROVED_QUANTITY,
                   to_char(l.ACCEPTED_BASE_QTY-nvl(a.APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AVAILABLE_FOR_APPROVAL
              from RRL_STORE_RECEIPT_LINE l left join(
                   select LINE_NO,sum(BASE_QTY) APPROVED from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID=:receipt group by LINE_NO
              )a on a.LINE_NO=l.LINE_NO where l.OPERATION_ID=:receipt order by l.LINE_NO fetch first 201 rows only
        """,{"receipt":receipt_id})
        approvals=self.gateway.fetch_all("""
            select a.OPERATION_ID,a.LINE_NO,a.DISPOSITION,a.REASON_TEXT,a.DECISION_REFERENCE,a.COMPLETE_GOOD_BOX,a.APPROVED_BY,a.APPROVED_AT,
                   to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,a.BASE_UOM,s.RETURN_DOCUMENT,s.WARE_ID,s.RECEIVE_CELL,s.IMPORTED_AT SAP_IMPORTED_AT
              from RRL_STORE_RETURN_APPROVAL a left join RRL_STORE_RETURN_SAP s on s.APPROVAL_OPERATION_ID=a.OPERATION_ID where a.RECEIPT_OPERATION_ID=:receipt
             order by a.APPROVED_AT desc,a.OPERATION_ID desc fetch first 101 rows only
        """,{"receipt":receipt_id})
        if len(lines)>200:
            raise StoreReceiptError("STORE_RETURN_LINE_BOUND_200","Исходная приёмка превышает диапазон200")
        return {"source":headers[0],"lines":lines,"approvals":approvals[:100],"has_older_approvals":len(approvals)>100,"physical_warehouse_receipt_confirmed":False}
