"""Receipt metadata staging only; quantities are posted by the stock coordinator."""
from datetime import date
from decimal import Decimal
from typing import Any
import json
import oracledb
from .receiving_marks import ReceivingMarks
from ..domain.regulatory_pallet import sscc_value

class ReceiptBooking:
    def _book_pallet(self, cur: oracledb.Cursor, order: tuple, line: tuple, payload: dict, marks: dict, placement: dict, actor: str, *, task_id: int | None = None, stock_quantity: Decimal | None = None, bindings: list | None = None, stock_base: str | None = None, receive_cell: str | None = None) -> int:
        sscc, qty, destination = payload['sscc'], Decimal(str(payload['quantity'])), placement['cell']
        expiry = date.fromisoformat(payload['expiry_date'])
        produced = date.fromisoformat(payload['produced_date']) if payload.get('produced_date') else None
        cur.execute('select ORDER_ID,LINE_NUMBER,PAYLOAD_JSON,STATUS from RRL_RECEIPT_LABEL where SSCC=:s for update', {'s': sscc})
        issued = cur.fetchone()
        if issued:
            details = json.loads(self._text(issued[2]))
            if issued[3]!='CONFIRMED' or issued[1]!=payload['line_number'] or details['article']!=line[0] or Decimal(str(details['quantity']))!=qty or details['batch']!=payload['supplier_batch'] or details['expiry']!=payload['expiry_date']:
                raise ValueError('Issued label must be confirmed and match actual pallet article, quantity, batch and expiry')
            cur.execute('select NAKLAD_ID from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i', {'i': issued[0]})
            if cur.fetchone()[0]!=order[0]:
                raise ValueError('Label belongs to another supply order')
        cur.callproc("RRL_SAP_RECEIPT_API.REGISTER_PALLET", [sscc, line[0], expiry, produced, stock_quantity if stock_quantity is not None else qty, order[0], actor])
        ReceivingMarks(cur).persist(sscc, marks, actor, bindings=bindings, base_uom=stock_base, cell=receive_cell)
        if task_id is None:
            cur.execute("select RRL_WAREHOUSE_TASK_SQ.nextval from dual")
            task_id = cur.fetchone()[0]
        cur.execute("""insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
          TARGET_ARTICUL,UID_PALLET,SSCC,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,UNIT_CODE,QTY_MODE,CREATED_BY,TO_CELL_SLOT_ID)
          values(:t,'PUTAWAY','SAP_RECEIPT','SAP_SUPPLY_ORDER',:n,:a,:p,:reg_sscc,:w,:f,:w,:dest,:q,:u,'PALLET',:actor,:slot)""",
                {"t": task_id, "n": order[0], "a": line[0], "p": sscc, "reg_sscc":sscc_value(sscc), "w": order[1], "f": order[2],
                 "dest": destination, "q": qty, "u": line[2], "actor": actor, "slot": placement["slot_id"]})
        cur.execute('update RRL_PALLETS set WEIGHT_BRUTTO=:weight,PRINTED=:printed where UID_PALLET=:p', {'p': sscc, 'weight': Decimal(str(payload['gross_weight'])) if payload.get('gross_weight') else None, 'printed': int(issued is not None)})
        if issued:
            cur.execute("update RRL_RECEIPT_LABEL set STATUS='USED' where SSCC=:s", {'s': sscc})
        if placement['slot_id'] is not None:
            cur.execute('insert into RRL_RECEIPT_SLOT_CLAIM(TASK_ID,UID_PALLET,CELL,CELL_SLOT_ID) values(:t,:p,:c,:slot)', {'t': task_id, 'p': sscc, 'c': destination, 'slot': placement['slot_id']})
        return task_id

    @staticmethod
    def _text(value: Any) -> str:
        return value.read() if hasattr(value,"read") else value
