"""Read original birth provenance without manufacturing a SAP receipt."""
from typing import Any
from ...platform.public import read_oracle_json

def cursor_rows(cur: Any) -> list[dict[str,Any]]:
    names=[column[0].lower()for column in cur.description]
    return [dict(zip(names,row))for row in cur.fetchall()]

def birth_provenance(cur: Any,pallet: str) -> tuple[list[dict[str,Any]],bool]:
    cur.execute("""with origins as (
      select nvl(STOCK_ORIGIN_UID,UID_PALLET)ORIGIN_UID from RRL_PALLETS where UID_PALLET=:lot_id
      union select UID_PALLET from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS!='ISSUED')
      select p.UID_PALLET ORIGIN_PALLET_IDENTIFIER,o.OPERATION_ID,o.COMMAND_TYPE,o.ACTOR,o.STATE,
      json_query(o.CANONICAL_REQUEST,'$.source' returning clob) SOURCE_JSON,m.MANIFEST_OPERATION_ID,s.SOURCE_KIND,s.SOURCE_DOC_ID,s.RAW_SHA256,s.DOCUMENT_REFERENCE,mv.MOVEMENT_ID BIRTH_MOVEMENT_ID
      from origins x join RRL_PALLETS p on p.UID_PALLET=x.ORIGIN_UID
      join RRL_STOCK_OPERATION o on o.OPERATION_ID=p.CREATED_BY_STOCK_OP and o.STATE='APPLIED'
      left join RRL_TRACE_MANIFEST_USE m on m.STOCK_OPERATION_ID=o.OPERATION_ID and m.UID_PALLET=p.UID_PALLET
      left join RRL_TRACE_SENDER_MANIFEST s on s.OPERATION_ID=m.MANIFEST_OPERATION_ID
      left join RRL_MES_MOVEMENT mv on mv.STOCK_OPERATION_ID=o.OPERATION_ID and mv.UID_PALLET=p.UID_PALLET and mv.MOVEMENT_TYPE='FG_PALLET_RELEASE'
      where o.COMMAND_TYPE in('SAP_RECEIPT','INVENTORY_REGISTER_LOT','MES_MOVEMENTS')
      order by p.UID_PALLET,o.OPERATION_ID fetch first 201 rows only""",lot_id=pallet)
    rows=cursor_rows(cur)
    for row in rows[:200]:
        original=read_oracle_json(row.pop("source_json"))
        row["source"]=original
        row["government_ack_verified"]=False
    return rows[:200],len(rows)>200
