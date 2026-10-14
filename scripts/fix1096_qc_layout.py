from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/outgoing-quality.css"
s=Path(p).read_text(encoding="utf-8")+'\n.warehouse-operations .warehouse-task-tools .panel.qc-workspace{display:block;padding:0;scroll-margin-top:95px}.qc-workspace .qc-columns{width:100%;box-sizing:border-box}\n'
h="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html"
print(json.dumps({p:s,h:Path(h).read_text(encoding="utf-8").replace("outgoing-quality.css?v=20261013-1094","outgoing-quality.css?v=20261013-1096")},ensure_ascii=True))
