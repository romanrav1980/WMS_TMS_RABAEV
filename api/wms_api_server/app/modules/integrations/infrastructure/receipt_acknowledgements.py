import json
from hashlib import sha256
import xml.etree.ElementTree as ET
import oracledb
from ....oracle_gateway import OracleGateway
from ..domain.artmas import MAX_IDOC_BYTES, local_name
from ..application.ingestion import IdocConflict


class ReceiptAcknowledgements:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, raw: bytes, actor: str) -> dict:
        if not raw or len(raw) > MAX_IDOC_BYTES:
            raise ValueError('Acknowledgement exceeds XML size limit')
        xml = raw.decode('utf-8-sig')
        if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
            raise ValueError('DTD/entities forbidden')
        root = ET.fromstring(xml)
        if local_name(root.tag) != 'WmsReceiptAcknowledgement' or root.get('version') != '1':
            raise ValueError('Expected WmsReceiptAcknowledgement version=1')
        fields = {}
        for node in root:
            name = local_name(node.tag)
            if len(node) or name in fields:
                raise ValueError('Duplicate/nested acknowledgement field')
            fields[name] = (node.text or '').strip()
        for name in ('Sender', 'MessageId', 'EventId', 'PayloadHash', 'Status'):
            if not fields.get(name) or len(fields[name].encode()) > 100:
                raise ValueError('Missing or oversized acknowledgement field: ' + name)
        if fields['Status'] not in {'ACCEPTED', 'REJECTED'}:
            raise ValueError('Status must be ACCEPTED/REJECTED')
        if fields['Status']=='ACCEPTED' and not fields.get('ExternalDocumentId'):
            raise ValueError('SAP acceptance requires an external document identifier')
        if len(fields.get('ExternalDocumentId','').encode()) > 100:
            raise ValueError('External document identifier too long')
        digest = sha256(raw).hexdigest()
        with self.gateway.transaction('NI01 record actual gateway SAP acknowledgement') as cur:
            cur.execute('select STATUS,FILE_HASH,EXTERNAL_DOCUMENT_ID,PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:i for update', {'i': fields['EventId']})
            event = cur.fetchone()
            if not event:
                raise LookupError('Receipt event not found')
            cur.execute('select PAYLOAD_HASH,RESULT_JSON from RRL_SAP_RECEIPT_ACK where SENDER=:s and MESSAGE_ID=:m', {'s': fields['Sender'], 'm': fields['MessageId']})
            previous = cur.fetchone()
            if previous:
                if previous[0] != digest:
                    raise IdocConflict('Acknowledgement MessageId payload conflict')
                return {**json.loads(self._text(previous[1])), 'idempotent': True}
            payload = json.loads(self._text(event[3]))
            sender = payload.get('sap_sender')
            if not sender and payload.get('pallet_identifier'):
                cur.execute('select o.SENDER from RRL_SAP_SUPPLY_ORDER o join RRL_PALLETS p on p.PRIHOD_NAKLAD_ID=o.NAKLAD_ID where p.UID_PALLET=:p', {'p': payload['pallet_identifier']})
                row = cur.fetchone(); sender = row[0] if row else None
            if not sender or sender != fields['Sender'] or event[1] != fields['PayloadHash']:
                raise IdocConflict('Acknowledgement source or exported payload hash mismatch')
            if event[0] not in {'EXPORTED', 'REJECTED', 'ACKNOWLEDGED'}:
                raise IdocConflict('Event has not been exported')
            if event[0]=='ACKNOWLEDGED' and (fields['Status']!='ACCEPTED' or event[2]!=fields['ExternalDocumentId']):
                raise IdocConflict('Confirmed SAP acceptance cannot be overwritten')
            status = 'ACKNOWLEDGED' if fields['Status']=='ACCEPTED' else 'REJECTED'
            result = {'event_id': fields['EventId'], 'status': status, 'external_document_id': fields.get('ExternalDocumentId'), 'idempotent': False}
            cur.execute('update RRL_SAP_RECEIPT_OUTBOX set STATUS=:s,ACKNOWLEDGED_AT=systimestamp,EXTERNAL_DOCUMENT_ID=:doc,LAST_ERROR=:e where EVENT_ID=:i', {'s': status, 'doc': fields.get('ExternalDocumentId'), 'e': fields.get('Message','')[:2000] if status=='REJECTED' else None, 'i': fields['EventId']})
            cur.setinputsizes(raw=oracledb.DB_TYPE_CLOB, result=oracledb.DB_TYPE_CLOB)
            cur.execute('insert into RRL_SAP_RECEIPT_ACK(SENDER,MESSAGE_ID,EVENT_ID,PAYLOAD_HASH,RAW_XML,RESULT_JSON,RECEIVED_BY) values(:s,:m,:i,:h,:raw,:result,:a)', {'s': fields['Sender'], 'm': fields['MessageId'], 'i': fields['EventId'], 'h': digest, 'raw': raw.decode('utf-8'), 'result': json.dumps(result), 'a': actor})
        return result

    def list_events(self, limit: int) -> list[dict]:
        return self.gateway.fetch_all("select EVENT_ID,EVENT_TYPE,STATUS,FILE_NAME,FILE_HASH,EXTERNAL_DOCUMENT_ID,LAST_ERROR,CREATED_AT,EXPORTED_AT,ACKNOWLEDGED_AT,JSON_VALUE(PAYLOAD_JSON,'$.sap_order_number') ORDER_NUMBER,JSON_VALUE(PAYLOAD_JSON,'$.pallet_identifier') PALLET_IDENTIFIER from RRL_SAP_RECEIPT_OUTBOX order by CREATED_AT desc fetch first :lim rows only", {'lim': limit})

    def retry(self, event_id: str) -> dict:
        count = self.gateway.execute("update RRL_SAP_RECEIPT_OUTBOX set STATUS='PENDING',LAST_ERROR=null where EVENT_ID=:i and STATUS in('ERROR','REJECTED','EXPORTED')", {'i': event_id})
        if count != 1:
            raise IdocConflict('Only failed/unacknowledged exported events can be retried')
        return {'event_id': event_id, 'status': 'PENDING'}

    @staticmethod
    def _text(value) -> str:
        return value.read() if hasattr(value, 'read') else value
