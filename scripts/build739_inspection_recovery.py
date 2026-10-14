from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8").replace('<p id="diPending">','<button id="diRecover" disabled>Сохранить архив и перечитать подписи</button>\n<p id="diPending">');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-inspection.js");s=p.read_text(encoding="utf-8")
s=s.replace('  el("diSave").disabled=', '  el("diReview").disabled=busy||!!pending;el("diRecover").disabled=busy||!corrupt||!el("diReview").value.trim();\n  el("diSave").disabled=',1)
pos=s.index(' async function send(')
recovery=""" async function recover(){
  if(busy||!corrupt)return;const identity=scope(),storageKey=key(),review=el("diReview").value.trim(),token=++epoch;
  if(!review)return;busy=true;controls();
  try{
   const raw=localStorage.getItem(storageKey);localStorage.setItem(storageKey+":archive:"+crypto.randomUUID(),raw||"");
   const value=await api("/reviews/"+encodeURIComponent(review)+"/shipping-inspections");
   if(identity!==scope()||token!==epoch)return;
   if(localStorage.getItem(storageKey)!==raw)throw Error("Исходник изменён другой вкладкой. Повторите восстановление.");
   localStorage.removeItem(storageKey);corrupt=false;pending=null;show(value);
   message("Исходник сохранён в архив. Подписи выбранной сверки перечитаны; перед новым осмотром проверьте её актуальность.");
  }catch(error){if(identity===scope()&&token===epoch)message(error.message+" Отправка остаётся заблокированной.");}
  finally{busy=false;controls();}
 }
"""
s=s[:pos]+recovery+s[pos:]
s=s.replace('el("diRead").onclick=read;','el("diRecover").onclick=recover;el("diRead").onclick=read;')
s=s.replace('if(!busy&&!pending&&!corrupt){el("diReview").value=event.detail.operation_id;read();}','if(!busy&&!pending){el("diReview").value=event.detail.operation_id;if(corrupt)controls();else read();}')
old='if(!value||typeof value.operation_id!=="string"||typeof value.review_operation_id!=="string"||!["WAREHOUSE_CHIEF","DISPATCHER"].includes(value.inspection_role)||typeof value.observed_empty!=="boolean"||typeof value.note!=="string"||!/^[a-f0-9]{64}$/.test(value.source_hash))'
new='if(!value||Object.keys(value).length!==6||typeof value.operation_id!=="string"||value.operation_id.length>100||!/^[A-Za-z0-9_.:-]+$/.test(value.operation_id)||typeof value.review_operation_id!=="string"||!value.review_operation_id||value.review_operation_id.length>100||!["WAREHOUSE_CHIEF","DISPATCHER"].includes(value.inspection_role)||typeof value.observed_empty!=="boolean"||typeof value.note!=="string"||value.note.trim().length<8||value.note.length>500||!/^[a-f0-9]{64}$/.test(value.source_hash))'
assert old in s;s=s.replace(old,new);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
