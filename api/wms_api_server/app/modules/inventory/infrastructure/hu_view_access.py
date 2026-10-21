"""Current native warehouse and stock-owner authority for bounded HU reads."""
import json
from typing import Any
import oracledb
from fastapi import HTTPException


def assert_hu_view(cur: Any, actor: str, warehouse: int) -> None:
    if type(warehouse) is not int or warehouse < 1:
        raise HTTPException(403, "HU_CURRENT_WARE_VIEWER_REQUIRED")
    cur.execute("select RRL_ACCESS_API.allowed(:p_actor,'warehouse_task_view','WAREHOUSE',:p_warehouse) from dual",
                p_actor=actor, p_warehouse=str(warehouse))
    row = cur.fetchone()
    if row is None or row[0] != 1:
        raise HTTPException(403, "HU_CURRENT_WARE_VIEWER_REQUIRED")


def assert_hu_stock_owners(cur: Any, actor: str, snapshot: dict[str, Any]) -> None:
    """Reject the entire composition if any physical TRADECASE leaf is hidden."""
    nodes = snapshot.get("nodes", [])
    if len(nodes) > 200:
        raise HTTPException(409, "HU_COMPOSITION_BOUND_200")
    cur.setinputsizes(nodes=oracledb.DB_TYPE_CLOB)
    cur.execute("""with owners as(select a.OWNER_ID,count(u.PHYSICAL_UNIT_KEY) TOTAL,
        count(a.PHYSICAL_UNIT_KEY) TAGGED,count(*)-count(u.PHYSICAL_UNIT_KEY) MISSING
        from json_table(:nodes,'$[*]'columns(K varchar2(20)path '$.kind',U varchar2(200)path '$.uid'))j
        left join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=j.U
        left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
        where j.K='STOCK' group by a.OWNER_ID), counts as(
        select nvl(sum(TOTAL),0) TOTAL,nvl(sum(TAGGED),0) TAGGED,
        nvl(sum(case when TAGGED>0 and RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,:ware,OWNER_ID,0)<>1 then 1 else 0 end),0) DENIED,
        nvl(sum(MISSING),0) MISSING from owners)
        select TOTAL,TAGGED,DENIED,MISSING,(select count(*)from RRL_TRADE_SITE where WARE_ID=:ware)
        from counts""", actor=actor, ware=int(snapshot["warehouse"]), nodes=json.dumps(nodes))
    total, tagged, denied, missing, trade_site = cur.fetchone()
    if denied or ((trade_site or tagged) and (total != tagged or missing)):
        raise HTTPException(403, "HU_CURRENT_STOCK_OWNER_VIEW_REQUIRED")


def assert_resolved_hu_view(gateway: Any, row: dict[str, Any], actor: str) -> None:
    """Resolve only warehouse metadata; never expose tree/stock/QC before authority.

    The caller owns one READ ONLY transaction covering resolution, authority and
    composition. An archived shipment uses its original physical warehouse.
    """
    if row.get("case_task_id") is not None:
        warehouses = gateway.fetch_all("select WARE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_task",
                                       {"p_task": row["case_task_id"]})
    elif row.get("hu_shipped_operation"):
        warehouses = gateway.fetch_all("""select json_value(RESULT_JSON,
            '$.composition_at_departure.warehouse' returning number) WARE_ID
            from RRL_STOCK_OPERATION where OPERATION_ID=:p_operation and STATE='APPLIED'""",
            {"p_operation": row["hu_shipped_operation"]})
    else:
        warehouses = gateway.fetch_all("""select WARE_ID from (
            select c.WARE_ID from RRL_PALLETS p join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL
             where p.UID_PALLET=:p_uid and p.HU_KIND='CONTAINER'
            union select c.WARE_ID from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
             where r.UID_POLETA=:p_uid and r.REMAIN>0) fetch first 3 rows only""",
            {"p_uid": row["uid_pallet"]})
    if not warehouses or len(warehouses) > 2:
        raise HTTPException(403, "HU_CURRENT_WARE_VIEWER_REQUIRED")
    for item in warehouses:
        warehouse = item.get("ware_id")
        if warehouse is None or int(warehouse) != warehouse:
            raise HTTPException(403, "HU_CURRENT_WARE_VIEWER_REQUIRED")
        assert_hu_view(gateway.cursor, actor, int(warehouse))
