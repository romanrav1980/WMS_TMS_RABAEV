(() => {
 "use strict";
 const el = id => document.getElementById(id);
 const base = () => window.wmsAdminAuth.state.apiBase.replace(/\/$/, "");
 const scope = () => JSON.stringify(["retailcase.unloadIntent", base(), window.wmsAdminAuth.state.user?.username || ""]);
 let pending = null, busy = false, rows = [], tripId = null;
 const status = text => { el("unloadStatus").textContent = text; };
 function controls() {
  el("unloadConfirm").disabled = busy || !!pending;
  el("unloadRefresh").disabled = busy || !!pending;
  el("unloadRetry").hidden = !pending;
  el("unloadRetry").disabled = busy;
  el("unloadRestart").hidden = !pending?.confirmed_rejection;
 }
 function update(data) {
  tripId = data.trip.id;
  rows = data.physical_places.filter(row => row.status === "LOADED" && row.root_case_task_id != null);
  const select = el("unloadSource");select.replaceChildren();
  for (const row of rows) {
   const option = document.createElement("option");option.value = row.load_operation_id;
   option.textContent = (row.root_scan_identifier || row.root_uid) + " · " + row.load_operation_id;select.appendChild(option);
  }
  showOrigin();
 }
 function showOrigin() {
  const row = rows.find(item => item.load_operation_id === el("unloadSource").value);
  el("unloadOrigin").textContent = row ? "Вернуть в исходную ячейку " + row.origin_cell + ". После выгрузки требуется новый контроль." : "Погруженных самостоятельных CASE для этого действия нет.";
 }
 async function request(path, body) {
  const response = await fetch(base() + path, {method: body ? "POST" : "GET",
   headers: window.wmsAdminAuth.headers(body ? {"Content-Type": "application/json"} : {}),
   ...(body ? {body: JSON.stringify(body)} : {})});
  const data = await response.json();
  if (!response.ok) {
   const error = new Error(data.detail?.message || JSON.stringify(data.detail || data));
   error.confirmed = response.status < 500 && data.detail?.outcome_confirmed !== false;throw error;
  }
  return data;
 }
 async function send(key) {
  if (busy || !pending) return;
  busy = true;controls();const saved = pending;
  try {
   const result = await request("/api/transport/loading/unload", saved.body);
   localStorage.removeItem(key);
   if (key !== scope()) return;
   pending = null;status("Выгрузка подтверждена: " + result.operation_id + ". Товар и резерв восстановлены; требуется контроль.");
   el("tripId").value = String(saved.trip_id);
   await window.wmsPhysicalLoadState.refresh();
  } catch (error) {
   if (key === scope()) {
    if (error.confirmed) {pending = {...saved, confirmed_rejection: true};localStorage.setItem(key, JSON.stringify(pending));}
    status(error.message + (error.confirmed ? " Отказ подтверждён." : " Исход неизвестен: повторите сохранённую команду."));
   }
  } finally {busy = false;controls();}
 }
 async function submit() {
  if (busy || pending || window.wmsPhysicalLoadState.isBusy() || window.wmsPhysicalLoadState.hasPending()) {
   status("Сначала завершите или повторите сохранённую операцию погрузки/выгрузки.");return;
  }
  try {
   const row = rows.find(item => item.load_operation_id === el("unloadSource").value);
   if (!row || tripId !== Number(el("tripId").value)) throw new Error("Обновите погруженные места этого рейса.");
   const body = {operation_id: "TT.UNLOAD:" + crypto.randomUUID(), load_operation_id: row.load_operation_id,
    expected_version: row.content_version, scan_container: el("unloadScan").value.trim(),
    scan_cell: el("unloadCell").value.trim(), scan_vehicle: el("unloadVehicle").value.trim(),
    scan_dock: el("unloadDock").value.trim(), reason: el("unloadReason").value.trim()};
   if (!body.scan_container || !body.scan_cell || !body.scan_vehicle || !body.scan_dock || !body.reason) throw new Error("Отсканируйте место, ячейку, машину, ворота и укажите причину.");
   const key = scope();pending = {body, trip_id: tripId};localStorage.setItem(key, JSON.stringify(pending));await send(key);
  } catch (error) {status(error.message);controls();}
 }
 function auth() {
  rows = [];tripId = null;pending = null;el("unloadSource").replaceChildren();
  for (const id of ["unloadScan", "unloadCell", "unloadVehicle", "unloadDock", "unloadReason"]) el(id).value = "";
  try {pending = JSON.parse(localStorage.getItem(scope()) || "null");} catch (error) {status(error.message);}
  if (pending) status("Есть сохранённая выгрузка; повторите исходную команду.");else status("");
  showOrigin();controls();
 }
 window.wmsPhysicalUnload = {hasPending: () => !!pending, isBusy: () => busy};
 window.addEventListener("wms-physical-load-status", event => update(event.detail));
 window.addEventListener("wms-admin-auth-ready", auth);
 el("unloadSource").addEventListener("change", showOrigin);
 el("unloadConfirm").addEventListener("click", submit);
 el("unloadRetry").addEventListener("click", () => send(scope()));
 el("unloadRefresh").addEventListener("click", () => window.wmsPhysicalLoadState.refresh());
 el("unloadRestart").addEventListener("click", () => {
  if (!busy && pending?.confirmed_rejection) {localStorage.removeItem(scope());pending = null;controls();status("Исправьте сканы и обновите места. Следующее действие создаст новую операцию.");}
 });
 auth();
})();
