(() => {
 "use strict";
 const el = id => document.getElementById(id);
 const base = () => window.wmsAdminAuth.state.apiBase.replace(/\/$/, "");
 const key = () => JSON.stringify(["nicora.tareLoadRecovery", base(), window.wmsAdminAuth.state.user?.username || ""]);
 let rows = [], pending = null, busy = false, generation = 0;
 const status = text => {el("recoveryStatus").textContent = text;};
 function controls() {
  for (const id of ["recoveryLoad","recoveryRefresh","recoverySource","recoveryScan","recoveryConfirm"]) el(id).disabled = busy || !!pending;
  el("recoveryRetry").hidden = !pending;el("recoveryRetry").disabled = busy;
  el("recoveryRestart").hidden = !pending?.confirmed_rejection;el("recoveryRestart").disabled = busy;
 }
 async function request(path, body) {
  const response = await fetch(base() + path, {method: body ? "POST" : "GET", headers: window.wmsAdminAuth.headers(body ? {"Content-Type":"application/json"} : {}),
   ...(body ? {body: JSON.stringify(body)} : {})});
  const data = await response.json();
  if (!response.ok) {
   const error = new Error(data.detail?.message || JSON.stringify(data.detail || data));
   error.confirmed = response.status === 422 || data.detail?.outcome_confirmed === true;throw error;
  }
  return data;
 }
 function render() {
  el("recoveryRows").replaceChildren();el("recoverySource").replaceChildren();
  for (const [index,row] of rows.entries()) {
   const line = document.createElement("p");
   line.textContent = (row.place_identifier || row.place_id) + " · " + row.pallet_type_name + " · принято: " + row.accepted_by
    + (row.recovery_operation_id ? " · закрепление: " + row.recovery_book_status : " · возвращённая тара ещё не закреплена");
   el("recoveryRows").appendChild(line);
   if (!row.recovery_operation_id && row.load_status === "LOADED") {
    const option = document.createElement("option");option.value = String(index);
    option.textContent = (row.place_identifier || row.place_id) + " · " + row.pallet_type_name + " · " + row.return_offer_operation_id;
    el("recoverySource").appendChild(option);
   }
  }
 }
 async function refresh() {
  if (busy || pending) return;
  const id = ++generation, scope = key(), load = el("recoveryLoad").value.trim();
  if (!load) {status("Выберите исходную погрузку.");return;}
  try {
   const data = await request("/api/inventory/tare/load-recovery-candidates?load_operation_id=" + encodeURIComponent(load));
   if (id !== generation || scope !== key() || load !== el("recoveryLoad").value.trim()) return;
   rows = data;render();status(rows.length ? "Показаны подтверждённые возвраты и их закрепления." : "Подтверждённых возвратов для этой погрузки нет.");
  } catch (error) {if (id === generation && scope === key()) status(error.message);}
 }
 async function send(scope) {
  if (busy || !pending) return;busy = true;controls();const saved = pending;
  try {
   const result = await request("/api/inventory/tare/book", saved.body);
   localStorage.removeItem(scope);
   if (scope !== key()) return;
   pending = null;busy = false;controls();
   await refresh();status("Возвращённая тара закреплена за исходным местом: " + result.operation_id + ". Подтвердите выгрузку товара.");
  } catch (error) {
   if (scope === key()) {
    if (error.confirmed) {pending = {...saved,confirmed_rejection:true};localStorage.setItem(scope,JSON.stringify(pending));}
    status(error.message + (error.confirmed ? " Отказ подтверждён." : " Исход неизвестен: повторите сохранённую команду."));
   }
  } finally {busy = false;controls();}
 }
 async function confirm() {
  if (busy || pending) return;
  const row = rows[Number(el("recoverySource").value)], scan = el("recoveryScan").value.trim(), load = el("recoveryLoad").value.trim();
  if (!row || row.load_operation_id !== load || row.recovery_operation_id || row.load_status !== "LOADED" || !scan) {status("Обновите погрузку, выберите возврат и отсканируйте физическое место.");return;}
  const body = {operation_id:"TARE.RECOVERY:" + crypto.randomUUID(),place_kind:row.place_kind || "CASE",place_id:row.place_id,pallet_type_id:row.pallet_type_id,
   expected_warehouse_id:row.ware_id,load_recovery:{load_operation_id:row.load_operation_id,original_booking_operation_id:row.original_booking_operation_id,
    return_offer_operation_id:row.return_offer_operation_id,expected_load_version:row.expected_load_version,scan_place:scan}};
  try {const saved = {body};localStorage.setItem(key(),JSON.stringify(saved));pending = saved;await send(key());}
  catch (error) {status(error.message);controls();}
 }
 function auth() {
  generation++;rows = [];render();pending = null;el("recoveryScan").value = "";
  try {pending = JSON.parse(localStorage.getItem(key()) || "null");} catch (error) {status(error.message);}
  status(pending ? "Есть сохранённое закрепление; повторите исходную команду." : "");controls();
 }
 el("recoveryRefresh").addEventListener("click",refresh);el("recoveryConfirm").addEventListener("click",confirm);
 el("recoveryRetry").addEventListener("click",() => send(key()));
 el("recoveryRestart").addEventListener("click",() => {
  if (!busy && pending?.confirmed_rejection) {localStorage.removeItem(key());pending = null;controls();status("Обновите возвраты и исправьте скан.");}
 });
 window.addEventListener("wms-admin-auth-ready",auth);
 el("recoveryLoad").value = new URLSearchParams(location.search).get("load_operation_id") || "";
 auth();
})();
