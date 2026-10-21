"""Read one Oracle snapshot of the external plan and native package/vehicle dimensions."""
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trade_transport import TradeTransportError
from ..domain.trade_capacity import box_capacity

def _document(cur:Any,ware:int,kind:str,key:str)->tuple[dict,int]:
    cur.execute("select BODY_JSON,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE=:k and EXTERNAL_ID=:id and STATUS='ACCEPTED'",w=ware,k=kind,id=key)
    row=cur.fetchone()
    if row is None:raise TradeTransportError('TRADE_CAPACITY_SOURCE_MISSING',409)
    body=read_oracle_json(row[0])
    if body.get('cancelled')or body.get('active')is False:raise TradeTransportError('TRADE_CAPACITY_SOURCE_INACTIVE',409)
    return body,int(row[1])

def _box(cur:Any,ware:int,sku:str)->dict:
    doc,version=_document(cur,ware,'SKU',sku)
    cur.execute('select COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:a',a=doc.get('wms_article_id'))
    row=cur.fetchone()
    if row is None or any(v is None or v<=0 for v in row):raise TradeTransportError('TRADE_CAPACITY_PACKAGE_MEASUREMENTS_REQUIRED',409)
    if row[0]!=doc['units_per_box']:raise TradeTransportError('TRADE_CAPACITY_PACKAGE_COEFFICIENT_MISMATCH',409)
    axes=tuple(Decimal(str(x))for x in row[2:]);weight=Decimal(str(row[1]))
    return dict(sku_id=sku,sku_version=version,units_per_box=doc['units_per_box'],weight=weight,volume=axes[0]*axes[1]*axes[2],dimensions=axes)

def _planned(cur:Any,ware:int,trip:dict,actor:str)->tuple[list[dict],list[dict],dict[str,dict]]:
    items=[];versions=[];boxes={};orders={};bound_lines={};checked_owners=set()
    for assignment in trip['orders']:
        identity=assignment['order_id']
        if identity not in orders:
            orders[identity]=_document(cur,ware,'ORDER',identity)
            versions.append(dict(order_id=identity,version=orders[identity][1]))
            cur.execute('select h.DOCUMENT_VERSION,l.EXTERNAL_LINE_ID,l.SKU_ID,l.SKU_VERSION from RRL_TRADE_ORDER_LINK h join RRL_TRADE_ORDER_LINE l on l.CUSTOMER_ORDER_ID=h.CUSTOMER_ORDER_ID where h.WARE_ID=:w and h.EXTERNAL_ID=:id',w=ware,id=identity)
            bound_lines[identity]={}
            for order_version,line_id,sku_id,sku_version in cur:
                if order_version!=orders[identity][1]:raise TradeTransportError('TRADE_CAPACITY_ORDER_BINDING_STALE',409)
                if line_id in bound_lines[identity]:raise TradeTransportError('TRADE_CAPACITY_ORDER_BINDING_AMBIGUOUS',409)
                bound_lines[identity][line_id]=(sku_id,int(sku_version))
        order=orders[identity][0]
        if order.get('order_kind')=='BUYOUT':raise TradeTransportError('TRADE_CAPACITY_SHIPMENT_ORDER_REQUIRED',409)
        line=next((x for x in order['lines']if x['line_id']==assignment['line_id']),None)
        if line is None or Decimal(str(assignment['quantity']))>Decimal(str(line['quantity'])):raise TradeTransportError('TRADE_CAPACITY_ORDER_LINE_MISMATCH',409)
        owner_pair=(line['source_owner_id'],line['target_owner_id'])
        if owner_pair not in checked_owners:
            cur.execute('select RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:src,0),RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:dst,0)from dual',a=actor,w=ware,src=owner_pair[0],dst=owner_pair[1])
            if max(cur.fetchone())!=1:raise TradeTransportError('TRADE_OWNER_ACCESS_DENIED',403)
            checked_owners.add(owner_pair)
        if line['sku_id']not in boxes:boxes[line['sku_id']]=_box(cur,ware,line['sku_id'])
        package=boxes[line['sku_id']]
        bound=bound_lines[identity]
        if bound and bound.get(assignment['line_id'])!=(line['sku_id'],package['sku_version']):raise TradeTransportError('TRADE_CAPACITY_BOUND_SKU_VERSION_CHANGED',409)
        quantity=Decimal(str(assignment['quantity']))
        n=quantity if line['uom']=='BOX'else quantity/Decimal(package['units_per_box'])
        if n!=n.to_integral_value():raise TradeTransportError('TRADE_CAPACITY_WHOLE_BOXES_REQUIRED',409)
        items.append(dict(package,boxes=n,recipient_id=order['recipient_id']))
    return items,versions,boxes

def capacity_context(cur:Any,ware:int,trip_id:str,actor:str)->dict:
    trip,version=_document(cur,ware,'TRIP',trip_id)
    planned,orders,packages=_planned(cur,ware,trip,actor)
    cur.execute('select ID from RRL_TR_VEHICLE where NUM=:v and nvl(DELETED,0)=0',v=trip['vehicle_id']);vehicles=cur.fetchall()
    if len(vehicles)!=1:raise TradeTransportError('TRADE_CAPACITY_VEHICLE_MAPPING_REQUIRED',409)
    profile=read_oracle_json(cur.callfunc('RRL_VEHICLE_PROFILE_API.describe_profile',oracledb.DB_TYPE_CLOB,[vehicles[0][0]]))
    if profile.get('state')!='READY':raise TradeTransportError('TRADE_CAPACITY_VEHICLE_PROFILE_STALE',409)
    data=profile.get('profile',profile)
    dimensions=tuple(Decimal(str((data.get(k)or 0)))/1000 for k in ['cargo_length_mm','cargo_width_mm','cargo_height_mm'])
    if any(d<=0 for d in dimensions):raise TradeTransportError('TRADE_CAPACITY_VEHICLE_DIMENSIONS_REQUIRED',409)
    cur.execute("select count(*)from RRL_TRADE_TRIP_LINK l join RRL_TT_HU_LOAD_FACT f on f.TT_ID=l.NATIVE_TASK_ID where l.WARE_ID=:w and l.TRIP_ID=:t and f.STATUS in('LOADED','DEPARTED')",w=ware,t=trip_id)
    started=cur.fetchone()[0]>0
    cur.execute('select MAX_WEIGHT_KG from RRL_TR_VEHICLE where ID=:id',id=vehicles[0][0]);native_weight=cur.fetchone()[0]
    if native_weight is None or native_weight<=0:raise TradeTransportError('TRADE_CAPACITY_VEHICLE_WEIGHT_REQUIRED',409)
    max_weight=min(Decimal(str(trip['capacity_kg'])),Decimal(str(native_weight)))
    max_volume=min(Decimal(str(trip['capacity_m3'])),dimensions[0]*dimensions[1]*dimensions[2])
    return dict(trip=trip,version=version,planned=planned,orders=orders,packages=packages,profile=profile,dimensions=dimensions,started=started,max_weight=max_weight,max_volume=max_volume)


def capacity_preview(gateway:Any,ware:int,trip_id:str,sku_id:str,requested:int,actor:str)->dict:
    try:
        with gateway.transaction('TRADECASE bounded whole-box capacity preview READ ONLY')as cur:
            cur.execute('set transaction read only')
            cur.execute("select RRL_ACCESS_API.allowed(:a,'tradecase_view','WAREHOUSE',:w)from dual",a=actor,w=str(ware))
            if cur.fetchone()[0]!=1:raise TradeTransportError('ACCESS_DENIED',403)
            context=capacity_context(cur,ware,trip_id,actor)
            trip,version,planned,orders,packages,profile,dimensions,started,max_weight,max_volume=(context[k]for k in ['trip','version','planned','orders','packages','profile','dimensions','started','max_weight','max_volume'])
            if sku_id not in packages:packages[sku_id]=_box(cur,ware,sku_id)
            result=box_capacity(max_weight,max_volume,dimensions,planned,packages[sku_id],requested)
            result.update(warehouse_id=ware,trip_id=trip_id,trip_version=version,sku_id=sku_id,order_versions=orders,profile_version=profile['version'],profile_base_hash=profile['base_hash'],
                          capacity_kg=str(max_weight),capacity_m3=str(max_volume),loading_started=started,loading_mode='BOX_FIXED_ORIENTATION',operational_admission=False,
                          stock_eligibility_checked=False,route_eligibility_checked=False,stacking_rules_checked=False,approval_available=False)
            if started:result.update(maximum_boxes=None,fitting_boxes=None,remaining_boxes=None,blocking_reason='LOAD_ALREADY_STARTED')
            elif result['maximum_boxes']is None:result['blocking_reason']='MIXED_PACKAGE_LAYOUT_REQUIRED'
            else:result['blocking_reason']=None
            result['calculation_signature']=sha256(json.dumps(dict(result,packages=packages),default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            return result
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],'code',0)
        raise TradeTransportError('TRADE_CAPACITY_READ_FAILED',403 if code==20882 else 503)from exc
