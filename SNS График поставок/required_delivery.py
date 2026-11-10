"""Resolve required dates from VBAK with explicit actual-date fallback."""
import datetime
import hashlib
import json
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).parent


def load_vbak():
    source = ROOT / 'Данные/babak8.txt'
    if not source.exists():
        return {}, {}
    raw = source.read_bytes()
    lines = raw.decode('cp1251').splitlines()
    header = next(line.split('\t') for line in lines if 'VBELN' in line and 'VDATU' in line)
    fields = {name.strip(): i for i, name in enumerate(header) if name.strip()}
    dates = {}
    count = 0
    for number, line in enumerate(lines, 1):
        cells = line.split('\t')
        if len(cells) <= fields['VBELN'] or not cells[fields['VBELN']].strip().isdigit():
            continue
        if len(cells) != len(header):
            raise ValueError(f'VBAK malformed row {number}')
        doc = cells[fields['VBELN']].strip().zfill(10)
        value = cells[fields['VDATU']].strip()
        date = datetime.datetime.strptime(value, '%d.%m.%Y').date().isoformat() if value not in ('', '00.00.0000') else None
        if doc in dates and dates[doc] != date:
            raise ValueError(f'Conflicting VDATU: {doc}')
        dates[doc] = date
        count += 1
    return dates, {'file': source.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': count,
                   'unique_orders': len(dates), 'with_vdatu': sum(bool(d) for d in dates.values())}


def set_dates(target, dates, source):
    values = sorted(set(filter(None, dates)))
    target['required_delivery_dates'] = values
    target['required_delivery_date'] = values[0] if len(values) == 1 else None
    target['required_delivery_source'] = source if values else 'missing'


def fill_required_dates(records, details):
    vbak, source = load_vbak()
    by_trip = defaultdict(list)
    for row in records:
        by_trip[row['trip']].append(row)
    conflicts = []
    counts = {'orders': 0, 'deliveries': 0, 'operations': 0}
    confirmed_trips, changed_trips = set(), set()
    for trip in sorted(set(details) | set(by_trip)):
        detail = details.get(trip, {'goods': [], 'orders': []})
        previous = list(detail.get('required_delivery_dates', []))
        rows = by_trip[trip]
        goods_ops, delivery_dates, operation_dates = (defaultdict(set) for _ in range(3))
        for g in detail['goods']:
            if g.get('delivery') and g.get('operation'):
                goods_ops[g['delivery']].add(g['operation'])
        for order in detail['orders']:
            date = vbak.get(str(order.get('document', '')).strip().zfill(10))
            derived = goods_ops[order.get('delivery', '')]
            op = order.get('operation', '')
            conflict = bool(op and derived and op not in derived)
            if conflict:
                conflicts.append({'trip': trip, 'document': order.get('document'), 'delivery': order.get('delivery'),
                                  'order_operation': op, 'goods_operations': sorted(derived)})
            if date:
                set_dates(order, [date], 'VBAK-VDATU')
                counts['orders'] += 1
                confirmed_trips.add(trip)
                if str(order.get('cancelled', '')).strip().lower() not in ('', 'нет', 'no', '0'):
                    continue
                if order.get('delivery'):
                    delivery_dates[order['delivery']].add(date)
                # Owner decision: both conflicting BLC references inherit the order plan.
                for operation in (({op} | derived) if conflict else ({op} if op else derived)):
                    operation_dates[operation].add(date)
            else:
                ids = {op} if op else derived
                matched = [r for r in rows if r['operation'] in ids]
                if not matched:
                    matched = [r for r in rows if order.get('recipient_id') and r.get('recipient_id') == order['recipient_id']]
                fallback = 'actual_delivery_fallback'
                if not matched:
                    matched = rows
                    fallback = 'trip_actual_dates_fallback'
                set_dates(order, [r.get('end') for r in matched], fallback)
        counts['deliveries'] += len(delivery_dates)
        counts['operations'] += len(operation_dates)
        actual_by_operation = defaultdict(set)
        for row in rows:
            dates = operation_dates[row['operation']]
            set_dates(row, dates or [row.get('end')], 'VBAK-VDATU' if dates else 'actual_delivery_fallback')
            if row.get('end'):
                actual_by_operation[row['operation']].add(row['end'])
        for g in detail['goods']:
            dates = delivery_dates[g.get('delivery', '')]
            set_dates(g, dates or actual_by_operation[g.get('operation', '')], 'VBAK-VDATU' if dates else 'actual_delivery_fallback')
        detail['operations'] = []
        for op in sorted(set(operation_dates) | {r['operation'] for r in rows} | {g['operation'] for g in detail['goods'] if g.get('operation')}):
            item = {'operation': op}
            dates = operation_dates[op]
            set_dates(item, dates or actual_by_operation[op], 'VBAK-VDATU' if dates else 'actual_delivery_fallback')
            detail['operations'].append(item)
        members = rows + detail['orders'] + detail['goods'] + detail['operations']
        sources = {m['required_delivery_source'] for m in members if m.get('required_delivery_dates')}
        origin = 'VBAK-VDATU' if sources == {'VBAK-VDATU'} else 'mixed' if 'VBAK-VDATU' in sources else 'actual_delivery_fallback'
        set_dates(detail, [date for m in members for date in m.get('required_delivery_dates', [])], origin)
        if previous != detail['required_delivery_dates']:
            changed_trips.add(trip)
    return {'source': source, 'total_transports': len(details), 'from_vbak': counts,
            'transports_with_vbak': len(confirmed_trips), 'transport_date_sets_changed': len(changed_trips),
            'missing_transports': sorted(t for t, d in details.items() if not d['required_delivery_dates']), 'link_conflicts': conflicts}


def planned_rows(details):
    result = []
    for trip, detail in details.items():
        for order in detail['orders']:
            if str(order.get('cancelled', '')).strip().lower() not in ('', 'нет', 'no', '0'):
                continue
            for date in order.get('required_delivery_dates', []):
                result.append({'date': date, 'trip': trip, 'document': order.get('document', ''),
                               'recipient': order.get('recipient_id', ''), 'delivery': order.get('delivery', ''),
                               'operation': order.get('operation', ''), 'source': order['required_delivery_source']})
    return result


if __name__ == '__main__':
    data = json.loads((ROOT / 'data/october.json').read_text(encoding='utf-8'))
    details = json.loads((ROOT / 'data/trip_details.json').read_text(encoding='utf-8'))
    report = fill_required_dates(data['records'], details)
    for name, value in [('october', data), ('trip_details', details), ('planned_delivery', planned_rows(details))]:
        (ROOT / f'data/{name}.json').write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (ROOT / 'reports/vbak8_required_dates.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
