from pathlib import Path
import json
files={}
base=Path("wiki-raw/wms_admin_ui_reference")
p=base/"store-returns.html";s=p.read_text(encoding="utf-8").replace('</head>','<link rel="stylesheet" href="store-return-progress.css"></head>').replace('<script src="store-returns.js">','<script src="store-return-progress.js"></script><script src="store-returns.js">');files[str(p)]=s
p=base/"store-returns.js";s=p.read_text(encoding="utf-8");anchor='  el("returnLine").replaceChildren(...data.lines.map'
s=s.replace(anchor,'  window.wmsReturnProgress?.render(data);\n'+anchor)
s=s.replace('unitPanel.replaceChildren();say("Возврат согласован:', 'unitPanel.replaceChildren();window.wmsReturnProgress?.clear();say("Возврат согласован:')
# Navigation/invalidation does not submit any command.
s=s.replace(' el("returnLoad").addEventListener("click",load);',' el("returnSource").addEventListener("input",()=>{serial++;dossier=null;window.wmsReturnProgress?.clear();el("returnLines").replaceChildren();unitPanel.replaceChildren();});\n el("returnLoad").addEventListener("click",load);')
files[str(p)]=s
for name in ["store-return-receiving.html","store-return-putaway.html","supplier-return.html","return-disposal.html"]:
 p=base/name;s=p.read_text(encoding="utf-8").replace('</body>','<script src="return-workspace-link.js"></script></body>');files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
