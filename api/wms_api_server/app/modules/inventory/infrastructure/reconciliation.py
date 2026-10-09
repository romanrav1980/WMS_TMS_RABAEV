import json
from hashlib import sha256
from decimal import Decimal
import oracledb
from ....oracle_gateway import OracleGateway


class ReceiptReconciliation:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def close(self, order_id: str, operation: str, reason: str, actor: str) -> dict:
        with self.gateway.transaction('NI01 close supply with explicit quantity reconciliation') as cur:
            cur.execute('select NAKLAD_ID,CLOSED_AT,RECONCILIATION_JSON,ORDER_NUMBER,SENDER,REVISION from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i for update', {'i': order_id})
            order = cur.fetchone()
            if not order:
                raise LookupError('Supply order not found')
            digest = sha256(json.dumps([order_id, operation, reason]).encode()).hexdigest()
            event_id = 'CLOSE:' + sha256(json.dumps([order_id, operation]).encode()).hexdigest()
            cur.execute('select PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:i', {'i': event_id})
            saved = cur.fetchone()
            if saved:
                old = json.loads(saved[0].read() if hasattr(saved[0], 'read') else saved[0])
                if old['payload_hash']!=digest:
                    raise ValueError('Reconciliation operation payload conflict')
                return {**old, 'idempotent': True}
            if order[1]:
                old = json.loads(order[2].read() if hasattr(order[2], 'read') else order[2])
                if old['operation_id']!=operation or old['payload_hash']!=digest:
                    raise ValueError('Supply already closed by another reconciliation')
                return {**old, 'idempotent': True}
            cur.execute('select ID from RRL_PRIHOD_NAKLAD where ID=:i for update', {'i': order[0]})
            cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
            prepared = cur.fetchone()[0] == "PREPARED"
            if prepared:
                cur.execute("select l.LINE_NUMBER,l.ARTICUL,to_char(l.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),to_char(nvl((select sum(UNIT_COUNT) from RRL_PALLETS p where p.PRIHOD_NAKLAD_ID=:n and p.ARTICUL=l.ARTICUL),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_SAP_SUPPLY_LINE l where l.ORDER_ID=:i", {'n': order[0], 'i': order_id})
                lines = [{'line_number': r[0], 'material': r[1], 'planned': r[2], 'accepted': r[3], 'shortage': str(Decimal(r[2])-Decimal(r[3]))} for r in cur.fetchall()]
            else:
                from ..domain.stock_quantity import convert_exact
                cur.execute("""select l.LINE_NUMBER,l.ARTICUL,l.BASE_UOM,
                    to_char(l.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
                    to_char(nvl(sum(rec.POSTED_BASE_QTY),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
                    u.NUMERATOR,u.DENOMINATOR,u.BASE_UOM,
                    sum(case when rec.OPERATION_ID is not null and (rec.POSTED_BASE_QTY is null or rec.STOCK_BASE_UOM is null or rec.STOCK_BASE_UOM!=u.BASE_UOM) then 1 else 0 end)
                    from RRL_SAP_SUPPLY_LINE l join RRL_STOCK_UOM_CONVERSION u on u.ARTICUL=l.ARTICUL and u.INPUT_UOM=l.BASE_UOM
                    and u.POLICY_VERSION=(select max(x.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION x where x.ARTICUL=l.ARTICUL and x.INPUT_UOM=l.BASE_UOM)
                    left join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=l.ORDER_ID and rec.LINE_NUMBER=l.LINE_NUMBER
                    where l.ORDER_ID=:i group by l.LINE_NUMBER,l.ARTICUL,l.BASE_UOM,l.PLANNED_QTY,u.NUMERATOR,u.DENOMINATOR,u.BASE_UOM
                    order by l.LINE_NUMBER""", i=order_id)
                lines = []
                for row in cur.fetchall():
                    if row[8]:
                        raise ValueError("Receipt fact has no consistent base quantity")
                    accepted = (convert_exact(row[4], int(row[6]), int(row[5]), 9)
                                if Decimal(row[4]) else Decimal(0))
                    lines.append({'line_number': row[0], 'material': row[1], 'unit': row[2],
                                  'planned': row[3], 'accepted': str(accepted),
                                  'shortage': str(Decimal(row[3])-accepted)})
                cur.execute("select count(*) from RRL_SAP_SUPPLY_LINE where ORDER_ID=:i", i=order_id)
                if len(lines) != cur.fetchone()[0]:
                    raise ValueError("Receipt reconciliation requires every line UOM policy")
            if any(Decimal(l['shortage'])<0 for l in lines):
                raise ValueError('Overreceipt must be reconciled before closing')
            result = {'operation_id': operation, 'payload_hash': digest, 'order_id': order_id, 'sap_order_number': order[3], 'sap_sender': order[4], 'order_revision': order[5], 'reason': reason, 'closed_by': actor, 'lines': lines, 'status': 'CLOSED', 'idempotent': False}
            cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)
            cur.execute('update RRL_SAP_SUPPLY_ORDER set CLOSED_AT=systimestamp,RECONCILIATION_JSON=:body where ORDER_ID=:i', {'body': json.dumps(result), 'i': order_id})
            cur.execute('update RRL_PRIHOD_NAKLAD set CONDITION=1,DATE_OF_ACCEPT=nvl(DATE_OF_ACCEPT,sysdate) where ID=:n', {'n': order[0]})
            cur.execute("insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON) values(:event,'SUPPLY_RECONCILED',:body)", {'event': event_id, 'body': json.dumps(result)})
        return result

    def reopen(self, order_id: str, operation: str, reason: str, actor: str) -> dict:
        event_id = 'REOPEN:' + sha256(json.dumps([order_id,operation]).encode()).hexdigest()
        digest = sha256(json.dumps([order_id,operation,reason]).encode()).hexdigest()
        with self.gateway.transaction('NI01 request reopening against a new SAP revision') as cur:
            cur.execute('select NAKLAD_ID,CLOSED_AT,ORDER_NUMBER,SENDER,REVISION from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i for update', {'i': order_id})
            order = cur.fetchone()
            if not order:
                raise LookupError('Supply order not found')
            cur.execute('select PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:i', {'i': event_id})
            old = cur.fetchone()
            if old:
                saved = json.loads(old[0].read() if hasattr(old[0], 'read') else old[0])
                if saved['payload_hash']!=digest:
                    raise ValueError('Reopening operation payload conflict')
                return {**saved, 'idempotent': True}
            if not order[1]:
                raise ValueError('Supply is not explicitly closed or reopening is already requested')
            result = {'order_id': order_id, 'sap_order_number': order[2], 'sap_sender': order[3], 'previous_revision': order[4], 'status': 'AWAITING_SAP_REVISION', 'operation_id': operation, 'payload_hash': digest, 'reason': reason, 'requested_by': actor, 'idempotent': False}
            cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)
            cur.execute('update RRL_SAP_SUPPLY_ORDER set CLOSED_AT=null,RECONCILIATION_JSON=:body where ORDER_ID=:i', {'i': order_id, 'body': json.dumps(result)})
            # Keep header closed until a strictly newer authoritative SAP plan is applied.
            cur.execute('update RRL_PRIHOD_NAKLAD set CONDITION=1 where ID=:n', {'n': order[0]})
            cur.execute("insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON) values(:i,'SUPPLY_REOPEN_REQUESTED',:body)", {'i': event_id, 'body': json.dumps(result)})
        return result
