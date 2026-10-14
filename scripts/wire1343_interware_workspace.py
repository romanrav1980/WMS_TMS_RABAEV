from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
s=s.replace('<link rel="stylesheet" href="styles.css">','<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="interwarehouse-workspace.css?v=20261014-1343">')
s=s.replace('<script src="interwarehouse.js"></script>','<script src="interwarehouse.js?v=20261014-1343"></script><script src="interwarehouse-workspace.js?v=20261014-1343"></script>')
p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('const scope=key(),seq=++serial;busy=true;controls();try{const id=Number(el("iwWare").value);','const scope=key(),seq=++serial,history=el("iwHistory").checked;busy=true;controls();try{const id=Number(el("iwWare").value);',1)
s=s.replace('"?include_completed="+el("iwHistory").checked);if(scope!==key()||seq!==serial)return;','"?include_completed="+history);if(scope!==key()||seq!==serial||history!==el("iwHistory").checked)return;',1)
s=s.replace('say("Планы обновлены. Физическая приёмка подтверждается отдельно.");','window.wmsInterwarehouseWorkspace?.render(rows,id);say("Планы обновлены. Физическая приёмка подтверждается отдельно.");',1)
s=s.replace('if(scope===key()&&pending===intent){pending=null;','if(scope===key()&&pending===intent){pending=null;window.wmsInterwarehouseWorkspace?.invalidate("Операция подтверждена. Обновите планы для следующего действия.");',1)
p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse-workspace.js");s=p.read_text(encoding="utf-8").replace('const heading=section.querySelector("h2");if(!heading)continue;','const heading=section.querySelector("h2");if(!heading||section.contains(board))continue;')
s=s.replace('  const parent=control.closest("details");','  const gate=control.closest("[data-permission]");if(gate&&!auth().hasPermission(gate.dataset.permission)){el("iwFlowCount").textContent="Для этого действия требуется право "+gate.dataset.permission;return;}\n  const parent=control.closest("details");')
p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js");s=p.read_text(encoding="utf-8")
s=s.replace('status("??????????? ?????? ?????? ?????????. ?????????? ?????? ??????; ???????? ?? ??????????.");','status("Сохранённый черновик сканов повреждён. Проверьте исходные данные; операция не выполнялась.");')
needle='window.addEventListener("wms-admin-auth-ready",changed);changed();'
assert needle in s
s=s.replace(needle,'''window.addEventListener("wms-admin-auth-ready",changed);changed();
let initialLinkRead=false;
function openLinkedPlan(){
 if(initialLinkRead||!auth()?.state.user||busy||pending)return;
 const query=new URLSearchParams(location.search),ware=Number(query.get("warehouse_id")),plan=query.get("plan_id");
 if(!Number.isSafeInteger(ware)||ware<1||!plan||plan.length>100)return;
 initialLinkRead=true;el("ggWare").value=String(ware);
 el("ggPlan").replaceChildren(new Option("Место из межскладского маршрута",plan));
 el("ggDetail").click();
}
window.addEventListener("wms-admin-auth-ready",openLinkedPlan);openLinkedPlan();''')
p.write_text(s,encoding="utf-8")
