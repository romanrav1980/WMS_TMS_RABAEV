from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/day-reconciliation.html"
s=Path(p).read_text(encoding="utf-8").replace("st-waiting-tasks.js?v=20261013-1078","st-waiting-tasks.js?v=20261013-1084")
print(json.dumps({p:s},ensure_ascii=True))
