window.cpScaleArchive=(()=>{
 const text=(tag,value)=>{const n=document.createElement(tag);n.textContent=value;return n;};
 function mount({panel,select,task,line,policy,isCurrent}){
  const who=cpTsdApiBase()+"|"+cpTsdUser(),taskId=task.case_pick_task_id,lineId=line.case_pick_line_id;
  const current=()=>isCurrent()&&who===cpTsdApiBase()+"|"+cpTsdUser()&&cpTsd.task?.case_pick_task_id===taskId&&cpTsdCurrentLine()?.case_pick_line_id===lineId;
  let serial=0,items=[],usage={},running=false;
  const tools=text("div","");tools.className="cp-scale-tools";
  const refresh=text("button","Обновить показания");refresh.type="button";refresh.title="Перечитать архив этой строки, сохранив введённые сканы";
  const message=text("p",""),detail=text("div","");message.setAttribute("role","status");detail.className="cp-scale-detail";
  const exact=text("details",""),summary=text("summary","Найти показание по точному ID");summary.title="Прочитать архивный пакет вне последних 50 записей";
  const label=text("label","ID архивного показания"),key=document.createElement("input");key.maxLength=64;key.autocomplete="off";key.placeholder="64 символа";key.title="Полный идентификатор сохранённого показания весового поста";key.setAttribute("aria-label","ID архивного показания");label.append(key);
  const find=text("button","Найти показание");find.type="button";find.title="Прочитать сохранённый пакет; взвешивание и отбор не создаются";exact.append(summary,label,find);
  tools.append(refresh,message,detail,exact);panel.append(tools);
  const reason=item=>{
   if(usage[item.capture_key])return "Уже использовано";
   if(item.capture_purpose&&item.capture_purpose!=="PICK")return "Иное назначение взвешивания";
   if(item.case_task_id!==taskId||item.case_line_id!==lineId)return "Другая строка сборки";
   if(item.basis!==(policy.serialized_weight_boxes?"GROSS":"NET"))return "Другая база веса";
   if(item.case_content_version!==task.content_version)return "Другая версия состава";
   return "";
  };
  function showDetail(explicit){
   detail.replaceChildren();const item=explicit?.capture_key?explicit:items.find(x=>x.capture_key===select.value);if(!item)return;
   detail.append(text("strong",item.weight_kg+" кг · "+(item.basis==="NET"?"нетто":"брутто")),text("p","Пост: "+item.post_cell+" · устройство "+item.device_id),
    text("p","Измерено: "+item.measured_at),text("p","Режим: "+(item.device_mode==="TEST"?"Тестовое устройство":"Аппаратное устройство")+" · версия состава "+item.case_content_version),
    text("p","Разрешение: "+item.resolution_kg+" кг · калибровка "+item.calibration_ref),
    text("p","Перед проведением сервер повторно проверит текущую версию, настройку весов и однократность показания."));
  }
  function render(preferred=""){
   select.replaceChildren(new Option(policy.loose_weight_kg?"Выберите обязательное нетто-показание":"Без показания весового поста",""));
   let eligible=0;
   for(const item of items){
    const why=reason(item),option=new Option(item.weight_kg+" кг "+item.basis+" · "+item.measured_at+(why?" · "+why:"")+" · "+item.device_mode,item.capture_key);
    option.disabled=!!why;select.append(option);if(!why)eligible++;
   }
   if(preferred&&items.some(i=>i.capture_key===preferred&&!reason(i)))select.value=preferred;
   select.dispatchEvent(new Event("change",{bubbles:true}));showDetail();return eligible;
  }
  async function read(exactKey){
   if(running||!current()||window.cpTsdStockBusy)return;
   if(exactKey&&!/^[0-9A-F]{64}$/.test(exactKey)){message.textContent="Укажите полный ID из 64 шестнадцатеричных символов.";return;}
   running=true;refresh.disabled=find.disabled=select.disabled=true;const token=++serial,previous=select.value;select.value="";detail.replaceChildren();
   try{
    const data=await cpTsdFetch("/api/inventory/warehouse-scales/captures"+(exactKey?"/"+exactKey:"?task="+taskId+"&line="+lineId));
    if(!current()||token!==serial)return;
    if(exactKey){
     if(!Object.prototype.hasOwnProperty.call(data,"used_operation_id"))throw Error("Сервер не сообщил использование показания. Обновите архив.");
     if(data.case_task_id!==taskId||data.case_line_id!==lineId)throw Error("Показание относится к другой строке сборки.");
     items=[data,...items.filter(x=>x.capture_key!==data.capture_key)].slice(0,100);
     if(data.used_operation_id)usage[data.capture_key]={operation_id:data.used_operation_id};else delete usage[data.capture_key];
     const eligible=render(data.capture_key);showDetail(data);message.textContent=(reason(data)+(data.used_operation_id?" · операция "+data.used_operation_id:""))||"Показание найдено. Доступных в показанном списке: "+eligible+".";
    }else{
     items=data.items;usage=data.use_by_capture||{};
     const eligible=render(previous);message.textContent="Показаний: "+items.length+" · подходят по текущей строке/версии: "+eligible+"."+(data.has_older?" Есть более ранние записи — используйте точный ID.":"");
    }
   }catch(e){if(current()&&token===serial){items=[];usage={};render();detail.replaceChildren();message.textContent=String(e);}}
   finally{running=false;if(current()){refresh.disabled=find.disabled=select.disabled=false;}}
  }
  select.addEventListener("change",showDetail);refresh.onclick=()=>void read();find.onclick=()=>void read(key.value.trim().toUpperCase());
  void read();
 }
 return{mount};
})();
