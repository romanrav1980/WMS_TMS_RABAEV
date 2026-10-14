(() => {
  if (resourceDemo) { document.querySelector(".breadcrumbs b").textContent+=" — демонстрационные данные"; return; }
  const status = document.createElement("p");
  status.setAttribute("role","status");
  document.querySelector(".resource-table-panel").prepend(status);
  const refresh = document.querySelector(".resource-refresh");
  async function load() {
    const auth=window.wmsAdminAuth;
    resourceRows=[];renderResources();
    if (!auth?.hasPermission("resource_management_view")) return;
    refresh.disabled=true;status.textContent="Загрузка ресурсов…";
    try {
      const response=await fetch(auth.state.apiBase.replace(/\/$/,"")+"/api/resources?active=1&limit=200",{headers:auth.headers()});
      const rows=await response.json();
      if (!response.ok) throw new Error(typeof rows.detail==="string"?rows.detail:JSON.stringify(rows.detail));
      resourceRows=rows.map(r=>({
        code:r.resource_code,type:r.resource_type,typeLabel:r.resource_type_name,
        equipment:r.equipment_code||"—",operator:r.active_operator_user_id||"—",
        shift:r.active_session_id?"Сессия "+r.active_session_id:"—",zone:r.zone_code||"",
        status:!r.active_session_id?"Недоступен":r.active_task_id||r.active_inventory_task_id?"В работе":r.active_session_status==="PAUSED"?"В простое":"Доступен",
        current:r.active_task_id?"Задание "+r.active_task_id:r.active_inventory_task_id?"Инвентаризация "+r.active_inventory_task_id:"—",
        currentKind:r.last_cell?"Ячейка "+r.last_cell:"",next:"—",nextKind:"",progress:null,
        resourceId:r.resource_id,sessionId:r.active_session_id
      }));
      renderResources();
      const values=[resourceRows.length,resourceRows.filter(r=>r.status==="Доступен").length,
        resourceRows.filter(r=>r.status==="В работе").length,resourceRows.filter(r=>r.status==="В простое").length,"—"];
      document.querySelectorAll(".resource-kpi").forEach((card,i)=>{
        card.querySelector("b").textContent=values[i];
        card.querySelector("em").textContent=i===4?"См. монитор восстановления":"В загруженном списке";
        card.querySelector("svg")?.remove();
      });
      const zones=[...new Set(resourceRows.map(r=>r.zone).filter(Boolean))].sort();
      const select=document.getElementById("resourceZoneFilter"),selected=select.value;
      select.replaceChildren(new Option("Все зоны",""),...zones.map(z=>new Option(z,z)));
      if(zones.includes(selected))select.value=selected;
      status.textContent="Данные Oracle; до 200 ресурсов. Допуск и занятость повторно проверяются при назначении.";
    } catch(error) {
      document.querySelectorAll(".resource-kpi b").forEach(e=>e.textContent="—");
      status.textContent="Ресурсы не загружены: "+error.message;
    } finally {refresh.disabled=false;}
  }
  refresh.addEventListener("click",load);
  refresh.title="Перечитать ресурсы и текущие сессии из базы";
  document.querySelectorAll(".resource-kpi b").forEach(e=>e.textContent="—");
  document.querySelectorAll(".resource-kpi em").forEach(e=>e.textContent="Ожидание загрузки");
  document.querySelectorAll(".resource-kpi svg").forEach(e=>e.remove());
  const clock=document.querySelectorAll(".sidebar-footer .footer-line.muted span");
  if(clock.length>=2){clock[0].textContent=new Date().toLocaleDateString("ru-RU");clock[1].textContent=new Date().toLocaleTimeString("ru-RU",{hour:"2-digit",minute:"2-digit"});}
  document.querySelector(".sidebar-footer b").textContent="По сессиям";
  document.querySelectorAll(".resource-top-select,.resource-top-date,.resource-topbar .round,.resource-gantt-panel button").forEach(e=>{
    e.disabled=true;e.title="Этот элемент ещё не подключён к рабочим данным";
  });
  document.querySelector(".resource-top-date").value=new Date().toLocaleDateString("sv-SE");
  document.querySelector(".resource-top-select").replaceChildren(new Option("Ресурсы всех складов",""));
  document.querySelector(".round.alert").textContent="—";
  window.addEventListener("wms-admin-auth-ready",load);
  load();
})();
