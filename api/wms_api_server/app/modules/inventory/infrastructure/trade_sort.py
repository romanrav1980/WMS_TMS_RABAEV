"""Resolve exact scanned units; reuse the stock coordinator for physical sorting."""
from decimal import Decimal
import json
from typing import Any
import oracledb
from ..contracts_trade_stock import TradeSort, TradeStockError
from ..contracts_stock import StockCommand
from ..domain.mark_identity import normalize_unit_scan_codes
from ..domain.stock_quantity import quantity_text
from .stock_posting_uow import StockPosting


def resolve(gateway: Any, warehouse: int, body: TradeSort) -> tuple[tuple[str, ...], str, str]:
    scans = normalize_unit_scan_codes([s.model_dump() for s in body.scans])
    identities = [(s["system_code"], s["code_hash"]) for s in scans]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate scanned marking code")
    found: dict[int, tuple[str, Decimal, str]] = {}
    with gateway.transaction("Resolve exact TRADECASE sorting scans") as cur:
        for start in range(0, len(scans), 500):
            batch = [dict(s, index=i) for i, s in enumerate(scans[start:start+500], start)]
            wire = cur.var(oracledb.DB_TYPE_CLOB)
            wire.setvalue(0, json.dumps(batch))
            cur.execute("""
                select j.I,u.PHYSICAL_UNIT_KEY,u.BASE_QTY,u.BASE_UOM
                from json_table(:scans,'$[*]' columns(I number path '$.index',S varchar2(40) path '$.system_code',
                    P varchar2(80) path '$.profile_code',H varchar2(64) path '$.code_hash'))j
                join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.S and c.CODE_HASH=j.H
                join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID
                join RRL_CELLS cell on cell.CELL=u.CURRENT_CELL and cell.WARE_ID=:ware
                where u.CURRENT_UID=:pallet_id and u.CURRENT_CELL=:cell and u.STOCK_STATUS<>'ISSUED'
                  and exists(select 1 from json_table(c.PROFILES_JSON,'$[*]'columns(P varchar2(80)path '$.profile'))p where p.P=j.P)
            """,scans=wire,ware=warehouse,pallet_id=body.source_pallet,cell=body.source_cell)
            for i,key,qty,uom in cur:
                if int(i) in found:
                    raise ValueError("Ambiguous physical unit for scanned code")
                found[int(i)] = (key,Decimal(str(qty)),uom)
    if len(found) != len(scans) or len({v[0] for v in found.values()}) != len(scans):
        raise ValueError("Scanned code is not a distinct unit on the source pallet")
    if len({v[2] for v in found.values()}) != 1:
        raise ValueError("Selected units have different base units")
    return tuple(sorted(v[0] for v in found.values())),quantity_text(sum((v[1] for v in found.values()),Decimal(0))),found[0][2]


def post_sort(gateway: Any, warehouse: int, body: TradeSort, actor: str) -> dict[str,Any]:
    submitted=body.model_dump(mode="json")
    if len(json.dumps(submitted,ensure_ascii=True).encode())>2*1024*1024:
        raise TradeStockError("TRADE_SORT_MESSAGE_TOO_LARGE",413)
    try:
        allowed=gateway.fetch_all("select RRL_ACCESS_API.allowed(:actor,'tradecase_stock_sort','WAREHOUSE',:ware) OK from dual",dict(actor=actor,ware=str(warehouse)))
        if not allowed or allowed[0]["ok"]!=1:
            raise TradeStockError("TRADE_SORT_FORBIDDEN",403)
        source={"warehouse_id":warehouse}
        saved=gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:o",dict(o=body.operation_id))
        if saved:
            wire=saved[0]["canonical_request"]
            old=wire if isinstance(wire,dict)else json.loads(wire.read()if hasattr(wire,"read")else wire)
            if old["actor"]!=actor or old["command_type"]!="INTERNAL_MOVE" or old["source"]!=source or old["metadata"].get("requested_sort")!=submitted:
                raise TradeStockError("OPERATION_CONTENT_CONFLICT")
            metadata,units=old["metadata"],tuple(old["units"])
        else:
            units,quantity,uom=resolve(gateway,warehouse,body)
            metadata=dict(tradecase_sorting=True,warehouse_id=warehouse,uid=body.source_pallet,source_cell=body.source_cell,
                target_cell=body.target_cell,quantity=quantity,unit=uom,requested_sort=submitted)
        return StockPosting().post(StockCommand(operation_id=body.operation_id,command_type="INTERNAL_MOVE",actor=actor,
            lines=(),source=source,units=units,metadata=metadata))
    except ValueError as exc:
        raise TradeStockError(str(exc),422)from exc
    except oracledb.DatabaseError as exc:
        raise TradeStockError("TRADE_SORT_RESULT_UNKNOWN",503)from exc
