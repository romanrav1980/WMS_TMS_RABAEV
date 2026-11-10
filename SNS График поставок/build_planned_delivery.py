"""Build plans from resolved VBAK/actual dates, never from EXPORT1-C."""
import json
from required_delivery import ROOT, fill_required_dates, planned_rows

data = json.loads((ROOT / 'data/october.json').read_text(encoding='utf-8'))
details = json.loads((ROOT / 'data/trip_details.json').read_text(encoding='utf-8'))
fill_required_dates(data['records'], details)
rows = planned_rows(details)
(ROOT / 'data/planned_delivery.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print('Resolved planned delivery rows:', len(rows))
