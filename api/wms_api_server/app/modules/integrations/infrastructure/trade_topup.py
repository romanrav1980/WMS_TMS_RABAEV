"""Fit ordered recipient needs into one consistent trip snapshot; no reservations."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR
from hashlib import sha256
import json
from typing import Any
import oracledb
from ..contracts_trade_topup import TopupPreview
from ..contracts_trade_transport import TradeTransportError
from ..contracts_tradecase import TradecaseError
from ..domain.trade_capacity import box_capacity
from .trade_capacity import after_load_admission, capacity_context, _box, _document
from .trade_need import need_snapshot


def _in_trip_boxes(cur: Any, ware: int, trip: dict, order_id: str | None, units_per_box: int) -> Decimal:
    """Boxes of the SAP top-up order that the current TRIP document already carries (counted there with the main orders)."""
    if not order_id:
        return Decimal(0)
    total = Decimal(0)
    for assignment in trip['orders']:
        if assignment['order_id'] != order_id:
            continue
        order, _ = _document(cur, ware, 'ORDER', order_id)
        line = next((x for x in order['lines'] if x['line_id'] == assignment['line_id']), None)
        if line is None:
            raise TradeTransportError('TRADE_CAPACITY_ORDER_LINE_MISMATCH', 409)
        quantity = Decimal(str(assignment['quantity']))
        total += quantity if line['uom'] == 'BOX' else quantity / units_per_box
    return total


def _confirmed(cur: Any, ware: int, trip_id: str, trip: dict) -> list[dict]:
    """Confirmed top-ups of this trip; `extra` is the part not yet in the TRIP document (only that occupies more space).
    C-0174: the extra is still held for this trip only by the proposal's ACTIVE holds. After the wave adopted them (ADOPTED), the
    TRIP document alone carries the order; a part later left out of a reduced trip is not this trip's load (no phantom boxes)."""
    cur.execute("select p.NEED_ID,p.SKU_ID,p.APPROVED_BOXES,p.SAP_ORDER_ID,p.UNITS_PER_BOX,"
                "(select nvl(sum(h.BASE_QTY),0) from RRL_TRADE_TOPUP_HOLD h where h.PROPOSAL_ID=p.PROPOSAL_ID and h.STATUS='ACTIVE')"
                " from RRL_TRADE_TOPUP_PROPOSAL p where p.WARE_ID=:w and p.TRIP_ID=:t and p.STATUS in('CONFIRMED','SAP_ACCEPTED') order by p.PROPOSAL_ID", w=ware, t=trip_id)
    out = []
    for need, sku, boxes, order, units, held_units in cur.fetchall():
        inside = _in_trip_boxes(cur, ware, trip, order, int(units))
        held = Decimal(held_units) / int(units)
        out.append(dict(need_id=need, sku_id=sku, inside=min(inside, Decimal(boxes)), extra=min(held, max(Decimal(0), Decimal(boxes) - inside))))
    return out


def _terms(cur: Any, ware: int, trip: dict, recipient: str, sku: str) -> dict:
    """Read receiver and SKU terms independently of orders; never guess an owner or MRC."""
    recipient_doc, _ = _document(cur, ware, 'RECIPIENT', recipient)
    sku_doc, _ = _document(cur, ware, 'SKU', sku)
    owners, prices = recipient_doc['permitted_source_owners'], sku_doc['permitted_mrc']
    if len(owners) != 1 or len(prices) != 1:
        raise TradeTransportError('TOPUP_STOCK_TERMS_AMBIGUOUS', 409)
    _document(cur, ware, 'OWNER', owners[0])
    if recipient_doc['target_owner_id'] != owners[0]:
        _document(cur, ware, 'OWNER', recipient_doc['target_owner_id'])
    days = recipient_doc['min_osg_days']
    if recipient_doc.get('osg_basis') == 'DELIVERY_DATE':
        days += recipient_doc['lead_time_days']
    departure = date.fromisoformat(trip['planned_departure_at'][:10])
    return dict(source_owner_id=owners[0], target_owner_id=recipient_doc['target_owner_id'], mrc=str(prices[0]), min_expiry_date=(departure + timedelta(days=days)).isoformat())


def _stock_boxes(cur: Any, ware: int, article: str, sku: str, terms: dict, units_per_box: int) -> int:
    """Eligible free whole boxes above the unallocated quantity of open main orders with the same terms."""
    expiry = date.fromisoformat(terms['min_expiry_date'])
    eligible = cur.callfunc('RRL_TRADE_TOPUP_READ.eligible_units', oracledb.DB_TYPE_NUMBER,
                            [ware, article, sku, terms['source_owner_id'], Decimal(terms['mrc']), expiry, units_per_box])
    protected = cur.callfunc('RRL_TRADE_TOPUP_READ.protected_units', oracledb.DB_TYPE_NUMBER,
                             [ware, sku, terms['source_owner_id'], Decimal(terms['mrc'])])
    return max(0, int((Decimal(eligible) - Decimal(protected)) // units_per_box))


def _uncovered_confirmations(cur: Any, ware: int, key: str, need: dict) -> Decimal:
    """Forecast already covers matched SAP movements; subtract each confirmed top-up only once."""
    cur.execute("select APPROVED_BOXES,SAP_ORDER_ID from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=:w and NEED_ID=:n and STATUS in('CONFIRMED','SAP_ACCEPTED') order by PROPOSAL_ID fetch first 1001 rows only", w=ware,n=key)
    rows=cur.fetchall()
    if len(rows)>1000:raise TradeTransportError('TOPUP_CONFIRMATION_BOUND_1000',409)
    covered={x['supply_id']:Decimal(x['base_quantity'])/need['units_per_box'] for x in need['supplies']
             if x['accounted_as'] in {'CURRENT_TRIP','IN_TRANSIT','PLANNED_OTHER_TRIP','DELIVERED'}}
    total=sum((Decimal(boxes)for boxes,_ in rows),Decimal(0))
    matched=sum((min(Decimal(boxes),covered.get(order,Decimal(0)))for boxes,order in rows),Decimal(0))
    need['topup_need_boxes']=str(Decimal(need['additional_boxes'])+matched)
    return total-matched


def _item(cur: Any, ware: int, context: dict, planned: list, need: dict, confirmed_boxes: Decimal) -> dict:
    packages = context['packages']
    if need['sku_id'] not in packages:
        packages[need['sku_id']] = _box(cur, ware, need['sku_id'])
    package = packages[need['sku_id']]
    sku_doc, _ = _document(cur, ware, 'SKU', need['sku_id'])
    terms = _terms(cur, ware, context['trip'], need['recipient_id'], need['sku_id'])
    remaining = max(Decimal(0), Decimal(need['additional_boxes']) - confirmed_boxes)
    requested = int(remaining.to_integral_value(rounding=ROUND_FLOOR))
    capacity = box_capacity(context['max_weight'], context['max_volume'], context['dimensions'], planned, package, requested)
    if capacity['maximum_boxes'] is None:
        raise TradeTransportError('TOPUP_MIXED_PACKAGE_LAYOUT_REQUIRED', 409)
    stock = _stock_boxes(cur, ware, sku_doc['wms_article_id'], need['sku_id'], terms, package['units_per_box']) if capacity['fitting_boxes'] else None
    fit = min(capacity['fitting_boxes'], stock) if stock is not None else 0
    limit = 'SENDER_STOCK' if stock is not None and stock < capacity['fitting_boxes'] else 'CAPACITY' if capacity['fitting_boxes'] < requested else None
    return dict(need=need, capacity=capacity, proposed_boxes=fit, uncovered_boxes=str(remaining - fit), already_confirmed_boxes=str(confirmed_boxes),
                sender_stock_boxes=stock, limited_by=limit, article=sku_doc['wms_article_id'], **terms)


def allocate(cur: Any, ware: int, trip: str, body: TopupPreview, actor: str) -> dict:
    context = capacity_context(cur, ware, trip, actor)
    block = after_load_admission(context, None, datetime.now(timezone.utc))  # C-0161: loaded main cargo allowed; departure/route on facts
    if block:
        raise TradeTransportError(block, 409)
    planned = list(context['planned']);packages = context['packages']
    confirmed_topups = _confirmed(cur, ware, trip, context['trip'])
    for topup in confirmed_topups:
        if topup['extra']:
            if topup['sku_id'] not in packages:
                packages[topup['sku_id']] = _box(cur, ware, topup['sku_id'])
            planned.append(dict(packages[topup['sku_id']], boxes=topup['extra'], recipient_id=None))
    selected = [];identities = set();now = datetime.now(timezone.utc)
    departure = datetime.fromisoformat(context['trip']['planned_departure_at'].replace('Z', '+00:00'))
    for key in body.need_ids:
        need = need_snapshot(cur, ware, key, body.max_age_minutes, now)
        if not need['topup_enabled']:
            raise TradeTransportError('TOPUP_RECIPIENT_DISABLED:'+key,409)
        if need['forecast_kind']!='MOVEMENT':
            raise TradeTransportError('TOPUP_MOVEMENT_FORECAST_REQUIRED:'+key,409)
        days=need['topup_horizon_days']
        start,end=(datetime.fromisoformat(need[k])for k in ('period_from','period_until'))
        if days is None or end-start>timedelta(days=days) or end>departure+timedelta(days=days):
            raise TradeTransportError('TOPUP_RECIPIENT_HORIZON_EXCEEDED:'+key,409)
        block = after_load_admission(context, need['recipient_id'], now)
        if block:
            raise TradeTransportError(block + ':' + key, 409)
        identity = (need['recipient_id'], need['sku_id'])
        if identity in identities:
            raise TradeTransportError('TOPUP_DUPLICATE_RECIPIENT_SKU', 409)
        identities.add(identity)
        if need['expired']:
            raise TradeTransportError('TOPUP_NEED_EXPIRED:'+key, 409)
        if not datetime.fromisoformat(need['period_from']) <= departure <= datetime.fromisoformat(need['period_until']):
            raise TradeTransportError('TOPUP_NEED_HORIZON_MISMATCH:'+key, 409)
        confirmed = _uncovered_confirmations(cur, ware, key, need)
        item = _item(cur, ware, context, planned, need, confirmed)
        item['priority'] = len(selected)+1
        selected.append(item)
        if item['proposed_boxes']:
            planned.append(dict(packages[need['sku_id']], boxes=Decimal(item['proposed_boxes']), recipient_id=need['recipient_id']))
    result = dict(warehouse_id=ware, trip_id=trip, trip_version=context['version'],
                  profile_version=context['profile']['version'], profile_base_hash=context['profile']['base_hash'],
                  order_versions=context['orders'], items=selected,
                  proposed_boxes=sum(x['proposed_boxes'] for x in selected),
                  physical_execution=False, approval_available=False, topup_order_created=False,
                  sender_stock_checked=all(x['sender_stock_boxes'] is not None for x in selected), route_checked=False, stacking_rules_checked=False,
                  loading_mode='BOX_FIXED_ORIENTATION', loading_started=context['started'],
                  loaded=context['loaded'], floor_places_checked=False)
    # Time-dependent age is displayed but is not an identity/version input.
    basis = dict(warehouse_id=ware, trip_id=trip, trip_version=context['version'],
                 trip=context['trip'],packages=packages,
                 loaded=context['loaded'],
                 capacity_kg=context['max_weight'],capacity_m3=context['max_volume'],dimensions=context['dimensions'],
                 profile_version=result['profile_version'], profile_base_hash=result['profile_base_hash'],
                 order_versions=result['order_versions'], max_age_minutes=body.max_age_minutes,
                 items=[dict(need_id=x['need']['document_id'], version=x['need']['document_version'],
                             signature=x['need']['calculation_signature'], proposed_boxes=x['proposed_boxes'], need_boxes=x['need']['topup_need_boxes']) for x in selected])
    result['calculation_signature'] = sha256(json.dumps(basis,default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result


def topup_preview(gateway: Any, ware: int, trip: str, body: TopupPreview, actor: str) -> dict:
    try:
        with gateway.transaction('TRADECASE bounded topup allocation READ ONLY') as cur:
            cur.execute('set transaction read only')
            cur.execute("select RRL_ACCESS_API.allowed(:a,'tradecase_view','WAREHOUSE',:w)from dual",a=actor,w=str(ware))
            if cur.fetchone()[0] != 1:
                raise TradeTransportError('TRADECASE_ACCESS_DENIED',403)
            return allocate(cur,ware,trip,body,actor)
    except TradecaseError as exc:
        raise TradeTransportError(exc.code,exc.status) from exc
    except ValueError as exc:
        raise TradeTransportError('TOPUP_STORED_SNAPSHOT_INVALID',409) from exc
    except oracledb.DatabaseError as exc:
        raise TradeTransportError('TOPUP_READ_FAILED',503) from exc
