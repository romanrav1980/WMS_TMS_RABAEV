"""Bounded original ORDERS preparation diagnostics; no orders, pallets or stock writes."""
from decimal import Decimal
from typing import Any
from .store_source_scope import actor_warehouse, assert_store_scope
from .store_calendar_rule import delivery_rule

_NUM = "'TM9','NLS_NUMERIC_CHARACTERS=''.,'''"

def preparation_readiness(gateway: Any, order: int, actor: str, permission: str = "customer_order_view") -> dict:
    with gateway.transaction("Original SAP ST preparation readiness READ ONLY") as cur:
        if not getattr(gateway, "transaction_bound", False):
            cur.execute("set transaction read only")
        actor_warehouse(cur, actor, permission)
        cur.execute("""select c.WARE_ID,c.STATUS,m.LEGACY_ADDR,s.ADMISSION_STATUS,s.PREPARATION_HASH,
            s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES,c.CUSTOMER_STORE_MAP_ID,
            case when from_tz(cast(s.PICKING_FINISH_AT as timestamp),
                case when s.UTC_OFFSET_MINUTES<0 then '-' else '+' end||
                lpad(trunc(abs(s.UTC_OFFSET_MINUTES)/60),2,'0')||':'||
                lpad(mod(abs(s.UTC_OFFSET_MINUTES),60),2,'0'))>systimestamp then 1 else 0 end,s.PICKING_FINISH_AT,c.SHIPMENT_DATE
            from RRL_CUSTOMER_ORDER c join RRL_SAP_STORE_ORDER s on s.CUSTOMER_ORDER_ID=c.CUSTOMER_ORDER_ID
            join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=c.CUSTOMER_STORE_MAP_ID
            where c.CUSTOMER_ORDER_ID=:order_id""", order_id=order)
        header=cur.fetchone()
        if header is None:
            raise LookupError("Original SAP source order not found")
        warehouse,status,address,admission,prepared,day,offset,map_id,future,finish,shipment=header
        assert_store_scope(cur,actor,permission,warehouse)
        proof=delivery_rule(cur,warehouse,map_id,day)
        blockers=[]
        if prepared:
            blockers.append("ALREADY_PREPARED_USE_SAVED_RESULT")
        if admission!="ACCEPTED":
            blockers.append("SOURCE_NOT_ADMITTED")
        if status not in ("DRAFT","OPEN","IMPORTED"):
            blockers.append("SOURCE_OPERATIONAL_STATE_FROZEN")
        if not address or not address.strip():
            blockers.append("LEGACY_ADDRESS_MISSING")
        if not proof["allowed"]:
            blockers.append("CURRENT_CALENDAR_CLOSED")
        if proof["utc_offset_minutes"]!=offset:
            blockers.append("CURRENT_CALENDAR_ZONE_CHANGED")
        if not future:
            blockers.append("PICKING_DEADLINE_PASSED")
        # Exactly one scalar logistics record is required by the original writer.
        cur.execute(f"""with demand as (select ARTICUL,sum(ORDER_QTY)ORDER_QTY,min(UNIT_CODE)UNIT_CODE,count(distinct UNIT_CODE)UNIT_COUNT
            from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id group by ARTICUL)
            select /* SOURCE_PICKING_READINESS268 */ r.ARTICUL,to_char(r.ORDER_QTY,{_NUM}),r.UNIT_CODE,
            a.ACTICUL,a.CELL,x.WARE_ID,to_char(a.COUNT_SHT_IN_KOR,{_NUM}),
            to_char(a.BRUTTO_WEIGHT_OF_KOR,{_NUM}),to_char(a.DIMKOR_X,{_NUM}),
            to_char(a.DIMKOR_Y,{_NUM}),to_char(a.DIMKOR_Z,{_NUM}),
            to_char(round(r.ORDER_QTY/nullif(a.COUNT_SHT_IN_KOR,0),nvl(a.ROUND_TO,0))
                *a.COUNT_SHT_IN_KOR,{_NUM}),
            (select count(*)from RRL_ARTICULS z where z.ACTICUL=r.ARTICUL),r.UNIT_COUNT,to_char(a.NORMA_UKLADKI,{_NUM}),
            to_char(cfg.TEMP_MIN,{_NUM}),to_char(cfg.TEMP_MAX,{_NUM})
            from demand r left join RRL_ARTICULS a on a.ACTICUL=r.ARTICUL
            left join RRL_CELLS x on x.CELL=a.CELL
            left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=:warehouse_id and cfg.ARTICUL=r.ARTICUL
            order by r.ARTICUL
            fetch first 1001 rows only""",order_id=order,warehouse_id=warehouse)
        raw=cur.fetchall()
        if len(raw)>1000:
            raise ValueError("SOURCE_READINESS_LINE_BOUND_1000")
        lines=[]
        for row in raw:
            article,quantity,uom,found,cell,cell_ware,pack,mass,dx,dy,dz,rounded,count,unit_count,norm,temp_min,temp_max=row
            errors=[]
            values=[Decimal(value) if value is not None else None for value in (pack,mass,dx,dy,dz)]
            if unit_count!=1:
                errors.append("SOURCE_BASE_UNIT_AMBIGUOUS")
            if count!=1 or not found:
                errors.append("LEGACY_ARTICLE_NOT_UNIQUE")
            if not cell or cell_ware!=warehouse:
                errors.append("SOURCE_PICKING_CELL_MISSING")
            if any(value is None or value<=0 for value in values):
                errors.append("PACKAGING_MASS_DIMENSIONS_REQUIRED")
            if rounded is None or Decimal(rounded)!=Decimal(quantity):
                errors.append("LEGACY_ROUNDING_CHANGES_SOURCE_QUANTITY")
            if values[0] and Decimal(quantity)/values[0]!=(Decimal(quantity)/values[0]).to_integral_value():
                errors.append("WHOLE_PACKAGING_LAYOUT_REQUIRED")
            lines.append({"articul":article,"quantity":quantity,"unit_code":uom,"picking_cell":cell,
                "pack_quantity":pack,"pallet_norm":norm,"pack_mass":mass,"dimensions":[dx,dy,dz],
                "legacy_rounded_quantity":rounded,"temp_min_c":temp_min,"temp_max_c":temp_max,"blockers":errors})
        if not lines:
            blockers.append("SOURCE_DEMAND_EMPTY")
        return {"customer_order_id":order,"warehouse_id":warehouse,"admission_status":admission,
            "customer_order_status":status,"already_prepared":bool(prepared),"legacy_address":address,
            "ready_for_operator_layout":not blockers and all(not line["blockers"] for line in lines),
            "blockers":blockers,"lines":lines,"calendar":proof,"consistent_snapshot":True,
            "picking_finish_at":finish.isoformat() if finish else None,
            "shipment_at":shipment.isoformat() if shipment else None,
            "stock_changed":False,"automatic_split_verified":False}
