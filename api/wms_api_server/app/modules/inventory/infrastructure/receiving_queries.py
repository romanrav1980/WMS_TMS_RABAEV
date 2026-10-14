"""Current stock, unit page and original birth provenance in one read-only snapshot."""
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts_composition import CompositionViewError
from .composition_provenance import cursor_rows,birth_provenance

class ReceivingQueries:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def composition(self,pallet: str,after: str="",limit: int=50,expected_signature: str|None=None) -> dict[str,Any]:
        limit=min(max(limit,1),100)
        with self.gateway.transaction("Pallet composition READ ONLY snapshot")as cur:
            cur.execute("set transaction read only")
            cur.execute("select STOCK_ORIGIN_UID,STOCK_COMPOSITION_VERSION from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=pallet)
            identity=cur.fetchone()
            if not identity:
                raise LookupError("Pallet not found")
            cur.execute("""select CELL,BASE_UOM,to_char(REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')REMAIN,
                to_char(HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')HARD_RESERVED_BASE,STOCK_VERSION
                from RRL_REMAINS where UID_POLETA=:lot_id and REMAIN>0 order by CELL fetch first 201 rows only""",lot_id=pallet)
            locations=cursor_rows(cur)
            if len(locations)>200:
                raise CompositionViewError("COMPOSITION_LOCATION_BOUND_200")
            signature=sha256(json.dumps([identity[1],locations],sort_keys=True,separators=(",",":")).encode()).hexdigest()
            if after and expected_signature is None:
                raise CompositionViewError("COMPOSITION_CURSOR_REQUIRES_SNAPSHOT")
            if expected_signature is not None and expected_signature!=signature:
                raise CompositionViewError("COMPOSITION_SNAPSHOT_CHANGED")
            cur.execute("""select count(*),to_char(nvl(sum(BASE_QTY),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
                from(select BASE_QTY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS!='ISSUED'and rownum<=10001)""",lot_id=pallet)
            count,total=cur.fetchone()
            if count>10000:
                raise CompositionViewError("COMPOSITION_UNIT_BOUND_10000")
            cur.execute("""select RESULT_JSON from RRL_SAP_PALLET_RECEIPT rec where rec.UID_PALLET=nvl(:origin,:lot_id)
                or exists(select 1 from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=:lot_id and u.STOCK_STATUS!='ISSUED'and u.UID_PALLET=rec.UID_PALLET)
                order by rec.OPERATION_ID fetch first 201 rows only""",origin=identity[0],lot_id=pallet)
            receipts_raw=cur.fetchall();receipts=[read_oracle_json(row[0])for row in receipts_raw[:200]]
            births,births_truncated=birth_provenance(cur,pallet)
            units,more=self._units(cur,pallet,after,limit)
        stock=sum((Decimal(row["remain"])for row in locations),Decimal(0))
        coverage="MATCHED" if Decimal(total)==stock else "NO_UNIT_CAPTURE" if count==0 else "MISMATCH"
        return {"pallet_identifier":pallet,"receipt":receipts[0]if receipts else None,"receipts":receipts,
            "receipts_truncated":len(receipts_raw)>200,"source_births":births,"source_births_truncated":births_truncated,
            "locations":locations,"units":units,"physical_unit_count":int(count),"captured_base_quantity":total,
            "stock_quantity":format(stock,"f"),"quantity_coverage":coverage,"composition_signature":signature,
            "composition_epoch":identity[1],"next_cursor":units[-1]["physical_unit_key"]if more else None}

    @staticmethod
    def _units(cur: Any,pallet: str,after: str,limit: int) -> tuple[list[dict[str,Any]],bool]:
        cur.execute("""with page as(select UID_PALLET,UNIT_ID,PHYSICAL_UNIT_KEY,CURRENT_CELL,BASE_UOM,STOCK_STATUS,
            to_char(BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')BASE_QTY,
            to_char(GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')GROSS_WEIGHT_KG,
            to_char(BOX_VOLUME_M3,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN from RRL_WMS_RECEIPT_UNIT
            where CURRENT_UID=:lot_id and STOCK_STATUS!='ISSUED'and(:after_key is null or PHYSICAL_UNIT_KEY>:after_key)
            order by PHYSICAL_UNIT_KEY fetch first :page_limit rows only)
            select page.*,c.SYSTEM_CODE,c.CANONICAL_CODE,c.RAW_CODE,c.PROFILES_JSON from page
            left join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=page.UID_PALLET and c.UNIT_ID=page.UNIT_ID
            order by page.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE""",lot_id=pallet,after_key=after or None,page_limit=limit+1)
        units={}
        for row in cursor_rows(cur):
            unit=units.setdefault(row["physical_unit_key"],{"unit_id":row["unit_id"],"physical_unit_key":row["physical_unit_key"],
                "receipt_pallet_identifier":row["uid_pallet"],"cell":row["current_cell"],"quantity":row["base_qty"],
                "unit":row["base_uom"],"stock_status":row["stock_status"],"codes":[],"gross_weight_kg":row["gross_weight_kg"],
                "volume_m3":row["box_volume_m3"],"measurement_reference":row["measurement_reference"],"weight_label_scan":row["weight_label_scan"]})
            if row["system_code"]is not None:
                raw=row["raw_code"];raw=raw.read()if hasattr(raw,"read")else raw
                unit["codes"].append({"system":row["system_code"],"canonical_code":row["canonical_code"],"raw_code":raw,
                    "profiles":read_oracle_json(row["profiles_json"])})
        return list(units.values())[:limit],len(units)>limit
