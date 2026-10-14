import json
from typing import Any
from decimal import Decimal
from hashlib import sha256
from uuid import uuid4
import oracledb
from ....oracle_gateway import OracleGateway
from ..domain.sscc_label import label_html, label_zpl
from ..domain.pallet_identifiers import normalize_incoming_sscc
from ...platform.public import read_oracle_json


class ReceiptLabels:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    @staticmethod
    def _scope(cur: Any, warehouse: int, actor: str) -> None:
        try:
            cur.callproc("RRL_SSCC_ALLOCATOR.assert_scope",[warehouse,actor,"warehouse_receipt_confirm"])
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)==20882:
                raise PermissionError("Receipt label warehouse access required") from exc
            raise

    def issue(self, order_id: str, payload: dict, actor: str) -> dict:
        digest = sha256(json.dumps({'order': order_id, **payload}, sort_keys=True).encode()).hexdigest()
        with self.gateway.transaction('NI01 issue SSCC receiving label') as cur:
            cur.execute('select o.WARE_ID,o.NAKLAD_ID,o.CLOSED_AT,h.CONDITION from RRL_SAP_SUPPLY_ORDER o join RRL_PRIHOD_NAKLAD h on h.ID=o.NAKLAD_ID where o.ORDER_ID=:i for update', {'i': order_id})
            order = cur.fetchone()
            if not order:
                raise LookupError('SAP supply order not found')
            self._scope(cur,order[0],actor)
            cur.execute('select LABEL_ID,SSCC,PAYLOAD_HASH,CREATED_BY from RRL_RECEIPT_LABEL where OPERATION_ID=:o', {'o': payload['operation_id']})
            old = cur.fetchone()
            if old:
                if old[2] != digest or old[3]!=actor:
                    raise ValueError('Label operation payload conflict')
                return {'label_id': old[0], 'sscc': old[1], 'idempotent': True}
            if order[2] or (order[3] or 0)!=0:
                raise ValueError('Supply is closed; cannot issue new pallet label')
            cur.execute('select ARTICUL,BASE_UOM from RRL_SAP_SUPPLY_LINE where ORDER_ID=:i and LINE_NUMBER=:l', {'i': order_id, 'l': payload['line_number']})
            line = cur.fetchone()
            if not line:
                raise LookupError('Supply line not found')
            result=cur.var(oracledb.DB_TYPE_VARCHAR,size=18)
            cur.execute("begin :result:=RRL_SSCC_ALLOCATOR.allocate(:ware,:actor,'warehouse_receipt_confirm');end;",result=result,ware=order[0],actor=actor)
            sscc=result.getvalue()
            label_id = uuid4().hex
            data = {'sscc': sscc, 'article': line[0], 'quantity': payload['quantity'], 'unit': line[1], 'batch': payload['supplier_batch'], 'expiry': payload['expiry_date']}
            cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_RECEIPT_LABEL(LABEL_ID,OPERATION_ID,ORDER_ID,LINE_NUMBER,SSCC,PAYLOAD_HASH,PAYLOAD_JSON,CREATED_BY) values(:id,:op,:o,:l,:s,:h,:body,:a)", {'id': label_id, 'op': payload['operation_id'], 'o': order_id, 'l': payload['line_number'], 's': sscc, 'h': digest, 'body': json.dumps(data), 'a': actor})
        return {'label_id': label_id, 'sscc': sscc, 'idempotent': False}

    def document(self, label_id: str, format: str, actor: str, dpi: int = 203) -> str:
        with self.gateway.transaction("Current warehouse receiving label document READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("select o.WARE_ID,l.PAYLOAD_JSON from RRL_RECEIPT_LABEL l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID where l.LABEL_ID=:label_id",label_id=label_id)
            row=cur.fetchone()
            if row is None:
                raise LookupError("Label not found")
            self._scope(cur,row[0],actor)
            data=read_oracle_json(row[1])
            return label_zpl(data,dpi) if format=="zpl" else label_html(data)

    def confirm(self, label_id: str, scan: str, actor: str) -> dict:
        with self.gateway.transaction('NI01 operator confirms attached label') as cur:
            cur.execute("select o.WARE_ID from RRL_RECEIPT_LABEL l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID where l.LABEL_ID=:label_id",label_id=label_id)
            source=cur.fetchone()
            if source is None:
                raise LookupError("Label not found")
            self._scope(cur,source[0],actor)
            cur.execute('select SSCC,STATUS from RRL_RECEIPT_LABEL where LABEL_ID=:i for update', {'i': label_id})
            row = cur.fetchone()
            cur.execute("select o.WARE_ID from RRL_RECEIPT_LABEL l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID where l.LABEL_ID=:label_id",label_id=label_id)
            current_source=cur.fetchone()
            if current_source is None:
                raise LookupError("Label source not found")
            self._scope(cur,current_source[0],actor)
            if not row:
                raise LookupError('Label not found')
            if normalize_incoming_sscc(scan) != row[0]:
                raise ValueError('Scan the printed and attached label')
            if row[1]=='USED':
                return {'label_id': label_id, 'status': 'USED', 'idempotent': True}
            cur.execute("update RRL_RECEIPT_LABEL set STATUS='CONFIRMED',CONFIRMED_AT=systimestamp,CONFIRMED_BY=:a where LABEL_ID=:i", {'a': actor, 'i': label_id})
            cur.execute('update RRL_PALLETS set PRINTED=1 where UID_PALLET=:p', {'p': row[0]})
        return {'label_id': label_id, 'status': 'CONFIRMED', 'idempotent': row[1]=='CONFIRMED'}
