(() => {
  const el=id=>document.getElementById(id);
  let view=null,pending=null,damaged=null,busy=false,generation=0,identity="";
  const intent=window.wmsHuIntent;
  const requestedIdentifier=new URLSearchParams(window.location.search).get("identifier")||"";
  const key=()=>"wms-hu-intent:"+window.wmsAdminAuth.state.apiBase+":"+(window.wmsAdminAuth.state.user?.username||"");
  const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,"");
  const status=text=>{el("huStatus").textContent=text;};
  function controls(){
    document.querySelectorAll("main input,main select,main button").forEach(node=>{node.disabled=busy;});
    el("huRetry").hidden=!pending;
    el("huRecoverDamaged").hidden=!damaged;
    for(const id of ["huCreate","huAttach","huDetach","huMove","huShip","huUnpack","huPlanMove","huRepackSlot","huRelocateSlot"]){
      el(id).disabled=busy||!!pending||!!damaged||(id!=="huCreate"&&(!view||view.historical_composition));
    }
    const note=el("huRecoveryStatus");
    note.textContent=damaged?"Повреждённый запрос блокирует новые операции. Сверьте текущее место и журнал операций; архив сохраняет исходный текст и не отменяет проведённое движение.":pending?"Ответ на сохранённую операцию не подтверждён. Повтор отправит исходный идентификатор, версии и сканы.":"";
    note.hidden=!(pending||damaged);
  }
  async function get(identifier){
    const r=await fetch(base()+"/api/warehouse-hus/composition?identifier="+encodeURIComponent(identifier),{headers:window.wmsAdminAuth.headers()});
    const data=await r.json();if(!r.ok)throw new Error(JSON.stringify(data.detail||data));return data;
  }
  const measureText=value=>String(value??"—").replace(/^[.]/,"0.").replace(".",",");
  const typeText=value=>({"ROLL_CAGE":"Ролл-кейдж","PALLET":"Паллета","BOX":"Коробка","BAG":"Мешок","STOCK":"Товарная партия","CASE":"CASE","CONTAINER":"Контейнер"}[value]||value);
  function render(data){
    window.wmsHuTree?.render(data);
    el("huRows").replaceChildren(...data.nodes.map(node=>{
      const tr=document.createElement("tr");
      [node.depth,node.uid,typeText(node.type||node.kind),node.article||"",node.quantity??"",node.hard_quantity??"",node.base_uom||"",node.cell].forEach((value,index)=>{
        const td=document.createElement("td");td.textContent=String(value);
        if(index===1&&node.kind==="CASE"&&node.uid!==data.root&&node.sscc){
          const link=document.createElement("a");link.textContent=String(value);link.href="warehouse-hus.html?identifier="+encodeURIComponent(node.sscc)+"#huComposition";td.replaceChildren(link);
        }
        tr.append(td);
      });return tr;
    }));
    el("huSummary").textContent=(data.historical_composition?"Отгружено; состав на момент отгрузки. ":"")+"Верхних мест: "+data.top_place_count+"; товарных листьев: "+data.leaf_count+
      (data.gross_weight_kg==null?"; расчётная масса состава отсутствует":"; расчётная масса состава: "+data.gross_weight_kg+" кг");
    const placement=el("huPlacement");placement.replaceChildren();placement.hidden=!data.placement;
    if(data.placement){
      const p=data.placement,label=document.createElement("strong"),note=document.createElement("span"),link=document.createElement("a");
      label.textContent="Физический слот: "+p.slot_code;
      note.textContent="Замер при размещении: "+measureText(p.gross_weight_kg)+" кг, "+measureText(p.bounding_volume_m3)+" м³; версия "+(p.content_version??"—")+
        (p.version_matches?"":" · версия места изменилась")+(p.slot_active?"":" · слот отключён")+". Новая операция повторно проверит состав и вместимость.";
      link.textContent="Задание размещения #"+p.task_id+" →";link.href="warehouse-tasks.html?task_id="+encodeURIComponent(p.task_id)+"#warehouseTaskDetail";
      placement.append(label,note,link);
    }
  }
  async function load(){
    if(busy)return;
    const input=el("huIdentifier").value,id=++generation,scope=key();
    try{
      const data=await get(input);
      if(id!==generation||key()!==scope||input!==el("huIdentifier").value)return;
      view=data;view.scannedIdentifier=input;render(data);controls();status("Состав получен. Версия "+data.nodes[0].version+".");
    }catch(e){if(id===generation&&key()===scope)status(e.message);}
  }
  function reviewed(){
    const scanned=el("huIdentifier").value;
    if(!view||(view.scannedIdentifier!==scanned&&![view.root,view.nodes[0].sscc].includes(scanned)))throw new Error("Сначала покажите состав выбранного места.");
    if(view.historical_composition)throw new Error("Место уже отгружено. Показан состав на момент отгрузки.");
    return view;
  }
  async function submit(action){
    if(busy)return;
    if(pending||damaged){status("Сначала восстановите сохранённую операцию.");return;}
    busy=true;controls();const scope=key();
    try{
      if(!el("huContainerScan").value.trim())throw new Error("Отсканируйте внешнее грузовое место перед операцией.");
      let body={operation_id:"HU:"+crypto.randomUUID()},current=null;
      if(action==="create"){
        body={...body,identifier:el("huIdentifier").value,warehouse:Number(el("huWarehouse").value),
          cell:el("huCell").value,container_type:el("huType").value,tare_weight_kg:el("huTare").value,
          sscc:el("huSscc").value||null,scan_container:el("huContainerScan").value,scan_cell:el("huCell").value};
      }else{
        current=reviewed();if(current.nodes[0].kind!=="CONTAINER"&&!(action==="relocate-slot"&&["STOCK","CASE"].includes(current.nodes[0].kind)))throw new Error("Выберите внешний контейнер для упаковки или движения.");body={...body,identifier:current.root,expected_version:current.nodes[0].version,scan_container:el("huContainerScan").value};
        if(action==="relocate-slot"){
          if(current.nodes[0].kind==="CASE")body.case_task_id=current.nodes[0].case_task_id;
          if(!el("huTargetSlot").value||!el("huReason").value)throw new Error("Выберите свободный слот этой ячейки и укажите причину.");
          body={...body,target_slot_id:Number(el("huTargetSlot").value),reason:el("huReason").value,
            scan_cell:el("huFrom").value,scan_from_slot:el("huParentSlotScan").value,scan_to_slot:el("huChildSlotScan").value,
            measurements:{origin:"MANUAL_CONFIRMED",content_version:current.nodes[0].version,gross_weight_kg:el("huGross").value,width_m:el("huWidth").value,depth_m:el("huDepth").value,height_m:el("huHeight").value}};
        }else if(action==="ship"){
          body.scan_cell=el("huShipCell").value;
        }else if(action==="move"||action==="plan-move"){
          body={...body,target_cell:el("huTo").value,scanned_from_cell:el("huFrom").value,scanned_to_cell:el("huTo").value};
          if(el("huTargetSlot").value){
            if(action!=="plan-move")throw new Error("Размещение в слот выполняется через складское задание.");
            body.target_slot_id=Number(el("huTargetSlot").value);
          }
          if(el("huGross").value)body.measurements={origin:"MANUAL_CONFIRMED",content_version:current.nodes[0].version,
            gross_weight_kg:el("huGross").value,width_m:el("huWidth").value,depth_m:el("huDepth").value,height_m:el("huHeight").value};
        }else{
          const childScan=el("huChild").value,child=await get(childScan);
          if(key()!==scope)throw new Error("Пользователь изменился; заново покажите состав.");
          body={...body,expected_child_version:child.nodes[0].version,scan_child:childScan,reason:el("huReason").value||null};
          if(action==="repack-slot"){({body,action}=slottedRepack(body,current,child));
          }else if(action==="unpack"){
            if(!["CONTAINER","STOCK","CASE"].includes(child.nodes[0].kind)||!el("huTargetSlot").value||!body.reason)throw new Error("Для вскрытия укажите вложенный контейнер или товарную паллету, свободный слот и причину.");
            if(child.case_task_id){body.child_case_task_id=child.case_task_id;action="unpack-case";}else body.child_uid=child.root;body.child_slot_id=Number(el("huTargetSlot").value);
            body.scan_cell=el("huFrom").value;body.scan_parent_slot=el("huParentSlotScan").value;body.scan_child_slot=el("huChildSlotScan").value;
            body.parent_measurements={origin:"MANUAL_CONFIRMED",content_version:current.nodes[0].version,
              gross_weight_kg:el("huGross").value,width_m:el("huWidth").value,depth_m:el("huDepth").value,height_m:el("huHeight").value};
            body.child_measurements={origin:"MANUAL_CONFIRMED",content_version:child.nodes[0].version,
              gross_weight_kg:el("huChildGross").value,width_m:el("huChildWidth").value,depth_m:el("huChildDepth").value,height_m:el("huChildHeight").value};
          }else if(child.case_task_id){body.child_case_task_id=child.case_task_id;
            if(action==="attach"&&child.tare_booking)body.retained_tare_booking_operation_id=child.tare_booking.operation_id;
            action+="-case";}
          else body.child_uid=child.root;
        }
      }
      try{intent.save({action,body});pending={action,body};}
      catch(e){pending=null;throw new Error("Операция не отправлена: "+e.message);}
      await send(scope,true);
    }catch(e){status(e.message+(pending?" Повторите сохранённую операцию.":""));}
    finally{busy=false;controls();}
  }
  function slottedRepack(body,current,child){
    if(!["CONTAINER","STOCK","CASE"].includes(child.nodes[0].kind)||!body.reason)throw new Error("Покажите вложение и укажите причину упаковки.");
    body={...body,scan_cell:el("huFrom").value,scan_parent_slot:el("huParentSlotScan").value,scan_child_slot:el("huChildSlotScan").value,
      measurements:{origin:"MANUAL_CONFIRMED",content_version:current.nodes[0].version,gross_weight_kg:el("huGross").value,
        width_m:el("huWidth").value,depth_m:el("huDepth").value,height_m:el("huHeight").value}};
    if(child.case_task_id){body.child_case_task_id=child.case_task_id;
      if(child.tare_booking)body.retained_tare_booking_operation_id=child.tare_booking.operation_id;
      return {body,action:"repack-case-slot"};}
    body.child_uid=child.root;return {body,action:"repack-slot"};
  }
  async function send(scope,firstAttempt=false){
    const record=intent.read(),saved=record.value;
    if(record.damaged||!saved||key()!==scope||JSON.stringify(saved)!==JSON.stringify(pending))
      throw new Error("Сохранённый запрос изменился. Перечитайте состояние.");

    const r=await fetch(base()+"/api/warehouse-hus/"+saved.action,{method:"POST",
      headers:{...window.wmsAdminAuth.headers(),"Content-Type":"application/json"},body:JSON.stringify(saved.body)});
    const data=await r.json();
    if(!r.ok){
      if(firstAttempt&&![401,403].includes(r.status)&&data.detail?.operation_id===saved.body.operation_id
        &&data.detail?.outcome_confirmed===true&&!data.detail?.retry_same_operation_id
        &&!["OPERATION_CONFLICT","OPERATION_PAYLOAD_CONFLICT"].includes(data.detail?.code)){
        intent.settle(record);if(key()===scope)pending=null;
      }
      throw new Error(JSON.stringify(data.detail||data));
    }
    if(!intent.confirms(saved,data))throw new Error("Ответ не соответствует сохранённой операции. Повторите исходный запрос.");
    if(key()!==scope)return;
    intent.settle(record);
    pending=null;view=null;el("huContainerScan").value="";
    if(saved.action==="plan-move"){
      status("Создано задание размещения #"+data.task_id+". Назначьте исполнителя в складских заданиях.");
      const link=document.createElement("a");link.href="warehouse-tasks.html?task_id="+encodeURIComponent(data.task_id)+"#warehouseTaskDetail";link.textContent="Открыть складские задания";el("huSummary").replaceChildren(link);return;
    }
    if(["unpack","unpack-case"].includes(saved.action)){
      const current=await get(saved.body.identifier);
      if(key()===scope){view=current;view.scannedIdentifier=el("huIdentifier").value;render(current);status("Вскрытие подтверждено. Количество сохранено; вложение размещено отдельно. Операция "+data.operation_id);}
      return;
    }
    if(saved.action==="ship"){
      const current=await get(saved.body.identifier);
      if(key()===scope){view=current;view.scannedIdentifier=el("huIdentifier").value;render(current);status("Место отгружено целиком. Операция "+data.operation_id+". Показан исторический состав.");}
      return;
    }
    status("Подтверждено: "+data.command+". Операция "+data.operation_id);render(data);
    try{const current=await get(data.root);if(key()===scope){view=current;view.scannedIdentifier=el("huIdentifier").value;render(current);}}
    catch(e){if(key()===scope)status("Операция подтверждена. Не удалось обновить состав: "+e.message);}
  }
  el("huLoadSlots").addEventListener("click",async()=>{
    if(busy)return;
    try{
      const current=reviewed(),cell=el("huTo").value,scope=key();
      const r=await fetch(base()+"/api/warehouse-hus/target-slots?cell="+encodeURIComponent(cell)+"&warehouse="+current.warehouse,{headers:window.wmsAdminAuth.headers()});
      const data=await r.json();if(!r.ok)throw new Error(JSON.stringify(data.detail||data));
      if(key()!==scope||el("huTo").value!==cell)return;
      const options=data.map(slot=>{
        const option=document.createElement("option");option.value=slot.cell_slot_id;
        option.textContent=slot.slot_code+(slot.unavailable_reason?" / "+slot.unavailable_reason:"");
        option.disabled=!!slot.unavailable_reason;return option;
      });
      const empty=document.createElement("option");empty.value="";empty.textContent="Без физического слота";
      el("huTargetSlot").replaceChildren(empty,...options);
      status("Слотов: "+data.length+". Выберите адрес и подтвердите измерения всего места.");
    }catch(e){status(e.message);}
  });
  el("huTo").addEventListener("input",()=>{el("huTargetSlot").replaceChildren(new Option("Сначала покажите слоты",""));});
  el("huLoad").addEventListener("click",load);
  ["Create","Attach","Detach","Move","Ship","Unpack"].forEach(name=>el("hu"+name).addEventListener("click",()=>submit(name.toLowerCase())));
  el("huPlanMove").addEventListener("click",()=>submit("plan-move"));
  el("huRepackSlot").addEventListener("click",()=>submit("repack-slot"));
  el("huRelocateSlot").addEventListener("click",()=>submit("relocate-slot"));
  el("huIdentifier").addEventListener("input",()=>{generation++;view=null;el("huContainerScan").value="";window.wmsHuTree?.clear();el("huRows").replaceChildren();el("huSummary").replaceChildren();el("huPlacement").replaceChildren();controls();});
  el("huRetry").addEventListener("click",async()=>{
    if(busy||!pending)return;
    busy=true;controls();const scope=key();
    try{await send(scope);}catch(e){status(e.message+" Повторите тот же сохранённый запрос.");}
    finally{busy=false;controls();}
  });
  function auth(){
    if(!window.wmsAdminAuth?.state?.user)return;
    const next=key();if(next===identity)return;
    identity=next;view=null;generation++;pending=null;damaged=null;el("huContainerScan").value="";window.wmsHuTree?.clear();el("huRows").replaceChildren();el("huSummary").replaceChildren();el("huPlacement").replaceChildren();
    try{const record=intent.read();pending=record.value;damaged=record.damaged?record:null;if(pending)el("huIdentifier").value=pending.body.identifier;}
    catch(e){status("Не удалось прочитать сохранённую операцию: "+e.message);}
    if(!pending&&requestedIdentifier)el("huIdentifier").value=requestedIdentifier;
    controls();
    if(!pending&&requestedIdentifier)load();
  }
  el("huRecoverDamaged").addEventListener("click",async()=>{
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
  window.addEventListener("wms-admin-auth-ready",auth);auth();
})();
