"""Build a readable table of transports without actual delivery dates."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ids = (ROOT / 'reports/transports_without_actual_delivery.txt').read_text(encoding='utf-8').split()
details = json.loads((ROOT / 'data/trip_details.json').read_text(encoding='utf-8'))
records = json.loads((ROOT / 'data/october.json').read_text(encoding='utf-8'))['records']
assert len(ids) == len(set(ids)) == 116
assert not any(r['trip'] in ids and r.get('end') for r in records)
e = lambda value: html.escape(str(value or '—'))
rows = []
for trip in ids:
    detail = details[trip]
    orders = detail.get('orders', [])
    order_lines = []
    for order in orders:
        operation = order.get('operation')
        derived = sorted({g['operation'] for g in detail['goods']
                          if order.get('delivery') and g.get('delivery') == order['delivery'] and g.get('operation')})
        op_text = e(operation) if operation else ', '.join(map(e, derived)) + ' (по поставке)' if derived else 'не найдена'
        order_lines.append(f'<div class="item"><b>{e(order.get("document"))}</b><br>'
                           f'EDI: {e(order.get("edi"))}<br>Поставка: {e(order.get("delivery"))}<br>'
                           f'BLC: {op_text}<br>Получатель: {e(order.get("recipient"))}<br>'
                           f'Отмена: {e(order.get("cancelled"))}</div>')
    goods = sorted({(g.get('operation', ''), g.get('delivery', ''), g.get('origin', ''),
                    g.get('destination', ''), g.get('client', ''), g.get('address', '')) for g in detail['goods']})
    goods_lines = [f'<div class="item"><b>BLC {e(op)}</b> · поставка {e(delivery)}<br>'
                   f'{e(origin)} → {e(destination)}'
                   + (f'<br>{e(client)}' if client else '')
                   + (f'<br>{e(address)}' if address else '') + '</div>'
                   for op, delivery, origin, destination, client, address in goods]
    rows.append(f'<tr><td><b>{e(trip)}</b></td><td>{len(orders)}</td>'
                f'<td>{"".join(order_lines) or "Связанные заказы в исходниках не найдены"}</td>'
                f'<td>{"".join(goods_lines) or "Номера операций не найдены"}</td>'
                '<td>В выгрузке операций BLC нет записи.<br>Фактическая и требуемая даты не заполнены.</td></tr>')
output = '''<!doctype html><html lang="ru"><meta charset="utf-8">
<title>116 транспортировок без фактической даты сдачи</title>
<style>body{font:14px/1.45 Arial,sans-serif;margin:24px;color:#17283c;background:#f4f7fb}
h1{font-size:24px}table{border-collapse:collapse;width:100%;background:white}th,td{border:1px solid #ced8e3;padding:10px;text-align:left;vertical-align:top}
th{background:#172b45;color:white;position:sticky;top:0}tr:nth-child(even){background:#eef4fa}.item+.item{border-top:1px solid #cbd5e1;margin-top:8px;padding-top:8px}
td:first-child{white-space:nowrap}p{max-width:1100px}@media print{th{position:static}body{margin:0;background:white}thead{display:table-header-group}}</style>
<h1>116 транспортировок без фактической даты сдачи</h1>
<p>Срез на 10.11.2026. У 18 транспортировок найдены 30 строк заказов; у 98 связь с заказом в исходниках не найдена.
В товарных строках этих транспортировок указаны 159 уникальных номеров BLC. Ни один из них не найден в выгрузке операций с датами.</p>
<p>Одна строка таблицы — одна транспортировка. Номер заказа — торговый документ VBAK-VBELN.
Связи BLC, восстановленные через поставку, подписаны отдельно. Отменённые заказы сохранены с исходным признаком отмены.
Отсутствие записи в выгрузке не означает отсутствие операции или заказа в SAP.</p>
<p>Источники: SAP октябрь.XLSX (товарные строки), EXPORT1.XLSX (заказы), SAP октябрь опер BLC.xlsx (операции);
подготовленные данные: data/trip_details.json и data/october.json.</p>
<table><thead><tr><th>Транспортировка</th><th>Строк заказов</th><th>Заказы и их поставки</th><th>Операции BLC и поставки из товарных строк</th><th>Причина отсутствия даты</th></tr></thead><tbody>'''
output += ''.join(rows) + '</tbody></table></html>'
target = ROOT / 'reports/transports_without_actual_delivery.html'
target.write_text(output, encoding='utf-8')
assert output.count('<tr>') == 117
print(f'Created {target.name}: {len(rows)} transport rows')
