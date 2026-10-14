import json
from pathlib import Path
files={}
p=Path("wiki-raw/wms_admin_ui_reference/order-picking-workspace.css")
files[str(p)]=p.read_text(encoding="utf-8")+"""
#preparedLayoutPanel{display:block}
#preparedLayoutPanel>h2{margin-bottom:12px}
#preparedLayoutPanel>p{line-height:1.55;margin:12px 0}
#preparedLayoutPanel>.rights-table-wrap{margin:16px 0}
#preparedLayoutPanel>.rights-toolbar{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr) auto;gap:12px;align-items:end;padding:16px;background:#f8fafc;border-radius:12px}
#preparedLayoutPanel select,#preparedLayoutPanel input{width:100%;box-sizing:border-box}
#preparedLayoutPanel>label{margin:16px 0}
#plComparison{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin:20px 0}
#plComparison>section{border:1px solid #dbe5f1;border-radius:12px;padding:14px;min-width:0}
#plComparison>section:last-child{background:#f0fdf4;border-color:#bbf7d0}
#plComparison h3{margin:0 0 12px}
#plComparison .rights-table{font-size:12px}
#plComparison td{overflow-wrap:anywhere}
#plMove{background:#2377eb;color:white;border-color:#2377eb}
#plStatus{background:#eff6ff;border-radius:10px;padding:14px}
@media(max-width:800px){#preparedLayoutPanel>.rights-toolbar,#plComparison{grid-template-columns:minmax(0,1fr)}}
"""
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<div id="plComparison" hidden><h3>','<div id="plComparison" hidden><section><h3>',1)
s=s.replace('<h3>После изменения</h3>','</section><section><h3>После изменения</h3>',1)
old='<tbody id="plAfterRows"></tbody></table></div></div>';assert old in s;s=s.replace(old,'<tbody id="plAfterRows"></tbody></table></div></section></div>',1)
files[str(p)]=s
print(json.dumps(files))
