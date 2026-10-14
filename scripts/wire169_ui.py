import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/"wiki-raw/wms_admin_ui_reference/wave-execution.js";s=p.read_text(encoding="utf-8")
s=s.replace('<button data-release>Завершить волну</button>','<button data-release>Завершить волну</button> <button data-defer>Завершить с возвратом потребности в планирование</button><label>Причина решения <input data-reason maxlength="1000"></label>')
s=s.replace('let pending=null,request=0,busy=false,identity="";','const deferButton=panel.querySelector("[data-defer]"),reasonInput=panel.querySelector("[data-reason]");\n  let pending=null,request=0,busy=false,identity="",deferEligible=false;')
s=s.replace('status.textContent=data.completed?"Волна завершена.":','status.textContent=data.completed?(data.completion_outcome==="UNFULFILLED_RETURNED_TO_PLANNING"?"Работа волны завершена; заказ не исполнен, потребность сохранена для планирования.":"Работа волны завершена. Исполнение заказа смотрите в его фактических местах."):')
s=s.replace('button.disabled=busy||(!pending&&(!data.ready||data.completed));','deferEligible=data.deferred_decision?.eligible===true;\n    button.disabled=busy||(!pending&&(!data.ready||data.completed));\n    deferButton.disabled=busy||(!pending&&!deferEligible);')
s=s.replace('async function release(){','async function release(disposition=null){')
s=s.replace('if(!pending){\n      pending={wave,body:{operation_id:"WAVE.FINISH:"+crypto.randomUUID()}};',
'''if(!pending){
      if(disposition&&(!deferEligible||!reasonInput.value.trim())){status.textContent="Требуются допустимая возвращённая волна и причина решения.";return;}
      pending={wave,body:{operation_id:"WAVE.FINISH:"+crypto.randomUUID(),...(disposition?{disposition,reason:reasonInput.value.trim()}:{})}};''')
s=s.replace('busy=true;input.disabled=true;button.disabled=true;','busy=true;input.disabled=true;reasonInput.disabled=true;deferButton.disabled=true;button.disabled=true;')
s=s.replace('finally{busy=false;input.disabled=false;button.disabled=false;}','finally{busy=false;input.disabled=false;reasonInput.disabled=false;button.disabled=true;deferButton.disabled=!pending;await load();}')
s=s.replace('button.addEventListener("click",release);','button.addEventListener("click",()=>release());\n  deferButton.addEventListener("click",()=>release("RETURNED_TO_PLANNING"));')
s=s.replace('button.hidden=!window.wmsAdminAuth?.hasPermission("pick_wave_launch");','button.hidden=!window.wmsAdminAuth?.hasPermission("pick_wave_launch");deferButton.hidden=button.hidden||!window.wmsAdminAuth?.hasPermission("pick_wave_cancel");')
print(json.dumps({str(p.relative_to(r)):s}))
