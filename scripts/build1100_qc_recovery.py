from pathlib import Path
import json
f={};p="wiki-raw/wms_admin_ui_reference/outgoing-quality.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace('<button data-load>Предъявить к контролю</button>','<button data-read>Прочитать состав</button><button data-load>Предъявить к контролю</button>',1)
s=s.replace('<p role="status" aria-live="polite"></p>', '<button data-recover hidden>Архивировать повреждённый исходник и перечитать состав</button><p role="status" aria-live="polite"></p>',1)
s=s.replace('finalGeneration=0;','finalGeneration=0,pendingRecord=null,draftRaw=null;',1)
s=s.replace(' const draftKey=()=>key()+":scans";',' const draftKey=()=>key()+":scans";\n const intent=window.wmsQualityIntent;',1)
s=s.replace(' function saveDraft(){localStorage.setItem(draftKey(),JSON.stringify(draft));count();}',""" function saveDraft(){
  if(!intent.validDraft(draft))throw Error("Некорректный состав сканов.");
  if(localStorage.getItem(draftKey())!==draftRaw)throw Error("Сканы изменены другой вкладкой. Перечитайте состав.");
  const raw=JSON.stringify(draft);localStorage.setItem(draftKey(),raw);
  if(localStorage.getItem(draftKey())!==raw)throw Error("Сканы не сохранены.");draftRaw=raw;count();controls();
 }
 function damaged(){return intent.read().damaged||intent.readDraft(draftKey()).damaged;}
 function controls(){
  if(!window.wmsAdminAuth?.state?.user?.username)return;
  const broken=Boolean(damaged());
  for(const name of ["load","scan","weight","add-item","add-mark","last","clear","print-label","final-refresh"])el(name).disabled=busy||broken;
  for(const name of ["add-item","add-mark","last","clear"])el(name).disabled=busy||broken||!!pending;
  el("id").disabled=busy||!!pending;el("read").disabled=busy;
  el("recover").hidden=!broken;el("recover").disabled=busy||!el("id").value.trim();
  el("load").textContent=pending?"Повторить сохранённую команду":"Предъявить к контролю";
 }
 async function readOnly(){
  if(busy)return;const id=el("id").value.trim(),current=++generation;if(!id||id.length>150)return;
  snapshot=null;busy=true;controls();
  try{const data=await call(path(id));if(current===generation&&el("id").value.trim()===id){
    if(data.shipment_identifier!==id)throw Error("Ответ относится к другой СТ.");show(data);
    if(damaged())message.textContent+=" Сохранённый исходник повреждён. Новые команды заблокированы.";
   }}catch(e){if(!e.obsolete&&current===generation)message.textContent=e.message;}
  finally{busy=false;controls();}
 }
 async function recover(){
  if(busy)return;const saved=intent.read(),scans=intent.readDraft(draftKey()),scope=key(),id=el("id").value.trim(),current=++generation;
  if((!saved.damaged&&!scans.damaged)||!id||id.length>150)return;
  busy=true;controls();
  try{
   const data=await call(path(id));
   if(current!==generation||scope!==key()||el("id").value.trim()!==id)return;
   if(data.shipment_identifier!==id)throw Error("Ответ относится к другой СТ.");
   if(saved.damaged)intent.archiveDamaged(saved);
   if(scans.damaged){
    if(scope!==key()||localStorage.getItem(scans.storageKey)!==scans.raw)throw Error("Исходник сканов изменился.");
    const archive=scans.storageKey+":damaged:"+crypto.randomUUID();localStorage.setItem(archive,scans.raw);
    if(localStorage.getItem(archive)!==scans.raw)throw Error("Архив сканов не сохранён.");
    localStorage.removeItem(scans.storageKey);
   }
   pendingRecord=intent.read();pending=pendingRecord.value;
   const latest=intent.readDraft(draftKey());draft=latest.value;draftRaw=latest.raw;show(data);
   message.textContent+=" Повреждённый исходник сохранён в архив. Физическое проведение прежней команды этим не подтверждается.";
  }catch(e){if(!e.obsolete&&current===generation)message.textContent=e.message+" Новые команды остаются заблокированными.";}
  finally{busy=false;controls();}
 }""",1)
# Finish render applies damaged/pending state even after read-only auto-link.
s=s.replace(':" "+explain(data.weight_policy_reason));', ':" "+explain(data.weight_policy_reason));controls();',1)
old='  const value={identifier,kind,body:clone(body)};localStorage.setItem(key(),JSON.stringify(value));pending=value;'
assert old in s
s=s.replace(old,'  const value={identifier,kind,body:clone(body)};pendingRecord=intent.save(value);pending=pendingRecord.value;controls();',1)
s=s.replace('  if(busy||!pending)return;','  if(busy||!pending)return;\n  if(damaged()||!pendingRecord||pendingRecord.storageKey!==key()||localStorage.getItem(pendingRecord.storageKey)!==pendingRecord.raw){message.textContent="Исходная команда изменилась или повреждена. Перечитайте состояние.";controls();return;}',1)
s=s.replace('   localStorage.removeItem(savedKey);pending=null;','   intent.settle(pendingRecord);pendingRecord=null;pending=null;',1)
# Keep another tab's scans instead of deleting its newer draft.
s=s.replace('localStorage.removeItem(draftKey());draft=null;}snapshot=null;', 'if(localStorage.getItem(draftKey())===draftRaw){localStorage.removeItem(draftKey());draftRaw=null;}draft=null;}snapshot=null;',1)
s=s.replace('localStorage.removeItem(key());pending=null;snapshot=null;', 'intent.settle(pendingRecord);pendingRecord=null;pending=null;snapshot=null;',1)
s=s.replace('el("kind").disabled=Boolean(snapshot?.final_scale_required);}\n }\n async function load', 'el("kind").disabled=Boolean(snapshot?.final_scale_required);controls();}\n }\n async function load',1)
s=s.replace('  if(busy)return;if(pending){await transmit();return;}\n  const id=', '  if(busy)return;if(damaged()){message.textContent="Сначала восстановите повреждённый исходник.";controls();return;}if(pending){await transmit();return;}\n  const id=',1)
s=s.replace('  if(busy||pending||!snapshot?.composition_signature', '  if(busy||pending||damaged()||!snapshot?.composition_signature',1)
s=s.replace('  if(busy||pending){message.textContent="Сначала повторите сохранённый результат.";return;}', '  if(busy||pending||damaged()){message.textContent="Сначала повторите или восстановите сохранённый результат.";return;}\n  if(localStorage.getItem(draftKey())!==draftRaw){message.textContent="Сканы изменены другой вкладкой.";return;}',1)
s=s.replace('localStorage.removeItem(draftKey());draft=snapshot?', 'localStorage.removeItem(draftKey());draftRaw=null;draft=snapshot?',1)
s=s.replace('  if(busy)return;if(pending){await transmit();return;}\n  if(!currentDraft()', '  if(busy)return;if(damaged()){controls();return;}if(pending){await transmit();return;}\n  if(!currentDraft()',1)
old='try{pending=JSON.parse(localStorage.getItem(key())||"null");const saved=JSON.parse(localStorage.getItem(draftKey())||"null");draft=saved?.entries?saved:null;count();'
assert old in s
s=s.replace(old,'try{pendingRecord=intent.read();pending=pendingRecord.value;const saved=intent.readDraft(draftKey());draft=saved.value;draftRaw=saved.raw;count();',1)
s=s.replace('   }catch(e){message.textContent=e.message;}\n  }\n }\n el("final-refresh")', '    if(damaged())message.textContent="Сохранённая команда или сканы повреждены. Укажите СТ, прочитайте актуальный состав и восстановите исходник.";controls();\n   }catch(e){message.textContent=e.message;}\n  }\n }\n el("final-refresh")',1)
s=s.replace('el("id").addEventListener("input",()=>{generation++;finalGeneration++;snapshot=null;finalPanel.hidden=true;});', 'el("read").onclick=readOnly;el("recover").onclick=recover;\n el("id").addEventListener("input",()=>{generation++;finalGeneration++;snapshot=null;finalPanel.hidden=true;controls();});',1)
s=s.replace(' window.addEventListener("wms-admin-auth-ready",rights);rights();',' window.addEventListener("storage",event=>{if(event.key===key()||event.key===draftKey())controls();});\n window.addEventListener("wms-admin-auth-ready",rights);rights();',1)
f[p]=s
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";s=Path(p).read_text(encoding="utf-8")
old='<script src="outgoing-quality.js?v=20261013-1094"></script>'
assert old in s
s=s.replace(old,'<script src="wave-command-intent.js?v=20261013-890"></script><script src="outgoing-quality-intent.js?v=20261013-1100"></script><script src="outgoing-quality.js?v=20261013-1100"></script>')
f[p]=s
p="wiki/components/retailcase_ni051_control_label_20261012.md";f[p]=Path(p).read_text(encoding="utf-8")+"\n1100 PREPARED UI recovery: shared wmsCommandIntent storage owner + separate QC contractvalidator; pending/draft damagedraw blocks newwrites. Read-only composition action separate fromPLAN; archive only after sameidentity freshGET beforedeletion. Exactoriginal command/raw retained andother-tabscans notdeleted. Native schema unchanged; runtime/JSfocused pending.\n"
f["wiki/index.md"]="- [QC recovery1100](components/retailcase_ni051_control_label_20261012.md): shared command storage + separate contractvalidator/read-only recovery; runtime pending.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
f["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1100: continue allspints, prepared damagedQC pending/draft restore with sharedstorage/refusedoverwrite/currentGET beforearchive-delete; nativeRoot unchanged, targetedruntime next.\n"
print(json.dumps(f,ensure_ascii=True))
