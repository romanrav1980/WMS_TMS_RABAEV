from pathlib import Path
import json
files={};p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js');t=p.read_text(encoding='utf-8')
needle='  warehouseTaskEl("warehouseTaskProgress").textContent = "-";'
assert needle in t;t=t.replace(needle,needle+'\n  window.dispatchEvent(new CustomEvent("warehouse-task-selected",{detail:task?{task_id:task.task_id,status:task.status}:null}));',1)
files[str(p)]=t
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');files[str(p)]=p.read_text(encoding='utf-8').replace('20261013-816','20261013-819').replace('src="resource-nearest.js"','src="resource-nearest.js?v=20261013-819"')
# VM context supports the same real selection event.
p=Path('scripts/check810_task_controls.cjs');files[str(p)]=p.read_text(encoding='utf-8').replace('addEventListener:(type,fn)=>events[type]=fn}', 'addEventListener:(type,fn)=>events[type]=fn,dispatchEvent(){}},\n CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}}')
print(json.dumps(files,ensure_ascii=True))
