"""Current return receiving queue/policy; detail proof is loaded for one selected source."""
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError

def require_scope(cur: Any,ware: int,actor: str,permission: str) -> None:
    cur.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,:permission)=1
        and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')""",actor=actor,permission=permission,ware=ware)
    if cur.fetchone()[0]!=1:raise StoreReturnReceiveError("STORE_RETURN_CURRENT_WARE_ACTOR_REQUIRED","Нет полномочий на приёмку возврата этого склада",403)

def policy(gateway: Any,ware: int,actor: str) -> dict:
    with gateway.transaction("Current return policy READ ONLY")as cur:
        cur.execute("set transaction read only");require_scope(cur,ware,actor,"warehouse_settings_edit")
        cur.execute("select WARE_ID,SUPPLIER_RECEIVE_CELL,DISPOSAL_RECEIVE_CELL,SUPPLIER_TARGET_CELL,DISPOSAL_TARGET_CELL,REUSE_RECEIVE_CELL,POLICY_VERSION from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=:ware",ware=ware)
        columns=[d[0].lower()for d in cur.description];row=cur.fetchone()
        return dict(zip(columns,row))if row else {"ware_id":ware,"policy_version":0}

def page(gateway: Any,ware: int,actor: str,after: str="",limit: int=20,pickup: str | None=None,proof: bool=False) -> dict:
    if not 1<=limit<=100 or len(after)>100:raise ValueError("RETURN_RECEIVING_PAGE_BOUND")
    with gateway.transaction("Current return queue and selected source READ ONLY")as cur:
        cur.execute("set transaction read only");require_scope(cur,ware,actor,"warehouse_return_receive")
        expression="RRL_STORE_RETURN_UNIT_CORE.approved_proof(a.OPERATION_ID)"if proof else "to_clob(null)"
        cur.execute(f"""with bounded as(
            select p.OPERATION_ID from RRL_STORE_RETURN_PICKUP p join RRL_STORE_RETURN_HANDOVER h on h.OPERATION_ID=p.HANDOVER_OPERATION_ID
            join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID
            join RRL_STORE_RETURN_SAP s on s.OPERATION_ID=t.SAP_OPERATION_ID
            where s.WARE_ID=:ware and p.OPERATION_ID>:after_key and(:pickup_id is null or p.OPERATION_ID=:pickup_id)
            and not exists(select 1 from RRL_STORE_RETURN_RECEIPT r where r.PICKUP_OPERATION_ID=p.OPERATION_ID)
            order by p.OPERATION_ID fetch first :row_limit rows only)
            select /* RETURN_RECEIVING_BOUNDED283 */ p.OPERATION_ID PICKUP_OPERATION_ID,p.VEHICLE_NUMBER,h.PALLET_IDENTIFIER,
            {expression} MARKED_UNIT_CONTROL,
            a.ARTICLE,a.LOT_UID,a.BASE_UOM,a.DISPOSITION,a.RETURN_BASIS,t.STORE_ADDR,
            RRL_STOCK_PLAN_HELPER.decimal_text(a.BASE_QTY)QUANTITY,RRL_STOCK_PLAN_HELPER.decimal_text(h.GROSS_WEIGHT_KG)GROSS_WEIGHT_KG,
            to_char(original.EXPIRY_DATE,'YYYY-MM-DD')EXPIRY_DATE,s.RETURN_DOCUMENT,
            case a.DISPOSITION when 'SUPPLIER'then policy.SUPPLIER_RECEIVE_CELL when 'DISPOSAL'then policy.DISPOSAL_RECEIVE_CELL when 'REUSE'then policy.REUSE_RECEIVE_CELL end RECEIVE_CELL,
            (select min(r.SUPPLIER_BATCH)from RRL_SAP_PALLET_RECEIPT r where r.UID_PALLET=nvl(original.STOCK_ORIGIN_UID,original.UID_PALLET))ORIGINAL_SUPPLIER_BATCH
            from bounded b join RRL_STORE_RETURN_PICKUP p on p.OPERATION_ID=b.OPERATION_ID
            join RRL_STORE_RETURN_HANDOVER h on h.OPERATION_ID=p.HANDOVER_OPERATION_ID
            join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID
            join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID
            join RRL_STORE_RETURN_SAP s on s.OPERATION_ID=t.SAP_OPERATION_ID
            join RRL_PALLETS original on original.UID_PALLET=a.LOT_UID
            left join RRL_STORE_RETURN_WARE_POLICY policy on policy.WARE_ID=s.WARE_ID
            order by p.OPERATION_ID""",ware=ware,after_key=after or " ",pickup_id=pickup,row_limit=limit+1)
        columns=[d[0].lower()for d in cur.description];records=cur.fetchall();more=len(records)>limit;items=[]
        for raw in records[:limit]:
            item=dict(zip(columns,raw))
            item["marked_unit_control"]=read_oracle_json(item["marked_unit_control"])if item["marked_unit_control"]is not None else None
            item["full_source_loaded"]=proof;items.append(item)
        return {"warehouse_id":ware,"items":items,"has_more":more,"next_after":items[-1]["pickup_operation_id"]if more else None,
                "consistent_snapshot":True,"stock_changed":False}

def source(gateway: Any,ware: int,pickup: str,actor: str) -> dict:
    result=page(gateway,ware,actor,pickup=pickup,limit=1,proof=True)
    if not result["items"]:raise StoreReturnReceiveError("RETURN_RECEIVING_SOURCE_NOT_PENDING","Возврат не ожидает приёмки в выбранном складе",404)
    return {**result["items"][0],"warehouse_id":ware,"consistent_snapshot":True,"stock_changed":False}
