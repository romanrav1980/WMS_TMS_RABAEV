import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];out={}
p=r/"api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py";s=p.read_text(encoding="utf-8").replace('Literal["RETURNED_TO_PLANNING"]','Literal["RETURNED_TO_PLANNING", "PARTIAL_SHIPPED_RETURNED"]')
s=s.replace("raise HTTPException(503 if uncertain else 409, detail={","raise HTTPException(503 if uncertain else 403 if exc.oracle_code == 20882 else 409, detail={")
out[str(p.relative_to(r))]=s
p=r/"api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py";s=p.read_text(encoding="utf-8")
needle='data["physical_stock_changed"] = False'
s=s.replace(needle,'''cur.execute("select RRL_WAVE_EXEC_ACCESS.mixed_snapshot_json(:p_wave)from dual", p_wave=wave)
        raw = cur.fetchone()[0]
        data["mixed_decision"] = json.loads(raw.read() if hasattr(raw, "read") else raw)
        data["physical_stock_changed"] = False''')
out[str(p.relative_to(r))]=s
p=r/"wiki-raw/wms_admin_ui_reference/wave-execution.js";s=p.read_text(encoding="utf-8")
s=s.replace('<label>Причина решения','<button data-partial>Завершить частично отгруженную волну</button><label>Причина решения')
s=s.replace('let pending=null,request=0,busy=false,identity="",deferEligible=false;','const partialButton=panel.querySelector("[data-partial]");\n  let pending=null,request=0,busy=false,identity="",deferEligible=false,mixedEligible=false;')
s=s.replace('deferEligible=data.deferred_decision?.eligible===true;','deferEligible=data.deferred_decision?.eligible===true;mixedEligible=data.mixed_decision?.eligible===true;')
s=s.replace('deferButton.disabled=busy||(!pending&&!deferEligible);','deferButton.disabled=busy||(!pending&&!deferEligible);partialButton.disabled=busy||(!pending&&!mixedEligible);')
s=s.replace('if(disposition&&(!deferEligible||!reasonInput.value.trim()))','if(disposition&&(!(disposition==="PARTIAL_SHIPPED_RETURNED"?mixedEligible:deferEligible)||!reasonInput.value.trim()))')
s=s.replace('reasonInput.disabled=true;deferButton.disabled=true;','reasonInput.disabled=true;partialButton.disabled=true;deferButton.disabled=true;')
s=s.replace('deferButton.disabled=!pending;await load();','deferButton.disabled=!pending;partialButton.disabled=!pending;await load();')
s=s.replace('deferButton.addEventListener("click",()=>release("RETURNED_TO_PLANNING"));','deferButton.addEventListener("click",()=>release("RETURNED_TO_PLANNING"));\n  partialButton.addEventListener("click",()=>release("PARTIAL_SHIPPED_RETURNED"));')
s=s.replace('deferButton.hidden=button.hidden||!window.wmsAdminAuth?.hasPermission("pick_wave_cancel");','deferButton.hidden=button.hidden||!window.wmsAdminAuth?.hasPermission("pick_wave_cancel");partialButton.hidden=deferButton.hidden;')
s=s.replace('if(!pending){\n      if(disposition','if(pending&&disposition&&pending.body.disposition!==disposition){status.textContent="Сначала повторите сохранённое решение.";return;}\n    if(!pending){\n      if(disposition')
s=s.replace('deferEligible=data.deferred_decision?.eligible===true;', 'button.textContent=pending?"Повторить сохранённое решение":"Завершить волну";\n    deferEligible=data.deferred_decision?.eligible===true;')
# Per-line quantities remain separate, explicitly not a shipping proof.
needle='    button.textContent=pending?'
pos=s.index(needle)
s=s[:pos]+'''    for(const demand of data.mixed_decision?.demands||data.deferred_decision?.demands||[]){
      const current=demand.current_planning;if(!current)continue;
      const p=document.createElement("p");p.textContent="Заказ "+current.order_id+", строка "+current.line_id+
        ": незакреплённая потребность "+current.quantity+" "+current.unit+"; отобрано "+current.picked_quantity+
        ", закреплено "+current.hard_quantity+". Это расчёт планирования, не подтверждение отгрузки.";
      panel.querySelector("[data-items]").append(p);
    }
'''+s[pos:]
out[str(p.relative_to(r))]=s
print(json.dumps(out))
