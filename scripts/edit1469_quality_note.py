from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/outgoing-quality-next.js');s=p.read_text(encoding='utf-8');s=s.replace("if(!snapshot||blocked||!window.wmsAdminAuth.hasPermission('transport_dispatch_view'))return;","if(!snapshot||blocked)return;");s=s.replace("  if(snapshot.ready!==true", "  if(!window.wmsAdminAuth.hasPermission('transport_dispatch_view')){panel.hidden=panel.childElementCount===0;return;}\n  if(snapshot.ready!==true");p.write_text(s,encoding='utf-8')
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json');import json;d=json.loads(p.read_text(encoding='utf-8'))
for x in d['increments']:x['architectureGate']='PASS_759_files_0_cycles_73_debt_24_tests_admin_terminal_typescript'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
