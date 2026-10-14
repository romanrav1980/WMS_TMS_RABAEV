(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let dossier=null,pending=null,busy=false,identity="",serial=0;
 const base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"wms-store-return:"+base()+":"+auth().state.user?.username;
 const unitPanel=document.createElement("section");unitPanel.id="returnUnitList";el("returnLines").after(unitPanel);
 const say=text=>{el("returnMessage").textContent=text;};
 const reusePanel=document.createElement("section"),reuseButton=document.createElement("button"),reuseMessage=document.createElement("p");
 reuseButton.type="button";reuseButton.textContent="Проверить исходную партию и полные коробки";
 reusePanel.append(reuseButton,reuseMessage);unitPanel.after(reusePanel);
 const reuseReasons={RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED:"Исходная партия не подтверждена приёмкой SAP",
 RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT:"Количество не соответствует полным коробкам текущей упаковки",
 RETURN_REUSE_SOURCE_EXPIRY_ARTICLE_REQUIRED:"Исходный срок годности истёк или данные партии неполны",
 RETURN_REUSE_CURRENT_SOURCE_BOX_UOM_REQUIRED:"Нет согласованной упаковки коробки"};
 async function previewReuse(){
  if(!dossier||busy||pending)return;
  if(el('returnBasis').value!=='ACCEPTED'){reuseMessage.textContent='Для отказа или повреждения нужна отдельная проверка качества; повторное использование здесь не разрешается.';return;}
  const token=serial,scope=key(),receipt=dossier.source.operation_id;
  const line=Number(el("returnLine").value),quantity=el("returnQuantity").value.trim();
  if(!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(quantity)){reuseMessage.textContent="Укажите точное количество.";return;}
  busy=true;controls();reuseMessage.textContent="";
  try{
   const q=new URLSearchParams({line_no:String(line),quantity});
   const v=await request("/api/delivery/store-returns/"+encodeURIComponent(receipt)+"/reuse-preview?"+q);
   if(token!==serial||scope!==key())return;
   reuseMessage.textContent=v.source_eligible
    ? "Исходная партия и упаковка подходят. "+(v.currently_approvable?"Количество доступно для согласования.":"Этого количества уже нет в доступном остатке согласования.")
      +" Комплектность и коды единиц проверяются отдельно при передаче и приёмке."
    : (reuseReasons[v.source_reason]||"Исходные данные не допускают повторное использование.");
  }catch(e){if(token===serial&&scope===key())reuseMessage.textContent=e.message;}
  finally{if(token===serial&&scope===key()){busy=false;controls();}}
 }
 reuseButton.addEventListener("click",previewReuse);
 for(const id of ["returnLine","returnQuantity","returnDisposition","returnBasis"])el(id)?.addEventListener("change",()=>{reuseMessage.textContent="";});

 function controls(){
  document.querySelectorAll("main input,main textarea,main select,main button").forEach(node=>{node.disabled=busy||!!pending;});
  el("returnDisposition").querySelector('option[value="REUSE"]').disabled=el("returnBasis").value!=="ACCEPTED";
  el("returnGoodBox").disabled=busy||!!pending||el("returnBasis").value!=="ACCEPTED";
  el("returnRetry").hidden=!pending;el("returnRetry").disabled=busy;
  el("returnRestart").hidden=!pending?.confirmed;el("returnRestart").disabled=busy;
 }
 async function request(path,body){
  const response=await fetch(base()+path,{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();
  if(!response.ok){
   const error=Error(typeof data.detail==="string"?data.detail:data.detail?.message||JSON.stringify(data.detail));
   error.confirmed=response.status<500&&data.detail?.outcome_confirmed===true&&!!body&&data.detail?.operation_id===body.operation_id;throw error;
  }
  return data;
 }
 function lines(target,rows,format){target.replaceChildren(...rows.map(row=>{const p=document.createElement("p");p.textContent=format(row);return p;}));}
 function render(data){
  dossier=data;el("returnSummary").textContent=data.source.operation_id+" · "+data.source.store_addr+" · "+data.source.receipt_state;
  lines(el("returnLines"),data.lines,row=>"Строка "+row.line_no+" · "+row.article+" · принято "+row.accepted_quantity+" "+row.base_uom+" · уже разрешено "+row.approved_quantity+" · возврат принятого доступен "+row.available_for_approval+" · отказ доступен "+row.refused_available+" · повреждение доступно "+row.damaged_available);
  lines(el("returnHistory"),data.approvals,row=>row.operation_id+" · "+row.quantity+" "+row.base_uom+" · "+(row.return_basis||"ACCEPTED")+" · "+row.disposition+" · "+row.approved_by+" · "+row.decision_reference+" · "+(row.return_document?"SAP: "+row.return_document+" · склад "+row.ware_id:"ожидает SAP-документ"));
  window.wmsReturnProgress?.render(data);
  el("returnLine").replaceChildren(...data.lines.map(row=>{const option=document.createElement("option");option.value=String(row.line_no);option.textContent="Строка "+row.line_no+" · "+row.article+" · "+row.available_for_approval+" "+row.base_uom;return option;}));
 }
 function renderUnits(){
  const line=Number(el("returnLine").value),basis=el("returnBasis").value;unitPanel.replaceChildren();
  for(const option of el("returnLine").options){
   const item=dossier?.lines.find(r=>r.line_no===Number(option.value));
   if(item)option.textContent="Строка "+item.line_no+" · "+item.article+" · доступно "+(basis==="ACCEPTED"?item.available_for_approval:basis==="REFUSED"?item.refused_available:item.damaged_available)+" "+item.base_uom;
  }
  for(const unit of (dossier?.units||[]).filter(u=>u.line_no===line&&(u.return_basis||"ACCEPTED")===basis)){
   const label=document.createElement("label"),box=document.createElement("input");box.type="checkbox";box.value=unit.key;box.dataset.unitKey="1";
   label.title=unit.key;label.append(box,document.createTextNode("Единица "+(unit.unit_id||unit.key.slice(-12))+" · "+unit.quantity+" "+unit.base_uom));unitPanel.append(label,document.createElement("br"));
  }
  if((dossier?.units||[]).length){const p=document.createElement("p");p.textContent="Выберите конкретные исходные единицы с выбранным результатом приёмки. Количество в решении должно совпадать с их количеством в базовых единицах.";unitPanel.prepend(p);}
 }
 async function load(){
  if(busy||pending)return;const source=el("returnSource").value,scope=key(),version=++serial;busy=true;controls();
  try{const data=await request("/api/delivery/store-returns/"+encodeURIComponent(source));if(scope===key()&&version===serial&&source===el("returnSource").value){render(data);renderUnits();say("");}}
  catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function send(scope){
  if(busy||!pending)return;const intent=pending;busy=true;controls();
  try{
   const result=await request(intent.path,intent.body);localStorage.removeItem(scope);
   if(scope===key()){pending=null;dossier=null;unitPanel.replaceChildren();window.wmsReturnProgress?.clear();say("Возврат согласован: "+result.quantity+" "+result.base_uom+". Ожидает SAP и логистику. Обновите поставку.");}
  }catch(error){if(scope===key()){pending={...intent,confirmed:error.confirmed};try{localStorage.setItem(scope,JSON.stringify(pending));}catch(storageError){say("Исходное согласование сохранено в памяти. Не закрывайте страницу.");}
   say(error.message+(error.confirmed?" Отказ подтверждён.":" Повторите исходное согласование."));}}
  finally{busy=false;controls();}
 }
 async function approve(){
  if(busy||pending||!dossier||dossier.source.operation_id!==el("returnSource").value){say("Покажите актуальную исходную приёмку.");return;}
  const line=Number(el("returnLine").value);if(!Number.isSafeInteger(line)||line<1){say("Выберите строку исходной поставки.");return;}
  const body={operation_id:"STORE.RETURN:"+crypto.randomUUID(),line_no:line,quantity:el("returnQuantity").value,
   disposition:el("returnDisposition").value,reason:el("returnReason").value,decision_reference:el("returnReference").value,complete_good_box:el("returnGoodBox").checked};
  const selected=[...unitPanel.querySelectorAll("input:checked")].map(n=>n.value);if(selected.length)body.unit_keys=selected;
  if(el("returnBasis").value!=="ACCEPTED")body.return_basis=el("returnBasis").value;
  if(!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(body.quantity)||!body.reason.trim()||!body.decision_reference.trim()){say("Укажите точное количество, причину и ссылку на решение.");return;}
  pending={path:"/api/delivery/store-returns/"+encodeURIComponent(dossier.source.operation_id)+"/approve",body};
  const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}catch(error){pending=null;controls();say("Согласование не направлено: не удалось сохранить исходную операцию.");return;}await send(scope);
 }
 function changedAuth(){
  const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(fingerprint===identity)return;identity=fingerprint;++serial;busy=false;dossier=null;pending=null;unitPanel.replaceChildren();reuseMessage.textContent="";
  for(const id of ["returnSummary","returnMessage"])el(id).textContent="";
  for(const id of ["returnLines","returnHistory","returnLine"])el(id).replaceChildren();
  for(const id of ["returnSource","returnQuantity","returnReason","returnReference"])el(id).value="";el("returnGoodBox").checked=false;
  try{pending=JSON.parse(localStorage.getItem(scope)||"null");}catch(error){say("Не удалось прочитать сохранённую операцию.");}controls();
 }
 el("returnBasis").addEventListener("change",()=>{
  if(el("returnBasis").value!=="ACCEPTED"){
   el("returnDisposition").value=el("returnBasis").value==="DAMAGED"?"DISPOSAL":"SUPPLIER";
   el("returnGoodBox").checked=false;
  }
  renderUnits();controls();
 });
 el("returnLine").addEventListener("change",renderUnits);
 el("returnSource").addEventListener("input",()=>{serial++;dossier=null;window.wmsReturnProgress?.clear();el("returnLines").replaceChildren();unitPanel.replaceChildren();});
 el("returnLoad").addEventListener("click",load);el("returnApprove").addEventListener("click",approve);
 el("returnRetry").addEventListener("click",()=>send(key()));
 el("returnRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed){localStorage.removeItem(key());pending=null;dossier=null;controls();say("Обновите поставку и исправьте данные.");}});
 window.addEventListener("wms-admin-auth-ready",changedAuth);changedAuth();
})();
