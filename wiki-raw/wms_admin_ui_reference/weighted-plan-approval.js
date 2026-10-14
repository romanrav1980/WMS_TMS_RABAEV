(() => {
  let sending = false;
  const prefix = () => JSON.stringify(["retailcase.weightedBoxChoice",orderApiBase(),window.wmsAdminAuth?.state?.user?.username || ""]);
  const key = row => prefix() + ":" + row;
  const retry = document.createElement("button");
  retry.type = "button"; retry.textContent = "Повторить сохранённый выбор коробки";
  document.querySelector("main").prepend(retry);
  async function post(path, body) {
    const r = await fetch(orderApiBase() + path, {method:"POST",headers:orderHeaders({"Content-Type":"application/json"}),body:JSON.stringify(body)});
    const answer = await r.json();
    if (!r.ok) {
      const detail = answer.detail || {};
      const message = detail.oracle_code === 1 ? "Для строки или коробки уже есть согласованный выбор." :
        detail.oracle_code === 20882 ? "Нет права согласования для текущего склада." :
        detail.operation_id_conflict ? "Этот идентификатор относится к другому выбору." :
        detail.reason?.includes("CURRENT_SOURCE_CHANGED") ? "Источник изменился. Обновите список коробок." :
        detail.reason?.includes("SAME_SCANNED") ? "Скан не совпадает с выбранной коробкой." :
        detail.reason?.includes("CANCEL_ASSOCIATED_PLAN") ? "Сначала отмените связанный план отбора." :
        detail.outcome_confirmed === false ? "Результат не подтверждён. Повторите сохранённый выбор." :
        "Выбор не сохранён. Проверьте скан и основание.";
      throw Object.assign(new Error(message), {detail});
    }
    return answer;
  }
  async function send(storageKey, body) {
    if (sending) throw new Error("Дождитесь ответа по текущему выбору.");
    sending = true;
    const wasUnknown = Boolean(localStorage.getItem(storageKey + ":unknown"));
    try {
      localStorage.setItem(storageKey + ":unknown", "1");
      const result = await post("/api/picking/weighted-box-choices", body);
      localStorage.removeItem(storageKey); localStorage.removeItem(storageKey + ":unknown");
      orderEl("orderStatusText").textContent = "Выбор согласован: целая коробка " + result.selected_net_weight_kg + " KG.";
    } catch (error) {
      if (!wasUnknown && error.detail?.outcome_confirmed === true && !error.detail?.operation_id_conflict) {
        localStorage.removeItem(storageKey); localStorage.removeItem(storageKey + ":unknown");
      }
      throw error;
    } finally { sending = false; }
  }
  retry.addEventListener("click", async () => {
    retry.disabled = true;
    try {
      const keys = Object.keys(localStorage).filter(k => k.startsWith(prefix() + ":") && !k.endsWith(":unknown"));
      for (const storageKey of keys) await send(storageKey, JSON.parse(localStorage.getItem(storageKey)));
      if (!keys.length) orderEl("orderStatusText").textContent = "Сохранённых выборов нет.";
    } catch (error) { orderEl("orderStatusText").textContent = error.message; }
    finally { retry.disabled = false; }
  });
  document.addEventListener("retailcase-weighted-options", event => {
    const {row,source,panel,body} = event.detail;
    if (!orderCan("case_pick_short_approve")) return;
    if (source.active_choice) {
      const note = document.createElement("p");
      note.textContent = "Согласованный выбор: " + source.active_choice.selected_net_weight_kg + " KG.";
      panel.appendChild(note);
      const cancel = document.createElement("button"); cancel.type="button"; cancel.textContent="Отменить неиспользованный выбор";
      cancel.disabled=source.active_choice.status!=="ACCEPTED";
      cancel.addEventListener("click", async () => {
        const reason=prompt("Основание отмены согласованного выбора:");
        if (reason===null)return;
        if(reason.trim().length<3){orderEl("orderStatusText").textContent="Укажите основание отмены.";return;}
        cancel.disabled=true;
        try {
          await post("/api/picking/weighted-box-choices/"+encodeURIComponent(source.active_choice.choice_id)+"/cancel",{reason:reason.trim()});
          note.textContent="Выбор отменён. Исходное согласование сохранено.";
        } catch(error){orderEl("orderStatusText").textContent=error.message;cancel.disabled=false;}
      });
      panel.appendChild(cancel);
      return;
    }
    const rows=Array.from(body.children);
    source.boxes.forEach((box,index) => {
      const cell=document.createElement("td"),button=document.createElement("button");
      button.type="button";button.textContent=box.exception_required?"Согласовать исключение":"Согласовать выбор";
      button.disabled=!box.measurements_ready;
      button.addEventListener("click",() => {
        const form=document.createElement("form");
        const scanLabel=document.createElement("label"),scan=document.createElement("input");
        scanLabel.textContent="Отсканируйте ШК выбранной весовой коробки ";scan.autocomplete="off";scan.maxLength=512;scan.required=true;scanLabel.appendChild(scan);
        const reasonLabel=document.createElement("label"),reason=document.createElement("textarea");
        reasonLabel.textContent="Основание согласования ";reason.required=true;reason.minLength=3;reason.maxLength=1000;reasonLabel.appendChild(reason);
        const save=document.createElement("button");save.type="submit";save.textContent="Сохранить согласование";
        form.append(scanLabel,reasonLabel,save);panel.appendChild(form);scan.focus();
        form.addEventListener("submit",async e => {
          e.preventDefault();save.disabled=true;
          try {
            const storageKey=key(row);
            if(localStorage.getItem(storageKey))throw new Error("Сначала повторите сохранённый выбор.");
            const request={choice_id:"WEIGHT.BOX.UI:"+crypto.randomUUID(),customer_order_row_id:row,physical_unit_key:box.physical_unit_key,
              weighted_box_barcode:scan.value,source_signature:source.source_signature,
              choice_mode:box.exception_required?"LAST_WHOLE_BOX":"WITHIN_TOLERANCE",reason:reason.value.trim()};
            localStorage.setItem(storageKey,JSON.stringify(request));
            await send(storageKey,request);form.remove();
            for(const action of body.querySelectorAll("button"))action.disabled=true;
          }catch(error){orderEl("orderStatusText").textContent=error.message;save.disabled=false;}
        });
      });
      cell.appendChild(button);rows[index].appendChild(cell);
    });
  });
})();
