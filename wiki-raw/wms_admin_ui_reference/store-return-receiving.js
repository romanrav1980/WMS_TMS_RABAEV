(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const markDraft=window.wmsReturnMarkDraft(document.getElementById('receiveUnitScans'));
 let rows=[],policy=null,pending=null,busy=false,identity="",serial=0,selectedSource=null,next=null;
 const base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"wms-return-receive:"+base()+":"+auth().state.user?.username;
 const say=text=>{el("receiveMessage").textContent=text;};
 const resultView=el("receiveResult"),receiptResult=window.wmsReturnReceiptResult,journal=window.wmsReturnCommandIntent;
 const reasons={
  STORE_RETURN_SEGREGATED_RECEIVING_CELL_REQUIRED:"Зона возврата должна блокировать отбор и пополнение.",
  STORE_RETURN_ORIGINAL_EXPIRY_CONFLICT:"Срок годности не соответствует исходной поставке.",
  STORE_RETURN_ORIGINAL_BATCH_CONFLICT:"Партия не соответствует исходной поставке.",
  STORE_RETURN_WAREHOUSE_FULL_ORIGINAL_QUANTITY_REQUIRED:"Количество, артикул или основная единица отличаются от согласованного возврата.",
  STORE_RETURN_WAREHOUSE_PALLET_VEHICLE_CELL_SCAN_REQUIRED:"Сканы машины, паллеты и ячейки должны соответствовать этому возврату.",
  STORE_RETURN_WAREHOUSE_WEIGHT_CONFLICT:"Масса отличается от подписанной передачи или нетто превышает брутто.",
  STORE_RETURN_REUSE_COMPLETE_BOX_PLACEMENT_FLOW_REQUIRED:"Этот возврат требует проверки полной исправной коробки и размещения в отбор.",
  STORE_RETURN_MARKED_UNIT_REGULATORY_FLOW_REQUIRED:"Требуется сверка уникальных маркированных единиц и их статусов.",
  QUALITY_FOREIGN_ITEM_BARCODE:"Штрихкод товара не найден.",
  QUALITY_ITEM_BARCODE_AMBIGUOUS:"Штрихкод сопоставлен нескольким упаковкам или товарам. Исправьте справочник.",
  STORE_RETURN_FOREIGN_ARTICLE_BARCODE:"Отсканирован товар другой позиции.",
  STORE_RETURN_FRESH_PALLET_REQUIRED:"Идентификатор паллеты уже используется. Проверьте исходную приёмку."
 };
 function controls(){
  document.querySelectorAll("main input,main select,main button").forEach(node=>{node.disabled=busy||!!pending;});
  el("receiveConfirm").disabled=busy||!!pending||!selectedSource;el("receiveNext").disabled=busy||!!pending||!next;
  el("receiveRecover").hidden=!pending?.damaged;el("receiveRecover").disabled=busy;if(pending?.damaged)el("receiveWare").disabled=busy;el("receiveRetry").hidden=!pending||!!pending.damaged;el("receiveRetry").disabled=busy;el("receiveRestart").hidden=!pending?.confirmed;el("receiveRestart").disabled=busy;
 }
 async function request(path,body,method){
  const response=await fetch(base()+"/api/inventory/store-returns"+path,{method:method||(body?"POST":"GET"),headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();
  if(!response.ok){const raw=typeof data.detail==="string"?data.detail:data.detail?.message||"Действие не подтверждено.";const error=Error(Object.entries(reasons).find(([code])=>raw.includes(code))?.[1]||raw);error.confirmed=response.status<500&&data.detail?.outcome_confirmed===true&&!!body&&data.detail?.operation_id===body.operation_id;throw error;}return data;
 }
 function warehouse(){const id=Number(el("receiveWare").value);if(!Number.isSafeInteger(id)||id<1)throw Error("Укажите принимающий склад.");return id;}
 function selected(){return selectedSource;}
 async function summary(){
  const row=rows.find(value=>value.pickup_operation_id===el("receivePickup").value),scope=key(),version=++serial;
  selectedSource=null;markDraft.setContext(null,scope+':source-pending');
  el("receiveBoxes").value="";el("receiveGoodBoxes").checked=false;
  for(const id of ["receiveVehicle","receivePallet","receiveCell","receiveBarcode","receiveQuantity","receiveBatch","receiveExpiry","receiveGross","receiveNet"])el(id).value="";
  el("receiveSource").textContent=row?"Читается исходный возврат…":"";controls();if(!row)return;
  try{
   const ware=warehouse(),source=await request("/warehouses/"+ware+"/pickups/"+encodeURIComponent(row.pickup_operation_id)+"/source");
   if(scope!==key()||version!==serial||ware!==Number(el("receiveWare").value)||source.pickup_operation_id!==el("receivePickup").value)return;
   selectedSource=source;markDraft.setContext(source.marked_unit_control||null,scope+':'+source.pickup_operation_id);
   el("receiveSource").textContent=source.store_addr+" · "+source.return_document+" · "+source.article+" · "+source.quantity+" "+source.base_uom+" · "+source.expiry_date+" · зона "+(source.receive_cell||"не настроена")+" · "+source.disposition;
  }catch(error){if(scope===key()&&version===serial)say(error.message);}
  finally{if(scope===key()&&version===serial)controls();}
 }
 async function load(nextPage=false){
  if(busy||pending)return;const scope=key(),version=++serial;busy=true;controls();
  try{const ware=warehouse(),data=await request("/warehouses/"+ware+"/pending-page?"+new URLSearchParams({limit:"20",after:nextPage===true&&next?next:""}));if(scope!==key()||version!==serial||ware!==Number(el("receiveWare").value))return;
   rows=data.items;next=data.next_after;el("receivePickup").replaceChildren(...rows.map(row=>{const option=document.createElement("option");option.value=row.pickup_operation_id;option.textContent=row.pallet_identifier+" · "+row.store_addr+" · "+row.quantity+" "+row.base_uom;return option;}));summary();say(rows.length?(data.has_more?"Показана страница очереди. Остальные возвраты доступны по кнопке продолжения.":""):"Нет возвратов, ожидающих приёмки.");
  }catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function loadPolicy(){
  if(busy||pending)return;const scope=key(),version=++serial;busy=true;controls();policy=null;
  try{const ware=warehouse(),data=await request("/warehouses/"+ware+"/policy");if(scope!==key()||version!==serial||ware!==Number(el("receiveWare").value))return;
   policy=data;el("receivePolicyVersion").textContent="Версия "+data.policy_version;el("receiveSupplierCell").value=data.supplier_receive_cell||"";el("receiveReuseCell").value=data.reuse_receive_cell||"";el("receiveDisposalCell").value=data.disposal_receive_cell||"";say("");
  }catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function saveReuse(){if(busy||pending)return;if(!policy)return say("Покажите текущие настройки.");const scope=key(),seq=++serial;busy=true;controls();try{const data=await request("/warehouses/"+warehouse()+"/reuse-receiving",{receive_cell:el("receiveReuseCell").value,expected_version:policy.policy_version},"PUT");if(scope===key()&&seq===serial){policy=data;el("receivePolicyVersion").textContent="Версия "+data.policy_version;rows=[];el("receivePickup").replaceChildren();summary();say("Зона исправного возврата сохранена.");}}catch(e){if(scope===key()){policy=null;say(e.message);}}finally{busy=false;controls();}}
 async function savePolicy(){
  if(busy||pending||!policy||policy.ware_id!==Number(el("receiveWare").value)){say("Покажите текущие настройки склада.");return;}
  const scope=key(),version=++serial,ware=policy.ware_id,body={supplier_receive_cell:el("receiveSupplierCell").value,disposal_receive_cell:el("receiveDisposalCell").value,expected_version:policy.policy_version};busy=true;controls();
  try{const data=await request("/warehouses/"+ware+"/policy",body,"PUT");if(scope===key()&&version===serial){policy=data;el("receivePolicyVersion").textContent="Версия "+data.policy_version;rows=[];el("receivePickup").replaceChildren();summary();say("Зоны сохранены. Обновите возвраты.");}}
  catch(error){if(scope===key()&&version===serial){policy=null;say(error.message+". Покажите текущие настройки перед повтором.");}}
  finally{busy=false;controls();}
 }
 async function send(scope){
  if(busy||!pending||pending.damaged)return;const intent=pending;busy=true;controls();
  try{
   journal.check(scope,intent);
   const result=receiptResult.validate(await request("/receive",intent.body),intent.body);journal.complete(scope,intent);
   if(scope===key()&&pending===intent){pending=null;rows=[];el("receivePickup").replaceChildren();summary();receiptResult.show(resultView,result);say("Приёмка подтверждена. Перейдите к размещению принятого возврата.");}
  }
  catch(error){if(scope===key()&&pending===intent){try{pending=journal.confirmed(scope,"receive",intent,error.confirmed);}catch(storageError){try{pending=journal.load(scope,"receive")||intent;}catch{pending={damaged:true};}say(storageError.message);}say(error.message);}}

  finally{busy=false;controls();}
 }
 async function confirm(){
  if(busy||pending)return;const row=selected();if(!row){say("Покажите и выберите исходный возврат.");return;}
  const body={operation_id:"RETURN.RECEIVE:"+crypto.randomUUID(),pickup_operation_id:row.pickup_operation_id,
   scan_pallet:el("receivePallet").value,scan_vehicle:el("receiveVehicle").value,scan_cell:el("receiveCell").value,scan_article:el("receiveBarcode").value,
   article:row.article,quantity:el("receiveQuantity").value,base_uom:row.base_uom,expiry_date:el("receiveExpiry").value,supplier_batch:el("receiveBatch").value,gross_weight_kg:el("receiveGross").value,net_weight_kg:el("receiveNet").value};
  if(![body.quantity,body.gross_weight_kg,body.net_weight_kg].every(value=>/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(value))||!body.scan_pallet||body.scan_pallet.length>50||!body.scan_vehicle||body.scan_vehicle.length>50||!body.scan_cell||body.scan_cell.length>60||!body.scan_article||body.scan_article.length>128||!body.supplier_batch||body.supplier_batch.length>100||!/^\d{4}-\d{2}-\d{2}$/.test(body.expiry_date)){say("Заполните сканы, партию, срок и точные десятичные количества и массы.");return;}
  if(row.disposition==="REUSE"){if(!/^[1-9][0-9]{0,17}$/.test(el("receiveBoxes").value)||!el("receiveGoodBoxes").checked){say("Для исправного возврата подтвердите комплектацию и количество полных коробок, отсканируйте ШК коробки.");return;}body.full_box_count=el("receiveBoxes").value;body.complete_good_boxes=true;}
  try{Object.assign(body,markDraft.getEvidence());}catch(error){say(error.message);return;}
  const scope=key();try{pending=journal.prepare(scope,"receive",{body});}catch(error){try{pending=journal.load(scope,"receive");}catch{pending={damaged:true};}controls();say(error.message);return;}await send(scope);
 }
 function changed(){
  const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(fingerprint===identity)return;identity=fingerprint;resultView.replaceChildren();resultView.hidden=true;++serial;rows=[];policy=null;pending=null;selectedSource=null;next=null;
  el("receivePickup").replaceChildren();el("receivePolicyVersion").textContent="";for(const id of ["receiveWare","receiveReuseCell","receiveSupplierCell","receiveDisposalCell","receiveVehicle","receivePallet","receiveCell","receiveBarcode","receiveQuantity","receiveBatch","receiveExpiry","receiveGross","receiveNet"])el(id).value="";summary();say("");
  try{pending=journal.load(scope,"receive");}catch(error){pending={damaged:true};say("Не удалось прочитать сохранённую приёмку.");}controls();
 }
 el("receiveWare").addEventListener("input",()=>{if(!busy&&!pending){++serial;rows=[];policy=null;selectedSource=null;next=null;el("receivePickup").replaceChildren();el("receivePolicyVersion").textContent="";summary();}});
 el("receiveLoad").addEventListener("click",()=>load());el("receiveNext").addEventListener("click",()=>load(true));el("receivePickup").addEventListener("change",summary);el("receivePolicyLoad").addEventListener("click",loadPolicy);el("receivePolicySave").addEventListener("click",savePolicy);el("receiveConfirm").addEventListener("click",confirm);
 el("receiveRetry").addEventListener("click",()=>send(key()));el("receiveRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed){try{journal.complete(key(),pending);}catch(error){say(error.message);return;}pending=null;rows=[];el("receivePickup").replaceChildren();controls();summary();say("Обновите исходный возврат и исправьте данные.");}});
 el("receiveReuseSave").addEventListener("click",saveReuse);
  el("receiveRecover").addEventListener("click",async()=>{
  if(busy||!pending?.damaged)return;const scope=key(),stamp=++serial;busy=true;controls();
  try{const ware=warehouse();await journal.archive(scope,()=>request("/warehouses/"+ware+"/pending-page?limit=20"),()=>scope===key()&&stamp===serial);pending=null;rows=[];selectedSource=null;el("receivePickup").replaceChildren();summary();say("Исходник сохранён в архив, склад перечитан. Покажите текущую очередь. Архив не подтверждает и не отменяет прежнюю приёмку.");}catch(error){if(scope===key())say(error.message);}finally{busy=false;controls();}
 });
 window.addEventListener("wms-admin-auth-ready",changed);changed();
})();
