import oracledb
"""Amend remaining obligations without replacing accepted pallet facts."""
from decimal import Decimal
from ..application.ingestion import IdocConflict


class SupplyAmendments:
    def __init__(self, cursor: oracledb.Cursor) -> None:
        self.cur = cursor

    def prepare(self, order_id: str, naklad_id: int, order: dict) -> dict[str, tuple]:
        cur = self.cur
        cur.execute('select CONDITION from RRL_PRIHOD_NAKLAD where ID=:i for update', {'i': naklad_id})
        incoming_header = cur.fetchone()
        if incoming_header is None:
            raise IdocConflict('Incoming document missing')
        if (incoming_header[0] or 0) not in {0,1}:
            raise IdocConflict('Incoming document is closed by another legacy process')
        cur.execute('select WARE_ID,RECEIVE_CELL,CLOSED_AT from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i', {'i': order_id})
        header = cur.fetchone()
        if header[2] is not None:
            raise IdocConflict('Explicitly reconciled supply must be reopened before amendment')
        cur.execute('select count(*) from RRL_SAP_PALLET_RECEIPT where ORDER_ID=:i', {'i': order_id})
        if cur.fetchone()[0] and header[:2] != (order['warehouse_id'], order['receive_cell']):
            raise IdocConflict('Cannot change warehouse/receiving zone after physical receipt')
        cur.execute('select LINE_NUMBER,ARTICUL,ROW_ID,BASE_UOM from RRL_SAP_SUPPLY_LINE where ORDER_ID=:i', {'i': order_id})
        previous = {r[0]: r[1:] for r in cur.fetchall()}
        incoming = {l['line_number']: l for l in order['lines']}
        for number, row in previous.items():
            cur.execute('select count(*) from RRL_SAP_PALLET_RECEIPT where ORDER_ID=:i and LINE_NUMBER=:l', {'i': order_id, 'l': number})
            received = cur.fetchone()[0] > 0
            if number not in incoming:
                if received:
                    raise IdocConflict('Received line cannot be deleted')
                cur.execute('delete from RRL_SAP_TRACE_AGG where ORDER_ID=:i and LINE_NUMBER=:l', {'i': order_id, 'l': number})
                cur.execute('delete from RRL_SAP_SUPPLY_LINE where ORDER_ID=:i and LINE_NUMBER=:l', {'i': order_id, 'l': number})
                cur.execute('delete from RRL_PRIHOD_NAKLAD_ROWS where ID=:r and not exists(select 1 from RRL_SAP_SUPPLY_LINE where ROW_ID=:r)', {'r': row[1]})
                continue
            if incoming[number]['material'] != row[0]:
                raise IdocConflict('Line material is immutable; add a new line instead')
        return previous

    def validate_quantity(self, order_id: str, line_number: str, base: str, quantity: Decimal) -> None:
        self.cur.execute("""select to_char(nvl(sum(POSTED_BASE_QTY),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
          count(case when POSTED_BASE_QTY is null or STOCK_BASE_UOM is null or STOCK_BASE_UOM!=:u then 1 end)
          from RRL_SAP_PALLET_RECEIPT where ORDER_ID=:i and LINE_NUMBER=:l""", i=order_id,l=line_number,u=base)
        accepted,invalid = self.cur.fetchone()
        if invalid:
            raise IdocConflict("Received line requires posted base-unit reconciliation")
        if quantity < Decimal(accepted):
            raise IdocConflict('SAP planned quantity cannot be less than already received quantity')

    def refresh_header(self, order_id: str, naklad_id: int) -> None:
        self.cur.execute("""select count(*)from RRL_SAP_SUPPLY_LINE l where l.ORDER_ID=:i and
          (l.PLANNED_QTY>(select nvl(sum(r.POSTED_BASE_QTY),0)from RRL_SAP_PALLET_RECEIPT r
             where r.ORDER_ID=l.ORDER_ID and r.LINE_NUMBER=l.LINE_NUMBER)
           or exists(select 1 from RRL_SAP_PALLET_RECEIPT r where r.ORDER_ID=l.ORDER_ID and r.LINE_NUMBER=l.LINE_NUMBER
             and(r.POSTED_BASE_QTY is null or r.STOCK_BASE_UOM is null or r.STOCK_BASE_UOM!=l.BASE_UOM)))""", i=order_id)
        complete = self.cur.fetchone()[0] == 0
        self.cur.execute('update RRL_PRIHOD_NAKLAD set CONDITION=:c,DATE_OF_ACCEPT=case when :c=1 then nvl(DATE_OF_ACCEPT,sysdate) else null end where ID=:i', {'c': int(complete), 'i': naklad_id})
