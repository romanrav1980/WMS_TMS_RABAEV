"""Original source and demand with current native warehouse authority in one snapshot."""
from typing import Any
from ...platform.public import read_oracle_json
from .store_source_scope import actor_warehouse, assert_store_scope


def rows(cur: Any) -> list[dict[str, Any]]:
    names = [column[0].lower() for column in cur.description]
    return [dict(zip(names, record)) for record in cur.fetchall()]


def list_store_orders(gateway: Any, warehouse: int | None, limit: int, actor: str) -> list[dict[str, Any]]:
    if not 1 <= limit <= 200:
        raise ValueError("STORE_ORDER_LIST_BOUND_200")
    with gateway.transaction("Original SAP customer worklist READ ONLY") as cur:
        cur.execute("set transaction read only")
        own, global_admin = actor_warehouse(cur, actor, "customer_order_view")
        if warehouse is not None:
            assert_store_scope(cur, actor, "customer_order_view", warehouse)
        target = warehouse if warehouse is not None else None if global_admin else own
        cur.execute("""select s.CUSTOMER_ORDER_ID,s.SENDER,s.ORDER_NUMBER,s.ADMISSION_STATUS,s.OPERATIONAL_DATE,
            s.DELIVERY_DATE,s.PICKING_START_AT,s.PICKING_FINISH_AT,s.SHIPMENT_AT,c.WARE_ID,m.STORE_CODE,m.ADDRESS_TEXT,c.STATUS
            from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID
            join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=c.CUSTOMER_STORE_MAP_ID
            where (:warehouse is null or c.WARE_ID=:warehouse)
            order by s.CREATED_AT desc,s.CUSTOMER_ORDER_ID fetch first :page_limit rows only""",
            warehouse=target, page_limit=limit)
        return rows(cur)


def store_order_detail(gateway: Any, order: int, actor: str) -> dict[str, Any]:
    with gateway.transaction("Original immutable SAP demand READ ONLY") as cur:
        cur.execute("set transaction read only")
        actor_warehouse(cur, actor, "customer_order_view")
        cur.execute("""select s.*,c.WARE_ID SOURCE_WARE_ID,c.STATUS CUSTOMER_ORDER_STATUS
            from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID
            where s.CUSTOMER_ORDER_ID=:order_id""", order_id=order)
        records = rows(cur)
        if not records:
            raise LookupError("SAP store order not found")
        result = records[0]
        assert_store_scope(cur, actor, "customer_order_view", result["source_ware_id"])
        for field in ("demand_json", "result_json", "preparation_json"):
            if result.get(field) is not None:
                result[field] = read_oracle_json(result[field])
        if hasattr(result.get("raw_xml"), "read"):
            result["raw_xml"] = result["raw_xml"].read()
        from .store_admission import read_admission
        result["admission_decision"] = read_admission(cur, order, actor)
        result["consistent_snapshot"] = True
        return result
