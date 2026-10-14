import json
from pathlib import Path
p=Path("db/migrations/2026-10-10_ni081_range_apply/006_core.sql");s=p.read_text(encoding="utf-8").replace("RRL_STOCK_MATH.quantity(s.get_string('undated_unpicked_quantity'))!=0", "not regexp_like(s.get_string('undated_unpicked_quantity'),'^0([.]0+)?$')")
print(json.dumps({str(p):s}))
