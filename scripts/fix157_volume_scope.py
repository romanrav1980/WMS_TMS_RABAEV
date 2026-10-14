import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8").replace("def native_template_volumes(cur: Any, templates:", "def native_template_volumes(cur: Any, article: str, templates:").replace("native_template_volumes(cur, templates)", "native_template_volumes(cur, article, templates)")
print(json.dumps({str(p):s}))
