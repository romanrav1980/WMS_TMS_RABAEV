"""Current warehouse-scoped group headers; detailed composition is loaded separately."""
from typing import Any
import json
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError


def _scope(q: Any,ware: int,actor: str)->None:
    q.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
        and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')
        and(RRL_HAS_WRIGHT(ID,'transport_dispatch_view')=1 or RRL_HAS_WRIGHT(ID,'interwarehouse_receive')=1)""",
              actor=actor,ware=ware)
    if q.fetchone()[0]!=1:
        raise StoreReturnReceiveError("INTERWARE_GROUP_WARE_FORBIDDEN","Current warehouse access required",403)


class InterwarehouseGroupRead:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    def queue(self,ware: int,actor: str,limit: int=200,after_operation_id: str|None=None)->list[dict[str,Any]]:
        with self.gateway.transaction("Bounded interwarehouse group worklist")as q:
            q.execute("set transaction read only");_scope(q,ware,actor)
            if not 1<=limit<=200:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PAGE_BOUND","Page size must be 1..200",422)
            if after_operation_id is not None:
                q.execute("select 1 from RRL_IW_GROUP_PLAN where OPERATION_ID=:after_id and TARGET_WARE_ID=:ware",after_id=after_operation_id,ware=ware)
                if q.fetchone() is None:
                    raise StoreReturnReceiveError("INTERWARE_GROUP_CURSOR_INVALID","Reload the warehouse queue",422)
            q.execute("""select p.OPERATION_ID,p.ROOT_UID,p.SOURCE_WARE_ID,p.TARGET_WARE_ID,p.SOURCE_TT_ID,
                p.TARGET_TT_ID,to_char(p.ARRIVAL_DUE,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM'),
                to_char(p.READY_DUE,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM'),
                u.OPERATION_ID,r.OPERATION_ID,r.RECEIVE_CELL,pp.TASK_ID,t.STATUS,placed.TARGET_CELL,
                json_value(p.SOURCE_JSON,'$.stock_leaf_count'returning number)
                from RRL_IW_GROUP_PLAN p left join RRL_IW_GROUP_PLAN anchor on anchor.OPERATION_ID=:after_id and anchor.TARGET_WARE_ID=:ware
                left join RRL_IW_GROUP_UNLOAD u on u.PLAN_OPERATION_ID=p.OPERATION_ID
                left join RRL_IW_GROUP_RECEIPT r on r.PLAN_OPERATION_ID=p.OPERATION_ID
                left join RRL_IW_GROUP_PUT_PLAN pp on pp.RECEIPT_OPERATION_ID=r.OPERATION_ID
                left join RRL_WAREHOUSE_TASK t on t.TASK_ID=pp.TASK_ID
                left join RRL_IW_GROUP_PLACEMENT placed on placed.RECEIPT_OPERATION_ID=r.OPERATION_ID
                where p.TARGET_WARE_ID=:ware
                and (:after_id is null or p.ARRIVAL_DUE<anchor.ARRIVAL_DUE
                    or (p.ARRIVAL_DUE=anchor.ARRIVAL_DUE and p.OPERATION_ID>anchor.OPERATION_ID))
                order by p.ARRIVAL_DUE desc,p.OPERATION_ID fetch first :page_limit rows only""",
                ware=ware,after_id=after_operation_id,page_limit=limit)
            fields=("operation_id","pallet_identifier","source_warehouse_id","target_warehouse_id","source_trip_id",
                    "target_trip_id","arrival_due","ready_due","unload_operation_id","receipt_operation_id",
                    "receive_cell","placement_task_id","placement_task_status","target_cell","stock_leaf_count")
            return [dict(zip(fields,row))for row in q.fetchall()]

    def detail(self,plan: str,actor: str)->dict[str,Any]:
        with self.gateway.transaction("Scoped grouped interwarehouse composition")as q:
            q.execute("set transaction read only")
            q.execute("select TARGET_WARE_ID from RRL_IW_GROUP_PLAN where OPERATION_ID=:plan_id",plan_id=plan)
            row=q.fetchone()
            if row is None:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PLAN_NOT_FOUND","Existing group plan required",404)
            _scope(q,row[0],actor)
            q.execute("select RESULT_JSON,SOURCE_JSON from RRL_IW_GROUP_PLAN where OPERATION_ID=:plan_id",plan_id=plan)
            result,source=q.fetchone();source=read_oracle_json(source)
            lots=[dict(uid=x["uid"],st_id=x["st_id"],article=x["article"],quantity=x["quantity"],
                       base_uom=x["base_uom"],profiles=x["profiles"],physical_unit_count=x["issued_manifest"]["physical_unit_count"])
                  for x in source["lots"]]
            q.execute("""select distinct card.ARTICUL,card.SYSTEM_CODE,card.PROFILE_CODE,card.PROFILE_VERSION,card.SCAN_MODE
                from json_table(:source_json,'$.lots[*]'columns(A varchar2(160)path '$.article'))selected
                join RRL_SKU_RECEIPT_PROFILE card on card.ARTICUL=selected.A
                order by card.ARTICUL,card.SYSTEM_CODE,card.PROFILE_CODE fetch first 4001 rows only""",source_json=json.dumps(source))
            current_profiles=q.fetchall()
            if len(current_profiles)>4000:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PROFILE_BOUND","Profile matrix exceeds 4000",422)
            for lot in lots:
                lot["scan_profiles"]=[dict(system_code=card[1],profile_code=card[2],profile_version=card[3],scan_mode=card[4])for card in current_profiles if card[0]==lot["article"]]
            q.execute("""select r.OPERATION_ID,r.RECEIVE_CELL,pp.TASK_ID,t.STATUS,t.HU_CONTENT_VERSION,
                placed.TARGET_CELL from RRL_IW_GROUP_RECEIPT r
                left join RRL_IW_GROUP_PUT_PLAN pp on pp.RECEIPT_OPERATION_ID=r.OPERATION_ID
                left join RRL_WAREHOUSE_TASK t on t.TASK_ID=pp.TASK_ID
                left join RRL_IW_GROUP_PLACEMENT placed on placed.RECEIPT_OPERATION_ID=r.OPERATION_ID
                where r.PLAN_OPERATION_ID=:plan_id""",plan_id=plan)
            state=q.fetchone()
            q.execute("""select c.OPERATION_ID,o.RESULT_JSON from RRL_IW_GROUP_CUSTODY c
                left join RRL_IW_GROUP_ONWARD o on o.RECEIPT_OPERATION_ID=c.RECEIPT_OPERATION_ID
                join RRL_IW_GROUP_RECEIPT r on r.OPERATION_ID=c.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=:plan_id""",plan_id=plan)
            onward=q.fetchone()
            q.execute("""select count(distinct d.ST_ID),count(distinct d.OPERATION_ID),
                count(distinct case when shop_line.SHIPPED_BASE_QTY=d.BASE_QTY and shop_line.ACCEPTED_BASE_QTY=d.BASE_QTY then d.ST_ID end)
                from RRL_IW_GROUP_DISPATCH d join RRL_IW_GROUP_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID
                left join RRL_STORE_RECEIPT_FACT shop on shop.LOAD_OPERATION_ID=d.OPERATION_ID
                left join RRL_STORE_RECEIPT_LINE shop_line on shop_line.OPERATION_ID=shop.OPERATION_ID and shop_line.LOT_UID=d.ROOT_UID
                where r.PLAN_OPERATION_ID=:plan_id""",plan_id=plan)
            loaded_members,load_count,accepted_members=q.fetchone()

            q.execute("""select p.HU_CONTENT_VERSION,p.HU_CURRENT_CELL from RRL_PALLETS p
                join RRL_IW_GROUP_PLAN g on g.ROOT_UID=p.UID_PALLET
                join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL and c.WARE_ID=g.TARGET_WARE_ID
                where g.OPERATION_ID=:plan_id""",plan_id=plan)
            current=q.fetchone()
            return dict(plan=read_oracle_json(result),lots=lots,
                        receipt_operation_id=state[0]if state else None,receive_cell=state[1]if state else None,
                        placement_task_id=state[2]if state else None,placement_task_status=state[3]if state else None,
                        placement_content_version=state[4]if state else None,target_cell=state[5]if state else None,
                        current_content_version=current[0]if current else None,current_cell=current[1]if current else None,
                        custody_operation_id=onward[0]if onward else None,
                        onward=read_oracle_json(onward[1])if onward and onward[1]else None,
                        loaded_members=loaded_members,load_count=load_count,accepted_members=accepted_members,
                        delivered=accepted_members==len(lots),grouped_receipt_available=True,stock_changed=False)
