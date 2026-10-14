from pathlib import Path
import json
files={};p=Path('wiki-raw/wms_admin_ui_reference/st-waiting-tasks.js');t=p.read_text(encoding='utf-8')
t=t.replace("el('swRead').disabled=loading||!selected;", "el('swRecover').disabled=true;\n   el('swRead').disabled=loading||!selected;")
t=t.replace("el('swPending').textContent=e.message;}","el('swPending').textContent=e.message;el('swRecover').disabled=busy||loading||!/^[A-Za-z0-9_.:-]{1,100}$/.test(el('swDecision').value.trim());}")
needle=' async function send(){'
insert=""" async function recover(){
  if(busy||loading)return;try{pending();return;}catch{}
  const savedKey=key(),raw=localStorage.getItem(savedKey),identity=scope(),decision=el('swDecision').value.trim(),epoch=++readEpoch;
  if(!/^[A-Za-z0-9_.:-]{1,100}$/.test(decision))return;
  loading=true;controls();
  try{
   localStorage.setItem(savedKey+':archive:'+crypto.randomUUID(),raw||'');
   const result=await request('?'+new URLSearchParams({decision_operation_id:decision,limit:'100'}));
   if(epoch!==readEpoch||identity!==scope()||el('swDecision').value.trim()!==decision)return;
   if(result.decision_operation_id!==decision||!Array.isArray(result.tasks))throw Error('Неожиданный ответ WMS.');
   if(localStorage.getItem(savedKey)!==raw)throw Error('Исходник изменён другой вкладкой.');
   localStorage.removeItem(savedKey);rows=result.tasks;next=result.next_after_task_id;shownDecision=decision;render();
   el('swMessage').textContent='Повреждённый исходник сохранён в архив. Текущие задания перечитаны. Проверьте их перед созданием нового плана; архивирование не подтверждает физическое перемещение.';
  }catch(error){if(epoch===readEpoch&&identity===scope())el('swMessage').textContent=error.message+' Создание остаётся заблокированным.';}
  finally{if(epoch===readEpoch)loading=false;controls();}
 }
"""
assert needle in t;t=t.replace(needle,insert+needle)
t=t.replace("el('swPlan').addEventListener('click',send);", "el('swRecover').addEventListener('click',recover);el('swPlan').addEventListener('click',send);")
t=t.replace(" controls();\n})();", " window.addEventListener('storage',event=>{if(event.key===key())controls();});\n controls();\n})();")
files[str(p)]=t
p=Path('wiki-raw/wms_admin_ui_reference/day-reconciliation.html');t=p.read_text(encoding='utf-8').replace('20261013-812','20261013-820')
t=t.replace('<p id="swPending"','<button data-permission="warehouse_task_edit" id="swRecover" disabled title="Сохранить повреждённую команду в архив и прочитать зарегистрированные задания">Архивировать черновик и прочитать задания</button>\n<p id="swPending"')
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
