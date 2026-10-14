"""Keep native pallet UID separate from proven regulatory aggregation SSCC."""
from typing import Any
import oracledb
from ..domain.regulatory_pallet import receipt_sscc

def create_receipt_parent(cur: Any,pallet: str,scanned: list[dict[str,Any]]) -> tuple[int|None,str|None]:
    cur.execute("select SSCC from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=pallet)
    row=cur.fetchone()
    if not row:
        raise ValueError("Physical pallet required before regulatory capture")
    sscc=receipt_sscc(pallet,row[0],scanned)
    if sscc is None:
        return None,None
    cur.execute("select UID_PALLET from RRL_CRPT_AGGREGATION where SSCC=:sscc",sscc=sscc)
    old=cur.fetchone()
    if old and old[0]!=pallet:
        raise ValueError("Regulatory SSCC belongs to another physical pallet")
    parent=cur.callfunc("RRL_PRODUCTION_API.CREATE_AGGREGATION",oracledb.DB_TYPE_NUMBER,[sscc,None,pallet,None,"PALLET"])
    return int(parent),sscc
