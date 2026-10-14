from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py");s=p.read_text(encoding="utf-8").replace("from decimal import Decimal","from decimal import Decimal, InvalidOperation")
s=s.replace("    number = Decimal(str(value))","    try:\n        number = Decimal(str(value))\n    except (InvalidOperation, ValueError) as exc:\n        raise ValueError(\"AUTO_LAYOUT_POSITIVE_LOGISTICS_REQUIRED\") from exc")
s=s.replace('exact_decimal(x["volume"], 18)','exact_decimal(x["volume"], 36)')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.js");s=p.read_text(encoding="utf-8")
s=s.replace(" function td(value){"," function display(value){return typeof value==='string'&&/^\\d+\\.\\d+$/.test(value)?value.replace(/0+$/,'').replace(/\\.$/,''):value;}\n function td(value){")
s=s.replace("String(value);return t;","String(display(value));return t;")
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8").replace("sap-automatic-preparation.js?v=20261013-1123","sap-automatic-preparation.js?v=20261013-1124");f[str(p)]=s
print(json.dumps(f,ensure_ascii=True))
