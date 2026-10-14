import json
from pathlib import Path
p=Path("db/migrations/2026-10-10_ni081_range_proposal/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("or s.get_number('warehouse_id')!=p_ware or s.get_string('article')!=p_article", "or s.get_number('warehouse_id')is null or s.get_string('article')is null\n    or s.get_number('warehouse_id')!=p_ware or s.get_string('article')!=p_article")
s=s.replace("if j.get_string('status')!='NOMINAL_RECOMMENDATION'or j.get_boolean('applied')then", "if j.get_string('status')is null or j.get_string('status')!='NOMINAL_RECOMMENDATION'\n    or j.get_boolean('applied')is null or j.get_boolean('applied')then")
s=s.replace("sig is null or length(sig)!=64", "sig is null or not regexp_like(sig,'^[0-9a-f]{64}$')or b.get_string('expected_source_signature')is null")
print(json.dumps({str(p):s}))
