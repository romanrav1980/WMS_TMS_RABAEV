from pathlib import Path
import json,re
files={}
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html")
s=p.read_text(encoding="utf-8")
s=re.sub(r'<button type="button" data-task-preset="([^"]+)"([^>]*)>([^<]+)</button>',lambda m:'<a href="warehouse-tasks.html?preset='+m[1]+'" data-task-preset="'+m[1]+'"'+m[2]+'>'+m[3]+'</a>',s)
s=s.replace("20261013-829","20261013-830")
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.js")
s=p.read_text(encoding="utf-8").replace("function setWarehouseTaskPreset(preset) {","function setWarehouseTaskPreset(preset, reload = true) {",1)
s=s.replace("  loadWarehouseTasks().catch(showWarehouseTaskError);\n}\n\nfunction renderWarehouseTasks()", "  if(reload)loadWarehouseTasks().catch(showWarehouseTaskError);\n}\n\nfunction renderWarehouseTasks()",1)
s=s.replace('  warehouseTaskState.initialTaskId = Number(params.get("task_id") || 0) || null;', '''  warehouseTaskState.initialTaskId = Number(params.get("task_id") || 0) || null;
  const preset=params.get("preset");
  if(["all","waiting","wave-pickface","shipping-zone","finished-goods","production-wave"].includes(preset)){
    setWarehouseTaskPreset(preset,false);
  }''',1)
old='button.addEventListener("click", () => setWarehouseTaskPreset(button.dataset.taskPreset));'
new='''button.addEventListener("click", event => {
      event.preventDefault();
      const url=new URL(window.location.href);
      url.searchParams.set("preset",button.dataset.taskPreset);
      url.searchParams.delete("task_id");
      window.history.replaceState(null,"",url);
      setWarehouseTaskPreset(button.dataset.taskPreset);
    });'''
assert old in s
s=s.replace(old,new,1)
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.css")
files[str(p)]=p.read_text(encoding="utf-8")+"""
.warehouse-operations .warehouse-task-tabs a{display:inline-flex;align-items:center;min-height:36px;padding:0 12px;border:1px solid #dbe3ee;border-radius:8px;color:#52677f;background:white;text-decoration:none;font-size:12px;box-sizing:border-box}
.warehouse-operations .warehouse-task-tabs a.active{background:#edf4ff;color:#2362ca;border-color:#cbdcf7}
.warehouse-operations .warehouse-task-tabs a:hover{background:#f3f7fe}
"""
# Extend established handler fixture for real URL navigation state.
p=Path("scripts/check810_task_controls.cjs")
s=p.read_text(encoding="utf-8").replace("window:{location:{search:'?task_id=1080'}","window:{history:{replaceState(){}},location:{search:'?task_id=1080',href:'http://local/warehouse-tasks.html?task_id=1080'}")
s=s.replace(" URLSearchParams,fetch:"," URL,URLSearchParams,fetch:")
s=s.replace("waiting.click();await flush();","waiting.click({preventDefault(){}});await flush();")
files[str(p)]=s
p=Path("scripts/check828_task_refresh.cjs")
s=p.read_text(encoding="utf-8").replace("window:{location:{search:'?task_id=1080'}","window:{history:{replaceState(){}},location:{search:'?task_id=1080',href:'http://local/warehouse-tasks.html?task_id=1080'}")
s=s.replace(" URLSearchParams,fetch:"," URL,URLSearchParams,fetch:")
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
