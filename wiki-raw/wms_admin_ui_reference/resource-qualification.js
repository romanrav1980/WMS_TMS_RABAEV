(() => {
  const panel = document.createElement("section");
  panel.className = "panel";
  panel.innerHTML = '<h2>Допуски к заданиям — данные Oracle</h2><label>ID ресурса <input id="qualResource" type="number" min="1"></label> <label>Вид задания <input id="qualTask" placeholder="REPLENISHMENT"></label> <button id="qualRead">Показать</button> <button id="qualEnable">Разрешить</button> <button id="qualDisable">Отозвать</button><p role="status"></p><pre></pre>';
  (document.querySelector("main") || document.body).prepend(panel);
  const api = async (method, body) => {
    const resource = panel.querySelector("#qualResource").value;
    if (!/^[1-9][0-9]*$/.test(resource)) throw new Error("Укажите ID ресурса.");
    const auth = window.wmsAdminAuth;
    const response = await fetch(auth.state.apiBase.replace(/\/$/,"") + "/api/resources/" + resource + "/qualifications",
      {method, headers: auth.headers(body ? {"Content-Type":"application/json"} : {}), body: body ? JSON.stringify(body) : undefined});
    const data = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(data.detail || data));
    return data;
  };
  async function action(active) {
    panel.querySelectorAll("button").forEach(button => button.disabled = true);
    try {
      if (active !== null) await api("PUT",{task_type:panel.querySelector("#qualTask").value.trim().toUpperCase(),active});
      panel.querySelector("pre").textContent = JSON.stringify(await api("GET"),null,2);
      panel.querySelector("p").textContent = "Допуски прочитаны из Oracle. Активные допуски проверяются при назначении и проведении.";
    } catch(error) { panel.querySelector("p").textContent = error.message; }
    finally { permissions(); }
  }
  function permissions() {
    const auth=window.wmsAdminAuth;
    panel.hidden=!auth?.hasPermission("resource_management_view");
    panel.querySelector("#qualRead").disabled=false;
    panel.querySelector("#qualEnable").disabled=!auth?.hasPermission("warehouse_settings_edit");
    panel.querySelector("#qualDisable").disabled=!auth?.hasPermission("warehouse_settings_edit");
  }
  panel.querySelector("#qualRead").addEventListener("click",()=>action(null));
  panel.querySelector("#qualEnable").addEventListener("click",()=>action(true));
  panel.querySelector("#qualDisable").addEventListener("click",()=>action(false));
  window.addEventListener("wms-admin-auth-ready",permissions);
  permissions();
})();
