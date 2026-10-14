"""One scoped snapshot of declared, accepted and missing interwarehouse cargo."""
from decimal import Decimal
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .interwarehouse_recovery_read import read_recovery

def read_shortage(gateway: Any,receipt_id: str,actor: str,selected_request: str|None=None) -> dict[str,Any]:
    with gateway.transaction("Interwarehouse shortage original unit reconciliation")as cur:
        cur.execute("set transaction read only")
        cur.execute("""select r.PLAN_OPERATION_ID,r.SOURCE_LOAD_OPERATION_ID,r.ROOT_UID,r.ORIGINAL_ROOT_UID,
            r.BASE_QTY,r.EXPECTED_BASE_QTY,r.BASE_UOM,r.WARE_ID,r.DISCREPANCY_REASON,r.DISCREPANCY_REFERENCE,
            o.RESOLVED_PLAN_JSON,c.CUSTODY_RELEASED_AT,p.SOURCE_WARE_ID
            from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID
            join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID and o.STATE='APPLIED'and o.COMMAND_TYPE='INTERWARE_RECEIVE'
            join RRL_TT_HU_LOAD_FACT c on c.LOAD_OPERATION_ID=r.SOURCE_LOAD_OPERATION_ID
            join RUSERS u on u.ID=:actor
            where r.OPERATION_ID=:receipt_id and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
            and(u.WARE_ID in(p.SOURCE_WARE_ID,p.TARGET_WARE_ID)or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",
            actor=actor,receipt_id=receipt_id)
        row=cur.fetchone()
        if row is None:
            raise StoreReturnReceiveError("INTERWARE_SHORTAGE_SCOPE_REQUIRED","Требуется текущий диспетчер склада одного из плеч",403)
        plan,load,accepted_uid,original_uid,qty,expected,uom,ware,reason,reference,resolved,released,source_ware=row
        domain=read_oracle_json(resolved)["domain"]
        originals=domain.get("original_source_units",[])
        accepted=domain.get("source_units",[])
        if len(originals)>10000 or len(accepted)>10000:
            raise StoreReturnReceiveError("INTERWARE_SHORTAGE_UNIT_BOUND","Состав превышает допустимый размер",409)
        accepted_keys={x["key"]for x in accepted}
        missing=[x for x in originals if x["key"]not in accepted_keys]
        if len({x["key"]for x in originals})!=len(originals)or len(accepted_keys)!=len(accepted):
            raise StoreReturnReceiveError("INTERWARE_SHORTAGE_DUPLICATE_FROZEN_UNIT","Исходный состав содержит неоднозначные единицы",409)
        shortage=Decimal(str(expected))-Decimal(str(qty))if original_uid else Decimal(0)
        missing_qty=sum((Decimal(str(x["quantity"]))for x in missing),Decimal(0))
        if originals and missing_qty!=shortage:
            raise StoreReturnReceiveError("INTERWARE_SHORTAGE_FROZEN_QUANTITY_MISMATCH","Количество недостающих единиц не соответствует приёмке",409)
        wire=cur.var(oracledb.DB_TYPE_CLOB)
        import json
        wire.setvalue(0,json.dumps(missing))
        cur.execute("""select /*+ leading(j u) use_nl(u) index(u RRL_RECEIPT_UNIT_PHYSICAL_UK) */ j.K,j.Q,j.B,u.UNIT_ID,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.UNIT_VERSION,
            u.BASE_QTY,u.BASE_UOM,
            (select /*+ index(c RRL_WMS_REC_CODE_PAL_IX) */ count(*)from RRL_WMS_RECEIPT_CODE c where c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID)CODE_COUNT
            from json_table(:missing_units,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j
            left join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K order by j.K""",missing_units=wire)
        units=[dict(key=r[0],declared_quantity=r[1],base_uom=r[2],unit_id=r[3],current_pallet_identifier=r[4],
                    current_cell=r[5],current_stock_status=r[6],current_unit_version=r[7],
                    current_quantity=None if r[8]is None else str(r[8]),current_base_uom=r[9],registered_code_count=int(r[10]))for r in cur.fetchall()]
        unresolved=[u["key"]for u in units if u["current_pallet_identifier"]!=original_uid or u["current_stock_status"]!="ISSUED"
                    or u["current_quantity"]is None or Decimal(u["current_quantity"])!=Decimal(u["declared_quantity"])or u["current_base_uom"]!=u["base_uom"]]
        cur.execute("""select req.OPERATION_ID,req.ACTOR,req.REASON_TEXT,req.EVIDENCE_REFERENCE,
            fact.OPERATION_ID,fact.ACTOR,fact.REASON_TEXT,fact.EVIDENCE_REFERENCE
            from RRL_INTERWARE_SHORTAGE_REQUEST req left join RRL_INTERWARE_SHORTAGE_FACT fact on fact.REQUEST_OPERATION_ID=req.OPERATION_ID
            where req.RECEIPT_OPERATION_ID=:receipt_id""",receipt_id=receipt_id)
        claim=cur.fetchone()
        recovery,placement_plan,placement,onward,recovery_cases=read_recovery(cur,claim,selected_request)
        recovered_keys=set()
        if claim and claim[4]:
            cur.execute("""select r.PHYSICAL_UNIT_KEY from RRL_INTERWARE_RECOVERY_UNIT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.RECOVERY_OPERATION_ID
                where r.LOSS_OPERATION_ID=:loss_id and o.STATE='APPLIED'and o.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'""",
                loss_id=claim[4])
            recovered_keys={r[0]for r in cur.fetchall()}
            unit_by_key={u["key"]:u for u in units}
            unresolved=[k for k in unresolved if k not in recovered_keys or
                unit_by_key[k]["current_quantity"]is None or Decimal(unit_by_key[k]["current_quantity"])!=Decimal(unit_by_key[k]["declared_quantity"])or
                unit_by_key[k]["current_base_uom"]!=unit_by_key[k]["base_uom"]or unit_by_key[k]["current_stock_status"]not in {"AVAILABLE","BLOCKED","ISSUED"}]
        claims={key:case["request_operation_id"]for case in recovery_cases if not case["cancel_operation_id"]for key in case["unit_keys"]}
        for unit in units:
            unit["recovered"]=unit["key"]in recovered_keys
            unit["recovery_report_operation_id"]=claims.get(unit["key"])
        cur.execute("""select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE
            where ARTICUL=(select ARTICLE from RRL_INTERWARE_RECEIPT where OPERATION_ID=:receipt_id)
            order by SYSTEM_CODE,PROFILE_CODE fetch first 51 rows only""",receipt_id=receipt_id)
        profiles=[dict(system_code=r[0],profile_code=r[1],profile_version=r[2],scan_mode=r[3])for r in cur.fetchall()]
        if len(profiles)>50:raise StoreReturnReceiveError("INTERWARE_RECOVERY_PROFILE_BOUND","Слишком много профилей маркировки",409)
        recovered_qty=sum((Decimal(case["recovered_quantity"])for case in recovery_cases if case["receipt_operation_id"]),Decimal(0))
        reported_qty=sum((Decimal(case["request_quantity"])for case in recovery_cases if not case["cancel_operation_id"]),Decimal(0))
        if recovered_qty>shortage or reported_qty>shortage:raise StoreReturnReceiveError("RECOVERY_HISTORY_QUANTITY_CONFLICT","Восстановление превышает исходную недостачу",409)
        return dict(receipt_operation_id=receipt_id,plan_operation_id=plan,source_load_operation_id=load,
                    source_warehouse_id=int(source_ware),target_warehouse_id=int(ware),
                    original_pallet_identifier=original_uid or accepted_uid,accepted_pallet_identifier=accepted_uid,
                    expected_quantity=str(expected if original_uid else qty),accepted_quantity=str(qty),short_quantity=str(shortage),
                    article=domain.get("article"),profiles=profiles,recovery_cases=recovery_cases,
                    unreported_recovery_quantity=str(shortage-reported_qty),recovery_selection_quantity=next((case["request_quantity"]for case in recovery_cases if recovery and case["request_operation_id"]==recovery[0]),None),net_unrecovered_short_quantity=str(shortage-recovered_qty),
                    currently_missing_units=[u for u in units if not u["recovered"]],
                    base_uom=uom,discrepancy_reason=reason,discrepancy_reference=reference,missing_units=units,
                    missing_unit_count=len(units),current_unit_state_conflicts=unresolved,
                    recovery_placement_task_id=placement_plan[0]if placement_plan else None,recovery_placement_task_status=placement_plan[1]if placement_plan else None,
                    recovery_placement_target_cell=placement_plan[2]if placement_plan else None,recovery_placement_operation_id=placement[3]if placement else None,
                    recovery_st_binding_operation_id=onward[0]if onward else None,recovery_st_id=onward[1]if onward else None,
                    recovery_st_identifier=onward[2]if onward else None,recovery_st_number=onward[3]if onward else None,
                    recovery_target_trip_id=onward[4]if onward else None,recovery_dispatch_operation_id=onward[5]if onward else None,
                    recovery_final_receipt_operation_id=onward[6]if onward else None,recovery_final_receipt_state=onward[7]if onward else None,
                    recovery_cancel_operation_id=next((case["cancel_operation_id"]for case in recovery_cases if recovery and case["request_operation_id"]==recovery[0]),None),
                    status="RECOVERY_REQUEST_CANCELLED"if recovery and any(case["request_operation_id"]==recovery[0]and case["cancel_operation_id"]for case in recovery_cases)else"RECOVERY_FINAL_RECEIPT_RECORDED"if onward and onward[6]else"RECOVERY_DISPATCHED"if onward and onward[5]else"RECOVERY_ST_PREPARED"if onward else"RECOVERED_PLACED_PENDING_REDELIVERY"if placement else"RECOVERED_PENDING_PLACEMENT"if recovery and recovery[4]else"CONFIRMED_CARRIER_SHORTAGE"if claim and claim[4]else"PENDING_INDEPENDENT_CONFIRMATION"if claim else"OPEN_SHORTAGE"if shortage>0 else"FULL_RECEIPT",
                    shortage_request_operation_id=claim[0]if claim else None,shortage_reporter=claim[1]if claim else None,
                    shortage_confirmation_operation_id=claim[4]if claim else None,shortage_approver=claim[5]if claim else None,
                    shortage_confirmation_reason=claim[6]if claim else None,shortage_confirmation_evidence=claim[7]if claim else None,
                    recovery_request_operation_id=recovery[0]if recovery else None,recovery_reporter=recovery[1]if recovery else None,
                    recovery_approval_operation_id=recovery[2]if recovery else None,recovery_approver=recovery[3]if recovery else None,
                    recovery_receipt_operation_id=recovery[4]if recovery else None,recovered_pallet_identifier=recovery[5]if recovery else None,
                    recovered_quantity=str(recovered_qty),
                    carrier_custody_released=released is not None,loss_confirmed=bool(claim and claim[4]),stock_changed=False,regulatory_ack_verified=False)
