from typing import Any
"""SAP supply plans reuse legacy incoming headers/rows; never book inventory."""
import json
from decimal import Decimal
from uuid import uuid4
from hashlib import sha256

import oracledb

from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..application.ingestion import IdocConflict
from ..domain.supply_order import read_supply_order
from .supply_amendments import SupplyAmendments
from .supply_scope import supply_transaction,assert_supply_scope


class SupplyOrders:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, raw: bytes, actor: str) -> dict:
        for attempt in range(2):
            try:
                return self._receive(raw, actor)
            except oracledb.DatabaseError as exc:
                if "SUPPLY_SOURCE_REPLAN_REQUIRED" not in str(exc):
                    raise
                if attempt == 1:
                    raise IdocConflict("Supply source changed; repeat the same XML") from exc
        raise RuntimeError("Unreachable supply retry")

    def _receive(self, raw: bytes, actor: str) -> dict:
        order = read_supply_order(raw)
        with supply_transaction(self.gateway,actor,order["warehouse_id"],order["sender"],order["order_number"],order["message_id"]) as cur:
            assert_supply_scope(cur,actor,order["warehouse_id"])
            cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_SAP_SUPPLY_MESSAGE where SENDER=:s and MESSAGE_ID=:m",
                        {"s": order["sender"], "m": order["message_id"]})
            old_message = cur.fetchone()
            if old_message:
                if old_message[0] != order["payload_hash"]:
                    raise IdocConflict("Supply MessageId already has a different payload")
                result = read_oracle_json(old_message[1])
                return {**result, "idempotent": True}
            self._destination(cur, order)
            cur.execute("select ORDER_ID,NAKLAD_ID,REVISION,PAYLOAD_HASH,WARE_ID from RRL_SAP_SUPPLY_ORDER where SENDER=:s and ORDER_NUMBER=:n for update wait 3",
                        {"s": order["sender"], "n": order["order_number"]})
            old = cur.fetchone()
            if old:
                assert_supply_scope(cur,actor,old[4])
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
              when matched then update set REVISION=:r,PAYLOAD_HASH=:h,WARE_ID=:w,RECEIVE_CELL=:c,UPDATED_AT=systimestamp,GATEWAY_CONTRACT_VERSION=:cv
              when not matched then insert(ORDER_ID,SENDER,ORDER_NUMBER,NAKLAD_ID,REVISION,PAYLOAD_HASH,WARE_ID,RECEIVE_CELL,GATEWAY_CONTRACT_VERSION)
                values(:i,:sender,:n,:legacy,:r,:h,:w,:c,:cv)""",
                        {"i": order_id, "sender": order["sender"], "n": order["order_number"], "legacy": naklad_id,
                         "r": order["revision"], "h": order["payload_hash"], "cv": order["gateway_contract_version"], "w": order["warehouse_id"], "c": order["receive_cell"]})
            self._lines(cur, order_id, naklad_id, order["lines"], previous_lines,order["sender"])
            SupplyAmendments(cur).refresh_header(order_id, naklad_id)
            for aggregate in order["aggregations"]:
                cur.execute('select UNITS_JSON,LINE_NUMBER,AGG_LEVEL from RRL_SAP_TRACE_AGG where ORDER_ID=:o and SYSTEM_CODE=:s and PROFILE_CODE=:p and CODE_HASH=:h', {'o': order_id, 's': aggregate['system'], 'p': aggregate['profile'], 'h': sha256(aggregate['code'].encode()).hexdigest()})
                known = cur.fetchone()
                if known:
                    if read_oracle_json(known[0]) != aggregate['units'] or known[1:] != (aggregate['line_number'], aggregate['level']):
                        raise IdocConflict('Aggregation identity cannot change its composition')
                    continue
                cur.setinputsizes(units=oracledb.DB_TYPE_CLOB, code_raw=oracledb.DB_TYPE_CLOB)
                cur.execute("insert into RRL_SAP_TRACE_AGG(ORDER_ID,LINE_NUMBER,SYSTEM_CODE,PROFILE_CODE,CODE_HASH,AGG_LEVEL,RAW_CODE,UNITS_JSON) values(:o,:l,:s,:p,:h,:agg_level,:code_raw,:units)",
                            {"o": order_id, "l": aggregate["line_number"], "s": aggregate["system"], "p": aggregate["profile"],
                             "h": sha256(aggregate["code"].encode()).hexdigest(), "agg_level": aggregate["level"],
                             "code_raw": aggregate["code"], "units": json.dumps(aggregate["units"], ensure_ascii=False)})
            result = {"status": "APPLIED", "order_id": order_id, "incoming_document_id": naklad_id,
                      "revision": order["revision"], "warehouse_id": order["warehouse_id"], "gateway_contract_version": order["gateway_contract_version"],
                      "lines": len(order["lines"]), "inventory_booked": False, "idempotent": False}
            cur.setinputsizes(xml_raw=oracledb.DB_TYPE_CLOB, result=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_SAP_SUPPLY_MESSAGE(SENDER,MESSAGE_ID,ORDER_ID,PAYLOAD_HASH,RAW_XML,RESULT_JSON,RECEIVED_BY) values(:s,:m,:i,:h,:xml_raw,:result,:actor)",
                        {"s": order["sender"], "m": order["message_id"], "i": order_id, "h": order["payload_hash"],
                         "xml_raw": order["raw_xml"], "result": json.dumps(result, default=str), "actor": actor})
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

    def _lines(self, cur: oracledb.Cursor, order_id: str, naklad_id: int, lines: list[dict], previous: dict,sender: str) -> None:
        from .supply_line_writer import SupplyLineWriter
        SupplyLineWriter(cur).write(order_id,naklad_id,lines,previous,sender)

    @staticmethod
    def _text(value: Any) -> str:
        return value.read() if hasattr(value, "read") else value

    def list(self, warehouse_id: int | None, limit: int, actor: str) -> list[dict]:
        from .supply_reads import list_supplies
        return list_supplies(self.gateway, warehouse_id, limit, actor)

    def by_receipt_document(self, document_id: int, actor: str) -> dict:
        from .supply_reads import supply_detail
        return supply_detail(self.gateway, None, document_id, actor)

    def get(self, order_id: str, actor: str) -> dict:
        from .supply_reads import supply_detail
        return supply_detail(self.gateway, order_id, None, actor)

    def receipt_history(self, order_id: str, limit: int, after: str | None, actor: str) -> dict:
        from .supply_receipt_history import receipt_history
        return receipt_history(self.gateway,order_id,limit,after,actor)

    def pallet_plan(self, order_id: str, body: dict[str, Any], actor: str) -> dict:
        from .supply_reads import pallet_plan
        return pallet_plan(self.gateway, order_id, body, actor)

