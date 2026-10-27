/* C-0189: manual NET kg for a CASE line whose server policy says weighted_kg (KG->KG 1:1, not serialized weighted boxes).
   Only the entered NET goes to POST .../weigh-line-manual; the server derives the cumulative fact. No fact_qty, no scale capture. */
window.cpManualNet=(()=>{
 let policy=null;
 const host=()=>document.getElementById('cpTsdManualNet');
 const HELP='/help/manual-weight.html#case-manual-net';
 // Marked KG lines have no electronic NET path here: manual NET with all marking scans is their only weighed route.
 const forced=()=>Boolean(policy?.weighted_kg&&policy.marking_required);
 function show(value){
  policy=value&&value.weighted_kg&&!value.serialized_weight_boxes?value:null;
  const box=host();box.replaceChildren();box.hidden=!policy;
  if(!policy)return;
  document.getElementById('cpTsdFactQty').disabled=true;  // a KG line never sends a cumulative fact
  const toggle=document.createElement('input');toggle.type='checkbox';toggle.id='cpTsdManualToggle';toggle.checked=forced();toggle.disabled=forced();
  toggle.title='Весы недоступны: ввести нетто этой строки вручную. Значение сохранится как ручной ввод оператора.';toggle.dataset.helpId='case.manual.net.toggle';
  toggle.style.cssText='width:auto;min-width:22px;height:22px;margin:0;flex:none';
  const toggleLabel=document.createElement('label');toggleLabel.style.cssText='display:flex;align-items:center;gap:10px;font-weight:600';toggleLabel.append(toggle,document.createTextNode(forced()?' Нетто вводится вручную (маркированный товар на развес)':' Весов нет — ввести нетто вручную'));
  const input=document.createElement('input');input.id='cpTsdManualNetKg';input.inputMode='decimal';input.autocomplete='off';input.placeholder='0.000';
  input.title='Фактическая масса нетто, взятая в этом подходе, в килограммах. Накопленный факт рассчитает система.';input.dataset.helpId='case.manual.net.kg';
  const inputLabel=document.createElement('label');inputLabel.append(document.createTextNode('Нетто вручную, кг'),input);inputLabel.hidden=!toggle.checked;
  const note=document.createElement('small');note.id='cpTsdManualNetNote';note.textContent='Введите только массу нетто текущего подхода. Это ручной ввод, не показание весов.';note.hidden=!toggle.checked;
  const help=document.createElement('a');help.href=HELP;help.target='_blank';help.rel='noopener';help.textContent='Как ввести нетто вручную';
  help.title='Открыть порядок ручного ввода нетто для строки на развес';help.style.display='block';help.dataset.helpId='case.manual.net.help';
  toggle.addEventListener('change',()=>{inputLabel.hidden=note.hidden=!toggle.checked;if(toggle.checked)input.focus();});
  input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();cpTsdConfirmLine();}});  // scanner/keyboard Enter confirms
  box.append(toggleLabel,inputLabel,note,help);
 }
 const active=()=>Boolean(policy&&document.getElementById('cpTsdManualToggle')?.checked);
 function payload(operation,cell,container,scans){
  const raw=document.getElementById('cpTsdManualNetKg').value.trim().replace(',','.');
  if(!/^[0-9]{1,18}([.][0-9]{1,9})?$/.test(raw)||Number(raw)<=0)throw Error('Введите нетто больше нуля в килограммах, не более 9 знаков после точки.');
  if(scans.length>50)throw Error('За одно ручное нетто — не более 50 кодов маркировки. Разделите подход.');
  return {operation_id:operation,net_weight_kg:raw,scan_cell:cell,scan_container:container,unit_scans:scans};
 }
 return {show,active,forced,payload,help:HELP};
})();
