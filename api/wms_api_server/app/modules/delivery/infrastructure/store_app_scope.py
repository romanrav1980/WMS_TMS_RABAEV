"""A native STORE assignment or the explicit legacy receiver binding, never a trip-wide grant."""
from typing import Any
from ..contracts import StoreReceiptError

STORE_KEY = "lower(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p.STORE_ADDR,'AL32UTF8'),4)))"
STORE_ALLOWED = """(RRL_ACCESS_API.allowed(:actor,'store_receipt_confirm','STORE',STORE_ID)=1
    or(RRL_HAS_WRIGHT(:actor,'store_receipt_confirm')=1 and exists(
    select 1 from RRL_STORE_RECEIPT_USER b where b.USER_ID=:actor and b.STORE_ADDR=p.STORE_ADDR)))"""
STORES_SQL = """select p.* from(select p.STORE_ADDR,p.RECEIPT_MODE,p.POLICY_VERSION,"""+STORE_KEY+""" STORE_ID
    from RRL_STORE_RECEIPT_POLICY p) p where exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0) and """+STORE_ALLOWED


def selected_store(cur: Any, actor: str, store: str) -> dict[str, Any]:
    cur.execute(STORES_SQL+" and STORE_ID=:store", actor=actor, store=store)
    row = cur.fetchone()
    if row is None:
        raise StoreReceiptError("STORE_APP_SCOPE_DENIED", "Магазин отсутствует или недоступен", 403)
    names = [c[0].lower() for c in cur.description]
    return dict(zip(names, row))
