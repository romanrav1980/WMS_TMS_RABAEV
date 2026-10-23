"""Read one Oracle snapshot of the external plan and native package/vehicle dimensions."""
from datetime import datetime, timezone
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
    return dict(sku_id=sku,sku_version=version,units_per_box=doc['units_per_box'],weight=weight,volume=axes[0]*axes[1]*axes[2],dimensions=axes,article=doc.get('wms_article_id'))

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

def _loaded(cur:Any,ware:int,trip_id:str,trip:dict,planned:list[dict])->dict|None:
    """C-0161: physical load already in the vehicle, counted once. The main plan already contains these goods as theoretical boxes;
    only the confirmed packaging excess of each loaded place (actual gross/bounding minus its boxes) is added, never the load again."""
    cur.execute("select l.NATIVE_TASK_ID,upper(trim(t.TRANSPORT))from RRL_TRADE_TRIP_LINK l join RRL_TRANSPORT_TASK t on t.ID=l.NATIVE_TASK_ID where l.WARE_ID=:w and l.TRIP_ID=:t",w=ware,t=trip_id)
    link=cur.fetchone()
    if link is None:return None  # without a native binding nothing can have been loaded for this trip
    cur.execute("select LOAD_OPERATION_ID,STATUS,upper(trim(VEHICLE_NUMBER)),GROSS_WEIGHT_KG,BOUNDING_VOLUME_M3,COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS in('LOADED','DEPARTED')order by LOAD_OPERATION_ID fetch first 201 rows only",t=link[0])
    rows=[(op,status,vehicle,gross,volume,read_oracle_json(raw))for op,status,vehicle,gross,volume,raw in cur.fetchall()]
    if not rows:return None
    if len(rows)>200:raise TradeTransportError('TOPUP_AFTER_LOAD_FACT_BOUND_200',409)
    if any(r[1]=='DEPARTED'for r in rows):raise TradeTransportError('TOPUP_TRIP_DEPARTED',409)
    vehicle=str(trip['vehicle_id']).strip().upper()
    if link[1]!=vehicle or any(r[2]!=vehicle for r in rows):raise TradeTransportError('TOPUP_AFTER_LOAD_VEHICLE_MISMATCH',409)
    by_article={p['article']:p for p in planned if p.get('article')}
    planned_units:dict[str,Decimal]={}
    for p in planned:planned_units[p.get('article')]=planned_units.get(p.get('article'),Decimal(0))+p['boxes']*p['units_per_box']
    loaded_units:dict[str,Decimal]={};over_kg=Decimal(0);over_m3=Decimal(0)
    for _,_,_,gross,volume,composition in rows:
        if gross is None or volume is None or gross<=0 or volume<=0:raise TradeTransportError('TOPUP_AFTER_LOAD_FACT_MEASURE_REQUIRED',409)
        theory_kg=Decimal(0);theory_m3=Decimal(0)
        for node in composition.get('nodes',[]):
            if node.get('kind')!='STOCK':continue
            package=by_article.get(node.get('article'))
            if package is None:raise TradeTransportError('TOPUP_AFTER_LOAD_UNPLANNED_GOODS',409)
            if node.get('base_uom')!='EA':raise TradeTransportError('TOPUP_AFTER_LOAD_BASE_UOM_UNSUPPORTED',409)
            units=Decimal(str(node['quantity']));boxes=units/Decimal(package['units_per_box'])
            loaded_units[node['article']]=loaded_units.get(node['article'],Decimal(0))+units
            theory_kg+=boxes*package['weight'];theory_m3+=boxes*package['volume']
        over_kg+=max(Decimal(0),Decimal(str(gross))-theory_kg);over_m3+=max(Decimal(0),Decimal(str(volume))-theory_m3)
    if any(units>planned_units.get(article,Decimal(0))for article,units in loaded_units.items()):raise TradeTransportError('TOPUP_AFTER_LOAD_UNPLANNED_GOODS',409)
    return dict(native_task_id=int(link[0]),places=len(rows),operations=[r[0]for r in rows],overhead_kg=over_kg,overhead_m3=over_m3,
                loaded_units={k:str(v)for k,v in sorted(loaded_units.items())},recipients=sorted({p['recipient_id']for p in planned if p.get('recipient_id')}))


def after_load_admission(context:dict,recipient:str|None,now:datetime)->str|None:
    """C-0161: what blocks a top-up while main cargo is already in the vehicle; None when nothing known blocks it. Departure time and
    unloading order are judged on facts only: a trip with several stops carries no stop sequence in its documents, so access to the
    cargo of each stop cannot be proven and is refused explicitly instead of assumed."""
    if not context['started']:return None
    if datetime.fromisoformat(context['trip']['planned_departure_at'].replace('Z','+00:00'))<=now:return 'TOPUP_DEPARTURE_TIME_PASSED'
    recipients=context['loaded']['recipients']
    if len(recipients)!=1:return 'TOPUP_AFTER_LOAD_ROUTE_ORDER_UNVERIFIED'
    if recipient is not None and recipient!=recipients[0]:return 'TOPUP_AFTER_LOAD_RECIPIENT_NOT_ON_TRIP'
    return None


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
    loaded=_loaded(cur,ware,trip_id,trip,planned);started=loaded is not None
    cur.execute('select MAX_WEIGHT_KG from RRL_TR_VEHICLE where ID=:id',id=vehicles[0][0]);native_weight=cur.fetchone()[0]
    if native_weight is None or native_weight<=0:raise TradeTransportError('TRADE_CAPACITY_VEHICLE_WEIGHT_REQUIRED',409)
    max_weight=min(Decimal(str(trip['capacity_kg'])),Decimal(str(native_weight)))
    max_volume=min(Decimal(str(trip['capacity_m3'])),dimensions[0]*dimensions[1]*dimensions[2])
    if loaded:  # confirmed packaging of loaded places takes space the theoretical boxes do not describe
        max_weight-=loaded['overhead_kg'];max_volume-=loaded['overhead_m3']
    return dict(trip=trip,version=version,planned=planned,orders=orders,packages=packages,profile=profile,dimensions=dimensions,started=started,
                loaded=loaded,max_weight=max_weight,max_volume=max_volume)


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
            block=after_load_admission(context,None,datetime.now(timezone.utc))
            if started:result.update(loaded_places=context['loaded']['places'],loaded_overhead_kg=str(context['loaded']['overhead_kg']),
                                     loaded_overhead_m3=str(context['loaded']['overhead_m3']),floor_places_checked=False)
            if block:result.update(maximum_boxes=None,fitting_boxes=None,remaining_boxes=None,blocking_reason=block)
            elif result['maximum_boxes']is None:result['blocking_reason']='MIXED_PACKAGE_LAYOUT_REQUIRED'
            else:result['blocking_reason']=None
            result['calculation_signature']=sha256(json.dumps(dict(result,packages=packages),default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            return result
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],'code',0)
        raise TradeTransportError('TRADE_CAPACITY_READ_FAILED',403 if code==20882 else 503)from exc
