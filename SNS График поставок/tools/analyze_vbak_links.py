"""Profile the supplied VBAK text against explicit order/delivery/BLC/trip links."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'Данные' / 'wwwwww.txt'
raw = source.read_bytes()
lines = raw.decode('cp1251').splitlines()
header = next(line.split('\t') for line in lines if '\tMANDT\tVBELN\t' in line)
rows = {}
duplicates = 0
malformed = []
for line_number, line in enumerate(lines, 1):
    cells = line.split('\t')
    if len(cells) < 3 or cells[1].strip() != '300':
        continue
    if len(cells) != len(header) or not cells[2].strip().isdigit():
        malformed.append(line_number)
        continue
    row = {name: cells[i].strip() for i, name in enumerate(header) if name}
    row['source_line'] = line_number
    duplicates += row['VBELN'] in rows
    rows[row['VBELN']] = row

def key(value):
    text = str(value).strip()
    return text.zfill(10) if text.isdigit() else ''

details = json.loads((ROOT / 'data/trip_details.json').read_text(encoding='utf-8'))
records = json.loads((ROOT / 'data/october.json').read_text(encoding='utf-8'))['records']
operations = {(str(r['trip']), str(r['operation'])) for r in records}
links = collections.defaultdict(set)
weak_links = collections.defaultdict(set)
for trip, detail in details.items():
    goods_links = {(str(g.get('operation', '')), str(g.get('delivery', ''))) for g in detail.get('goods', [])}
    for order in detail.get('orders', []):
        doc = key(order.get('document', ''))
        if not doc:
            continue
        operation = str(order.get('operation', ''))
        delivery = str(order.get('delivery', ''))
        link = (trip, operation, delivery)
        weak_links[doc].add(link)
        if operation and delivery and (trip, operation) in operations and (operation, delivery) in goods_links:
            links[doc].add(link)
        if delivery and not operation:
            for goods_operation, goods_delivery in goods_links:
                if goods_delivery == delivery and (trip, goods_operation) in operations:
                    links[doc].add((trip, goods_operation, delivery))

# Load only the XLSX reader definitions, never execute build_analysis's rebuild.
reader_path = ROOT / 'build_analysis.py'
scope = {'__file__': str(reader_path)}
exec(reader_path.read_text(encoding='utf-8').split('trips={};details=')[0], scope)
raw_orders = collections.defaultdict(set)
for order in scope['read_sheet']('EXPORT1.XLSX', 'Sheet1'):
    doc = key(order.get('Y', ''))
    if doc:
        raw_orders[doc].add((order.get('AN', ''), order.get('AO', ''), order.get('Z', '')))

matched = set(rows) & set(links)
raw_matched = set(rows) & set(raw_orders)
fields = ['VBTYP', 'AUART', 'VKORG', 'VTWEG', 'SPART', 'VKGRP', 'VKBUR']
types = sorted({rows[v]['AUART'] for v in matched})
candidate = {v for v, r in rows.items() if r['VBTYP'] == 'C' and r['VTWEG'] == '20' and r['AUART'] in types}
by_type = []
for kind, count in collections.Counter(r['AUART'] for r in rows.values()).most_common():
    ids = {v for v, r in rows.items() if r['AUART'] == kind}
    by_type.append({'AUART': kind, 'all': count, 'trip_order_matches': len(ids & set(weak_links)), 'confirmed_links': len(ids & matched), 'raw_export1_matches': len(ids & raw_matched), 'candidate': len(ids & candidate)})

report = {
    'source': str(source.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
    'rows': len(rows), 'duplicates': duplicates, 'malformed_lines': malformed,
    'fields': [h for h in header if h],
    'dates': dict(sorted(collections.Counter(r['ERDAT'] for r in rows.values()).items(), key=lambda x: datetime.datetime.strptime(x[0], '%d.%m.%Y'))),
    'known_order_documents': len(weak_links), 'known_confirmed_documents': len(links),
    'matched_order_documents': len(set(rows) & set(weak_links)),
    'confirmed_documents': len(matched), 'raw_export1_matches': len(raw_matched),
    'derived_links_absent_in_raw': sorted(v for v in matched if not any(t == rt and d == rd and (not ro or o == ro) for t, o, d in links[v] for rt, ro, rd in raw_orders[v])),
    'raw_matches_without_confirmed_link': sorted(raw_matched - matched),
    'trip_order_links_not_fully_consistent': [{'VBELN': v, 'declared_links': sorted(weak_links[v])} for v in sorted((set(rows) & set(weak_links)) - matched)],
    'raw_orders_without_trip': sorted(v for v in raw_matched if all(not t for t, o, d in raw_orders[v])),
    'candidate_rows': len(candidate), 'candidate_known_matches': len(candidate & matched),
    'excluded_known_matches': sorted(matched - candidate),
    'by_type': by_type,
    'matched_fields': {f: dict(collections.Counter(rows[v][f] for v in matched).most_common()) for f in fields},
    'raw_matched_fields': {f: dict(collections.Counter(rows[v][f] for v in raw_matched).most_common()) for f in fields},
    'candidate_unconfirmed_examples': {t: sorted(v for v in candidate - matched if rows[v]['AUART'] == t)[:5] for t in types},
    'confirmed_examples': {t: [{'VBAK': rows[v], 'links': sorted(links[v])} for v in sorted(matched) if rows[v]['AUART'] == t][:3] for t in types},
    'documents': [{'VBELN': v, 'source_line': rows[v]['source_line'], **{f: rows[v][f] for f in fields}, 'links': sorted(links[v])} for v in sorted(matched)],
    'limitations': ['Local October transport data is incomplete; absence of a match does not prove absence of logistics.', 'Header filter is inferred from known positive matches, not a complete SAP classification.', 'VDATU and KUNNR are absent from this text export.'],
}
out = ROOT / 'reports' / 'vbak_wwwwww_links.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
(out.parent / 'vbak_known_trip_orders.txt').write_text('\n'.join(sorted(set(rows) & set(weak_links))) + '\n', encoding='utf-8')
print(json.dumps({k: report[k] for k in ('rows', 'duplicates', 'known_order_documents', 'matched_order_documents', 'confirmed_documents', 'raw_export1_matches', 'candidate_rows', 'candidate_known_matches', 'excluded_known_matches', 'derived_links_absent_in_raw', 'matched_fields', 'raw_matched_fields')}, ensure_ascii=True))
print('BY_TYPE', json.dumps([t for t in by_type if t['raw_export1_matches'] or t['all'] > 10000], ensure_ascii=True))
