from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
needle="async function prepareSapSt() {\n"
guard="""async function prepareSapSt() {
  const auth=window.wmsAdminAuth.state,who=auth.user?.username;
  if(localStorage.getItem('sap-auto-preparation:'+auth.apiBase+':'+who)||
     localStorage.getItem('sap-st-preparation:'+JSON.stringify([auth.apiBase,who])))
    throw new Error('Сначала выясните исход сохранённой подготовки СТ; новый запрос заблокирован.');
"""
assert needle in s;s=s.replace(needle,guard,1)
print(json.dumps({str(p):s},ensure_ascii=True))
