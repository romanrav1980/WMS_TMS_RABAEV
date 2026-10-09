"""SAP supply plans reuse legacy incoming headers/rows; never book inventory."""
import json
from decimal import Decimal
from uuid import uuid4
from hashlib import sha256

import oracledb

from ....oracle_gateway import OracleGateway
from ..application.ingestion import IdocConflict
from ..domain.supply_order import read_supply_order
from .supply_amendments import SupplyAmendments


class SupplyOrders:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, raw: bytes, actor: str) -> dict:
        order = read_supply_order(raw)
        with self.gateway.transaction("NI01 SAP warehouse supply order") as cur:
            # Legacy headers have no source identity constraint. Serialize source mapping only.
            cur.execute("lock table RRL_SAP_SUPPLY_ORDER in share row exclusive mode")
            cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_SAP_SUPPLY_MESSAGE where SENDER=:s and MESSAGE_ID=:m",
                        {"s": order["sender"], "m": order["message_id"]})
            old_message = cur.fetchone()
            if old_message:
                if old_message[0] != order["payload_hash"]:
                    raise IdocConflict("Supply MessageId already has a different payload")
                result = json.loads(self._text(old_message[1]))
                return {**result, "idempotent": True}
            self._destination(cur, order)
            cur.execute("select ORDER_ID,NAKLAD_ID,REVISION,PAYLOAD_HASH from RRL_SAP_SUPPLY_ORDER where SENDER=:s and ORDER_NUMBER=:n for update",
                        {"s": order["sender"], "n": order["order_number"]})
            old = cur.fetchone()
            if old and order["revision"] <= old[2]:
                raise IdocConflict("Supply revision must increase; repeat the original MessageId to retry")
            if old:
                order_id, naklad_id = old[:2]
                previous_lines = SupplyAmendments(cur).prepare(order_id, naklad_id, order)
            else:
                previous_lines = {}
                order_id = uuid4().hex
                cur.execute("select RRL_PRIHOD_NAKLAD_SQ.nextval from dual")
                naklad_id = cur.fetchone()[0]
                cur.execute("insert into RRL_PRIHOD_NAKLAD (ID,NAKLAD_NUMBER,ZAKAZ_NUMBER,DATE_OF_NAKLAD,WARE_ID,POSTAVSHIK_NAME,CONDITION) values(:i,:n,:n,sysdate,:w,:s,0)",
                            {"i": naklad_id, "n": order["order_number"], "w": order["warehouse_id"], "s": order["supplier"]})
            cur.execute("update RRL_PRIHOD_NAKLAD set WARE_ID=:w,POSTAVSHIK_NAME=:s where ID=:n",
                        {"n": naklad_id, "w": order["warehouse_id"], "s": order["supplier"]})
            cur.execute("""merge into RRL_SAP_SUPPLY_ORDER d using(select :i ORDER_ID from dual)s on(d.ORDER_ID=s.ORDER_ID)
              when matched then update set REVISION=:r,PAYLOAD_HASH=:h,WARE_ID=:w,RECEIVE_CELL=:c,UPDATED_AT=systimestamp
              when not matched then insert(ORDER_ID,SENDER,ORDER_NUMBER,NAKLAD_ID,REVISION,PAYLOAD_HASH,WARE_ID,RECEIVE_CELL)
                values(:i,:sender,:n,:legacy,:r,:h,:w,:c)""",
                        {"i": order_id, "sender": order["sender"], "n": order["order_number"], "legacy": naklad_id,
                         "r": order["revision"], "h": order["payload_hash"], "w": order["warehouse_id"], "c": order["receive_cell"]})
            self._lines(cur, order_id, naklad_id, order["lines"], previous_lines)
            SupplyAmendments(cur).refresh_header(order_id, naklad_id)
            for aggregate in order["aggregations"]:
                cur.execute('select UNITS_JSON,LINE_NUMBER,AGG_LEVEL from RRL_SAP_TRACE_AGG where ORDER_ID=:o and SYSTEM_CODE=:s and PROFILE_CODE=:p and CODE_HASH=:h', {'o': order_id, 's': aggregate['system'], 'p': aggregate['profile'], 'h': sha256(aggregate['code'].encode()).hexdigest()})
                known = cur.fetchone()
                if known:
                    if json.loads(self._text(known[0])) != aggregate['units'] or known[1:] != (aggregate['line_number'], aggregate['level']):
                        raise IdocConflict('Aggregation identity cannot change its composition')
                    continue
                cur.setinputsizes(units=oracledb.DB_TYPE_CLOB, raw=oracledb.DB_TYPE_CLOB)
                cur.execute("insert into RRL_SAP_TRACE_AGG(ORDER_ID,LINE_NUMBER,SYSTEM_CODE,PROFILE_CODE,CODE_HASH,AGG_LEVEL,RAW_CODE,UNITS_JSON) values(:o,:l,:s,:p,:h,:level,:raw,:units)",
                            {"o": order_id, "l": aggregate["line_number"], "s": aggregate["system"], "p": aggregate["profile"],
                             "h": sha256(aggregate["code"].encode()).hexdigest(), "level": aggregate["level"],
                             "raw": aggregate["code"], "units": json.dumps(aggregate["units"], ensure_ascii=False)})
            result = {"status": "APPLIED", "order_id": order_id, "incoming_document_id": naklad_id,
                      "revision": order["revision"], "warehouse_id": order["warehouse_id"],
                      "lines": len(order["lines"]), "inventory_booked": False, "idempotent": False}
            cur.setinputsizes(raw=oracledb.DB_TYPE_CLOB, result=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_SAP_SUPPLY_MESSAGE(SENDER,MESSAGE_ID,ORDER_ID,PAYLOAD_HASH,RAW_XML,RESULT_JSON,RECEIVED_BY) values(:s,:m,:i,:h,:raw,:result,:actor)",
                        {"s": order["sender"], "m": order["message_id"], "i": order_id, "h": order["payload_hash"],
                         "raw": order["raw_xml"], "result": json.dumps(result, default=str), "actor": actor})
        return result

    def _destination(self, cur: oracledb.Cursor, order: dict) -> None:
        cur.execute("select ID,DEFAULT_RECEIVE_CELL from RRL_WARES where ID=:w", {"w": order["warehouse_id"]})
        warehouses = cur.fetchall()
        if len(warehouses) != 1:
            raise ValueError("Warehouse recipient does not identify exactly one WMS warehouse")
        if not warehouses[0][1] or warehouses[0][1] != order["receive_cell"]:
            raise ValueError("ReceiveCell must match configured warehouse receiving zone")
        cur.execute("select CELL from RRL_CELLS where CELL=:c and WARE_ID=:w and nvl(BLOCKED_FOR_ACCEPT,0)=0",
                    {"c": order["receive_cell"], "w": order["warehouse_id"]})
        if len(cur.fetchall()) != 1:
            raise ValueError("Receiving cell must belong to recipient warehouse and allow receipt")

    def _lines(self, cur: oracledb.Cursor, order_id: str, naklad_id: int, lines: list[dict], previous: dict) -> None:
        for line in lines:
            cur.execute("select BASE_UOM,UNITS_JSON,SENDER from RRL_SAP_ARTICLE_META where ARTICUL=:a", {"a": line["material"]})
            master = cur.fetchone()
            if not master:
                raise ValueError(f"Import article via ARTMAS first: {line['material']}")
            cur.execute("select ACTICUL from RRL_ARTICULS where ACTICUL=:a", {"a": line["material"]})
            if len(cur.fetchall()) != 1:
                raise ValueError("Article missing or ambiguous in legacy master")
            units = json.loads(self._text(master[1]))
            ratios = [Decimal(u["ratio"]) for u in units if u["uom"] == line["unit"]]
            if line["unit"] == master[0]:
                ratio = Decimal(1)
            elif len(ratios) == 1:
                ratio = ratios[0]
            else:
                raise ValueError("Supply UoM has no unique SAP conversion")
            quantity = Decimal(line["quantity"]) * ratio
            if quantity > Decimal("999999999999") or quantity.as_tuple().exponent < -6:
                raise ValueError("Converted quantity exceeds WMS precision")
            SupplyAmendments(cur).validate_quantity(naklad_id, line["material"], quantity)
            old = previous.get(line['line_number'])
            if old and old[2] != master[0]:
                raise IdocConflict('Base unit of an existing line is immutable')
            if old:
                row_id = old[1]
                cur.execute('update RRL_PRIHOD_NAKLAD_ROWS set COUNT1=:q where ID=:r', {'q': quantity, 'r': row_id})
                cur.execute('update RRL_SAP_SUPPLY_LINE set PLANNED_QTY=:q,SOURCE_QTY=:sq,SOURCE_UOM=:su where ORDER_ID=:o and LINE_NUMBER=:l', {'q': quantity, 'sq': Decimal(line['quantity']), 'su': line['unit'], 'o': order_id, 'l': line['line_number']})
            else:
                cur.execute("select RRL_PRIHOD_NAKLAD_ROWS_SQ.nextval from dual")
                row_id = cur.fetchone()[0]
                cur.execute("insert into RRL_PRIHOD_NAKLAD_ROWS(ID,ORDID,ARTICUL,COUNT1) values(:i,:n,:a,:q)",
                            {"i": row_id, "n": naklad_id, "a": line["material"], "q": quantity})
                cur.execute("insert into RRL_SAP_SUPPLY_LINE(ORDER_ID,LINE_NUMBER,ROW_ID,ARTICUL,PLANNED_QTY,BASE_UOM,SOURCE_QTY,SOURCE_UOM) values(:o,:l,:r,:a,:q,:u,:sq,:su)",
                            {"o": order_id, "l": line["line_number"], "r": row_id, "a": line["material"],
                             "q": quantity, "u": master[0], "sq": Decimal(line["quantity"]), "su": line["unit"]})

    @staticmethod
    def _text(value) -> str:
        return value.read() if hasattr(value, "read") else value

    def list(self, warehouse_id: int | None, limit: int = 100) -> list[dict]:
        return self.gateway.fetch_all("""select s.ORDER_ID,s.ORDER_NUMBER,s.REVISION,s.WARE_ID,s.RECEIVE_CELL,s.NAKLAD_ID,
          h.CONDITION,h.DATE_OF_ACCEPT from RRL_SAP_SUPPLY_ORDER s join RRL_PRIHOD_NAKLAD h on h.ID=s.NAKLAD_ID
          where (:w is null or s.WARE_ID=:w) order by s.UPDATED_AT desc fetch first :lim rows only""",
                                      {"w": warehouse_id, "lim": limit})

    def by_receipt_document(self, document_id: int) -> dict:
        rows = self.gateway.fetch_all(
            "select ORDER_ID from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=:i",
            {"i": document_id})
        if not rows:
            raise LookupError("Накладная не связана с разрешённой поставкой SAP")
        if len(rows) != 1:
            raise ValueError("Неоднозначная связь накладной с заказом SAP")
        return self.get(rows[0]["order_id"])

    def get(self, order_id: str) -> dict:
        rows = self.gateway.fetch_all("select * from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i", {"i": order_id})
        if not rows:
            raise LookupError("Supply order not found")
        # Accepted quantity is read from existing pallets, not a second inventory balance.
        rows[0]["lines"] = self.gateway.fetch_all("""select l.LINE_NUMBER,l.ROW_ID,l.ARTICUL,a.NAME,
          to_char(l.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,l.BASE_UOM,
          to_char(a.NORMA_UKLADKI,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') NORMA_UKLADKI,P.POLICY_VERSION,P.MARKING_REQUIRED,
          to_char(nvl((select sum(UNIT_COUNT) from RRL_PALLETS where PRIHOD_NAKLAD_ID=:n and ARTICUL=l.ARTICUL),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ACCEPTED_QTY
          from RRL_SAP_SUPPLY_LINE l join RRL_ARTICULS a on a.ACTICUL=l.ARTICUL
          left join RRL_SKU_RECEIPT_POLICY p on p.ARTICUL=l.ARTICUL where l.ORDER_ID=:i order by l.LINE_NUMBER""",
                                                     {"i": order_id, "n": rows[0]["naklad_id"]})
        for line in rows[0]["lines"]:
            remaining = max(Decimal(0), Decimal(str(line["planned_qty"])) - Decimal(str(line["accepted_qty"])))
            norm = Decimal(str(line["norma_ukladki"] or 0))
            line["remaining_qty"] = str(remaining)
            if norm > 0:
                from decimal import ROUND_CEILING
                count = int((remaining / norm).to_integral_value(rounding=ROUND_CEILING))
                line["suggested_pallet_count"] = count
                line["suggested_pallet_quantity"] = str(min(norm, remaining))
                line["last_pallet_quantity"] = str(remaining - norm * (count - 1)) if count else "0"
            else:
                line["suggested_pallet_count"] = None
                line["suggested_pallet_quantity"] = None
                line["last_pallet_quantity"] = None
        return rows[0]
