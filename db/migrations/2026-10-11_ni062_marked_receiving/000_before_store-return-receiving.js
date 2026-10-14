(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let rows=[],policy=null,pending=null,busy=false,identity="",serial=0;
 const base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"wms-return-receive:"+base()+":"+auth().state.user?.username;
 const say=text=>{el("receiveMessage").textContent=text;};
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
  el("receiveRetry").hidden=!pending;el("receiveRetry").disabled=busy;el("receiveRestart").hidden=!pending?.confirmed;el("receiveRestart").disabled=busy;
 }
 async function request(path,body,method){
  const response=await fetch(base()+"/api/inventory/store-returns"+path,{method:method||(body?"POST":"GET"),headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();
  if(!response.ok){const raw=typeof data.detail==="string"?data.detail:data.detail?.message||"Действие не подтверждено.";const error=Error(Object.entries(reasons).find(([code])=>raw.includes(code))?.[1]||raw);error.confirmed=response.status<500&&data.detail?.outcome_confirmed===true&&!!body&&data.detail?.operation_id===body.operation_id;throw error;}return data;
 }
 function warehouse(){const id=Number(el("receiveWare").value);if(!Number.isSafeInteger(id)||id<1)throw Error("Укажите принимающий склад.");return id;}
 function selected(){return rows.find(row=>row.pickup_operation_id===el("receivePickup").value);}
 function summary(){el("receiveBoxes").value="";el("receiveGoodBoxes").checked=false;for(const id of ["receiveVehicle","receivePallet","receiveCell","receiveBarcode","receiveQuantity","receiveBatch","receiveExpiry","receiveGross","receiveNet"])el(id).value="";const row=selected();el("receiveSource").textContent=row?row.store_addr+" · "+row.return_document+" · "+row.article+" · "+row.quantity+" "+row.base_uom+" · "+row.expiry_date+" · зона "+(row.receive_cell||"не настроена")+" · "+row.disposition:"";}
 async function load(){
  if(busy||pending)return;const scope=key(),version=++serial;busy=true;controls();
  try{const ware=warehouse(),data=await request("/warehouses/"+ware+"/pending");if(scope!==key()||version!==serial||ware!==Number(el("receiveWare").value))return;
   rows=data;el("receivePickup").replaceChildren(...rows.map(row=>{const option=document.createElement("option");option.value=row.pickup_operation_id;option.textContent=row.pallet_identifier+" · "+row.store_addr+" · "+row.quantity+" "+row.base_uom;return option;}));summary();say(data.length?"":"Нет возвратов, ожидающих приёмки.");
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
  if(busy||!pending)return;const intent=pending;busy=true;controls();
  try{const result=await request("/receive",intent.body);localStorage.removeItem(scope);if(scope===key()){pending=null;rows=[];el("receivePickup").replaceChildren();summary();say("Склад принял "+result.quantity+" "+result.base_uom+" в "+result.cell+". Документ возврата "+result.receiving_document_id+". Товар ожидает размещения.");}}
  catch(error){if(scope===key()){pending={...intent,confirmed:error.confirmed};try{localStorage.setItem(scope,JSON.stringify(pending));}catch(storageError){}say(error.message+(error.confirmed?" Отказ подтверждён.":" Повторите исходную сохранённую приёмку."));}}
  finally{busy=false;controls();}
 }
 async function confirm(){
  if(busy||pending)return;const row=selected();if(!row){say("Покажите и выберите исходный возврат.");return;}
  const body={operation_id:"RETURN.RECEIVE:"+crypto.randomUUID(),pickup_operation_id:row.pickup_operation_id,
   scan_pallet:el("receivePallet").value,scan_vehicle:el("receiveVehicle").value,scan_cell:el("receiveCell").value,scan_article:el("receiveBarcode").value,
   article:row.article,quantity:el("receiveQuantity").value,base_uom:row.base_uom,expiry_date:el("receiveExpiry").value,supplier_batch:el("receiveBatch").value,gross_weight_kg:el("receiveGross").value,net_weight_kg:el("receiveNet").value};
  if(![body.quantity,body.gross_weight_kg,body.net_weight_kg].every(value=>/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(value))||!body.scan_pallet||body.scan_pallet.length>50||!body.scan_vehicle||body.scan_vehicle.length>50||!body.scan_cell||body.scan_cell.length>60||!body.scan_article||body.scan_article.length>128||!body.supplier_batch||body.supplier_batch.length>100||!/^\d{4}-\d{2}-\d{2}$/.test(body.expiry_date)){say("Заполните сканы, партию, срок и точные десятичные количества и массы.");return;}
  if(row.disposition==="REUSE"){if(!/^[1-9][0-9]{0,17}$/.test(el("receiveBoxes").value)||!el("receiveGoodBoxes").checked){say("Для исправного возврата подтвердите комплектацию и количество полных коробок, отсканируйте ШК коробки.");return;}body.full_box_count=el("receiveBoxes").value;body.complete_good_boxes=true;}
  pending={body};const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}catch(error){pending=null;controls();say("Приёмка не отправлена: не удалось сохранить исходную операцию.");return;}await send(scope);
 }
 function changed(){
  const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(fingerprint===identity)return;identity=fingerprint;++serial;rows=[];policy=null;pending=null;
  el("receivePickup").replaceChildren();el("receivePolicyVersion").textContent="";for(const id of ["receiveWare","receiveReuseCell","receiveSupplierCell","receiveDisposalCell","receiveVehicle","receivePallet","receiveCell","receiveBarcode","receiveQuantity","receiveBatch","receiveExpiry","receiveGross","receiveNet"])el(id).value="";summary();say("");
  try{pending=JSON.parse(localStorage.getItem(scope)||"null");}catch(error){say("Не удалось прочитать сохранённую приёмку.");}controls();
 }
 el("receiveWare").addEventListener("input",()=>{if(!busy&&!pending){++serial;rows=[];policy=null;el("receivePickup").replaceChildren();el("receivePolicyVersion").textContent="";summary();}});
 el("receiveLoad").addEventListener("click",load);el("receivePickup").addEventListener("change",summary);el("receivePolicyLoad").addEventListener("click",loadPolicy);el("receivePolicySave").addEventListener("click",savePolicy);el("receiveConfirm").addEventListener("click",confirm);
 el("receiveRetry").addEventListener("click",()=>send(key()));el("receiveRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed){localStorage.removeItem(key());pending=null;rows=[];el("receivePickup").replaceChildren();controls();summary();say("Обновите исходный возврат и исправьте данные.");}});
 el("receiveReuseSave").addEventListener("click",saveReuse);
 window.addEventListener("wms-admin-auth-ready",changed);changed();
})();
