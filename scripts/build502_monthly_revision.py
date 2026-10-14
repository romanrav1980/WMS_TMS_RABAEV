import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_rates.py");s=p.read_text(encoding="utf-8")
old='if effective<=cur.fetchone()[0]:raise LogisticsCostError("COST_RATE_EFFECTIVE_ORDER","Новая ставка должна начинаться после предыдущей")'
new='if effective<cur.fetchone()[0]:raise LogisticsCostError("COST_RATE_EFFECTIVE_ORDER","Дата новой редакции не может предшествовать последнему периоду")'
assert s.count(old)==1;s=s.replace(old,new)
print(json.dumps({str(p):s}))
