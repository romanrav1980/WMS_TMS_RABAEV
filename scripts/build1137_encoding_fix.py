from pathlib import Path
import json
files={}
for name in ("scripts/build1131_auto_assignment_bridge.py","wiki-raw/wms_admin_ui_reference/customer-orders.js"):
 p=Path(name);text=p.read_text(encoding="utf-8").replace("ТМС"+chr(0x2026),"ТМС.")
 files[name]=text
print(json.dumps(files,ensure_ascii=True))
