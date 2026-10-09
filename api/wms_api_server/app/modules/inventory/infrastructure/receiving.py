"""Atomic physical receipt and putaway on existing pallet/event/task tables."""
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json

import oracledb

from ....oracle_gateway import OracleGateway
from .receiving_marks import ReceivingMarks
from .placement import ReceiptPlacement
from .metadata_transactions import receipt_task_metadata
from ..domain.pallet_identifiers import normalize_incoming_sscc


class Receiving:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, order_id: str, payload: dict, actor: str) -> dict:
        from .receipt_commands import receive_command
        posted = receive_command(self.gateway, order_id, payload, actor)
        if posted is not None:
            return posted
        canonical = json.dumps({"order_id": order_id, **payload}, sort_keys=True, ensure_ascii=False)
        digest = sha256(canonical.encode()).hexdigest()
        sscc = payload["sscc"]
        check = (10 - sum(int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(sscc[:17]))) % 10) % 10
        if check != int(sscc[-1]):
            raise ValueError("Invalid SSCC check digit")
        expiry = date.fromisoformat(payload["expiry_date"])
        produced = date.fromisoformat(payload["produced_date"]) if payload.get("produced_date") else None
        qty = Decimal(str(payload["quantity"]))
        with self.gateway.transaction("NI01 confirm incoming pallet and create putaway") as cur:
            # Order lock serializes its remaining quantity, retries and amendments.
            cur.execute("select NAKLAD_ID,WARE_ID,RECEIVE_CELL,ORDER_NUMBER,SENDER,REVISION from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i for update", {"i": order_id})
            order = cur.fetchone()
            if not order:
                raise LookupError("SAP supply order not found")
            cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_SAP_PALLET_RECEIPT where OPERATION_ID=:op", {"op": payload["operation_id"]})
            previous = cur.fetchone()
            if previous:
                if previous[0] != digest:
                    raise ValueError("Receipt operation already has a different payload")
                return {**json.loads(self._text(previous[1])), "idempotent": True}
            if expiry < date.today() or (produced and (produced > date.today() or produced > expiry)):
                raise ValueError("Invalid production or expiry date")
            cur.execute("select CONDITION from RRL_PRIHOD_NAKLAD where ID=:n for update", {"n": order[0]})
            header = cur.fetchone()
            if not header or (header[0] or 0) != 0:
                raise ValueError("Incoming document is closed")
            cur.execute("select ARTICUL,to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),BASE_UOM from RRL_SAP_SUPPLY_LINE where ORDER_ID=:i and LINE_NUMBER=:l",
                        {"i": order_id, "l": payload["line_number"]})
            line = cur.fetchone()
            if not line:
                raise LookupError("SAP order line not found")
            marks = ReceivingMarks(cur).resolve(order_id, line[0], payload["line_number"], qty, payload, line[2])
            cur.execute("select to_char(nvl(sum(UNIT_COUNT),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_PALLETS where PRIHOD_NAKLAD_ID=:n and ARTICUL=:a",
                        {"n": order[0], "a": line[0]})
            if Decimal(str(cur.fetchone()[0])) + qty > Decimal(str(line[1])):
                raise ValueError("Pallet quantity exceeds remaining SAP order quantity")
            # Serialize pallet identity and empty-cell claims across receiving orders.
            cur.execute("lock table RRL_SAP_PALLET_RECEIPT in share row exclusive mode")
            cur.execute("select PAYLOAD_HASH from RRL_SAP_PALLET_RECEIPT where OPERATION_ID=:op", {"op": payload["operation_id"]})
            if cur.fetchone():
                raise ValueError("Receipt operation identifier is already used by another order")
            cur.execute("select count(*) from RRL_PALLETS where UID_PALLET=:p or SSCC=:p", {"p": sscc})
            if cur.fetchone()[0]:
                raise ValueError("Pallet identifier/SSCC already exists")
            placement = ReceiptPlacement(cur).choose(order[1], order[2], line[0], payload)
            destination = placement['cell']
            cur.execute("select CELL from RRL_CELLS where CELL=:c and WARE_ID=:w and nvl(BLOCKED_FOR_ACCEPT,0)=0 for update",
                        {"c": order[2], "w": order[1]})
            if len(cur.fetchall()) != 1:
                raise ValueError("Receiving cell unavailable")
            task_id = self._book_pallet(cur, order, line, payload, marks, placement, actor)
            result = {"status": "RECEIVED", "pallet_identifier": sscc, "sscc": sscc, "quantity": str(qty),
                      "sap_order_number": order[3], "sap_sender": order[4], "order_revision": order[5],
                      "line_number": payload["line_number"], "material": line[0], "unit": line[2],
                      "supplier_batch": payload["supplier_batch"], "expiry_date": payload["expiry_date"],
                      "produced_date": payload.get("produced_date"), "warehouse_id": order[1],
                      "physical_measurements": {k: payload.get(k) for k in ("gross_weight", "pallet_height", "pallet_height_m", "volume_m3")},
                      "receive_cell": order[2], "putaway_cell": destination, "task_id": task_id, "placement": placement,
                      "marking_units": len(marks["units"]), "marking_policy_version": marks["policy_version"],
                      "marking_aggregations": [{"system": a["system"], "profile": a["profile"], "version": a["version"],
                         "level": a["level"], "code_hash": sha256(a["code"].encode()).hexdigest()} for a in marks["scanned"]],
                      "regulatory_validation": "NOT_PERFORMED" if marks["units"] else "NOT_APPLICABLE", "idempotent": False}
            cur.setinputsizes(result=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_SAP_PALLET_RECEIPT(OPERATION_ID,ORDER_ID,LINE_NUMBER,UID_PALLET,SUPPLIER_BATCH,PAYLOAD_HASH,RESULT_JSON,RECEIVED_BY) values(:op,:o,:l,:p,:b,:h,:result,:actor)",
                        {"op": payload["operation_id"], "o": order_id, "l": payload["line_number"], "p": sscc,
                         "b": payload["supplier_batch"], "h": digest, "result": json.dumps(result), "actor": actor})
            self._outbox(cur, payload["operation_id"], "PALLET_RECEIVED", result)
            cur.execute("""select count(*) from RRL_SAP_SUPPLY_LINE l where l.ORDER_ID=:i
              and l.PLANNED_QTY>(select nvl(sum(p.UNIT_COUNT),0) from RRL_PALLETS p
                where p.PRIHOD_NAKLAD_ID=:n and p.ARTICUL=l.ARTICUL)""", {"i": order_id, "n": order[0]})
            if cur.fetchone()[0] == 0:
                cur.execute("update RRL_PRIHOD_NAKLAD set CONDITION=1,DATE_OF_ACCEPT=sysdate where ID=:n", {"n": order[0]})
        return result

    def _book_pallet(self, cur: oracledb.Cursor, order: tuple, line: tuple, payload: dict, marks: dict, placement: dict, actor: str, *, task_id: int | None = None, stock_quantity: Decimal | None = None, emit_event: bool = True, bindings: list | None = None, stock_base: str | None = None, receive_cell: str | None = None) -> int:
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
        if emit_event:
            self._event(cur, sscc, qty, order[0], None, order[2], 1, actor)
        if task_id is None:
            cur.execute("select RRL_WAREHOUSE_TASK_SQ.nextval from dual")
            task_id = cur.fetchone()[0]
        cur.execute("""insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
          TARGET_ARTICUL,UID_PALLET,SSCC,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,UNIT_CODE,QTY_MODE,CREATED_BY,TO_CELL_SLOT_ID)
          values(:t,'PUTAWAY','SAP_RECEIPT','SAP_SUPPLY_ORDER',:n,:a,:p,:p,:w,:f,:w,:dest,:q,:u,'PALLET',:actor,:slot)""",
                {"t": task_id, "n": order[0], "a": line[0], "p": sscc, "w": order[1], "f": order[2],
                 "dest": destination, "q": qty, "u": line[2], "actor": actor, "slot": placement["slot_id"]})
        cur.execute('update RRL_PALLETS set WEIGHT_BRUTTO=:weight,PRINTED=:printed where UID_PALLET=:p', {'p': sscc, 'weight': Decimal(str(payload['gross_weight'])) if payload.get('gross_weight') else None, 'printed': int(issued is not None)})
        if issued:
            cur.execute("update RRL_RECEIPT_LABEL set STATUS='USED' where SSCC=:s", {'s': sscc})
        if placement['slot_id'] is not None:
            cur.execute('insert into RRL_RECEIPT_SLOT_CLAIM(TASK_ID,UID_PALLET,CELL,CELL_SLOT_ID) values(:t,:p,:c,:slot)', {'t': task_id, 'p': sscc, 'c': destination, 'slot': placement['slot_id']})
        return task_id

    def complete(self, task_id: int, scans: dict, actor: str) -> dict:
        rows = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if not rows or rows[0]["state"] != "PREPARED":
            from .task_completion import complete_existing_task
            from ....schemas import WarehouseTaskStatusRequest
            return complete_existing_task(self.gateway, task_id, WarehouseTaskStatusRequest(**scans), actor)
        scans = {**scans, "scanned_pallet": normalize_incoming_sscc(scans.get("scanned_pallet"))}
        with self.gateway.transaction("NI01 confirm full pallet putaway") as cur:
            cur.execute("select UID_PALLET,FROM_CELL,TO_CELL,to_char(QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),STATUS,SOURCE_DOC_ID,TASK_SOURCE,TO_WARE_ID,TO_CELL_SLOT_ID from RRL_WAREHOUSE_TASK where TASK_ID=:t for update", {"t": task_id})
            task = cur.fetchone()
            if not task or task[6] != "SAP_RECEIPT":
                raise LookupError("SAP receiving putaway task not found")
            if tuple(scans.get(k) for k in ("scanned_pallet", "scanned_from_cell", "scanned_to_cell")) != task[:3]:
                raise ValueError("Scan the assigned pallet, receiving cell and destination")
            if task[4] == "DONE":
                return {"task_id": task_id, "status": "DONE", "idempotent": True}
            if task[4] not in {"PLANNED", "ASSIGNED", "IN_PROGRESS"}:
                raise ValueError("Task cannot be completed in its current status")
            cur.execute("select CELL from RRL_CELLS where CELL=:c and WARE_ID=:w and nvl(BLOCKED_FOR_ACCEPT,0)=0 and nvl(BLOCKED_FOR_REMAINS,0)=0 and nvl(BLOCKED_FOR_POPOLNENIE,0)=0 for update", {"c": task[2], "w": task[7]})
            if len(cur.fetchall()) != 1:
                raise ValueError("Destination cell is blocked")
            cur.execute("select to_char(REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_REMAINS where CELL=:c and UID_POLETA=:p for update", {"c": task[1], "p": task[0]})
            stock = cur.fetchall()
            if len(stock) != 1 or Decimal(stock[0][0]) != Decimal(task[3]):
                raise ValueError("Source pallet quantity has changed")
            cur.execute("select count(*) from RRL_REMAINS r where r.CELL=:c and r.REMAIN<>0 and not exists(select 1 from RRL_RECEIPT_SLOT_CLAIM cl where cl.CELL=:c and cl.UID_PALLET=r.UID_POLETA and cl.STATUS='OCCUPIED' and cl.CELL_SLOT_ID<>:slot)", {"c": task[2], "slot": task[8]})
            if cur.fetchone()[0]:
                raise ValueError("Destination cell is occupied")
            if task[8] is not None:
                cur.execute("select s.CELL_SLOT_ID from RRL_TOPOLOGY_CELL_SLOT s join RRL_RECEIPT_SLOT_CLAIM cl on cl.CELL_SLOT_ID=s.CELL_SLOT_ID where cl.TASK_ID=:t and cl.STATUS='RESERVED' and s.ACTIVE=1 for update", {'t': task_id})
                if not cur.fetchone():
                    raise ValueError('Assigned storage slot is unavailable')
                cur.execute("update RRL_RECEIPT_SLOT_CLAIM set STATUS='OCCUPIED' where TASK_ID=:t", {'t': task_id})
            cur.execute('select RESULT_JSON from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p', {'p': task[0]})
            receipt = json.loads(self._text(cur.fetchone()[0]))
            ReceiptPlacement(cur).validate_target(task[7], task[2], task[8], receipt)
            self._event(cur, task[0], task[3], task[5], task[1], task[2], 2, actor)
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='DONE',FACT_QTY=QTY,FINISHED_AT=systimestamp,ASSIGNED_TO=:a,LAST_ERROR=null where TASK_ID=:t", {"t": task_id, "a": actor})
            result = {"task_id": task_id, "status": "DONE", "pallet_identifier": task[0], "cell": task[2], "sap_sender": receipt["sap_sender"], "sap_order_number": receipt["sap_order_number"], "line_number": receipt["line_number"], "quantity": receipt["quantity"], "material": receipt["material"], "idempotent": False}
            self._outbox(cur, f"PUTAWAY:{task_id}", "PALLET_PUTAWAY", result)
        return result

    def replan(self, task_id: int, body: dict, actor: str) -> dict:
        event_id = 'REPLAN:' + body['operation_id']
        digest = sha256(json.dumps({'task_id': task_id, **body}, sort_keys=True).encode()).hexdigest()
        with receipt_task_metadata(self.gateway, 'Replan incoming pallet destination', actor, 'warehouse_task_assign') as cur:
            cur.execute('select PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:i', {'i': event_id})
            previous = cur.fetchone()
            if previous:
                result = json.loads(self._text(previous[0]))
                if result['request_hash'] != digest:
                    raise ValueError('Replanning operation payload conflict')
                return {**result, 'idempotent': True}
            cur.execute("select SOURCE_DOC_ID from RRL_WAREHOUSE_TASK where TASK_ID=:t and TASK_SOURCE='SAP_RECEIPT'", {'t': task_id})
            source_doc = cur.fetchone()
            if not source_doc:
                raise LookupError('Incoming pallet task not found')
            cur.execute('select CONDITION from RRL_PRIHOD_NAKLAD where ID=:d for update', {'d': source_doc[0]})
            header = cur.fetchone()
            if not header or header[0] not in (0, 1, 2):
                raise ValueError('Incoming document is unavailable')
            cur.execute('select UID_PALLET,FROM_CELL,FROM_WARE_ID,STATUS,TASK_SOURCE,SOURCE_DOC_ID from RRL_WAREHOUSE_TASK where TASK_ID=:t for update', {'t': task_id})
            task = cur.fetchone()
            if not task or task[4]!='SAP_RECEIPT' or task[5] != source_doc[0]:
                raise LookupError('Incoming pallet task not found')
            if task[3] not in {'PLANNED','ASSIGNED','ERROR','CANCELLED'}:
                raise ValueError('Stop active execution before replanning; completed pallet cannot be replanned')
            if normalize_incoming_sscc(body['scanned_pallet'])!=task[0] or body['scanned_from_cell']!=task[1]:
                raise ValueError('Scan pallet and its receiving cell before replanning')
            cur.execute('select RESULT_JSON from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p', {'p': task[0]})
            receipt = json.loads(self._text(cur.fetchone()[0]))
            cur.execute("select to_char(REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_REMAINS where CELL=:c and UID_POLETA=:p for update", {'c': task[1], 'p': task[0]})
            source = cur.fetchall()
            cur.execute("select to_char(POSTED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p", {'p': task[0]})
            admitted = cur.fetchone()
            admitted_qty = admitted[0] if admitted and admitted[0] is not None else receipt['quantity']
            if len(source)!=1 or Decimal(source[0][0])!=Decimal(str(admitted_qty)):
                raise ValueError('Pallet source quantity changed; cannot replan blindly')
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:t", {'t': task_id})
            cur.execute('delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t', {'t': task_id})
            payload = {'expiry_date': receipt['expiry_date'], **receipt.get('physical_measurements',{})}
            placement = ReceiptPlacement(cur).choose(task[2], task[1], receipt['material'], payload)
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='PLANNED',TO_CELL=:c,TO_CELL_SLOT_ID=:s,ASSIGNED_TO=null,RESOURCE_ID=null,RESOURCE_SESSION_ID=null,EQUIPMENT_ID=null,CANCELLED_AT=null,CANCELLED_BY=null,LAST_ERROR=null where TASK_ID=:t", {'t': task_id, 'c': placement['cell'], 's': placement['slot_id']})
            if placement['slot_id'] is not None:
                cur.execute('insert into RRL_RECEIPT_SLOT_CLAIM(TASK_ID,UID_PALLET,CELL,CELL_SLOT_ID) values(:t,:p,:c,:s)', {'t': task_id, 'p': task[0], 'c': placement['cell'], 's': placement['slot_id']})
            result = {'task_id': task_id, 'status': 'PLANNED', 'pallet_identifier': task[0], 'placement': placement, 'sap_sender': receipt['sap_sender'], 'sap_order_number': receipt['sap_order_number'], 'reason': body['reason'], 'request_hash': digest, 'replanned_by': actor, 'idempotent': False}
            self._outbox(cur, event_id, 'PUTAWAY_REPLANNED', result)
        return result

    def cancel(self, task_id: int, reason: str, actor: str) -> dict:
        if not reason.strip():
            raise ValueError('Cancellation reason is required')
        with receipt_task_metadata(self.gateway, 'Cancel putaway and release storage reservation', actor, 'warehouse_task_edit') as cur:
            cur.execute("select SOURCE_DOC_ID from RRL_WAREHOUSE_TASK where TASK_ID=:t and TASK_SOURCE='SAP_RECEIPT'", {'t': task_id})
            source_doc = cur.fetchone()
            if not source_doc:
                raise LookupError('Incoming pallet task not found')
            cur.execute('select CONDITION from RRL_PRIHOD_NAKLAD where ID=:d for update', {'d': source_doc[0]})
            header = cur.fetchone()
            if not header or header[0] not in (0, 1, 2):
                raise ValueError('Incoming document is unavailable')
            cur.execute('select STATUS,TASK_SOURCE,UID_PALLET,SOURCE_DOC_ID from RRL_WAREHOUSE_TASK where TASK_ID=:t for update', {'t': task_id})
            task = cur.fetchone()
            if not task or task[1] != 'SAP_RECEIPT' or task[3] != source_doc[0]:
                raise LookupError('Incoming pallet task not found')
            if task[0] == 'CANCELLED':
                return {'task_id': task_id, 'status': 'CANCELLED', 'idempotent': True}
            if task[0] in {'DONE', 'IN_PROGRESS'}:
                raise ValueError('Stop active putaway before cancellation; completed facts require correction')
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=:a,LAST_ERROR=:r where TASK_ID=:t", {'t': task_id, 'a': actor, 'r': reason})
            cur.execute("delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t and STATUS='RESERVED'", {'t': task_id})
            cur.execute('select RESULT_JSON from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p', {'p': task[2]})
            receipt = json.loads(self._text(cur.fetchone()[0]))
            result = {'task_id': task_id, 'status': 'CANCELLED', 'pallet_identifier': task[2], 'sap_sender': receipt['sap_sender'], 'sap_order_number': receipt['sap_order_number'], 'reason': reason, 'cancelled_by': actor}
            cur.execute("select count(*) from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='PUTAWAY_CANCELLED' and json_value(PAYLOAD_JSON,'$.task_id' returning number)=:t", {'t': task_id})
            cycle = cur.fetchone()[0] + 1
            self._outbox(cur, f'PUTAWAY_CANCEL:{task_id}:{cycle}', 'PUTAWAY_CANCELLED', result)
        return result

    def _event(self, cur: oracledb.Cursor, pallet: str, quantity, document: int, source: str | None, destination: str, kind: int, actor: str) -> None:
        # Only dormant legacy receipt reaches this helper. ACTIVE uses receipt_commands.
        cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        release = cur.fetchone()
        if not release or release[0] != "PREPARED":
            raise RuntimeError("RECEIPT_POSTING_REQUIRED")
        cur.execute("insert into RRL_EVENTS(ID_EVENT,CELL_FROM,CELL_TO,DATE_EVENT,COUNT_EVENT,TYPE_EVENT,UID_POLETA,USER_ID,PRIHOD_NAKL_ID) values(RRL_EVENT_ID_SQ.nextval,:f,:t,sysdate,:q,:kind,:p,:actor,:n)",
                    {"f": source, "t": destination, "q": Decimal(str(quantity)), "kind": kind, "p": pallet, "actor": actor, "n": document})

    def _outbox(self, cur: oracledb.Cursor, event_id: str, kind: str, result: dict) -> None:
        cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)
        cur.execute("insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON) values(:i,:kind,:body)",
                    {"i": event_id, "kind": kind, "body": json.dumps(result, default=str)})

    @staticmethod
    def _text(value) -> str:
        return value.read() if hasattr(value, "read") else value
