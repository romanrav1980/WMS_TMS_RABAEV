(() => {
  "use strict";
  let busy = false;
  async function bind() {
    if (busy || window.cpTsdStockBusy) return;
    busy = true; window.cpTsdStockBusy = true;
    cpTsdEl("cpTsdBindShipment").disabled = true;
    try {
      if (!cpTsd.task) throw new Error("Выберите паллету отбора.");
      for (const kind of ["nicora.casePickIntent", "nicora.caseCarrierMove", "nicora.caseCarrierReturn"]) {
        if (localStorage.getItem(JSON.stringify([kind, cpTsdApiBase(), cpTsdUser()])))
          throw new Error("Сначала повторите незавершённую команду.");
      }
      const pallet = cpTsdEl("cpTsdShipmentIdentifier").value.trim();
      const scan = cpTsdEl("cpTsdScanContainer").value.trim();
      if (!pallet || !scan) throw new Error("Отсканируйте паллету отбора и подготовленную паллету СТ.");
      await cpTsdFetch("/api/case-pick/tasks/" + cpTsd.task.case_pick_task_id + "/bind-shipment",
        {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
          pallet_identifier:pallet,scan_container:scan,expected_content_version:cpTsd.task.content_version})});
      cpTsd.task = await cpTsdFetch("/api/case-pick/tasks/" + cpTsd.task.case_pick_task_id);
      cpTsdRender(); cpTsdSetState("Паллета связана с отгрузкой СТ.");
    } catch (error) { cpTsdSetState(error.message); }
    finally { busy = false; window.cpTsdStockBusy = false; cpTsdEl("cpTsdBindShipment").disabled = false; }
  }
  window.addEventListener("DOMContentLoaded",()=>cpTsdEl("cpTsdBindShipment").addEventListener("click",bind));
})();
