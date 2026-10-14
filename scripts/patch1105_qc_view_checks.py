from pathlib import Path
import json
f={}
p="scripts/check1097_qc_response.js";s=Path(p).read_text(encoding="utf-8")
needle=" vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality.js','utf8'),ctx);"
s=s.replace(needle," vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality-scan-view.js','utf8'),ctx);\n"+needle,1)
f[p]=s
p="scripts/check1102_qc_damaged.js";s=Path(p).read_text(encoding="utf-8").replace("'outgoing-quality-intent.js','outgoing-quality.js'","'outgoing-quality-intent.js','outgoing-quality-scan-view.js','outgoing-quality.js'")
f[p]=s
print(json.dumps(f,ensure_ascii=True))
