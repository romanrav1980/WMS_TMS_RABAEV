(() => {
  const el = id => document.getElementById(id), auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const owner = () => base() + "|" + (auth().state.user?.username || auth().state.user?.id || "");
  const key = () => "wmsWaveTimePending:" + owner();
  let context = null, sequence = 0, currentOwner = "", busy=false;
  const message = value => { el("wtMessage").textContent = value; };
  const intent=window.wmsResourcePending.create(key,'wave','wtRetry',async()=>{reset();await load();message('Исходник архивирован. Сверьте утверждённое окно перед новой командой.');});
  const pending=()=>{if(!auth().state.user)return null;const r=intent.read();return r.damaged?{damaged:true}:r.value;};
  function reset() {
    ++sequence; context = null; el("wtContext").textContent = "";
    el("wtApprove").disabled = true; el("wtRetry").hidden = !pending();
  }
  async function request(path, method = "GET", body) {
    const response = await fetch(base() + "/api/resources/workload/waves" + path,
      { method, headers: {...auth().headers(), "Content-Type": "application/json"},
        ...(body ? {body: JSON.stringify(body)} : {}) });
    const result = await response.json();
    if (!response.ok) {
      const error = Error(result.detail?.message || result.detail?.code || JSON.stringify(result.detail));
      error.status = response.status; error.code=result.detail?.code; throw error;
    }
    return result;
  }
  async function load() {
    const serial = ++sequence, identity = owner(), wave = Number(el("wtWave").value);
    context = null; el("wtApprove").disabled = true;
    try {
      if (!Number.isSafeInteger(wave) || wave <= 0) throw Error("Укажите волну.");
      const result = await request("/" + wave + "/time-context");
      if (serial !== sequence || identity !== owner()) return;
      if (result.warehouse_id !== Number(el("rwWare").value)) throw Error("Волна относится к другому выбранному складу.");
      context = result;
      el("wtContext").textContent = "Волна " + wave + " · " + result.wave_status + " · версия " + result.version +
        (result.plan_status === "APPROVED" ? " · " + result.start_at + " — " + result.finish_at :
          result.plan_status === "LEGACY_PLAN_CHANGED" ? " · прежний план изменён: требуется новое утверждение" : " · окно не утверждено");
      el("wtApprove").disabled = !auth().hasPermission("pick_wave_launch");
      message("Актуальная волна прочитана.");
    } catch (error) { if (serial === sequence) message(error.message); }
  }
  function at(id) {
    const value = el(id).value;
    if (!value) throw Error("Заполните окно комплектации.");
    const offsets = {"UTC": "+00:00", "Europe/Moscow": "+03:00", "Asia/Tbilisi": "+04:00"};
    return value + (value.length === 16 ? ":00" : "") + offsets[el("wtZone").value];
  }
  async function approve() {
    if(busy)return;
    try {
      if (pending()) throw Error("Сначала повторите сохранённое утверждение.");
      if (!context || context.wave_id !== Number(el("wtWave").value) || context.warehouse_id !== Number(el("rwWare").value)) throw Error("Сначала прочитайте актуальную волну.");
      const saved = {operation_id: "WAVE.TIME.UI:" + crypto.randomUUID(), wave_id: context.wave_id,
        expected_version: context.version, source_token: context.source_token,
        start_at: at("wtStart"), finish_at: at("wtFinish"), time_zone: el("wtZone").value,
        reason: el("wtReason").value};
      intent.save(saved); el("wtRetry").hidden = false;
      await retry();
    } catch (error) { message(error.message); }
  }
  async function retry() {
    if(busy)return;
    let record;const identity=owner();
    busy=true;el("wtRetry").disabled=true;el("wtApprove").disabled=true;
    try {
      record=intent.read();
      if(record.damaged)throw Error('Запрос повреждён. Архивируйте исходник и перечитайте волну.');
      if(!record.value)return;
      const result=await request('/approve-time','POST',record.value);
      if(identity!==owner())return;
      if(!intent.confirms(record.value,result))throw Error('Ответ не подтверждает исходное утверждение. Повторите сохранённый запрос.');
      intent.settle(record);reset();await load();
      message('Окно волны '+result.wave_id+' утверждено. Пересчитайте нагрузку; наличие дефицита проверяется отдельно.');
    } catch(error) {
      if(identity!==owner())return;
      if(record?.value&&intent.rejected(error))intent.settle(record);
      message(error.message+(pending()?' Повторите исходное утверждение.':' Перечитайте волну перед исправлением.'));
      el("wtRetry").hidden=!pending();
    } finally {
      busy=false;
      if(identity===owner()){el("wtRetry").disabled=false;el("wtApprove").disabled=!!pending()||!context||!auth().hasPermission('pick_wave_launch');}
    }
  }
  el("wtLoad").addEventListener("click", load);
  el("wtApprove").addEventListener("click", approve);
  el("wtRetry").addEventListener("click", retry);
  ["wtWave", "rwWare"].forEach(id => el(id).addEventListener("input", reset));
  window.addEventListener("wms-admin-auth-ready", () => {
    if (currentOwner !== owner()) { currentOwner = owner(); reset(); }
    el("wtPanel").hidden = !auth().hasPermission("pick_wave_view");
    el("wtApprove").hidden = !auth().hasPermission("pick_wave_launch");
  });
})();
