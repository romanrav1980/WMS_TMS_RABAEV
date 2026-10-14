"""Emit the prepared 1142 source checkpoint; supersedes the failed string patch."""
from pathlib import Path
import ast
import json
files={}
for name in ("api/wms_api_server/app/modules/inventory/infrastructure/shipping_temperature_read.py","scripts/read1142_thermal_preflight.py"):
 value=Path(name).read_text(encoding="utf-8")
 ast.parse(value,filename=name)
 files[name]=value
print(json.dumps(files,ensure_ascii=True))
