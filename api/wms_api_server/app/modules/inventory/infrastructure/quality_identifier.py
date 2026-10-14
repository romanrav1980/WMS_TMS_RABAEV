"""Resolve physical CASE labels to the existing logical QC source, read-only."""
import oracledb
from ..contracts_stock import StockPostingError

def quality_identifier(cur: oracledb.Cursor, value: str, actor: str) -> str:
    cur.execute("""select 1 from RUSERS u where u.ID=:a and nvl(u.DELETED,0)=0
        and (RRL_HAS_WRIGHT(:a,'outgoing_pallet_check')=1
        or RRL_HAS_WRIGHT(:a,'stock_posting_shipping')=1
        or RRL_HAS_WRIGHT(:a,'CLOSE_OTHOD_NAKLAD')=1)""", a=actor)
    if cur.fetchone() is None:
        raise StockPostingError("OUTGOING_QC_FORBIDDEN", "", 20882)
    case_id = None
    if value.startswith("CASE:") and value[5:].isdigit() and len(value[5:]) <= 18:
        case_id = int(value[5:])
    cur.execute("""select distinct PALLET_UID from (
        select s.PALLET_UID from RRL_SBORKA_PALLETS s where s.PALLET_UID=:p_code
        union all select s.PALLET_UID from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s
        on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.SSCC=:p_code
        union all select s.PALLET_UID from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s
        on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.CASE_PICK_TASK_ID=:p_case)
        fetch first 3 rows only""", p_code=value, p_case=case_id)
    identifiers = [r[0] for r in cur.fetchall()]
    if not identifiers:
        # Preserve the native current-source/actor denial contract.
        cur.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier", [value, actor])
        return value
    for identifier in identifiers:
        cur.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier", [identifier, actor])
    if len(identifiers) != 1:
        raise StockPostingError("OUTGOING_QC_IDENTIFIER_AMBIGUOUS", "", 20886)
    return identifiers[0]
