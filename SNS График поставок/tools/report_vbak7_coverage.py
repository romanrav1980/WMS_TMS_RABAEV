"""Report explicit sales-order coverage without substituting other dates for VDATU."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'Данные/vbak7.txt'
raw = source.read_bytes()
lines = raw.decode('cp1251').splitlines()
header = next(line.split('\t') for line in lines if '\tMANDT\tVBELN\t' in line)
documents = set()
count = 0
for number, line in enumerate(lines, 1):
    cells = line.split('\t')
    if len(cells) < 3 or cells[1].strip() != '300':
        continue
    if len(cells) != len(header) or not cells[2].strip().isdigit():
        raise ValueError(f'Malformed VBAK row {number}')
    documents.add(cells[2].strip().zfill(10))
    count += 1

details = json.loads((ROOT / 'data/trip_details.json').read_text(encoding='utf-8'))
records = json.loads((ROOT / 'data/october.json').read_text(encoding='utf-8'))['records']
blc_trips = {r['trip'] for r in records if r['trip']}
rows = []
for trip in sorted(set(details) | blc_trips):
    orders = {str(o.get('document', '')).strip().zfill(10)
              for o in details.get(trip, {}).get('orders', [])
              if str(o.get('document', '')).strip().isdigit()}
    found = orders & documents
    status = ('нет связи с заказом' if not orders else
              'заказы отсутствуют в VBAK' if not found else
              'часть заказов найдена' if found != orders else 'все заказы найдены')
    rows.append({'Транспортировка': trip, 'Есть операции BLC': int(trip in blc_trips),
                 'Результат': status, 'Заказы': ', '.join(sorted(orders)),
                 'Найдены в VBAK': ', '.join(sorted(found)),
                 'Отсутствуют в VBAK': ', '.join(sorted(orders - found))})
report = ROOT / 'reports'
report.mkdir(exist_ok=True)
for name, selected in [('vbak7_transport_coverage.csv', rows),
                       ('vbak7_transports_without_orders.csv', [r for r in rows if not r['Найдены в VBAK']])]:
    with (report / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter=';')
        writer.writeheader()
        writer.writerows(selected)
summary = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'rows': count,
           'unique_orders': len(documents), 'fields': [h for h in header if h],
           'has_vdatu': 'VDATU' in header, 'total_transports': len(rows),
           'transports_with_blc': len(blc_trips),
           'statuses': dict(Counter(r['Результат'] for r in rows)),
           'blc_statuses': dict(Counter(r['Результат'] for r in rows if r['Есть операции BLC'])),
           'required_dates_updated': 0}
(report / 'vbak7_coverage_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
