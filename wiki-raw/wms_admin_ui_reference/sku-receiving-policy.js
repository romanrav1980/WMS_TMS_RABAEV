window.fgReceivingPolicy = (() => {
  let article = null, version = null, loadId = 0;
  const el = id => document.getElementById(id);
  const status = text => { el("fgReceiptStatus").textContent = text; };
  function addProfile(profile = {}) {
    const row = document.createElement("div");
    row.className = "rights-editor receipt-profile";
    for (const [key, label] of [["system_code","Система"],["profile_code","Профиль"],["profile_version","Версия"],["scan_mode","Приёмка"]]) {
      const wrapper = document.createElement("label");
      wrapper.textContent = label;
      const input = document.createElement(key === "scan_mode" ? "select" : "input");
      input.dataset.key = key;
      if (key === "scan_mode") {
        for (const [value, text] of [["UNIT","Коды единиц"],["BOX","Агрегация коробки"],["PALLET","Агрегация паллеты"],["UNIT_OR_AGGREGATION","Единицы или агрегация"]]) {
          const option = document.createElement("option"); option.value = value; option.textContent = text; input.appendChild(option);
        }
      }
      if (key === "system_code") input.setAttribute("list", "fgReceiptSystems");
      if (key !== "scan_mode") input.maxLength = key === "profile_code" ? 80 : 40;
      input.value = profile[key] || (key === "scan_mode" ? "UNIT" : "");
      wrapper.appendChild(input); row.appendChild(wrapper);
    }
    const remove = document.createElement("button"); remove.type="button"; remove.textContent="Удалить";
    remove.addEventListener("click", () => row.remove()); row.appendChild(remove);
    el("fgReceiptProfiles").appendChild(row);
  }
  function readProfiles() {
    return Array.from(el("fgReceiptProfiles").querySelectorAll(".receipt-profile")).map(row =>
      Object.fromEntries(Array.from(row.querySelectorAll("[data-key]")).map(input => [input.dataset.key, input.value.trim()])));
  }
  async function load(articul) {
    article = articul; version = null;
    const requestId = ++loadId;
    el("fgReceiptSave").disabled = true;
    el("fgReceiptProfiles").replaceChildren();
    status("Загрузка настроек приёмки...");
    try {
      const response = await fetch(`${fgApiBase()}/api/finished-goods/skus/${encodeURIComponent(articul)}/receiving-policy`, { headers: fgHeaders() });
      const data = await response.json();
      if (requestId !== loadId) return;
      if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
      version = data.version;
      el("fgReceiptMarked").checked = data.marking_required;
      data.profiles.forEach(addProfile);
      if (data.configured) {
        el("fgEditCrpt").value = String(Number(data.profiles.some(p => p.system_code === "CRPT")));
        el("fgEditAggregation").value = String(Number(data.profiles.some(p => p.scan_mode !== "UNIT")));
      }
      el("fgReceiptSave").disabled = !fgCan("finished_goods_edit");
      el("fgEditCrpt").disabled = data.configured;
      el("fgEditAggregation").disabled = data.configured;
      status(data.legacy_mismatch ? "Настройки расходятся с прежним CRPT. Согласуйте и сохраните профиль." : data.configured ? `Версия ${version}. Сохранено в WMS.` : "Настройки нового режима ещё не заданы.");
    } catch (error) { if (requestId === loadId) status(error.message); }
  }
  async function save() {
    if (!article || version === null || !fgCan("finished_goods_edit")) return;
    const selected = article;
    const marked = el("fgReceiptMarked").checked;
    const profiles = marked ? readProfiles() : [];
    el("fgReceiptSave").disabled = true;
    try {
      const response = await fetch(`${fgApiBase()}/api/finished-goods/skus/${encodeURIComponent(selected)}/receiving-policy`, {
        method: "PUT", headers: fgHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ expected_version: version, marking_required: marked, profiles }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail));
      if (article === selected) {
        fgEl("fgEditCrpt").value = String(Number(profiles.some(p => p.system_code === "CRPT")));
        fgEl("fgEditAggregation").value = String(Number(profiles.some(p => p.scan_mode !== "UNIT")));
        await load(selected);
      }
    } finally { el("fgReceiptSave").disabled = version === null || !fgCan("finished_goods_edit"); }
  }
  el("fgReceiptSave").addEventListener("click", () => save().catch(error => status(error.message)));
  el("fgReceiptAddProfile").addEventListener("click", () => { if (article && fgCan("finished_goods_edit")) { el("fgReceiptMarked").checked=true; addProfile(); } });
  return { load };
})();