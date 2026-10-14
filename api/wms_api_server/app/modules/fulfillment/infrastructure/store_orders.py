"""One transaction: immutable SAP demand, existing customer order and message result."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from .store_source_scope import source_transaction, assert_store_scope
from ..domain.store_order import read_order, calendar, positive
from ..application.ports import StoreOrderConflict


class StoreOrders:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, raw: bytes, actor: str) -> dict:
        data = read_order(raw)
        received = datetime.now(timezone.utc)
        with source_transaction(self.gateway,'NI02 receive immutable SAP customer demand',actor,'sap_store_order_import',int(data['WarehouseId'])) as cur:
            cur.execute('lock table RRL_SAP_STORE_ORDER in share row exclusive mode wait 3')
            assert_store_scope(cur,actor,'sap_store_order_import',int(data['WarehouseId']))
            cur.execute('select PAYLOAD_HASH,RESULT_JSON from RRL_SAP_STORE_MESSAGE where SENDER=:s and MESSAGE_ID=:m', {'s':data['Sender'],'m':data['MessageId']})
            old = cur.fetchone()
            if old:
                if old[0]!=data['payload_hash']:
                    raise StoreOrderConflict('MessageId payload conflict')
                return {**read_oracle_json(old[1]), 'idempotent': True}
            cur.execute('select CUSTOMER_ORDER_ID,CONTENT_HASH,RESULT_JSON from RRL_SAP_STORE_ORDER where SENDER=:s and ORDER_NUMBER=:n', {'s':data['Sender'],'n':data['OrderNumber']})
            previous = cur.fetchone()
            if previous:
                if previous[1]!=data['content_hash']:
                    raise StoreOrderConflict('Changes to an imported SAP customer order are forbidden')
                result = {**read_oracle_json(previous[2]), 'idempotent': True}
            else:
                store, times = self._destination(cur,data,received)
                cur.execute('select RRL_CUSTOMER_ORDER_SQ.nextval from dual')
                order_id = int(cur.fetchone()[0])
                cur.execute("""insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,CUSTOMER_STORE_MAP_ID,WARE_ID,ORDER_DATE,SHIPMENT_DATE,ROUTE_ID,DOCK_ID,STATUS,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)
                  values(:id,:n,:customer,:store,:w,:od,:ship,:route,:dock,:status,'SAP_RETAIL',sysdate,:actor)""",
                  {'id':order_id,'n':data['OrderNumber'],'customer':store[1],'store':store[0],'w':int(data['WarehouseId']),
                   'od':datetime.fromisoformat(data['OrderDate']),'ship':times['shipment'],'route':store[3],'dock':store[4],
                   'status':'DRAFT' if times['late'] or not times['calendar_allowed'] else 'IMPORTED','actor':actor[:50]})
                self._lines(cur,order_id,data,actor)
                result = {'customer_order_id':order_id,'order_number':data['OrderNumber'], 'admission_status':'PENDING_CALENDAR' if not times['calendar_allowed'] else 'PENDING_LATE' if times['late'] else 'ACCEPTED',
                          'operational_date':data['OperationalDate'],'picking_start_at':times['picking_start'].isoformat(),
                          'picking_finish_at':times['picking_finish'].isoformat(),'shipment_at':times['shipment'].isoformat(),
                          'delivery_date':data['DeliveryDate'],'utc_offset_minutes':times['offset_minutes'],'idempotent':False,
                          'calendar_basis':times['calendar_basis'],'calendar_exception':times.get('calendar_exception'),
                          'late':times['late'],'calendar_allowed':times['calendar_allowed']}
                cur.setinputsizes(xml_raw=oracledb.DB_TYPE_CLOB,parsed=oracledb.DB_TYPE_CLOB,result=oracledb.DB_TYPE_CLOB)
                cur.execute("""insert into RRL_SAP_STORE_ORDER(CUSTOMER_ORDER_ID,SENDER,ORDER_NUMBER,CONTENT_HASH,RAW_XML,DEMAND_JSON,RESULT_JSON,ADMISSION_STATUS,OPERATIONAL_DATE,DELIVERY_DATE,PICKING_START_AT,PICKING_FINISH_AT,SHIPMENT_AT,UTC_OFFSET_MINUTES)
                  values(:id,:s,:n,:h,:xml_raw,:parsed,:result,:status,:day,:delivery,:startat,:finishat,:shipment,:offsetm)""",
                  {'id':order_id,'s':data['Sender'],'n':data['OrderNumber'],'h':data['content_hash'],'xml_raw':raw.decode('utf-8-sig'),
                   'parsed':json.dumps(data),'result':json.dumps(result),'status':result['admission_status'],
                   'day':datetime.fromisoformat(data['OperationalDate']),'delivery':datetime.fromisoformat(data['DeliveryDate']),
                   'startat':times['picking_start'],'finishat':times['picking_finish'],'shipment':times['shipment'],'offsetm':times['offset_minutes']})
            cur.setinputsizes(xml_raw=oracledb.DB_TYPE_CLOB,result=oracledb.DB_TYPE_CLOB)
            cur.execute('insert into RRL_SAP_STORE_MESSAGE(SENDER,MESSAGE_ID,CUSTOMER_ORDER_ID,PAYLOAD_HASH,RAW_XML,RESULT_JSON,CREATED_BY) values(:s,:m,:id,:h,:xml_raw,:result,:a)',
                        {'s':data['Sender'],'m':data['MessageId'],'id':result['customer_order_id'],'h':data['payload_hash'],'xml_raw':raw.decode('utf-8-sig'),'result':json.dumps(result),'a':actor})
        return result

    def _destination(self, cur: oracledb.Cursor, data: dict, received: datetime) -> tuple:
        cur.execute("""select m.CUSTOMER_STORE_MAP_ID,m.CUSTOMER_ID,m.CREATED_AT,m.DEFAULT_ROUTE_ID,m.DEFAULT_DOCK_ID
          from RRL_CUSTOMER_STORE_MAP m join RRL_CUSTOMER c on c.CUSTOMER_ID=m.CUSTOMER_ID
          where m.STORE_CODE=:store and c.CUSTOMER_CODE=:customer and m.ACTIVE=1 and c.ACTIVE=1""", {'store':data['StoreCode'],'customer':data['CustomerCode']})
        stores = cur.fetchall()
        if len(stores)!=1:
            raise ValueError('Store/customer must uniquely match active existing WMS address')
        store = stores[0]
        cur.execute('select count(*) from RRL_WARES where ID=:w', {'w':int(data['WarehouseId'])})
        if cur.fetchone()[0]!=1:
            raise ValueError('Unknown warehouse')
        from .store_calendar_rule import delivery_rule
        proof=delivery_rule(cur,int(data['WarehouseId']),store[0],datetime.fromisoformat(data['DeliveryDate']))
        settings=(proof["utc_offset_minutes"],proof["delivery_weekdays"],proof["allow_same_day"])
        times=calendar(data,settings[0],settings[1],bool(settings[2]),received,proof["allowed"])
        times['calendar_basis']=proof["calendar_basis"]
        times['calendar_exception']=proof if proof.get("exception_state") else None
        local_day = (received+timedelta(minutes=settings[0])).date()
        if not store[2] or local_day < store[2].date()+timedelta(days=7):
            raise ValueError('Address must be registered at least seven days before first order')
        return store, times

    def _lines(self, cur: oracledb.Cursor, order_id: int, data: dict, actor: str) -> None:
        for line in data['Lines']:
            cur.execute('select m.BASE_UOM,m.UNITS_JSON,m.SENDER,a.NAME from RRL_SAP_ARTICLE_META m join RRL_ARTICULS a on a.ACTICUL=m.ARTICUL where m.ARTICUL=:a', {'a':line['material']})
            rows = cur.fetchall()
            if len(rows)!=1 or rows[0][2]!=data['Sender']:
                raise ValueError('Import unique SAP article from the same sender before ordering')
            base,units,_,name = rows[0]
            from ...inventory.public import convert_sap_source_quantity
            qty = convert_sap_source_quantity(cur,line["material"],line["unit"],line["quantity"],base,read_oracle_json(units))
            weight = Decimal(line['target_weight_kg']) if line['target_weight_kg'] else (qty if base.upper()=='KG' else None)
            cur.execute("""insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,ORDER_WEIGHT,WARE_ID,STATUS,CREATED_AT,CREATED_BY)
              values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:id,:line,:a,:name,:u,:q,:weight,:w,'OPEN',sysdate,:actor)""",
              {'id':order_id,'line':line['line_number'],'a':line['material'],'name':name,'u':base,'q':qty,'weight':weight,'w':int(data['WarehouseId']),'actor':actor[:50]})

    def configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict:
        from .store_calendar import configure_calendar
        return configure_calendar(self.gateway, warehouse, store_code, body, actor)

    def calendar_context(self, warehouse: int, store_code: str, day: str, actor: str) -> dict:
        from .store_calendar import calendar_context
        return calendar_context(self.gateway, warehouse, store_code, day, actor)

    def set_calendar_exception(self, operation: str, body: dict, actor: str) -> dict:
        from .store_calendar import set_exception
        return set_exception(self.gateway, operation, body, actor)

    def list(self, warehouse: int | None, limit: int, actor: str) -> list[dict]:
        from .store_order_reads import list_store_orders
        return list_store_orders(self.gateway, warehouse, limit, actor)

    def get(self, order_id: int, actor: str) -> dict:
        from .store_order_reads import store_order_detail
        return store_order_detail(self.gateway, order_id, actor)
