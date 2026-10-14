from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/wave-command-intent.js";v=read(p).replace("function create(prefix,valid) {","function create(prefix,valid,options={}) {",1).replace("throw new Error('Некорректное решение по волне.');","throw new Error(options.invalid||'Некорректное решение по волне.');",1).replace("  window.wmsWaveCommandIntent={create,baseValid};","  window.wmsCommandIntent={create};\n  window.wmsWaveCommandIntent={create,baseValid};",1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.js";v=read(p)
v=v.replace('let view=null,pending=null,busy=false,generation=0,identity="";','let view=null,pending=null,damaged=null,busy=false,generation=0,identity="";\n  const intent=window.wmsHuIntent;',1)
v=v.replace('    el("huRetry").hidden=!pending;','''    el("huRetry").hidden=!pending;
    el("huRecoverDamaged").hidden=!damaged;
    for(const id of ["huCreate","huAttach","huDetach","huMove","huShip","huUnpack","huPlanMove","huRepackSlot","huRelocateSlot"]){
      el(id).disabled=busy||!!pending||!!damaged;
    }
    const note=el("huRecoveryStatus");
    note.textContent=damaged?"Повреждённый запрос блокирует новые операции. Сверьте текущее место и журнал операций; архив сохраняет исходный текст и не отменяет проведённое движение.":pending?"Ответ на сохранённую операцию не подтверждён. Повтор отправит исходный идентификатор, версии и сканы.":"";
    note.hidden=!(pending||damaged);''',1)
v=v.replace('    if(pending){status("Сначала повторите сохранённую операцию.");return;}','    if(pending||damaged){status("Сначала восстановите сохранённую операцию.");return;}',1)
old='      pending={action,body};try{localStorage.setItem(scope,JSON.stringify(pending));}catch(e){pending=null;throw new Error("Не удалось сохранить операцию: "+e.message);}\n      await send(scope);'
assert old in v
v=v.replace(old,'''      try{intent.save({action,body});pending={action,body};}
      catch(e){pending=null;throw new Error("Операция не отправлена: "+e.message);}
      await send(scope,true);''',1)
v=v.replace('  async function send(scope){\n    const saved=pending;','''  async function send(scope,firstAttempt=false){
    const record=intent.read(),saved=record.value;
    if(record.damaged||!saved||key()!==scope||JSON.stringify(saved)!==JSON.stringify(pending))
      throw new Error("Сохранённый запрос изменился. Перечитайте состояние.");
''',1)
v=v.replace('      if(data.detail?.outcome_confirmed===true){localStorage.removeItem(scope);if(key()===scope)pending=null;}','''      if(firstAttempt&&![401,403].includes(r.status)&&data.detail?.operation_id===saved.body.operation_id
        &&data.detail?.outcome_confirmed===true&&!data.detail?.retry_same_operation_id
        &&!["OPERATION_CONFLICT","OPERATION_PAYLOAD_CONFLICT"].includes(data.detail?.code)){
        intent.settle(record);if(key()===scope)pending=null;
      }''',1)
v=v.replace('    localStorage.removeItem(scope);\n    if(key()!==scope)return;','''    if(!intent.confirms(saved,data))throw new Error("Ответ не соответствует сохранённой операции. Повторите исходный запрос.");
    if(key()!==scope)return;
    intent.settle(record);''',1)
old='    try{pending=JSON.parse(localStorage.getItem(next)||"null");if(pending)el("huIdentifier").value=pending.body.identifier;}'
assert old in v
v=v.replace(old,'''    try{const record=intent.read();pending=record.value;damaged=record.damaged?record:null;if(pending)el("huIdentifier").value=pending.body.identifier;}''',1)
v=v.replace('identity=next;view=null;generation++;pending=null;','identity=next;view=null;generation++;pending=null;damaged=null;',1)
needle='  window.addEventListener("wms-admin-auth-ready",auth);auth();'
assert needle in v
v=v.replace(needle,'''  el("huRecoverDamaged").addEventListener("click",async()=>{
    if(busy||!damaged)return;
    busy=true;controls();const record=damaged,scope=key(),identifier=el("huIdentifier").value;
    try{
      if(!identifier)throw new Error("Укажите место для сверки.");
      const current=await get(identifier);
      if(scope!==key()||identifier!==el("huIdentifier").value)throw new Error("Контекст места изменился.");
      if(!current?.root||!Array.isArray(current.nodes)||!current.nodes.length)throw new Error("Состав не получен.");
      intent.archiveDamaged(record);damaged=null;pending=null;view=current;view.scannedIdentifier=identifier;render(current);
      status("Исходный текст запроса сохранён в архиве. Текущий состав перечитан; прошлое движение не отменено.");
    }catch(e){status(e.message);}finally{busy=false;controls();}
  });
  window.addEventListener("storage",event=>{
    if(event.key!==identity||busy)return;
    try{const record=intent.read();pending=record.value;damaged=record.damaged?record:null;view=null;generation++;controls();}
    catch(e){status(e.message);}
  });
'''+needle,1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.html";v=read(p).replace('<p id="huStatus" role="status"></p>','<p id="huStatus" role="status"></p><p id="huRecoveryStatus" class="hu-helper" role="status" hidden></p><button id="huRecoverDamaged" hidden>Сверить состав и архивировать повреждённый запрос</button>',1).replace('<script src="warehouse-hus.js?v=20261013-997">','<script src="wave-command-intent.js?v=20261013-1004"></script><script src="hu-command-intent.js?v=20261013-1004"></script><script src="warehouse-hus.js?v=20261013-1004">',1);files[p]=v
print(json.dumps(files,ensure_ascii=True))
