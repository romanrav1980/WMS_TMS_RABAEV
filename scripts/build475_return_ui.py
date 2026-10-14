import json
from pathlib import Path
out={}
p=Path("wiki-raw/wms_admin_ui_reference/store-returns.html");s=p.read_text(encoding="utf-8")
s=s.replace('<label>Количество в основной единице','<label>Результат исходной приёмки<select id="returnBasis"><option value="ACCEPTED">Товар принят магазином</option><option value="REFUSED">Отказ при доставке</option><option value="DAMAGED">Повреждение при доставке</option></select></label><label>Количество в основной единице')
s=s.replace("После согласования логист","Товар из отказа или повреждений не увеличивает количество, принятое магазином. Его повторное использование требует отдельной проверки качества. После согласования логист")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-returns.js");s=p.read_text(encoding="utf-8")
s=s.replace("  if(!dossier||busy||pending)return;","  if(!dossier||busy||pending)return;\n  if(el('returnBasis').value!=='ACCEPTED'){reuseMessage.textContent='Для отказа или повреждения нужна отдельная проверка качества; повторное использование здесь не разрешается.';return;}",1)
s=s.replace('["returnLine","returnQuantity","returnDisposition"]','["returnLine","returnQuantity","returnDisposition","returnBasis"]')
s=s.replace('  el("returnRetry").hidden=!pending;',"""  el("returnDisposition").querySelector('option[value="REUSE"]').disabled=el("returnBasis").value!=="ACCEPTED";
  el("returnGoodBox").disabled=busy||!!pending||el("returnBasis").value!=="ACCEPTED";
  el("returnRetry").hidden=!pending;""",1)
s=s.replace('" · доступно "+row.available_for_approval','" · возврат принятого доступен "+row.available_for_approval+" · отказ доступен "+row.refused_available+" · повреждение доступно "+row.damaged_available')
s=s.replace('row.quantity+" "+row.base_uom+" · "+row.disposition','row.quantity+" "+row.base_uom+" · "+(row.return_basis||"ACCEPTED")+" · "+row.disposition')
s=s.replace(' const line=Number(el("returnLine").value);unitPanel.replaceChildren();',''' const line=Number(el("returnLine").value),basis=el("returnBasis").value;unitPanel.replaceChildren();
  for(const option of el("returnLine").options){
   const item=dossier?.lines.find(r=>r.line_no===Number(option.value));
   if(item)option.textContent="Строка "+item.line_no+" · "+item.article+" · доступно "+(basis==="ACCEPTED"?item.available_for_approval:basis==="REFUSED"?item.refused_available:item.damaged_available)+" "+item.base_uom;
  }''')
s=s.replace('filter(u=>u.line_no===line)','filter(u=>u.line_no===line&&(u.return_basis||"ACCEPTED")===basis)')
s=s.replace("Выберите конкретные ранее принятые единицы.","Выберите конкретные исходные единицы с выбранным результатом приёмки.")
s=s.replace('  const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}', '  const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}')
marker='  if(!/^[0-9]{1,18}'
# Insert into approve only immediately after body construction.
start=s.index(" async function approve(){")
a=s.index('  if(!/^[0-9]{1,18}',start)
s=s[:a]+'''  if(el("returnBasis").value!=="ACCEPTED")body.return_basis=el("returnBasis").value;
'''+s[a:]
s=s.replace(' el("returnLine").addEventListener("change",renderUnits);',''' el("returnBasis").addEventListener("change",()=>{
  if(el("returnBasis").value!=="ACCEPTED"){
   el("returnDisposition").value=el("returnBasis").value==="DAMAGED"?"DISPOSAL":"SUPPLIER";
   el("returnGoodBox").checked=false;
  }
  renderUnits();controls();
 });
 el("returnLine").addEventListener("change",renderUnits);''')
out[str(p)]=s
print(json.dumps(out))
