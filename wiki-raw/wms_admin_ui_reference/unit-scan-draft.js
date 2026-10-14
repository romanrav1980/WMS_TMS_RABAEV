/* Reusable bounded QR draft. Native Oracle remains the composition authority. */
window.wmsUnitScanDraft=function(host){
 let context=null,key="",scans=[];
 const label=document.createElement("p"),profile=document.createElement("select"),code=document.createElement("input"),add=document.createElement("button"),clear=document.createElement("button"),message=document.createElement("p");
 code.autocomplete="off";code.placeholder="QR уникальной единицы";add.type="button";add.textContent="Добавить QR";clear.type="button";clear.textContent="Очистить QR";
 host.replaceChildren(label,profile,code,add,clear,message);
 function render(){label.textContent=context?"Сканы обязательных профилей: "+scans.length+" из "+context.expected_scan_count:"";host.hidden=!context;}
 function save(next){try{localStorage.setItem(key,JSON.stringify(next));scans=next;message.textContent="";render();return true;}catch{message.textContent="Не удалось сохранить QR. Операция не отправлена.";return false;}}
 function append(){
  const selected=context?.profiles?.[Number(profile.value)];
  if(!selected||!code.value)return;
  if(code.value.length>4000||scans.length>=20000){message.textContent="Превышен допустимый размер QR.";return;}
  if(scans.some(x=>x.system_code===selected.system_code&&x.profile_code===selected.profile_code&&x.code===code.value)){message.textContent="Этот QR уже добавлен.";return;}
  if(save([...scans,{system_code:selected.system_code,profile_code:selected.profile_code,code:code.value}]))code.value="";
 }
 add.addEventListener("click",append);clear.addEventListener("click",()=>save([]));code.addEventListener("keydown",event=>{if(event.key==="Enter"){event.preventDefault();append();}});
 return {
  setContext(control,scope){
   context=control;key="wms-unit-scan:"+scope+":"+JSON.stringify(control);scans=[];code.value="";message.textContent="";profile.replaceChildren();
   if(context){
    (context.profiles||[]).forEach((p,i)=>{const option=document.createElement("option");option.value=String(i);option.textContent=p.system_code+" / "+p.profile_code;profile.append(option);});
    try{const old=JSON.parse(localStorage.getItem(key)||"[]");if(Array.isArray(old)&&old.length<=20000&&old.every(x=>typeof x.code==="string"&&x.code.length>0&&x.code.length<=4000&&context.profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code)))scans=old;}catch{message.textContent="Не удалось восстановить QR.";}
   }render();
  },
  getScans(){if(!context)return [];if(!context.supported||scans.length!==context.expected_scan_count)throw Error("Сканируйте все обязательные профили согласованного возврата.");return scans.map(x=>({...x}));}
 };
};
