"""Normalized gateway contract; never represented as a standard SAP IDoc."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import xml.etree.ElementTree as ET


def scalar(node: ET.Element, name: str, maximum: int = 100) -> str:
    found = [n for n in node if n.tag.split('}')[-1] == name]
    if len(found) != 1 or len(found[0]):
        raise ValueError('Exactly one scalar required: ' + name)
    value = (found[0].text or '').strip()
    if not value or len(value.encode('utf-8')) > maximum:
        raise ValueError('Missing/oversized ' + name)
    return value


def positive(value: str) -> Decimal:
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError('Invalid quantity') from exc
    if not number.is_finite() or not 0 < number <= Decimal('999999999999') or number.normalize().as_tuple().exponent < -6:
        raise ValueError('Quantity must be positive, at most 6 decimal places')
    return number


def read_order(raw: bytes) -> dict:
    if not raw or len(raw) > 4 * 1024 * 1024:
        raise ValueError('XML exceeds 4 MiB')
    text = raw.decode('utf-8-sig')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('DTD/entities forbidden')
    root = ET.fromstring(text)
    if root.tag.split('}')[-1] != 'WarehouseCustomerOrder' or root.get('version') != '1':
        raise ValueError('Expected WarehouseCustomerOrder version=1')
    names = {'Sender','MessageId','OrderNumber','CustomerCode','StoreCode','WarehouseId','OrderDate',
             'OperationalDate','DeliveryDate','PickingStartAt','PickingFinishAt','ShipmentAt','Lines'}
    if any(n.tag.split('}')[-1] not in names for n in root):
        raise ValueError('Unknown order field: update gateway contract explicitly')
    data = {name: scalar(root, name) for name in names - {'Lines'}}
    if not data['WarehouseId'].isascii() or not data['WarehouseId'].isdigit() or not 0 < int(data['WarehouseId']) <= 10**12:
        raise ValueError('WarehouseId must identify WMS warehouse')
    for name in ('OrderDate','OperationalDate','DeliveryDate'):
        if date.fromisoformat(data[name]).isoformat() != data[name]:
            raise ValueError('Dates must use YYYY-MM-DD')
    for name in ('PickingStartAt','PickingFinishAt','ShipmentAt'):
        if datetime.fromisoformat(data[name]).utcoffset() is None:
            raise ValueError('Planned timestamps require explicit UTC offset')
    containers = [n for n in root if n.tag.split('}')[-1] == 'Lines']
    if len(containers) != 1 or not 1 <= len(containers[0]) <= 1000:
        raise ValueError('Order requires 1..1000 lines')
    lines, seen = [], set()
    for node in containers[0]:
        if node.tag.split('}')[-1] != 'Line' or any(n.tag.split('}')[-1] not in {'LineNumber','Material','Quantity','TargetWeightKg'} for n in node):
            raise ValueError('Unexpected order line field')
        number = scalar(node, 'LineNumber', 9)
        if not number.isascii() or not number.isdigit() or not 0 < int(number) < 10**9 or int(number) in seen:
            raise ValueError('LineNumber must be unique positive integer')
        seen.add(int(number))
        qty = positive(scalar(node, 'Quantity', 30))
        qnode = next(n for n in node if n.tag.split('}')[-1] == 'Quantity')
        unit = qnode.get('unit', '').strip()
        if not unit or len(unit.encode()) > 20:
            raise ValueError('Quantity unit is required')
        weight = scalar(node, 'TargetWeightKg', 30) if any(n.tag.split('}')[-1]=='TargetWeightKg' for n in node) else None
        lines.append({'line_number': int(number), 'material': scalar(node,'Material',40), 'quantity': str(qty),
                      'unit': unit, 'target_weight_kg': str(positive(weight)) if weight else None})
    data['Lines'] = sorted(lines, key=lambda line: line['line_number'])
    content = {k:v for k,v in data.items() if k!='MessageId'}
    data['content_hash'] = sha256(json.dumps(content,sort_keys=True).encode()).hexdigest()
    data['payload_hash'] = sha256(raw).hexdigest()
    return data


def calendar(data: dict, offset_minutes: int, weekdays: str, same_day: bool, received: datetime) -> dict:
    from datetime import timezone, timedelta, time
    zone = timezone(timedelta(minutes=offset_minutes))
    start, finish, shipment = [datetime.fromisoformat(data[n]).astimezone(zone) for n in ('PickingStartAt','PickingFinishAt','ShipmentAt')]
    operational, delivery = date.fromisoformat(data['OperationalDate']), date.fromisoformat(data['DeliveryDate'])
    if start.date()!=operational or not start < finish <= shipment or shipment.date()>delivery:
        raise ValueError('Invalid planned picking/shipment/delivery timeline')
    if date.fromisoformat(data['OrderDate'])>operational:
        raise ValueError('OrderDate cannot follow operational start day')
    if shipment.date()!=operational+timedelta(days=1) and not (same_day and shipment.date()==operational):
        raise ValueError('Same-day shipment requires configured source book')
    if str(delivery.isoweekday()) not in weekdays.split(','):
        raise ValueError('Delivery date is outside store calendar')
    late = received.astimezone(zone) > datetime.combine(operational,time(16),zone)
    return {'operational_date': operational, 'delivery_date': delivery, 'picking_start': start.replace(tzinfo=None),
            'picking_finish': finish.replace(tzinfo=None), 'shipment': shipment.replace(tzinfo=None),
            'late': late, 'offset_minutes': offset_minutes}
