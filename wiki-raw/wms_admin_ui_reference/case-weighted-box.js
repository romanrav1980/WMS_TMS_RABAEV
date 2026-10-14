window.cpWeightedBox = (() => {
  let panel, generation = 0;
  function show(policy) {
    panel ||= document.getElementById("cpTsdWeightedBox");
    const currentGeneration = ++generation;
    panel.replaceChildren();
    panel.hidden = !policy.serialized_weight_boxes && !policy.loose_weight_kg;
    const fact = document.getElementById("cpTsdFactQty");
    fact.disabled = Boolean(policy.serialized_weight_boxes || policy.loose_weight_kg);
    if (panel.hidden) return;
    const note = document.createElement("p");
    note.textContent = policy.serialized_weight_boxes ? "Отсканируйте серийную весовую коробку. Факт в KG рассчитает система по её массе нетто." : "Для товара на развес выберите архивное нетто-показание. Количество рассчитает система.";
    panel.appendChild(note);
    const label = document.createElement("label");
    label.textContent = "Архив весового поста: ";
    const select = document.createElement("select");
    select.dataset.scale = "capture"; select.setAttribute("aria-label", "Архив весового поста"); select.title = "Выберите неиспользованное показание для текущей строки и версии состава";
    select.appendChild(new Option(policy.loose_weight_kg ? "Выберите обязательное нетто-показание" : "Без показания весового поста", ""));
    select.addEventListener("change", () => { fact.disabled = Boolean(policy.serialized_weight_boxes || policy.loose_weight_kg || select.value); });
    label.appendChild(select); panel.appendChild(label);
    const task = cpTsd.task, line = cpTsdCurrentLine();
    if (task && line) {
      const admission = document.createElement("p"); admission.textContent = "Расчёт допуска заказа...";
      panel.appendChild(admission);
      cpTsdFetch("/api/case-pick/tasks/" + task.case_pick_task_id + "/lines/" + line.case_pick_line_id + "/order-weight-preview")
        .then(data => {
          if (generation !== currentGeneration) return;
          admission.textContent = "Заказ: " + data.requested_quantity + " KG; отобрано: " + data.picked_quantity +
            " KG; допуск: " + data.tolerance_pct + "% (" + data.lower_quantity + "–" + data.upper_quantity + " KG). " +
            (data.within_tolerance ? "В пределах допуска. Для завершения требуется решение." : "Текущее количество вне допуска.");
        }).catch(error => { if (generation === currentGeneration) admission.textContent = error.message; });
    }

    if(task&&line)window.cpScaleArchive.mount({panel,select,task,line,policy,isCurrent:()=>generation===currentGeneration});

    for (const profile of policy.profiles) {
      const label = document.createElement("label");
      label.textContent = profile.system_code + " / " + profile.profile_code + ": код этой коробки";
      const input = document.createElement("input");
      input.autocomplete = "off";
      input.dataset.system = profile.system_code;
      input.dataset.profile = profile.profile_code;
      label.appendChild(input); panel.appendChild(label);
    }
  }
  function payload(operation, cell, container) {
    const barcode = document.getElementById("cpTsdScanBox").value;
    if (!barcode) throw new Error("Отсканируйте этикетку весовой коробки.");
    const scans = Array.from(panel.querySelectorAll("input[data-system][data-profile]")).map(input => {
      if (!input.value) throw new Error("Отсканируйте код для каждого применимого профиля маркировки.");
      return { system_code: input.dataset.system, profile_code: input.dataset.profile, code: input.value };
    });
    const scale = panel.querySelector("select[data-scale]").value;
    return { ...(scale ? {warehouse_scale_capture: scale} : {}), operation_id: operation, weighted_box_barcode: barcode, scan_cell: cell,
      scan_container: container, unit_scans: scans };
  }
  function selectedScale() { return panel?.querySelector("select[data-scale]")?.value || ""; }
  function netPayload(operation, cell, container) {
    const capture = selectedScale();
    if (!capture) throw new Error("Выберите нетто-показание весового поста.");
    return {operation_id: operation, warehouse_scale_capture: capture, scan_cell: cell, scan_container: container};
  }
  return { show, payload, selectedScale, netPayload };
})();
