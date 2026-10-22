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
from .trade_capacity import capacity_context, _box, _document
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
    """Confirmed top-ups of this trip; `extra` is the part not yet in the TRIP document (only that occupies more space)."""
    cur.execute("select NEED_ID,SKU_ID,APPROVED_BOXES,SAP_ORDER_ID,UNITS_PER_BOX from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=:w and TRIP_ID=:t "
                "and STATUS in('CONFIRMED','SAP_ACCEPTED') order by PROPOSAL_ID", w=ware, t=trip_id)
    out = []
    for need, sku, boxes, order, units in cur.fetchall():
        inside = _in_trip_boxes(cur, ware, trip, order, int(units))
        out.append(dict(need_id=need, sku_id=sku, inside=min(inside, Decimal(boxes)), extra=max(Decimal(0), Decimal(boxes) - inside)))
    return out


def _terms(cur: Any, ware: int, trip: dict, recipient: str, sku: str) -> dict:
    """Owner/MRC/shelf-life come from the main order of the same recipient and goods; unknown terms block the top-up."""
    found = set()
    for assignment in trip['orders']:
        order, _ = _document(cur, ware, 'ORDER', assignment['order_id'])
        line = next((x for x in order['lines'] if x['line_id'] == assignment['line_id']), None)
        if order.get('recipient_id') == recipient and line and line['sku_id'] == sku:
            found.add((line['source_owner_id'], line['target_owner_id'], str(line['mrc']), int(line.get('min_osg_days') or 0)))
    if not found:
        raise TradeTransportError('TOPUP_STOCK_TERMS_REQUIRED', 409)
    if len(found) > 1:
        raise TradeTransportError('TOPUP_STOCK_TERMS_AMBIGUOUS', 409)
    owner, target, mrc, days = found.pop()
    departure = date.fromisoformat(trip['planned_departure_at'][:10])
    return dict(source_owner_id=owner, target_owner_id=target, mrc=mrc, min_expiry_date=(departure + timedelta(days=days)).isoformat())


def _stock_boxes(cur: Any, ware: int, article: str, sku: str, terms: dict, units_per_box: int) -> int:
    """Eligible free whole boxes above the unallocated quantity of open main orders with the same terms."""
    expiry = date.fromisoformat(terms['min_expiry_date'])
    eligible = cur.callfunc('RRL_TRADE_TOPUP_READ.eligible_units', oracledb.DB_TYPE_NUMBER,
                            [ware, article, sku, terms['source_owner_id'], Decimal(terms['mrc']), expiry, units_per_box])
    protected = cur.callfunc('RRL_TRADE_TOPUP_READ.protected_units', oracledb.DB_TYPE_NUMBER,
                             [ware, sku, terms['source_owner_id'], Decimal(terms['mrc'])])
    return max(0, int((Decimal(eligible) - Decimal(protected)) // units_per_box))


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
    stock = _stock_boxes(cur, ware, sku_doc['wms_article_id'], need['sku_id'], terms, package['units_per_box'])
    fit = min(capacity['fitting_boxes'], stock)
    limit = 'SENDER_STOCK' if stock < capacity['fitting_boxes'] else 'CAPACITY' if capacity['fitting_boxes'] < requested else None
    return dict(need=need, capacity=capacity, proposed_boxes=fit, uncovered_boxes=str(remaining - fit), already_confirmed_boxes=str(confirmed_boxes),
                sender_stock_boxes=stock, limited_by=limit, article=sku_doc['wms_article_id'], **terms)


def allocate(cur: Any, ware: int, trip: str, body: TopupPreview, actor: str) -> dict:
    context = capacity_context(cur, ware, trip, actor)
    if context['started']:
        raise TradeTransportError('TOPUP_LOADING_ALREADY_STARTED', 409)
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
        identity = (need['recipient_id'], need['sku_id'])
        if identity in identities:
            raise TradeTransportError('TOPUP_DUPLICATE_RECIPIENT_SKU', 409)
        identities.add(identity)
        if need['expired']:
            raise TradeTransportError('TOPUP_NEED_EXPIRED:'+key, 409)
        if not datetime.fromisoformat(need['period_from']) <= departure <= datetime.fromisoformat(need['period_until']):
            raise TradeTransportError('TOPUP_NEED_HORIZON_MISMATCH:'+key, 409)
        primary = sum((p['boxes']*p['units_per_box'] for p in context['planned']
                       if (p['recipient_id'],p['sku_id']) == identity), Decimal(0))
        if primary != Decimal(need['current_trip_quantity']):
            raise TradeTransportError('TOPUP_PRIMARY_SNAPSHOT_MISMATCH:'+key, 409)
        # The part of this trip's top-up already inside the TRIP is in need.current_trip_quantity (checked above): not again.
        inside = sum((t['inside'] for t in confirmed_topups if t['need_id'] == key), Decimal(0))
        confirmed = Decimal(cur.callfunc('RRL_TRADE_TOPUP_READ.need_confirmed_boxes', oracledb.DB_TYPE_NUMBER, [ware, key, None])) - inside
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
                  sender_stock_checked=True, route_checked=False, stacking_rules_checked=False,
                  loading_mode='BOX_FIXED_ORIENTATION')
    # Time-dependent age is displayed but is not an identity/version input.
    basis = dict(warehouse_id=ware, trip_id=trip, trip_version=context['version'],
                 trip=context['trip'],packages=packages,
                 capacity_kg=context['max_weight'],capacity_m3=context['max_volume'],dimensions=context['dimensions'],
                 profile_version=result['profile_version'], profile_base_hash=result['profile_base_hash'],
                 order_versions=result['order_versions'], max_age_minutes=body.max_age_minutes,
                 items=[dict(need_id=x['need']['document_id'], version=x['need']['document_version'],
                             signature=x['need']['calculation_signature'], proposed_boxes=x['proposed_boxes']) for x in selected])
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
