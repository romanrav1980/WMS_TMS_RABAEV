"""Bounded destination worklist and receipts for the independent store application."""
from typing import Any
from ..contracts import StoreReceiptError
from ...platform.public import read_oracle_json
from ...inventory.public import normalize_pallet_scan_identifier
from .store_app_scope import STORES_SQL, selected_store
from .store_receipt_read import read_store_preview

ELIGIBLE = """select lf.LOAD_OPERATION_ID,lf.TT_ID TRIP_ID,
    coalesce(lf.ROOT_UID,'CASE:'||to_char(lf.ROOT_CASE_TASK_ID)) ROOT_KEY,
    lf.GROSS_WEIGHT_KG,lf.DEPARTED_AT,receipt.OPERATION_ID RECEIPT_OPERATION_ID,
    receipt.RECEIPT_STATE,lf.LOADED_AT SORT_AT
    from RRL_TT_HU_LOAD_FACT lf
    left join RRL_STORE_RECEIPT_FACT receipt on receipt.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
    where lf.STATUS='DEPARTED'
    and not exists(select 1 from RRL_INTERWARE_PLAN leg where leg.SOURCE_LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID)
    and exists(select 1 from RRL_TT_HU_LOAD_ST m where m.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
        and m.ACTIVE_FLAG=1 and m.DESTINATION_ADDR=:address)
    and not exists(select 1 from RRL_TT_HU_LOAD_ST m where m.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
        and m.ACTIVE_FLAG=1 and(m.DESTINATION_ADDR is null or m.DESTINATION_ADDR<>:address))
    and exists(select 1 from RRL_STOCK_OPERATION o where o.OPERATION_ID=lf.LOAD_OPERATION_ID and o.STATE='APPLIED')
    and exists(select 1 from RRL_STOCK_OPERATION o where o.OPERATION_ID=lf.DEPARTURE_OPERATION_ID and o.STATE='APPLIED')"""


class StoreAppReads:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def session(self, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Store application identity and stores READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("select NAME from RUSERS where ID=:actor and nvl(DELETED,0)=0", actor=actor)
            user = cur.fetchone()
            if user is None:
                raise StoreReceiptError("STORE_LOGIN_REQUIRED", "Требуется вход приёмщика", 401)
            cur.execute(STORES_SQL+" order by p.STORE_ADDR fetch first 201 rows only", actor=actor)
            rows = cur.fetchall()
            cur.execute("select REVISION from RRL_ACCESS_REV where ID=1")
            revision = cur.fetchone()[0]
        return {"username": actor, "display_name": user[0] or actor, "access_revision": revision,
                "stores": [{"address": r[0], "receipt_mode": r[1], "policy_version": r[2], "store_id": r[3]} for r in rows[:200]],
                "limit": 200, "has_more": len(rows)>200, "auth_scope": "STORE_RECEIPT"}

    def deliveries(self, actor: str, store: str, after: str, limit: int) -> dict[str, Any]:
        with self.gateway.transaction("Store destination deliveries READ ONLY") as cur:
            cur.execute("set transaction read only")
            own = selected_store(cur, actor, store)
            params = {"address": own["store_addr"], "after": after or None, "page_size": limit+1}
            if after:
                cur.execute("with eligible as("+ELIGIBLE+")select count(*)from eligible where LOAD_OPERATION_ID=:after",
                            address=params["address"], after=after)
                if cur.fetchone()[0]!=1:
                    raise StoreReceiptError("STORE_APP_CURSOR_SCOPE", "Курсор другой поставки или магазина", 422)
            cur.execute("with eligible as("+ELIGIBLE+""")select * from eligible e where :after is null or exists(
                select 1 from eligible a where a.LOAD_OPERATION_ID=:after
                and(e.SORT_AT>a.SORT_AT or(e.SORT_AT=a.SORT_AT and e.LOAD_OPERATION_ID>a.LOAD_OPERATION_ID)))
                order by SORT_AT,LOAD_OPERATION_ID fetch first :page_size rows only""", params)
            names = [column[0].lower() for column in cur.description]
            rows = [dict(zip(names,row)) for row in cur.fetchall()]
        items = [{k:v for k,v in row.items() if k!="sort_at"} for row in rows[:limit]]
        for item in items:
            item["time_status"] = "UNRESOLVED_SERVER_LOCAL"
        return {"store_id": store, "items": items, "limit": limit,
                "next_after": items[-1]["load_operation_id"] if len(rows)>limit else None}

    def lookup(self, actor: str, store: str, code: str) -> dict[str, Any]:
        with self.gateway.transaction("Resolve scanned final destination load READ ONLY") as cur:
            cur.execute("set transaction read only")
            own = selected_store(cur,actor,store)
            alias = normalize_pallet_scan_identifier(code)
            # Exact internal/legacy identifiers win; a GS1 alias is a fallback.
            for scanned in ((code,) if alias == code else (code, alias)):
                cur.execute("with eligible as("+ELIGIBLE+")select e.LOAD_OPERATION_ID,e.RECEIPT_OPERATION_ID from eligible e join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=e.LOAD_OPERATION_ID where e.ROOT_KEY=:scan or e.LOAD_OPERATION_ID=:scan or json_value(f.COMPOSITION_JSON,'$.nodes[0].sscc')=:scan or json_value(f.COMPOSITION_JSON,'$.root')=:scan order by case when e.RECEIPT_OPERATION_ID is null then 0 else 1 end,e.SORT_AT desc,e.LOAD_OPERATION_ID desc fetch first 2 rows only",
                            address=own["store_addr"],scan=scanned)
                rows=cur.fetchall()
                if rows:
                    break
        if not rows:
            raise StoreReceiptError("STORE_SCAN_NOT_FOUND","Код не найден в поставках этого магазина",404)
        if len(rows)!=1 and (rows[0][1] is not None or rows[1][1] is None):
            raise StoreReceiptError("STORE_SCAN_AMBIGUOUS","По этому коду несколько поставок. Выберите рейс в списке",409)
        return {"load_operation_id":rows[0][0],"store_id":store,"scanned_code":code}

    def preview(self, actor: str, store: str, load: str) -> dict[str, Any]:
        with self.gateway.transaction("Store application selected destination READ ONLY") as cur:
            cur.execute("set transaction read only")
            own = selected_store(cur, actor, store)
        return read_store_preview(self.gateway, load, own["store_addr"], actor)

    def receipt(self, actor: str, store: str, operation: str) -> dict[str, Any]:
        with self.gateway.transaction("Store application receipt READ ONLY") as cur:
            cur.execute("set transaction read only")
            own = selected_store(cur, actor, store)
            cur.execute("""select o.STATE,o.RESULT_JSON from RRL_STOCK_OPERATION o
                join RRL_STORE_RECEIPT_FACT f on f.OPERATION_ID=o.OPERATION_ID
                where o.OPERATION_ID=:operation and o.COMMAND_TYPE='STORE_RECEIPT'and f.STORE_ADDR=:address""",
                        operation=operation, address=own["store_addr"])
            row = cur.fetchone()
            return {"operation_id": operation, "state": row[0] if row else "NOT_VISIBLE",
                    "outcome_confirmed": bool(row and row[0]=="APPLIED"),
                    "result": read_oracle_json(row[1]) if row and row[1] else None}
