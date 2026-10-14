import json
out={}
import subprocess
from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/finished-goods.html")
s=subprocess.check_output(["git","show","HEAD:"+p.as_posix()]).decode("utf-8")
s=s.replace('<label><input id="fgReceiptMarked" type="checkbox" /> Товар подлежит маркировке</label>','<label><input id="fgReceiptMarked" type="checkbox" /> Товар подлежит маркировке</label>\n            <label><input id="fgReceiptWeightedBoxes" type="checkbox" /> Серийные весовые коробки (KG, GS1)</label>\n            <p class="muted">Масса нетто и серийный номер считываются с этикетки коробки. Требование государственной маркировки настраивается отдельно.</p>').replace("sku-receiving-policy.js?v=20261007-ni01","sku-receiving-policy.js?v=20261011-weighted-boxes")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sku-receiving-policy.js")
s=subprocess.check_output(["git","show","HEAD:"+p.as_posix()]).decode("utf-8").replace('      el("fgReceiptMarked").checked = data.marking_required;','      el("fgReceiptMarked").checked = data.marking_required;\n      el("fgReceiptWeightedBoxes").checked = Boolean(data.serialized_weight_boxes);').replace('marking_required: marked, profiles','marking_required: marked, serialized_weight_boxes: el("fgReceiptWeightedBoxes").checked, profiles')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
