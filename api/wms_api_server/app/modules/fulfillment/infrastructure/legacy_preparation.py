"""SAP adapter to legacy ORDERS/SBORKA writers; no replacement pallet splitter."""
from collections import defaultdict
from decimal import Decimal
from hashlib import sha256
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ..application.ports import StoreOrderConflict


class LegacyPreparation:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def prepare(self, order_id: int, payload: dict, actor: str) -> dict:
        digest = sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        with self.gateway.transaction('SAP demand to existing legacy ST preparation') as cur:
            cur.execute("""select s.ADMISSION_STATUS,s.PREPARATION_HASH,s.PREPARATION_JSON,c.WARE_ID,m.LEGACY_ADDR,c.SHIPMENT_DATE
              from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID
              join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=c.CUSTOMER_STORE_MAP_ID where s.CUSTOMER_ORDER_ID=:id for update of s.PREPARATION_HASH""", {'id':order_id})
            row=cur.fetchone()
            if not row:
                raise LookupError('SAP customer order not found')
            if row[1]:
                if row[1]!=digest:
                    raise StoreOrderConflict('Prepared SAP order already has another layout/operation')
                return {**json.loads(self._text(row[2])), 'idempotent':True}
            if row[0]!='ACCEPTED':
                raise StoreOrderConflict('Late/rejected order requires logistics admission')
            if not row[4]:
                raise ValueError('Configure existing legacy delivery address before preparing ST')
            st_number='SAP_'+str(order_id)
            # The old functions deduplicate by unqualified string identity: never claim foreign rows.
            cur.execute('lock table RRL_ORDERS in share row exclusive mode')
            cur.execute('select count(*) from RRL_ORDERS where ORD_NUMBER=:n', {'n':st_number})
            if cur.fetchone()[0]:
                raise StoreOrderConflict('Legacy order identity already exists outside this SAP preparation')
            cur.execute('select count(*) from RRL_SBORKA_PALLETS where ST_NUMBER=:n', {'n':st_number})
            if cur.fetchone()[0]:
                raise StoreOrderConflict('ST identity already exists outside this SAP preparation')
            quantities=self._demand(cur,order_id,payload)
            legacy_id=cur.callfunc('ORDERS.CREATE_ORDER',oracledb.DB_TYPE_NUMBER,[st_number,row[5],row[3],row[4],'1',row[5],actor[:50]])
            if not legacy_id or legacy_id<=0:
                raise ValueError('Legacy order writer failed')
            articles=self._legacy_rows(cur,legacy_id,row[3],quantities)
            identifiers=[]
            for index,pallet in enumerate(payload['pallets'],1):
                uid=f'OP_{st_number}_{index}'
                cur.execute('select count(*) from RRL_SBORKA_PALLETS where PALLET_UID=:p', {'p':uid})
                if cur.fetchone()[0]:
                    raise StoreOrderConflict('Legacy pallet identifier already exists')
                pallet_id=cur.callfunc('RRL_SBORKA_PALLETS_ADD2',oracledb.DB_TYPE_NUMBER,[st_number,row[4],index,uid,'1',row[5],'',actor[:50],row[3]])
                if not pallet_id or pallet_id<=0:
                    raise ValueError('Existing ST pallet writer failed')
                cur.execute('update RRL_SBORKA_PALLETS set ORIGINAL_ORDER_NUMBER=:n,ORIGINAL_ST_NUMBER=:n,CONDITION=0 where ID=:id', {'n':st_number,'id':pallet_id})
                self._pallet_rows(cur,uid,pallet['lines'],articles,row[3],st_number)
                cur.execute("""insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)
                  values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,:id,:pid,:p,:addr,'PLANNED',0,0,'SAP_RETAIL',sysdate,:a)""", {'id':order_id,'pid':pallet_id,'p':uid,'addr':row[4],'a':actor[:50]})
                identifiers.append(uid)
            cur.execute('update RRL_CUSTOMER_ORDER set LEGACY_ORDER_ID=:legacy where CUSTOMER_ORDER_ID=:id', {'legacy':legacy_id,'id':order_id})
            result={'customer_order_id':order_id,'legacy_order_id':int(legacy_id),'st_number':st_number,'pallet_identifiers':identifiers,
                    'status':'ST_PREPARED','layout_source':'OPERATOR','prepared_by':actor,'idempotent':False}
            cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)
            cur.execute('update RRL_SAP_STORE_ORDER set PREPARATION_HASH=:h,PREPARATION_JSON=:body,PREPARED_AT=systimestamp where CUSTOMER_ORDER_ID=:id', {'id':order_id,'h':digest,'body':json.dumps(result)})
        return result

    def _demand(self, cur: oracledb.Cursor, order_id: int, payload: dict) -> dict:
        cur.execute("select ARTICUL,to_char(sum(ORDER_QTY),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY,min(UNIT_CODE),count(distinct UNIT_CODE) from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:id group by ARTICUL", {'id':order_id})
        demand={a:(Decimal(q),u) for a,q,u,count in cur.fetchall() if count==1}
        totals=defaultdict(Decimal)
        for pallet in payload['pallets']:
            seen=set()
            for item in pallet['lines']:
                if item['articul'] in seen:
                    raise ValueError('One legacy pallet row per article; combine identical articles in its layout')
                seen.add(item['articul']);totals[item['articul']]+=Decimal(item['quantity'])
        if dict(totals)!={a:value[0] for a,value in demand.items()}:
            raise ValueError('Explicit pallet layout must preserve entire original customer demand exactly')
        return demand

    def _legacy_rows(self, cur: oracledb.Cursor, legacy_id: int, warehouse: int, demand: dict) -> dict:
        result={}
        for articul,(quantity,unit) in demand.items():
            cur.execute('select a.ACTICUL from RRL_ARTICULS a join RRL_CELLS c on c.CELL=a.CELL where a.ACTICUL=:a and c.WARE_ID=:w', {'a':articul,'w':warehouse})
            if len(cur.fetchall())!=1:
                raise ValueError('Legacy picking cell must uniquely belong to source warehouse')
            status=cur.callfunc('ORDERS.ADD_ORDER_ROW',oracledb.DB_TYPE_NUMBER,[legacy_id,articul,quantity,warehouse])
            if status!=1:
                raise ValueError('Legacy order row requires actual packaging dimensions and weight')
            cur.execute("""select r.ID,to_char(r.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),r.SHORTNAME,a.BARCODE_SHT,r.TAREWEIGHT,r.TARESIZE,r.SORTFIELD,
              to_char(r.PACK_COUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),to_char(r.ORDER_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
              from RRL_ORDER_ROWS r join RRL_ARTICULS a on a.ACTICUL=r.ARTICUL where r.ORDER_ID=:id and r.ARTICUL=:a""", {'id':legacy_id,'a':articul})
            rows=cur.fetchall()
            if len(rows)!=1 or Decimal(rows[0][1])!=quantity:
                raise ValueError('Legacy box rounding would change SAP quantity; correct packaging/layout before preparing ST')
            row=rows[0]
            if not row[4] or row[4]<=0 or not row[5] or row[5]<=0 or not row[7] or Decimal(row[7])<=0 or not row[8] or Decimal(row[8])<=0:
                raise ValueError('Real legacy logistics parameters are required; zero defaults cannot plan transport')
            cur.execute('update RRL_ORDER_ROWS set EI=:u,QUANTITY_PLANNED=QUANTITY where ID=:id', {'id':row[0],'u':unit})
            result[articul]=(row,unit,quantity)
        return result

    def _pallet_rows(self, cur: oracledb.Cursor, uid: str, lines: list[dict], articles: dict, warehouse: int, st_number: str) -> None:
        for item in lines:
            row,unit,total=articles[item['articul']]
            quantity=Decimal(item['quantity']);fraction=quantity/total
            packs=Decimal(row[7])*fraction
            if packs!=packs.to_integral_value():
                raise ValueError('Current legacy row writer requires whole packaging units in each pallet layout')
            weight=Decimal(row[8])*fraction
            row_id=cur.callfunc('RRL_SBORKA_PALLET_ROWS_ADD4',oracledb.DB_TYPE_NUMBER,[uid,item['articul'],row[2],row[3],unit,row[4],'',weight,row[5],quantity,row[6] or 0,None,st_number,warehouse,int(packs)])
            if not row_id or row_id<=0:
                raise ValueError('Existing ST article writer failed')

    @staticmethod
    def _text(value: object) -> str:
        return value.read() if hasattr(value,'read') else str(value)
