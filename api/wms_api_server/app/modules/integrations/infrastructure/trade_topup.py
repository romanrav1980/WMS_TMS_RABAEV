"""Fit ordered recipient needs into one consistent trip snapshot; no reservations."""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR
from hashlib import sha256
import json
from typing import Any
import oracledb
from ..contracts_trade_topup import TopupPreview
from ..contracts_trade_transport import TradeTransportError
from ..contracts_tradecase import TradecaseError
from ..domain.trade_capacity import box_capacity
from .trade_capacity import capacity_context, _box
from .trade_need import need_snapshot


def allocate(cur: Any, ware: int, trip: str, body: TopupPreview, actor: str) -> dict:
    context = capacity_context(cur, ware, trip, actor)
    if context['started']:
        raise TradeTransportError('TOPUP_LOADING_ALREADY_STARTED', 409)
    planned = list(context['planned']);packages = context['packages']
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
        if need['sku_id'] not in packages:
            packages[need['sku_id']] = _box(cur, ware, need['sku_id'])
        package = packages[need['sku_id']]
        requested = int(Decimal(need['additional_boxes']).to_integral_value(rounding=ROUND_FLOOR))
        capacity = box_capacity(context['max_weight'], context['max_volume'], context['dimensions'], planned, package, requested)
        if capacity['maximum_boxes'] is None:
            raise TradeTransportError('TOPUP_MIXED_PACKAGE_LAYOUT_REQUIRED', 409)
        fit = capacity['fitting_boxes']
        selected.append(dict(priority=len(selected)+1, need=need, capacity=capacity, proposed_boxes=fit,
                             uncovered_boxes=str(Decimal(need['additional_boxes'])-fit)))
        if fit:
            planned.append(dict(package, boxes=Decimal(fit), recipient_id=need['recipient_id']))
    result = dict(warehouse_id=ware, trip_id=trip, trip_version=context['version'],
                  profile_version=context['profile']['version'], profile_base_hash=context['profile']['base_hash'],
                  order_versions=context['orders'], items=selected,
                  proposed_boxes=sum(x['proposed_boxes'] for x in selected),
                  physical_execution=False, approval_available=False, topup_order_created=False,
                  sender_stock_checked=False, route_checked=False, stacking_rules_checked=False,
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
