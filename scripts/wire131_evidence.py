from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/integrations/public.py");s=p.read_text(encoding="utf-8");s+='\nfrom .domain.adapter_evidence import adapter_request_evidence\n';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/services/traceability_service.py");s=p.read_text(encoding="utf-8")
s='from ..modules.integrations.public import adapter_request_evidence\n'+s if not s.startswith('from __future__') else s.replace('from __future__ import annotations','from __future__ import annotations\nfrom ..modules.integrations.public import adapter_request_evidence',1)
start=s.index('    def list_adapter_requests(');end=s.index('    def get_adapter_request(',start)
part=s[start:end];assert part.count('return self.gateway.fetch_all(')==1
part=part.replace('return self.gateway.fetch_all(','return [adapter_request_evidence(row) for row in self.gateway.fetch_all(',1)
needle='            params,\n        )';assert needle in part;part=part.replace(needle,'            params,\n        )]',1)
s=s[:start]+part+s[end:]
start=s.index('    def get_adapter_request(');end=s.find('\n    def ',start+8)
if end==-1:end=len(s)
part=s[start:end];assert 'return rows[0] if rows else {}'in part
part=part.replace('return rows[0] if rows else {}','return adapter_request_evidence(rows[0]) if rows else {}',1)
s=s[:start]+part+s[end:];out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/external-outbox.html");s=p.read_text(encoding="utf-8").replace('<main class="workspace">','<main class="workspace"><p id="regulatoryRuntimeStatus" role="status">Проверка режима внешнего обмена…</p>',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/external-outbox.js");s=p.read_text(encoding="utf-8")
s=s.replace('  externalState.events = await response.json();','  externalState.events = await response.json();\n  await loadRegulatoryRuntime();',1)
s=s.replace('escapeExternal(row.external_status ?? "")','escapeExternal(row.simulation ? "Имитация; квитанции государства нет" : (row.external_status ?? "") + " · квитанция не проверена")',1)
s+="""
async function loadRegulatoryRuntime() {
  const owner = JSON.stringify([externalApiBase(), window.wmsAdminAuth?.state.user?.username]);
  const response = await fetch(externalApiBase() + "/api/integrations/regulatory/runtime", {headers: externalHeaders()});
  const result = await response.json();
  if (owner !== JSON.stringify([externalApiBase(), window.wmsAdminAuth?.state.user?.username])) return;
  outboxEl("regulatoryRuntimeStatus").textContent = response.ok ? result.message : "Не удалось подтвердить режим внешнего обмена.";
}
""";out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
