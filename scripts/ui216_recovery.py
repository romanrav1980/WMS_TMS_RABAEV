from pathlib import Path
import json
out={}
out["wiki-raw/wms_admin_ui_reference/tare-load-recovery.html"]='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Тара возвращённой погрузки</title><link rel="stylesheet" href="styles.css"></head><body class="auth-pending" data-required-permission="wms_admin_login"><div class="app"><aside class="sidebar"><div class="brand">WMS</div><nav class="nav" data-admin-nav data-active-nav="tare-load-recovery"></nav></aside><main class="workspace"><header class="topbar"><h1>Тара возвращённой погрузки</h1></header><section class="panel" data-permission="tare_view"><label>Исходная погрузка<input id="recoveryLoad" maxlength="100" autocomplete="off"></label><button id="recoveryRefresh">Показать подтверждённые возвраты</button><p>Возврат из машины подтверждают водитель и склад в разделе «Оборотная тара». Здесь возвращённая тара закрепляется за прежним физическим местом. Выгрузку товара подтвердите на странице погрузки.</p><div id="recoveryRows"></div></section><section class="panel" data-permission="tare_plan"><label>Возвращённое место<select id="recoverySource"></select></label><label>Идентификатор паллеты<input id="recoveryScan" autocomplete="off" maxlength="200" title="Отсканируйте исходное физическое место, вернувшееся из машины."></label><button id="recoveryConfirm">Закрепить возвращённую тару</button><button id="recoveryRetry" hidden>Повторить сохранённое закрепление</button><button id="recoveryRestart" hidden>Исправить данные после отказа</button></section><p id="recoveryStatus" role="status"></p></main></div><script src="admin-nav.js"></script><script src="admin-auth.js"></script><script src="tare-load-recovery.js"></script></body></html>'''
out["wiki-raw/wms_admin_ui_reference/tare-load-recovery.js"]='''(() => {
 "use strict";
 const el = id => document.getElementById(id);
 const base = () => window.wmsAdminAuth.state.apiBase.replace(/\\/$/, "");
 const key = () => JSON.stringify(["retailcase.tareLoadRecovery", base(), window.wmsAdminAuth.state.user?.username || ""]);
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
  const body = {operation_id:"TARE.RECOVERY:" + crypto.randomUUID(),place_kind:"CASE",place_id:row.place_id,pallet_type_id:row.pallet_type_id,
   expected_warehouse_id:row.ware_id,load_recovery:{load_operation_id:row.load_operation_id,original_booking_operation_id:row.original_booking_operation_id,
    return_offer_operation_id:row.return_offer_operation_id,expected_load_version:row.expected_load_version,scan_place:scan}};
  try {pending = {body};localStorage.setItem(key(),JSON.stringify(pending));await send(key());}
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
'''
p=Path("wiki-raw/wms_admin_ui_reference/admin-nav.js");s=p.read_text(encoding="utf-8").replace("const WMS_ADMIN_NAV_ITEMS = [","const WMS_ADMIN_NAV_ITEMS = [\n  { key: 'tare-load-recovery', label: 'Тара возвращённой погрузки', href: 'tare-load-recovery.html', icon: 'orders', permission: 'tare_view' },",1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8").replace('<button id="unloadLoadSlots"','<a id="unloadTareRecovery" href="tare-load-recovery.html" data-permission="tare_view">Возврат и закрепление тары</a>\n<button id="unloadLoadSlots"',1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-unloading.js");s=p.read_text(encoding="utf-8").replace('  el("unloadOrigin").textContent','  el("unloadTareRecovery").href = "tare-load-recovery.html" + (row ? "?load_operation_id=" + encodeURIComponent(row.load_operation_id) : "");\n  el("unloadOrigin").textContent',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
