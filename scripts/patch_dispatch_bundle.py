raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
p=Path("scripts/stock_posting_current_bundle.py");s=p.read_text(encoding="utf-8")
s=s.replace('m=json.loads((d/"current_runtime_manifest.json").read_text(encoding="utf-8"))','m=json.loads((d/"current_runtime_manifest.json").read_text(encoding="utf-8"))\nfrom stock_posting_dispatch_contract import assert_runtime_dispatch\nassert_runtime_dispatch(m,d)')
print(json.dumps({str(p):s},ensure_ascii=True))
