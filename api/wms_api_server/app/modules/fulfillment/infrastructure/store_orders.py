"""One transaction: immutable SAP demand, existing customer order and message result."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ..domain.store_order import read_order, calendar, positive
from ..application.ports import StoreOrderConflict


class StoreOrders:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, raw: bytes, actor: str) -> dict:
        data = read_order(raw)
        received = datetime.now(timezone.utc)
        with self.gateway.transaction('NI02 receive immutable SAP customer demand') as cur:
            cur.execute('lock table RRL_SAP_STORE_ORDER in share row exclusive mode')
            cur.execute('select PAYLOAD_HASH,RESULT_JSON from RRL_SAP_STORE_MESSAGE where SENDER=:s and MESSAGE_ID=:m', {'s':data['Sender'],'m':data['MessageId']})
            old = cur.fetchone()
            if old:
                if old[0]!=data['payload_hash']:
                    raise StoreOrderConflict('MessageId payload conflict')
                return {**json.loads(self._text(old[1])), 'idempotent': True}
            cur.execute('select CUSTOMER_ORDER_ID,CONTENT_HASH,RESULT_JSON from RRL_SAP_STORE_ORDER where SENDER=:s and ORDER_NUMBER=:n', {'s':data['Sender'],'n':data['OrderNumber']})
            previous = cur.fetchone()
            if previous:
                if previous[1]!=data['content_hash']:
                    raise StoreOrderConflict('Changes to an imported SAP customer order are forbidden')
                result = {**json.loads(self._text(previous[2])), 'idempotent': True}
            else:
                store, times = self._destination(cur,data,received)
                cur.execute('select RRL_CUSTOMER_ORDER_SQ.nextval from dual')
                order_id = int(cur.fetchone()[0])
                cur.execute("""insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,CUSTOMER_STORE_MAP_ID,WARE_ID,ORDER_DATE,SHIPMENT_DATE,ROUTE_ID,DOCK_ID,STATUS,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)
                  values(:id,:n,:customer,:store,:w,:od,:ship,:route,:dock,:status,'SAP_RETAIL',sysdate,:actor)""",
                  {'id':order_id,'n':data['OrderNumber'],'customer':store[1],'store':store[0],'w':int(data['WarehouseId']),
                   'od':datetime.fromisoformat(data['OrderDate']),'ship':times['shipment'],'route':store[3],'dock':store[4],
                   'status':'DRAFT' if times['late'] else 'IMPORTED','actor':actor[:50]})
                self._lines(cur,order_id,data,actor)
                result = {'customer_order_id':order_id,'order_number':data['OrderNumber'], 'admission_status':'PENDING_LATE' if times['late'] else 'ACCEPTED',
                          'operational_date':data['OperationalDate'],'picking_start_at':times['picking_start'].isoformat(),
                          'picking_finish_at':times['picking_finish'].isoformat(),'shipment_at':times['shipment'].isoformat(),
                          'delivery_date':data['DeliveryDate'],'utc_offset_minutes':times['offset_minutes'],'idempotent':False}
                cur.setinputsizes(raw=oracledb.DB_TYPE_CLOB,parsed=oracledb.DB_TYPE_CLOB,result=oracledb.DB_TYPE_CLOB)
                cur.execute("""insert into RRL_SAP_STORE_ORDER(CUSTOMER_ORDER_ID,SENDER,ORDER_NUMBER,CONTENT_HASH,RAW_XML,DEMAND_JSON,RESULT_JSON,ADMISSION_STATUS,OPERATIONAL_DATE,DELIVERY_DATE,PICKING_START_AT,PICKING_FINISH_AT,SHIPMENT_AT,UTC_OFFSET_MINUTES)
                  values(:id,:s,:n,:h,:raw,:parsed,:result,:status,:day,:delivery,:startat,:finishat,:shipment,:offsetm)""",
                  {'id':order_id,'s':data['Sender'],'n':data['OrderNumber'],'h':data['content_hash'],'raw':raw.decode('utf-8-sig'),
                   'parsed':json.dumps(data),'result':json.dumps(result),'status':result['admission_status'],
                   'day':datetime.fromisoformat(data['OperationalDate']),'delivery':datetime.fromisoformat(data['DeliveryDate']),
                   'startat':times['picking_start'],'finishat':times['picking_finish'],'shipment':times['shipment'],'offsetm':times['offset_minutes']})
            cur.setinputsizes(raw=oracledb.DB_TYPE_CLOB,result=oracledb.DB_TYPE_CLOB)
            cur.execute('insert into RRL_SAP_STORE_MESSAGE(SENDER,MESSAGE_ID,CUSTOMER_ORDER_ID,PAYLOAD_HASH,RAW_XML,RESULT_JSON,CREATED_BY) values(:s,:m,:id,:h,:raw,:result,:a)',
                        {'s':data['Sender'],'m':data['MessageId'],'id':result['customer_order_id'],'h':data['payload_hash'],'raw':raw.decode('utf-8-sig'),'result':json.dumps(result),'a':actor})
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
        cur.execute('select UTC_OFFSET_MINUTES,DELIVERY_WEEKDAYS,ALLOW_SAME_DAY from RRL_SAP_STORE_CALENDAR where WARE_ID=:w and CUSTOMER_STORE_MAP_ID=:s', {'w':int(data['WarehouseId']),'s':store[0]})
        settings = cur.fetchone()
        if not settings:
            raise ValueError('Configure warehouse/store source book and calendar before importing demand')
        times = calendar(data,settings[0],settings[1],bool(settings[2]),received)
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
            factors = [Decimal(u['ratio']) for u in json.loads(self._text(units)) if u['uom']==line['unit']]
            if base==line['unit']:
                ratio=Decimal(1)
            elif len(factors)==1:
                ratio=factors[0]
            else:
                raise ValueError('Missing/ambiguous SAP unit conversion')
            qty = positive(str(Decimal(line['quantity'])*ratio))
            weight = Decimal(line['target_weight_kg']) if line['target_weight_kg'] else (qty if base.upper()=='KG' else None)
            cur.execute("""insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,ORDER_WEIGHT,WARE_ID,STATUS,CREATED_AT,CREATED_BY)
              values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:id,:line,:a,:name,:u,:q,:weight,:w,'OPEN',sysdate,:actor)""",
              {'id':order_id,'line':line['line_number'],'a':line['material'],'name':name,'u':base,'q':qty,'weight':weight,'w':int(data['WarehouseId']),'actor':actor[:50]})

    def configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict:
        with self.gateway.transaction('NI02 configure existing store source book') as cur:
            cur.execute('select CUSTOMER_STORE_MAP_ID from RRL_CUSTOMER_STORE_MAP where STORE_CODE=:s and ACTIVE=1', {'s':store_code})
            rows=cur.fetchall()
            if len(rows)!=1:
                raise ValueError('Store code must identify one existing active address')
            cur.execute('select count(*) from RRL_WARES where ID=:w', {'w':warehouse})
            if cur.fetchone()[0]!=1:
                raise ValueError('Unknown warehouse')
            cur.execute("""merge into RRL_SAP_STORE_CALENDAR d using(select :w WARE_ID,:s CUSTOMER_STORE_MAP_ID from dual)t on(d.WARE_ID=t.WARE_ID and d.CUSTOMER_STORE_MAP_ID=t.CUSTOMER_STORE_MAP_ID)
              when matched then update set UTC_OFFSET_MINUTES=:offsetm,DELIVERY_WEEKDAYS=:days,ALLOW_SAME_DAY=:same,UPDATED_BY=:actor,UPDATED_AT=systimestamp
              when not matched then insert(WARE_ID,CUSTOMER_STORE_MAP_ID,UTC_OFFSET_MINUTES,DELIVERY_WEEKDAYS,ALLOW_SAME_DAY,UPDATED_BY)
              values(:w,:s,:offsetm,:days,:same,:actor)""", {'w':warehouse,'s':rows[0][0],'offsetm':body['utc_offset_minutes'],'days':','.join(str(n) for n in sorted(set(body['delivery_weekdays']))),'same':int(body['allow_same_day']),'actor':actor})
        return {'warehouse_id':warehouse,'store_code':store_code,**body}

    def list(self, warehouse: int | None, limit: int = 100) -> list[dict]:
        return self.gateway.fetch_all("""select s.CUSTOMER_ORDER_ID,s.SENDER,s.ORDER_NUMBER,s.ADMISSION_STATUS,s.OPERATIONAL_DATE,s.DELIVERY_DATE,s.PICKING_START_AT,s.PICKING_FINISH_AT,s.SHIPMENT_AT,c.WARE_ID,m.STORE_CODE,m.ADDRESS_TEXT,c.STATUS
          from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID
          join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=c.CUSTOMER_STORE_MAP_ID
          where (:w is null or c.WARE_ID=:w) order by s.CREATED_AT desc fetch first :lim rows only""", {'w':warehouse,'lim':limit})

    def get(self, order_id: int) -> dict:
        rows = self.gateway.fetch_all('select * from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:id', {'id':order_id})
        if not rows:
            raise LookupError('SAP store order not found')
        result=rows[0]
        result['demand_json']=json.loads(result['demand_json'])
        result['result_json']=json.loads(result['result_json'])
        return result

    @staticmethod
    def _text(value: object) -> str:
        return value.read() if hasattr(value,'read') else str(value)
