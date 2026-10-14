from pathlib import Path
import json
p="scripts/check1097_qc_response.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace(" URLSearchParams,Option:", " URLSearchParams,TextEncoder,Option:",1)
old=" vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality.js','utf8'),ctx);"
assert old in s
s=s.replace(old," vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/wave-command-intent.js','utf8'),ctx);\n vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality-intent.js','utf8'),ctx);\n"+old,1)
print(json.dumps({p:s},ensure_ascii=True))
