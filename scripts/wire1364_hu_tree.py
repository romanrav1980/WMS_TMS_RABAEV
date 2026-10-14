from pathlib import Path
import json
files={}
base=Path("wiki-raw/wms_admin_ui_reference")
p=base/"warehouse-hus.html";s=p.read_text(encoding="utf-8").replace('</head>','<link rel="stylesheet" href="warehouse-hu-tree.css"></head>')
s=s.replace('<script src="warehouse-hus.js', '<script src="warehouse-hu-tree.js"></script><script src="warehouse-hus.js')
files[str(p)]=s
p=base/"warehouse-hus.js";s=p.read_text(encoding="utf-8").replace('  function render(data){','  function render(data){\n    window.wmsHuTree?.render(data);')
s=s.replace('el(id).disabled=busy||!!pending||!!damaged;', 'el(id).disabled=busy||!!pending||!!damaged||(id!=="huCreate"&&(!view||view.historical_composition));')
s=s.replace('render(data);status("Состав получен.', 'render(data);controls();status("Состав получен.')
s=s.replace('el("huIdentifier").addEventListener("input",()=>{generation++;view=null;});','el("huIdentifier").addEventListener("input",()=>{generation++;view=null;window.wmsHuTree?.clear();el("huRows").replaceChildren();el("huSummary").replaceChildren();el("huPlacement").replaceChildren();controls();});')
s=s.replace('identity=next;view=null;generation++;pending=null;damaged=null;', 'identity=next;view=null;generation++;pending=null;damaged=null;window.wmsHuTree?.clear();el("huRows").replaceChildren();el("huSummary").replaceChildren();el("huPlacement").replaceChildren();')
files[str(p)]=s
p=base/"pallet-composition.js";s=p.read_text(encoding="utf-8")
s=s.replace('  window.addEventListener("wms-admin-auth-ready", () => {', '  let openedLink=false;\n  window.addEventListener("wms-admin-auth-ready", () => {')
s=s.replace('identity = scope; clear(); el("pcPallet").value = ""; } });','identity = scope; clear(); el("pcPallet").value = ""; }\n    const linked=new URLSearchParams(location.search).get("identifier");\n    if(!openedLink&&auth().state.user&&linked&&linked.length<=200){openedLink=true;el("pcPallet").value=linked;void load(false);}\n  });')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
