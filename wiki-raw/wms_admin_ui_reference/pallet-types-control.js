(() => {
  let panel, rows = [], selected = null, unresolved = false;
  async function request(path, body) {
    const options = {headers: window.wmsAdminAuth.headers(body ? {"Content-Type":"application/json"} : {})};
    if (body) { options.method = "POST"; options.body = JSON.stringify(body); }
    const response = await fetch((window.wmsAdminAuth.state.apiBase || "http://127.0.0.1:8088").replace(/\/$/,"") + path, options);
    const result = await response.json();
    if (!response.ok) { const error = new Error(typeof result.detail === "string" ? result.detail : JSON.stringify(result.detail)); error.status = response.status; throw error; }
    return result;
  }
  function node(tag, text) { const element = document.createElement(tag); if (text !== undefined) element.textContent = text; return element; }
  async function open() {
    if (panel || !window.wmsAdminAuth?.hasPermission("case_pick_manage") || new URLSearchParams(location.search).get("demo") === "1") return;
    const host = document.querySelector(".case-page"); if (!host) return;
    panel = node("section"); panel.className = "case-panel";
    panel.append(node("h2","Типы тары и финальное взвешивание"));
    panel.append(node("p","Обязательное взвешивание этого места сохраняется при освобождении родительской паллеты от контроля. Справочный вес типа не заменяет измерение."));
    const choice = node("select"); choice.setAttribute("aria-label","Тип тары");
    const code = node("input"), name = node("input"), volume = node("input"), weight = node("input");
    const kind = node("select"); ["PALLET","TROLLEY","CONTAINER"].forEach(value => { const option=node("option",value); option.value=value;kind.append(option); });
    const required = node("input"); required.type = "checkbox";
    for (const [caption,input] of [["Код",code],["Название",name],["Класс",kind],["Справочный объём, м³",volume],["Справочная масса, кг",weight],["Обязательное финальное взвешивание",required]]) {
      const label=node("label",caption + " "); label.append(input);panel.append(label);
    }
    code.maxLength=50;name.maxLength=160;
    const refresh=node("button","Обновить карточку"),save=node("button","Сохранить"),message=node("p");
    panel.prepend(choice);panel.append(refresh,save,message);host.append(panel);
    function render() {
      selected = rows.find(row => String(row.pallet_type_id) === choice.value) || null;
      code.value=selected?.pallet_type_code || ""; name.value=selected?.pallet_type_name || "";
      kind.value=selected?.load_unit_class || "CONTAINER";
      volume.value=selected?.default_volume_m3 ?? "";weight.value=selected?.default_weight_kg ?? "";
      required.checked=Boolean(selected?.final_weight_required);
      message.textContent=selected ? "Версия " + selected.type_version : "Новый тип тары";
    }
    async function load() {
      try {
        const current=choice.value;rows=await request("/api/case-pick/pallet-types");
        choice.replaceChildren(node("option","Новый тип"));choice.options[0].value="";
        for(const row of rows){const option=node("option",row.pallet_type_code+" — "+row.pallet_type_name);option.value=String(row.pallet_type_id);choice.append(option);}
        choice.value=current;unresolved=false;save.disabled=false;render();
      }catch(error){message.textContent=error.message;}
    }
    choice.addEventListener("change",render);refresh.addEventListener("click",load);
    save.addEventListener("click",async () => {
      if (unresolved) return;
      const body={pallet_type_id:selected?.pallet_type_id ?? null,pallet_type_code:code.value,pallet_type_name:name.value,
        load_unit_class:kind.value,default_volume_m3:volume.value || null,default_weight_kg:weight.value || null,
        length_mm:selected?.length_mm ?? null,width_mm:selected?.width_mm ?? null,height_mm:selected?.height_mm ?? null,
        default_max_client_pallets:selected?.default_max_client_pallets ?? 1,active:selected?.active ?? 1,
        final_weight_required:required.checked,expected_version:selected?.type_version ?? 0};
      save.disabled=true;
      try { const result=await request("/api/case-pick/pallet-types",body);choice.value=String(result.pallet_type_id);await load();choice.value=String(result.pallet_type_id);render();message.textContent="Сохранено."; }
      catch(error){unresolved=!error.status || error.status>=500;message.textContent=unresolved ? "Ответ о сохранении не получен. Обновите карточку перед следующим изменением." : error.message;}
      finally{save.disabled=unresolved;}
    });
    await load();
  }
  window.addEventListener("wms-admin-auth-ready",open);
  if(window.wmsAdminAuth?.state?.user)open();
})();
