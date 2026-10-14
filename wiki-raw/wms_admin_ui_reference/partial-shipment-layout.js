(() => {
  "use strict";
  let proposal = null, busy = false;
  const e = id => document.getElementById(id);
  const key = () => JSON.stringify(["retailcase.partialShipmentLayout", cpTsdApiBase(), cpTsdUser()]);
  const saved = () => JSON.parse(localStorage.getItem(key()) || "null");
  function pendingState() {
    const pending = saved();
    e("cpTsdRetryPartialLayout").hidden = !pending;
    e("cpTsdPartialPreview").disabled = busy || !!pending;
    e("cpTsdPartialPrepare").disabled = busy || !!pending || !proposal;
    e("cpTsdPartialReason").disabled = !!pending;
  }
  async function preview() {
    if (!cpTsd.task) throw Error("Выберите закрытую паллету отбора.");
    if (saved()) throw Error("Сначала повторите сохранённую укладку.");
    const identifier = e("cpTsdShipmentIdentifier").value.trim(), task = cpTsd.task.case_pick_task_id;
    if (!identifier) throw Error("Отсканируйте идентификатор подготовленной паллеты СТ.");
    const data = await cpTsdFetch("/api/case-pick/tasks/" + task + "/partial-shipment-layout?pallet_identifier=" + encodeURIComponent(identifier));
    if (cpTsd.task?.case_pick_task_id !== task || e("cpTsdShipmentIdentifier").value.trim() !== identifier) return;
    proposal = {...data, pallet_identifier: identifier};
    e("cpTsdPartialComposition").replaceChildren();
    for (const row of data.package_counts) {
      const label = document.createElement("label"), input = document.createElement("input");
      label.append(document.createTextNode(row.article + ": " + row.quantity + " " + row.base_uom + " · упаковок "));
      input.type = "number"; input.min = "1"; input.max = "1000000000"; input.step = "1";
      input.dataset.article = row.article; input.value = row.proposed_pack_count ?? "";
      label.append(input); e("cpTsdPartialComposition").append(label);
    }
    cpTsdSetState("Проверьте фактическое число упаковок. Вес для планирования будет пересчитан по нормативу.");
  }
  async function send(pending) {
    try {
      await cpTsdFetch("/api/case-pick/tasks/" + pending.task_id + "/partial-shipment-layout",
        {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(pending.request)});
      localStorage.removeItem(key()); proposal = null;
      if (cpTsd.task?.case_pick_task_id === pending.task_id) {
        cpTsd.task = await cpTsdFetch("/api/case-pick/tasks/" + pending.task_id);
        cpTsdRender();
      }
      cpTsdSetState("Частичная укладка СТ сохранена. Теперь свяжите с ней паллету отбора.");
    } catch (error) {
      if (error.status >= 400 && error.status < 500 && !String(error.message).includes("operation content conflict")) {
        localStorage.removeItem(key()); proposal = null;
      }
      throw error;
    }
  }
  async function prepare() {
    if(busy||window.cpTsdStockBusy||window.wmsCaseType?.hasPending())throw Error("Сначала завершите сохранённую складскую команду.");
    if (!proposal || !cpTsd.task) throw Error("Сначала загрузите фактический состав.");
    if (cpTsd.task.case_pick_task_id !== proposal.task_id || e("cpTsdShipmentIdentifier").value.trim() !== proposal.pallet_identifier)
      throw Error("Выбранная паллета изменилась; загрузите состав снова.");
    const reason = e("cpTsdPartialReason").value.trim(), scan = e("cpTsdScanContainer").value.trim();
    if (reason.length < 3 || scan !== proposal.carrier_identifier) throw Error("Отсканируйте носитель и укажите причину частичной отгрузки.");
    const packs = {};
    for (const input of e("cpTsdPartialComposition").querySelectorAll("input[data-article]")) {
      const n = Number(input.value);
      if (!Number.isInteger(n) || n < 1 || n > 1000000000) throw Error("Укажите целое число фактических упаковок для каждого товара.");
      packs[input.dataset.article] = n;
    }
    const pending = {task_id:proposal.task_id, request:{
      operation_id:"PART.LAYOUT:"+crypto.randomUUID(), pallet_identifier:proposal.pallet_identifier,
      scan_container:scan, expected_content_version:proposal.content_version,
      expected_physical_signature:proposal.physical_signature, expected_layout_signature:proposal.layout_signature,
      reason, actual_pack_counts:packs}};
    localStorage.setItem(key(), JSON.stringify(pending));
    await send(pending);
  }
  function action(id, fn) {
    e(id).addEventListener("click", async () => {
      if (busy || window.cpTsdStockBusy || window.wmsCaseType?.hasPending()) return;
      busy = true; window.cpTsdStockBusy = true; pendingState();
      try {await fn();} catch (error) {cpTsdSetState(error.message);}
      finally {busy = false; window.cpTsdStockBusy = false; pendingState();}
    });
  }
  window.addEventListener("DOMContentLoaded", () => {
    action("cpTsdPartialPreview", preview); action("cpTsdPartialPrepare", prepare);
    action("cpTsdRetryPartialLayout", async () => {const pending=saved(); if(pending)await send(pending);});
    pendingState();
    if (saved()) cpTsdSetState("Повторите сохранение укладки, чтобы подтвердить результат.");
  });
})();
