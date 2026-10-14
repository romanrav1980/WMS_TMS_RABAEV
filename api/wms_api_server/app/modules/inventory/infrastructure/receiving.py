"""Atomic physical receipt and putaway on existing pallet/event/task tables."""
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json

import oracledb

from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from .receiving_marks import ReceivingMarks
from .placement import ReceiptPlacement
from .metadata_transactions import receipt_task_metadata
from .receipt_task_access import assert_receipt_task_scope
from ..domain.pallet_identifiers import normalize_incoming_sscc


class Receiving:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, order_id: str, payload: dict, actor: str) -> dict:
        from .receipt_posting import receive_command
        return receive_command(self.gateway,order_id,payload,actor)

    def complete(self, task_id: int, scans: dict, actor: str) -> dict:
        from .task_completion import complete_existing_task
        from ....schemas import WarehouseTaskStatusRequest
        return complete_existing_task(self.gateway,task_id,WarehouseTaskStatusRequest(**scans),actor)

    def replan(self, task_id: int, body: dict, actor: str) -> dict:
        event_id = 'REPLAN:' + body['operation_id']
        digest = sha256(json.dumps({'task_id': task_id, **body}, sort_keys=True).encode()).hexdigest()
        with receipt_task_metadata(self.gateway, 'Replan incoming pallet destination', actor, 'warehouse_task_assign') as cur:
            assert_receipt_task_scope(cur,task_id,actor)
            cur.execute('select PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:i', {'i': event_id})
            previous = cur.fetchone()
            if previous:
                result = read_oracle_json(previous[0])
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
            cur.execute('select UID_PALLET,FROM_CELL,FROM_WARE_ID,STATUS,TASK_SOURCE,SOURCE_DOC_ID,QTY,LAST_ERROR from RRL_WAREHOUSE_TASK where TASK_ID=:t for update', {'t': task_id})
            task = cur.fetchone()
            assert_receipt_task_scope(cur,task_id,actor)
            if not task or task[4]!='SAP_RECEIPT' or task[5] != source_doc[0]:
                raise LookupError('Incoming pallet task not found')
            if task[3] not in {'PLANNED','ASSIGNED','ERROR','CANCELLED'}:
                raise ValueError('Stop active execution before replanning; completed pallet cannot be replanned')
            if (body['scanned_pallet']!=task[0] and normalize_incoming_sscc(body['scanned_pallet'])!=task[0]) or body['scanned_from_cell']!=task[1]:
                raise ValueError('Scan pallet and its receiving cell before replanning')
            cur.execute('select RESULT_JSON from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p', {'p': task[0]})
            receipt = read_oracle_json(cur.fetchone()[0])
            from .receipt_replan_source import admit_current_source
            source_proof = admit_current_source(cur,task_id,task,receipt)
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:t", {'t': task_id})
            cur.execute('delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t', {'t': task_id})
            payload = {'expiry_date': receipt['expiry_date'], **receipt.get('physical_measurements',{})}
            placement = ReceiptPlacement(cur).choose(task[2], task[1], receipt['material'], payload)
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='PLANNED',QTY=:q,TO_CELL=:c,TO_CELL_SLOT_ID=:s,ASSIGNED_TO=null,RESOURCE_ID=null,RESOURCE_SESSION_ID=null,EQUIPMENT_ID=null,CANCELLED_AT=null,CANCELLED_BY=null,LAST_ERROR=null where TASK_ID=:t", {'t': task_id, 'q': Decimal(source_proof['current_task_quantity']), 'c': placement['cell'], 's': placement['slot_id']})
            if placement['slot_id'] is not None:
                cur.execute('insert into RRL_RECEIPT_SLOT_CLAIM(TASK_ID,UID_PALLET,CELL,CELL_SLOT_ID) values(:t,:p,:c,:s)', {'t': task_id, 'p': task[0], 'c': placement['cell'], 's': placement['slot_id']})
            result = {'task_id': task_id, 'status': 'PLANNED', 'pallet_identifier': task[0], 'placement': placement, 'sap_sender': receipt['sap_sender'], 'sap_order_number': receipt['sap_order_number'], 'reason': body['reason'], 'request_hash': digest, 'replanned_by': actor, 'idempotent': False, **source_proof}
            self._outbox(cur, event_id, 'PUTAWAY_REPLANNED', result)
        return result

    def cancel(self, task_id: int, reason: str, actor: str) -> dict:
        if not reason.strip():
            raise ValueError('Cancellation reason is required')
        with receipt_task_metadata(self.gateway, 'Cancel putaway and release storage reservation', actor, 'warehouse_task_edit') as cur:
            assert_receipt_task_scope(cur,task_id,actor)
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
            assert_receipt_task_scope(cur,task_id,actor)
            if not task or task[1] != 'SAP_RECEIPT' or task[3] != source_doc[0]:
                raise LookupError('Incoming pallet task not found')
            if task[0] == 'CANCELLED':
                return {'task_id': task_id, 'status': 'CANCELLED', 'idempotent': True}
            if task[0] in {'DONE', 'IN_PROGRESS'}:
                raise ValueError('Stop active putaway before cancellation; completed facts require correction')
            cur.execute("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=:a,LAST_ERROR=:r where TASK_ID=:t", {'t': task_id, 'a': actor, 'r': reason})
            cur.execute("delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t and STATUS='RESERVED'", {'t': task_id})
            cur.execute('select RESULT_JSON from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p', {'p': task[2]})
            receipt = read_oracle_json(cur.fetchone()[0])
            result = {'task_id': task_id, 'status': 'CANCELLED', 'pallet_identifier': task[2], 'sap_sender': receipt['sap_sender'], 'sap_order_number': receipt['sap_order_number'], 'reason': reason, 'cancelled_by': actor}
            cur.execute("select count(*) from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='PUTAWAY_CANCELLED' and json_value(PAYLOAD_JSON,'$.task_id' returning number)=:t", {'t': task_id})
            cycle = cur.fetchone()[0] + 1
            self._outbox(cur, f'PUTAWAY_CANCEL:{task_id}:{cycle}', 'PUTAWAY_CANCELLED', result)
        return result

    def _outbox(self, cur: oracledb.Cursor, event_id: str, kind: str, result: dict) -> None:
        cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)
        cur.execute("insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON) values(:i,:kind,:body)",
                    {"i": event_id, "kind": kind, "body": json.dumps(result, default=str)})

    @staticmethod
    def _text(value: object) -> str:
        return value.read() if hasattr(value, "read") else value
