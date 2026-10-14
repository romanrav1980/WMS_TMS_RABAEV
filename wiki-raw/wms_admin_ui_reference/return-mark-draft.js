/* Registered return BOX codes are expanded and validated by Oracle. */
window.wmsReturnMarkDraft=function(host){
 let context=null,key="",damaged=false,observed=null,draft={scans:[],aggregation_scans:[]};
 const label=document.createElement("p"),profile=document.createElement("select"),kind=document.createElement("select"),code=document.createElement("input"),add=document.createElement("button"),clear=document.createElement("button"),message=document.createElement("p");
 for(const [value,text]of [["UNIT","QR единицы"],["BOX","Агрегация коробки"],["PALLET","Агрегация исходной паллеты"]]){const o=document.createElement("option");o.value=value;o.textContent=text;kind.append(o);}
 code.autocomplete="off";add.type=clear.type="button";add.textContent="Добавить код";clear.textContent="Очистить сканы";
 const remove=document.createElement("button");remove.type="button";remove.textContent="Убрать последний скан в выбранном режиме";
 host.replaceChildren(label,profile,kind,code,add,remove,clear,message);
 const selected=()=>context?.profiles?.[Number(profile.value)];
 function render(){
  host.hidden=!context;label.textContent=context?"QR единиц: "+draft.scans.length+". Коды коробок: "+draft.aggregation_scans.length+". Полный состав проверяет сервер.":"";
  const mode=selected()?.scan_mode;kind.hidden=mode!=="UNIT_OR_AGGREGATION";
  if(mode==="BOX"||mode==="PALLET")kind.value=mode;else if(mode==="UNIT")kind.value="UNIT";
  code.placeholder=kind.value==="PALLET"?"Код исходной паллеты (сохраните идентификатор) ":kind.value==="BOX"?"Код агрегации коробки":"QR единицы";
  add.disabled=damaged||!context?.supported||context.profiles.some(p=>!["UNIT","BOX","PALLET","UNIT_OR_AGGREGATION"].includes(p.scan_mode));
 }
 function save(value){try{if(damaged||localStorage.getItem(key)!==observed)throw Error("Изменённый исходник");const wire=JSON.stringify(value);localStorage.setItem(key,wire);if(localStorage.getItem(key)!==wire)throw Error("Запись не подтверждена");observed=wire;draft=value;message.textContent="";render();return true;}catch{message.textContent="Не удалось сохранить сканы. Приёмка не отправлена.";return false;}}
 function append(){
  const p=selected();if(!p||!code.value||code.value.length>4000||add.disabled)return;
  const box=kind.value!=="UNIT",list=box?draft.aggregation_scans:draft.scans;
  if(list.length>=(box?1000:20000)||list.some(x=>x.system_code===p.system_code&&x.profile_code===p.profile_code&&x.code===code.value)){message.textContent="Повтор кода или превышен размер состава.";return;}
  const item={system_code:p.system_code,profile_code:p.profile_code,code:code.value,...(box?{level:kind.value}:{})};
  if(save({...draft,[box?"aggregation_scans":"scans"]:[...list,item]}))code.value="";
 }
 remove.addEventListener("click",()=>{
  const p=selected();if(!p||add.disabled)return;
  const field=kind.value==="UNIT"?"scans":"aggregation_scans",list=draft[field];let index=-1;
  for(let i=list.length-1;i>=0;i--)if(list[i].system_code===p.system_code&&list[i].profile_code===p.profile_code&&(kind.value==="UNIT"||list[i].level===kind.value)){index=i;break;}
  if(index>=0)save({...draft,[field]:list.filter((_,i)=>i!==index)});
 });
 profile.addEventListener("change",render);kind.addEventListener("change",render);add.addEventListener("click",append);clear.addEventListener("click",()=>{
 if(!context)return;
 try{const raw=localStorage.getItem(key);if(raw!==observed)throw Error("Сканы изменены другой вкладкой; перечитайте возврат.");
  if(raw!==null){const archive=key+":archive:"+crypto.randomUUID();localStorage.setItem(archive,raw);if(localStorage.getItem(archive)!==raw||localStorage.getItem(key)!==raw)throw Error("Архив сканов не подтверждён.");}
  localStorage.removeItem(key);if(localStorage.getItem(key)!==null)throw Error("Очистка не подтверждена.");observed=null;damaged=false;draft={scans:[],aggregation_scans:[]};render();message.textContent="Прежние сканы сохранены в архив. Сканируйте состав заново.";
 }catch(error){message.textContent=error.message;}
});code.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();append();}});
 return {
  setContext(control,scope){
   context=control;damaged=false;observed=null;key="wms-return-mark:"+scope+":"+JSON.stringify(control);draft={scans:[],aggregation_scans:[]};code.value="";message.textContent="";profile.replaceChildren();
   if(context){
    (context.profiles||[]).forEach((p,i)=>{const o=document.createElement("option");o.value=String(i);o.textContent=p.system_code+" / "+p.profile_code+" · "+p.scan_mode;profile.append(o);});
    try{
     observed=localStorage.getItem(key);const old=JSON.parse(observed||"null");
     const valid=(x,box)=>typeof x?.code==="string"&&x.code.length>0&&x.code.length<=4000&&context.profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code&&(box?(p.scan_mode===x.level||p.scan_mode==="UNIT_OR_AGGREGATION"):["UNIT","UNIT_OR_AGGREGATION"].includes(p.scan_mode)))&&(!box||["BOX","PALLET"].includes(x.level));
     if(old){if(!Array.isArray(old.scans)||!Array.isArray(old.aggregation_scans)||old.scans.length>20000||old.aggregation_scans.length>1000||!old.scans.every(x=>valid(x,false))||!old.aggregation_scans.every(x=>valid(x,true)))throw Error("invalid");draft=old;}
    }catch{damaged=true;message.textContent="Черновик повреждён. Приёмка заблокирована. Кнопка очистки сохранит исходник в архив перед новым сканированием.";}
   }render();
  },
  getEvidence(){
   if(!context)return {};
   if(damaged||localStorage.getItem(key)!==observed)throw Error("Сохранённые сканы повреждены или изменены другой вкладкой. Перечитайте возврат либо архивируйте исходник кнопкой очистки.");
   if(!context.supported||context.profiles.some(p=>!["UNIT","BOX","PALLET","UNIT_OR_AGGREGATION"].includes(p.scan_mode)))throw Error("Неподдерживаемый профиль маркировки возврата.");
   for(const p of context.profiles){
    const matches=x=>x.system_code===p.system_code&&x.profile_code===p.profile_code;
    const units=draft.scans.filter(matches).length,boxes=draft.aggregation_scans.filter(x=>matches(x)&&(p.scan_mode==="UNIT_OR_AGGREGATION"||x.level===p.scan_mode)).length;
    const expected=(context.units||[]).filter(u=>u.profiles?.some(matches)).length||context.physical_unit_count||0;
    if(!(["BOX","PALLET"].includes(p.scan_mode)?boxes>0:units===expected||(p.scan_mode==="UNIT_OR_AGGREGATION"&&boxes>0)))throw Error("Сканируйте каждый обязательный профиль согласованного возврата.");
   }
   return JSON.parse(JSON.stringify(draft));
  }
 };
};
