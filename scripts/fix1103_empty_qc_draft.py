from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/outgoing-quality.js";s=Path(p).read_text(encoding="utf-8")
old='  if(!draft)draft={identifier:data.shipment_identifier,signature:data.composition_signature,entries:[]};'
assert old in s
s=s.replace(old,'  if(!draft||(draftRaw===null&&!draft.entries.length))draft={identifier:data.shipment_identifier,signature:data.composition_signature,entries:[]};',1)
print(json.dumps({p:s},ensure_ascii=True))
