from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");t=p.read_text(encoding="utf-8")
needle="async function api(path,options={}) {"
insert="""async function recover(){
  if(busy)return;try{pending();return;}catch{}
  const identity=scope(),storageKey=key(),raw=localStorage.getItem(storageKey),st=el('sdSt').value.trim(),token=++epoch;
  if(!st)return;busy=true;context=null;clearTrip();showSummary(null);controls();
  try{
   localStorage.setItem(storageKey+':archive:'+crypto.randomUUID(),raw||'');
   const value=await api('/context?'+new URLSearchParams({st_number:st}));
   if(identity!==scope()||token!==epoch||st!==el('sdSt').value.trim())return;
   if(localStorage.getItem(storageKey)!==raw)throw Error('Команда изменена другой вкладкой. Исходник сохранён.');
   localStorage.removeItem(storageKey);context=value;showSummary(value);
   el('sdMessage').textContent='Повреждённый исходник сохранён в архив. Текущее состояние СТ перечитано. Перед новой командой проверьте историю переносов.';
  }catch(error){if(identity===scope()&&token===epoch)el('sdMessage').textContent=error.message+' Новая отправка остаётся заблокированной.';}
  finally{busy=false;controls();}
 }
 """
assert needle in t;t=t.replace(needle,insert+needle)
t=t.replace("el('sdPending').textContent=damaged?","el('sdRecover').disabled=busy||!damaged||!el('sdSt').value.trim();\n  el('sdPending').textContent=damaged?")
t=t.replace("el('sdRead').addEventListener('click',read);","el('sdRecover').addEventListener('click',recover);el('sdRead').addEventListener('click',read);")
# Check cross-tab before signalling confirmed selection.
line="if(localStorage.getItem(requestKey)!==requestRaw)throw Error('Команда в другой вкладке изменилась. Её исходник сохранён.');"
t=t.replace("   "+line+"\n","")
t=t.replace("   window.dispatchEvent(new CustomEvent('wms-st-deferral-selected',{detail:result}));","   "+line+"\n   window.dispatchEvent(new CustomEvent('wms-st-deferral-selected',{detail:result}));")
files[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");t=p.read_text(encoding="utf-8")
t=t.replace('<p id="sdPending"', '<button data-permission="transport_dispatch_edit" id="sdRecover" disabled title="Сохранить повреждённый исходник в архив и перечитать текущее состояние СТ">Восстановить повреждённый черновик</button>\n<p id="sdPending"')
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
