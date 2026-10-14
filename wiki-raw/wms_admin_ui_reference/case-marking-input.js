/* Current SKU profiles determine visible scan fields; the existing server resolves physical identities. */
window.cpCaseMarking=(()=>{
 let policy=null;
 const panel=()=>document.getElementById('cpTsdMarking');
 function show(value){
  policy=value;const host=panel();host.replaceChildren();host.hidden=!value?.marking_required||Boolean(value?.serialized_weight_boxes);
  if(host.hidden)return;
  const heading=document.createElement('h2');heading.textContent='Коды маркированных единиц';host.append(heading);
  const note=document.createElement('p');note.textContent='Для каждого профиля отсканируйте коды одних и тех же фактически взятых единиц. Штрихкод товара не заменяет уникальный код штуки.';host.append(note);
  if(!value.profiles?.length){const warning=document.createElement('p');warning.textContent='У товара не настроены профили. Обратитесь к ответственному за карточку товара.';host.append(warning);return;}
  for(const profile of value.profiles){
   const label=document.createElement('label'),title=document.createElement('span'),input=document.createElement('textarea'),count=document.createElement('small');
   title.textContent=profile.system_code+' / '+profile.profile_code;
   input.rows=3;input.autocomplete='off';input.spellcheck=false;input.dataset.system=profile.system_code;input.dataset.profile=profile.profile_code;
   input.title='Уникальные коды этого профиля, по одному на строку. Управляющие разделители кода сохраняются.';
   input.addEventListener('input',()=>{count.textContent='Считано кодов: '+input.value.split(/\r?\n/).filter(x=>x.length>0).length;});
   count.textContent='Считано кодов: 0';label.append(title,input,count);host.append(label);
  }
 }
 function collect(){
  if(!policy)throw Error('Дождитесь актуальных настроек товара.');
  if(!policy.marking_required)return [];
  if(!policy.profiles?.length)throw Error('У товара отсутствует профиль маркировки.');
  const scans=[];let count=null;
  for(const input of panel().querySelectorAll('textarea')){
   const codes=input.value.split(/\r?\n/).filter(x=>x.length>0);
   if(!codes.length)throw Error('Отсканируйте коды профиля '+input.dataset.profile+'.');
   if(new Set(codes).size!==codes.length)throw Error('Повтор кода в профиле '+input.dataset.profile+'.');
   if(count!==null&&codes.length!==count)throw Error('Число кодов по профилям различается. Проверьте одни и те же единицы товара.');
   count=codes.length;
   for(const code of codes)scans.push({system_code:input.dataset.system,profile_code:input.dataset.profile,code});
  }
  if(!scans.length||scans.length>10000)throw Error('Допускается от 1 до 10000 кодов за подтверждение.');
  return scans;
 }
 return {show,collect};
})();
