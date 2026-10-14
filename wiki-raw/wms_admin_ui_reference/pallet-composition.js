(() => {
  const el = id => document.getElementById(id), auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const owner = () => JSON.stringify([base(), auth().state.user?.username]);
  let busy = false, sequence = 0, selected = "", signature = null, cursor = null, identity = "";
  function clear() {
    ++sequence; selected = ""; signature = cursor = null; busy = false;
    for (const id of ["pcSummary", "pcSources", "pcLocations", "pcUnits"]) el(id).replaceChildren();
    el("pcNext").hidden = true; el("pcLoad").disabled = false;
  }
  function paragraph(parent, text) { const p = document.createElement("p"); p.textContent = text; parent.appendChild(p); }
  function normalize(value) {
    let code = value.startsWith("]C1") ? value.slice(3) : value;
    if (/^\(00\)[0-9]{18}$/.test(code)) code = code.slice(4);
    else if (/^00[0-9]{18}$/.test(code)) code = code.slice(2);
    return code;
  }
  function sourceLabel(birth) {
    const source = birth.source || {};
    if (birth.command_type === "INVENTORY_REGISTER_LOT") return "Пересчёт, ревизия " + source.revision_id;
    if (birth.command_type === "MES_MOVEMENTS") return "MES, заказ " + source.production_order_id
      + ", движение " + (birth.birth_movement_id || birth.source_doc_id || source.movement_ids?.join(", "));
    return "Приёмка SAP, " + (source.order_id || birth.operation_id);
  }
  function render(result, append) {
    if (!append) {
      el("pcSummary").replaceChildren();
      paragraph(el("pcSummary"), "Остаток: " + result.stock_quantity + " · физических единиц: "
        + result.physical_unit_count + " · количество по кодам: " + result.captured_base_quantity);
      const coverage = {MATCHED: "Количество по единицам соответствует остатку", NO_UNIT_CAPTURE: "Коды физических единиц не фиксировались", MISMATCH: "Обнаружено расхождение остатка и состава единиц"};
      paragraph(el("pcSummary"), coverage[result.quantity_coverage] || result.quantity_coverage);
      el("pcLocations").replaceChildren();
      for (const row of result.locations) paragraph(el("pcLocations"), row.cell + " · " + row.remain
        + " " + row.base_uom + " · резерв " + row.hard_reserved_base);
      el("pcSources").replaceChildren();
      for (const receipt of result.receipts) paragraph(el("pcSources"), "SAP: " + receipt.sap_order_number
        + " · партия " + receipt.supplier_batch + " · срок " + receipt.expiry_date);
      for (const birth of result.source_births) paragraph(el("pcSources"), sourceLabel(birth) + " · "
        + birth.operation_id + " · исходная паллета " + birth.origin_pallet_identifier
        + (birth.manifest_operation_id ? " · состав отправителя " + birth.manifest_operation_id : "")
        + " · государственная квитанция не проверена");
      if (result.receipts_truncated || result.source_births_truncated)
        paragraph(el("pcSources"), "Показано до 200 источников. Полная история требует дополнительной выборки.");
      el("pcUnits").replaceChildren();
    }
    for (const unit of result.units) {
      const block = document.createElement("details"), title = document.createElement("summary");
      title.textContent = "Единица " + unit.unit_id + " · " + unit.quantity + " " + unit.unit
        + " · " + unit.cell + " · систем маркировки " + unit.codes.length;
      block.appendChild(title);
      for (const code of unit.codes) {
        paragraph(block, code.system + " · " + code.profiles.map(p => p.profile + " / " + p.version).join(", "));
        const raw = document.createElement("pre"); raw.textContent = code.raw_code; block.appendChild(raw);
      }
      el("pcUnits").appendChild(block);
    }
    cursor = result.next_cursor; signature = result.composition_signature;
    el("pcNext").hidden = !cursor;
  }
  async function load(next) {
    if (busy) return;
    const pallet = normalize(el("pcPallet").value);
    if (!pallet) { el("pcMessage").textContent = "Отсканируйте идентификатор паллеты."; return; }
    if (!next) clear();
    if (next && (pallet !== selected || !cursor || !signature)) return;
    selected = pallet; const scope = owner(), serial = ++sequence;
    busy = true; el("pcLoad").disabled = el("pcNext").disabled = true;
    try {
      const params = new URLSearchParams({limit: "50"});
      if (next) { params.set("after", cursor); params.set("expected_signature", signature); }
      const response = await fetch(base() + "/api/receiving/pallets/" + encodeURIComponent(pallet)
        + "/composition?" + params, {headers: auth().headers()});
      const result = await response.json();
      if (scope !== owner() || serial !== sequence || pallet !== normalize(el("pcPallet").value)) return;
      if (!response.ok) throw Error(result.detail?.code || result.detail || "Состав не получен.");
      render(result, next); el("pcMessage").textContent = "Показан согласованный состав паллеты.";
    } catch (error) {
      if (scope === owner() && serial === sequence) { clear(); el("pcMessage").textContent = error.message + " Загрузите актуальный состав."; }
    } finally {
      if (scope === owner() && serial === sequence) { busy = false; el("pcLoad").disabled = el("pcNext").disabled = false; }
    }
  }
  el("pcLoad").addEventListener("click", () => load(false));
  el("pcNext").addEventListener("click", () => load(true));
  el("pcPallet").addEventListener("input", clear);
  el("pcPallet").addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); load(false); } });
  let openedLink=false;
  window.addEventListener("wms-admin-auth-ready", () => { const scope = owner(); if (identity !== scope) { identity = scope; clear(); el("pcPallet").value = ""; }
    const linked=new URLSearchParams(location.search).get("identifier");
    if(!openedLink&&auth().state.user&&linked&&linked.length<=200){openedLink=true;el("pcPallet").value=linked;void load(false);}
  });
})();
