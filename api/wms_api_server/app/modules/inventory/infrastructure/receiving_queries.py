"""Current stock composition with immutable receiving provenance."""
import json
from ....oracle_gateway import OracleGateway


class ReceivingQueries:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def composition(self, pallet: str, after: str = "", limit: int = 50) -> dict:
        limit = min(max(limit, 1), 100)
        identity = self.gateway.fetch_all(
            "select STOCK_ORIGIN_UID from RRL_PALLETS where UID_PALLET=:p", {"p": pallet})
        if not identity:
            raise LookupError("Pallet not found")
        origins = self.gateway.fetch_all("""select RESULT_JSON from RRL_SAP_PALLET_RECEIPT rec
            where rec.UID_PALLET=nvl(:origin,:p) or exists(
                select 1 from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=:p
                  and u.STOCK_STATUS!='ISSUED' and u.UID_PALLET=rec.UID_PALLET)
            order by rec.OPERATION_ID fetch first 201 rows only""",
            {"p": pallet, "origin": identity[0]["stock_origin_uid"]})
        receipts = [json.loads(r["result_json"]) for r in origins[:200]]
        rows = self.gateway.fetch_all("""with page as (
            select UID_PALLET,UNIT_ID,PHYSICAL_UNIT_KEY,CURRENT_CELL,BASE_UOM,STOCK_STATUS,
                   to_char(BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') BASE_QTY
            from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p and STOCK_STATUS!='ISSUED'
              and (:after is null or PHYSICAL_UNIT_KEY>:after)
            order by PHYSICAL_UNIT_KEY fetch first :lim rows only)
            select page.*,c.SYSTEM_CODE,c.CANONICAL_CODE,c.RAW_CODE,c.PROFILES_JSON
            from page left join RRL_WMS_RECEIPT_CODE c
              on c.UID_PALLET=page.UID_PALLET and c.UNIT_ID=page.UNIT_ID
            order by page.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE""",
            {"p": pallet, "after": after or None, "lim": limit})
        units = {}
        for row in rows:
            unit = units.setdefault(row["physical_unit_key"], {
                "unit_id": row["unit_id"], "physical_unit_key": row["physical_unit_key"],
                "receipt_pallet_identifier": row["uid_pallet"], "cell": row["current_cell"],
                "quantity": row["base_qty"], "unit": row["base_uom"],
                "stock_status": row["stock_status"], "codes": []})
            if row["system_code"] is not None:
                unit["codes"].append({"system": row["system_code"],
                    "canonical_code": row["canonical_code"], "raw_code": row["raw_code"],
                    "profiles": json.loads(row["profiles_json"])})
        locations = self.gateway.fetch_all("""select CELL,BASE_UOM,
            to_char(REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REMAIN,
            to_char(HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_RESERVED_BASE
            from RRL_REMAINS where UID_POLETA=:p and REMAIN>0 order by CELL""", {"p": pallet})
        return {"pallet_identifier": pallet, "receipt": receipts[0] if receipts else None,
                "receipts": receipts, "receipts_truncated": len(origins) > 200,
                "locations": locations, "units": list(units.values()),
                "next_cursor": list(units)[-1] if len(units) == limit else None}
