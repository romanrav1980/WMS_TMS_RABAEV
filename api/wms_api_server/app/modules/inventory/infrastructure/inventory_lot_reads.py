"""One read-only snapshot for current authority, lot rows and marking profiles."""
from typing import Any
from ....db import rows_as_dicts
from ..contracts_observations import InventoryObservationError
from .inventory_scope import assert_inventory_cursor_scope
from .hu_view_access import assert_hu_stock_owners


def inventory_lots(gateway: Any, revision: int, cell: str, article: str | None, actor: str,
                   task: int | None = None) -> dict[str, Any]:
    with gateway.transaction("Current scoped inventory lots") as cursor:
        cursor.execute("set transaction read only")
        assert_inventory_cursor_scope(cursor, actor, revision=revision, task=task, cell=cell, article=article)
        cursor.execute("""select r.UID_POLETA LOT_UID,p.ARTICUL ARTICLE,r.CELL,
            to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QTY,
            to_char(r.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QTY,
            r.STOCK_VERSION,p.EXPIRY_DATE,r.BASE_UOM UNIT
            from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
            where r.CELL=:cell and (:article is null or p.ARTICUL=:article) and exists(
                select 1 from RRL_REVIZION d join RRL_CELLS c on c.CELL=r.CELL
                where d.ID=:revision and d.WARE_ID=c.WARE_ID and d.CONDITION in (0,1))
            order by p.ARTICUL,p.EXPIRY_DATE,r.UID_POLETA fetch first 201 rows only""",
            cell=cell, revision=revision, article=article)
        rows = rows_as_dicts(cursor)
        if len(rows) > 200:
            raise InventoryObservationError("INVENTORY_CELL_BATCH_BOUND")
        if rows:
            cursor.execute("select WARE_ID from RRL_REVIZION where ID=:revision", revision=revision)
            warehouse = cursor.fetchone()[0]
            assert_hu_stock_owners(cursor, actor, {
                "warehouse": int(warehouse),
                "nodes": [{"kind": "STOCK", "uid": row["lot_uid"]} for row in rows],
            })
        for row in rows:
            row["uid"] = row.pop("lot_uid")
        articles = sorted({row["article"] for row in rows})
        if articles:
            params = {"article" + str(i): value for i, value in enumerate(articles)}
            cursor.execute("select ARTICUL,SYSTEM_CODE,PROFILE_CODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL in (" +
                ",".join(":" + key for key in params) + ") order by ARTICUL,SYSTEM_CODE,PROFILE_CODE", params)
            profiles = rows_as_dicts(cursor)
            for row in rows:
                row["marking_profiles"] = [{"system_code": p["system_code"], "profile_code": p["profile_code"]}
                    for p in profiles if p["articul"] == row["article"]]
        return {"revision_id": revision, "cell": cell, "lots": rows}
