"""SAP receipt worklist and detailed quantity proposal in one current warehouse snapshot."""
from decimal import Decimal, ROUND_CEILING
from typing import Any


def rows(cur: Any) -> list[dict[str, Any]]:
    names = [column[0].lower() for column in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def scope(cur: Any, actor: str) -> tuple[int | None, bool]:
    cur.execute("""select WARE_ID,case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'then 1 else 0 end
        from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'sap_supply_view')=1""", actor=actor)
    result = cur.fetchone()
    if result is None or (not result[1] and result[0] is None):
        raise PermissionError("SUPPLY_CURRENT_WARE_ACTOR_REQUIRED")
    return result[0], bool(result[1])


def allowed(ware: int | None, own: int | None, global_admin: bool) -> None:
    if ware is None or (not global_admin and ware != own):
        raise PermissionError("SUPPLY_CURRENT_WARE_FORBIDDEN")


def list_supplies(gateway: Any, warehouse: int | None, limit: int, actor: str) -> list[dict[str, Any]]:
    if not 1 <= limit <= 200:
        raise ValueError("SUPPLY_LIST_BOUND_200")
    with gateway.transaction("SAP supply worklist READ ONLY current scope") as cur:
        if not getattr(gateway,"transaction_bound",False):
            cur.execute("set transaction read only")
        own, global_admin = scope(cur, actor)
        if warehouse is not None:
            allowed(warehouse, own, global_admin)
        target = warehouse if warehouse is not None else None if global_admin else own
        cur.execute("""select s.ORDER_ID,s.ORDER_NUMBER,s.REVISION,s.WARE_ID,s.RECEIVE_CELL,s.NAKLAD_ID,
            h.CONDITION,h.DATE_OF_ACCEPT from RRL_SAP_SUPPLY_ORDER s
            join RRL_PRIHOD_NAKLAD h on h.ID=s.NAKLAD_ID
            where (:warehouse is null or s.WARE_ID=:warehouse)
            order by s.UPDATED_AT desc,s.ORDER_ID fetch first :page_limit rows only""",
            warehouse=target, page_limit=limit)
        return rows(cur)


def supply_detail(gateway: Any, order: str | None, document: int | None, actor: str) -> dict[str, Any]:
    with gateway.transaction("SAP source and pallet proposal READ ONLY current scope") as cur:
        if not getattr(gateway,"transaction_bound",False):
            cur.execute("set transaction read only")
        own, global_admin = scope(cur, actor)
        if document is not None:
            cur.execute("select ORDER_ID from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=:document_id", document_id=document)
            source = cur.fetchall()
            if not source:
                raise LookupError("Накладная не связана с разрешённой поставкой SAP")
            if len(source) != 1:
                raise ValueError("Неоднозначная связь накладной с заказом SAP")
            order = source[0][0]
        cur.execute("select s.*,h.CONDITION INCOMING_CONDITION from RRL_SAP_SUPPLY_ORDER s join RRL_PRIHOD_NAKLAD h on h.ID=s.NAKLAD_ID where s.ORDER_ID=:order_id", order_id=order)
        headers = rows(cur)
        if not headers:
            raise LookupError("Supply order not found")
        header = headers[0]
        allowed(header["ware_id"], own, global_admin)
        cur.execute("""select l.LINE_NUMBER,l.ROW_ID,l.ARTICUL,a.NAME,
            to_char(l.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,l.BASE_UOM,
            to_char(a.NORMA_UKLADKI,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') NORMA_UKLADKI,
            p.POLICY_VERSION,p.MARKING_REQUIRED,
            to_char(nvl((select sum(rec.POSTED_BASE_QTY)from RRL_SAP_PALLET_RECEIPT rec
              where rec.ORDER_ID=l.ORDER_ID and rec.LINE_NUMBER=l.LINE_NUMBER),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')ACCEPTED_QTY,
            (select count(*)from RRL_SAP_PALLET_RECEIPT rec where rec.ORDER_ID=l.ORDER_ID and rec.LINE_NUMBER=l.LINE_NUMBER
              and(rec.POSTED_BASE_QTY is null or rec.STOCK_BASE_UOM is null or rec.STOCK_BASE_UOM!=l.BASE_UOM))INVALID_RECEIPT_ROWS
            from RRL_SAP_SUPPLY_LINE l join RRL_ARTICULS a on a.ACTICUL=l.ARTICUL
            left join RRL_SKU_RECEIPT_POLICY p on p.ARTICUL=l.ARTICUL
            where l.ORDER_ID=:order_id order by l.LINE_NUMBER fetch first 1001 rows only""",
            order_id=order)
        lines = rows(cur)
        if len(lines) > 1000:
            raise ValueError("SUPPLY_LINE_BOUND_1000")
        for line in lines:
            if line.pop("invalid_receipt_rows",0):
                raise ValueError("RECEIPT_POSTED_BASE_UNIT_RECONCILIATION_REQUIRED")
            remaining = max(Decimal(0), Decimal(line["planned_qty"]) - Decimal(line["accepted_qty"]))
            norm = Decimal(line["norma_ukladki"] or "0")
            line["remaining_qty"] = str(remaining)
            count = int((remaining / norm).to_integral_value(rounding=ROUND_CEILING)) if norm > 0 else None
            line["suggested_pallet_count"] = count
            line["suggested_pallet_quantity"] = str(min(norm, remaining)) if norm > 0 else None
            line["last_pallet_quantity"] = str(remaining - norm * (count - 1)) if count else "0" if count == 0 else None
        header["receipt_allowed"] = header["incoming_condition"] == 0 and header.get("closed_at") is None
        header["receipt_state"] = "REVERSED" if header["incoming_condition"] == 3 else "RECONCILED" if header.get("closed_at") is not None else "OPEN" if header["incoming_condition"] == 0 else "COMPLETE" if header["incoming_condition"] == 1 else "LEGACY_CLOSED"
        header["lines"] = lines
        header["consistent_snapshot"] = True
        return header

def pallet_plan(gateway: Any, order: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    from hashlib import sha256
    import json
    from ...inventory.public import propose_receipt_layout
    source = supply_detail(gateway, order, None, actor)
    lines = [line for line in source["lines"] if line["line_number"] == body["line_number"]]
    if len(lines) != 1:
        raise ValueError("RECEIPT_LAYOUT_CURRENT_LINE_REQUIRED")
    line = lines[0]
    signature = sha256(json.dumps([source["order_id"], source["revision"], source["ware_id"],
        line["line_number"], line["planned_qty"], line["accepted_qty"], line["norma_ukladki"]],
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    if body.get("expected_source_signature") is not None and body["expected_source_signature"] != signature:
        raise ValueError("RECEIPT_LAYOUT_SOURCE_CHANGED")
    proposal = propose_receipt_layout(line["remaining_qty"], line["base_uom"], line["norma_ukladki"],
        body.get("pallet_count"), body.get("quantities"), body.get("quantity_step"))
    return {"order_id": order, "revision": source["revision"], "warehouse_id": source["ware_id"],
            "line_number": line["line_number"], "source_signature": signature,
            "remaining_quantity": line["remaining_qty"], "consistent_snapshot": True,
            "read_only": True, **proposal}
