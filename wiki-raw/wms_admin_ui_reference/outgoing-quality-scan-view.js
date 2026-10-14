/* Bounded rendering of draft evidence; physical acceptance stays in Oracle. */
(() => {
 function render(host,entries,editable,remove){
  host.replaceChildren();
  const heading=document.createElement('p');heading.className='qc-scan-heading';
  heading.textContent=entries.length?'Последние сканы · '+Math.min(entries.length,50)+' из '+entries.length:'Новые сканы появятся здесь.';
  host.append(heading);if(!entries.length)return;
  const wrap=document.createElement('div');wrap.className='qc-scan-scroll';
  const table=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');
  for(const label of ['Вид','Штрихкод / профиль','Действие']){const th=document.createElement('th');th.textContent=label;tr.append(th);}
  head.append(tr);table.append(head);const body=document.createElement('tbody');table.append(body);
  const start=Math.max(0,entries.length-50);
  for(let index=entries.length-1;index>=start;index--){
   const entry=entries[index],value=entry.value,row=document.createElement('tr'),kind=document.createElement('td'),code=document.createElement('td'),actions=document.createElement('td');
   kind.textContent=entry.kind==='mark'?'QR единицы':'ШК товара / коробки';
   const raw=entry.kind==='mark'?value.code:value.barcode,shown=raw.length>80?raw.slice(0,60)+'…'+raw.slice(-12):raw;
   const identity=document.createElement('span');identity.textContent=shown;identity.title=raw;identity.className='qc-scan-code';code.append(identity);
   if(entry.kind==='mark'){const profile=document.createElement('small');profile.textContent=value.system_code+' / '+value.profile_code;code.append(profile);}
   const button=document.createElement('button');button.type='button';button.textContent='Удалить';button.disabled=!editable;
   button.title='Удалить этот скан из неподтверждённого состава';button.addEventListener('click',()=>remove(index));actions.append(button);
   row.append(kind,code,actions);body.append(row);
  }
  wrap.append(table);host.append(wrap);
 }
 window.wmsQualityScanView={render};
})();
