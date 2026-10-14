from .return_progress import return_progress
from collections.abc import Callable
from typing import Any
from ..contracts import StoreReceiptError
from ...platform.public import read_oracle_json


class StoreReturns:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def approve(self,operation_id: str,receipt_id: str,line_no: int,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_APPROVE",operation_id,{"receipt_operation_id":receipt_id,"line_no":line_no},metadata,actor)

    def original(self,receipt_id: str,actor: str|None=None) -> dict[str,Any]:
        with self.gateway.transaction("Consistent current supply-chain return dossier") as q:
            q.execute("set transaction read only")
            if actor is not None:
                q.execute("select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_return_approve')=1",actor=actor)
                if q.fetchone()[0]!=1:
                    raise StoreReceiptError("STORE_RETURN_CURRENT_READER_REQUIRED","Нет действующего права согласования возврата",403)
            def rows(sql: str,binds: dict) -> list[dict[str,Any]]:
                q.execute(sql,binds)
                names=[item[0].lower() for item in q.description]
                return [dict(zip(names,row)) for row in q.fetchall()]
            headers=rows("select OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,RECEIPT_STATE,RECEIVED_AT from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:receipt",{"receipt":receipt_id})
            if len(headers)!=1:
                raise StoreReceiptError("STORE_RETURN_ORIGINAL_NOT_FOUND","Исходная приёмка не найдена",404)
            lines=rows("""
                select l.LINE_NO,l.LOT_UID,l.ARTICLE,l.BASE_UOM,
                       to_char(l.ACCEPTED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ACCEPTED_QUANTITY,
                       to_char(nvl(a.APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') APPROVED_QUANTITY,
                       to_char(l.ACCEPTED_BASE_QTY-nvl(a.APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AVAILABLE_FOR_APPROVAL,
                       to_char(l.REFUSED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REFUSED_QUANTITY,
                       to_char(l.DAMAGED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DAMAGED_QUANTITY,
                       to_char(l.REFUSED_BASE_QTY-nvl(a.REFUSED_APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REFUSED_AVAILABLE,
                       to_char(l.DAMAGED_BASE_QTY-nvl(a.DAMAGED_APPROVED,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DAMAGED_AVAILABLE
                  from RRL_STORE_RECEIPT_LINE l left join(
                       select LINE_NO,sum(case when RETURN_BASIS='ACCEPTED'then BASE_QTY else 0 end) APPROVED,
                       sum(case when RETURN_BASIS='REFUSED'then BASE_QTY else 0 end) REFUSED_APPROVED,
                       sum(case when RETURN_BASIS='DAMAGED'then BASE_QTY else 0 end) DAMAGED_APPROVED from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID=:receipt group by LINE_NO
                  )a on a.LINE_NO=l.LINE_NO where l.OPERATION_ID=:receipt order by l.LINE_NO fetch first 201 rows only
            """,{"receipt":receipt_id})
            approvals=rows("""
                select a.OPERATION_ID,a.LINE_NO,a.RETURN_BASIS,a.DISPOSITION,a.REASON_TEXT,a.DECISION_REFERENCE,a.COMPLETE_GOOD_BOX,a.APPROVED_BY,a.APPROVED_AT,
                       to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,a.BASE_UOM,s.RETURN_DOCUMENT,s.WARE_ID,s.RECEIVE_CELL,s.IMPORTED_AT SAP_IMPORTED_AT
                  from RRL_STORE_RETURN_APPROVAL a left join RRL_STORE_RETURN_SAP s on s.APPROVAL_OPERATION_ID=a.OPERATION_ID where a.RECEIPT_OPERATION_ID=:receipt
                 order by a.APPROVED_AT desc,a.OPERATION_ID desc fetch first 101 rows only
            """,{"receipt":receipt_id})
            progress=return_progress(q,[a["operation_id"]for a in approvals[:100]],actor)
            for approval in approvals[:100]:
                approval["progress"]=progress.get(approval["operation_id"],{"warehouse_progress_visible":False})
            if len(lines)>200:
                raise StoreReceiptError("STORE_RETURN_LINE_BOUND_200","Исходная приёмка превышает диапазон200")
            q.execute("select count(*)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:receipt",receipt=receipt_id)
            modern=q.fetchone()[0]>0
            units=[]
            if modern:
                units=rows("""select u.PHYSICAL_UNIT_KEY KEY,u.UNIT_ID,u.UID_PALLET ORIGIN_UID,
                    to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                    u.BASE_UOM,u.UNIT_VERSION VERSION,l.LINE_NO,l.LOT_UID,fact.UNIT_DISPOSITION RETURN_BASIS
                    from RRL_STORE_RECEIPT_UNIT fact
                    join RRL_STORE_RECEIPT_FACT header on header.OPERATION_ID=fact.OPERATION_ID
                    join RRL_STOCK_OPERATION root on root.OPERATION_ID=header.OPERATION_ID and root.STATE='APPLIED'and root.COMMAND_TYPE='STORE_RECEIPT'
                    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=fact.PHYSICAL_UNIT_KEY
                    and u.BASE_QTY=fact.BASE_QTY and u.BASE_UOM=fact.BASE_UOM and u.UNIT_VERSION=fact.SOURCE_UNIT_VERSION
                    join RRL_STORE_RECEIPT_LINE l on l.OPERATION_ID=fact.OPERATION_ID and l.LOT_UID=u.CURRENT_UID and l.BASE_UOM=u.BASE_UOM
                    where fact.OPERATION_ID=:receipt and fact.UNIT_DISPOSITION in('ACCEPTED','REFUSED','DAMAGED')
                    and u.CURRENT_CELL=json_value(header.COMPOSITION_JSON,'$.cell')
                    and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null
                    and not exists(select 1 from RRL_STORE_RETURN_UNIT assigned where assigned.RECEIPT_OPERATION_ID=fact.OPERATION_ID and assigned.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY)
                    order by l.LINE_NO,fact.UNIT_DISPOSITION,u.PHYSICAL_UNIT_KEY fetch first 10001 rows only""",{"receipt":receipt_id})
                if len(units)>10000 or len({u["key"]for u in units})!=len(units):
                    raise StoreReceiptError("STORE_RETURN_UNIT_BOUND_OR_AMBIGUOUS_LINE","Разбейте состав или уточните исходную строку")
            else:
                for line in lines:
                    q.execute("select RRL_STORE_RETURN_UNIT_CORE.accepted_units(:receipt,:lot_id,:uom) from dual",receipt=receipt_id,lot_id=line["lot_uid"],uom=line["base_uom"])
                    available=read_oracle_json(q.fetchone()[0])
                    if len(available)>10000 or len(units)+len(available)>10000:
                        raise StoreReceiptError("STORE_RETURN_UNIT_BOUND","Разбейте возврат на отдельные приёмки")
                    units.extend(dict(unit,line_no=line["line_no"],lot_uid=line["lot_uid"],return_basis="ACCEPTED") for unit in available)
            return {"units":units,"source":headers[0],"lines":lines,"approvals":approvals[:100],"has_older_approvals":len(approvals)>100,"physical_warehouse_receipt_confirmed":False}
    

    def reuse_preview(self,receipt_id: str,line_no: int,quantity: str,actor: str) -> dict[str,Any]:
        import oracledb
        try:
            with self.gateway.transaction("Current return reuse source READ ONLY")as q:
                q.execute("set transaction read only");out=q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_RETURN_REUSE_API.preview",[receipt_id,line_no,quantity,actor,out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            raise StoreReceiptError("RETURN_REUSE_PREVIEW_REFUSED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409 if 20800<=code<=20999 else 503)from exc
