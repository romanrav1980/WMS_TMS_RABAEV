(() => {
  const el = id => document.getElementById(id);
  let context = null, units = new Map(), sequence = 0, busy = false;
  const auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const sourceId = () => Number(el(el("tmBirthKind").value === "MES" ? "tmMovement" : "tmRevision").value);
  const identity = () => JSON.stringify([base(), auth().state.user?.username, el("tmBirthKind").value,
    sourceId(), el("tmPallet").value, el("tmArticle").value, el("tmCell").value]);
  let boundIdentity = "";
  function say(text) { el("tmUnitMessage").textContent = text; }
  function render() {
    el("tmUnitRows").replaceChildren(...[...units.entries()].map(([id, unit]) => {
      const row = document.createElement("p");
      row.textContent = "Физическая единица " + id + " · " + unit.quantity + " " + context.base_uom
        + " · подтверждены профили: " + unit.codes.map(c => c.system_code + "/" + c.profile_code).join(", ");
      return row;
    }));
  }
  function reset() {
    ++sequence; context = null; units = new Map(); busy = false; boundIdentity = "";
    el("tmUnitProfile").replaceChildren(); el("tmUnitRows").replaceChildren();
    el("tmUnitCode").value = ""; say("Загрузите действующие настройки для выбранного источника и паллеты.");
  }
  async function load() {
    if (busy) return;
    const scope = identity(), serial = ++sequence;
    const documentId = sourceId();
    if (!Number.isSafeInteger(documentId) || documentId < 1) {
      say("Укажите действующую ревизию или движение выпуска."); return;
    }
    busy = true; el("tmUnitLoad").disabled = true;
    try {
      const body = {source_document_id: documentId, article: el("tmArticle").value,
        cell: el("tmCell").value, pallet_identifier: el("tmPallet").value};
      const kind = el("tmBirthKind").value === "MES" ? "mes" : "inventory";
      const response = await fetch(base() + "/api/inventory/trace-manifests/" + kind + "-context", {
        method: "POST", headers: auth().headers({"Content-Type": "application/json"}), body: JSON.stringify(body)
      });
      const result = await response.json();
      if (scope !== identity() || serial !== sequence) return;
      if (!response.ok) throw Error(result.detail?.message || result.detail?.code || "Настройки не получены.");
      context = result; boundIdentity = scope; units = new Map(); render();
      const profiles = result.profile_versions.filter(p => ["UNIT", "UNIT_OR_AGGREGATION"].includes(p.mode));
      el("tmUnitProfile").replaceChildren(...profiles.map(p =>
        new Option(p.system_code + " / " + p.profile_code + " · " + p.version, JSON.stringify(p))));
      say(profiles.length ? "Настройки загружены. Базовая единица: " + result.base_uom
        : "Профили требуют агрегации. Используйте состав отправителя и скан коробки или паллеты.");
    } catch (error) {
      if (scope === identity() && serial === sequence) say(error.message);
    } finally {
      if (scope === identity() && serial === sequence) { busy = false; el("tmUnitLoad").disabled = false; }
    }
  }
  function add() {
    try {
      if (!context || boundIdentity !== identity()) throw Error("Сначала загрузите актуальные настройки.");
      const id = el("tmPhysicalUnit").value, quantity = el("tmPhysicalQty").value;
      if (!id || id.includes(String.fromCharCode(0)) || new TextEncoder().encode(id).length > 100) throw Error("Укажите идентификатор физической единицы до 100 байт.");
      if (!units.has(id) && units.size >= 10000) throw Error("Не более 10000 физических единиц в операции.");
      if (!/^[0-9]+(\.[0-9]{1,9})?$/.test(quantity) || !/[1-9]/.test(quantity)) throw Error("Укажите положительное количество в базовой единице.");
      const profile = JSON.parse(el("tmUnitProfile").value || "null");
      const code = el("tmUnitCode").value;
      if (!profile || !code || new TextEncoder().encode(code).length > 4000) throw Error("Выберите профиль и отсканируйте QR штуки.");
      const unit = units.get(id) || {unit_id: id, quantity, codes: []};
      if (unit.quantity !== quantity) throw Error("Для одной физической единицы количество должно совпадать.");
      if (unit.codes.some(c => c.system_code === profile.system_code && c.profile_code === profile.profile_code))
        throw Error("Этот профиль данной физической единицы уже отсканирован.");
      unit.codes.push({system_code: profile.system_code, profile_code: profile.profile_code, code});
      units.set(id, unit); el("tmUnitCode").value = ""; render(); say("Скан добавлен к физической единице " + id + ".");
    } catch (error) { say(error.message); }
  }
  function capture(complete) {
    if (!context || boundIdentity !== identity() || !units.size) throw Error("Загрузите настройки и отсканируйте физические единицы.");
    const rows = [...units.values()];
    if (complete && rows.some(unit => unit.codes.length !== context.profile_versions.length))
      throw Error("Каждая физическая единица должна содержать все обязательные профили. Для смешанного режима используйте также агрегации.");
    return {units: rows, aggregations: [], expected_policy_version: context.policy_version,
      expected_profile_versions: context.profile_versions};
  }
  el("tmUnitLoad").addEventListener("click", load);
  el("tmUnitAdd").addEventListener("click", add);
  el("tmUnitCode").addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); add(); } });
  el("tmUnitClear").addEventListener("click", () => { units = new Map(); render(); });
  for (const id of ["tmBirthKind", "tmRevision", "tmMovement", "tmPallet", "tmArticle", "tmCell"])
    el(id).addEventListener("change", reset);
  window.addEventListener("wms-admin-auth-ready", () => { if (!context || boundIdentity !== identity()) reset(); });
  window.retailcaseUnitCapture = {capture, reset};
})();
