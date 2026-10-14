from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/store-returns.js");s=p.read_text(encoding="utf-8")
s=s.replace(' const say=text=>',' const unitPanel=document.createElement("section");unitPanel.id="returnUnitList";el("returnLines").after(unitPanel);\n const say=text=>',1)
s=s.replace(' async function load(){',''' function renderUnits(){
  const line=Number(el("returnLine").value);unitPanel.replaceChildren();
  for(const unit of (dossier?.units||[]).filter(u=>u.line_no===line)){
   const label=document.createElement("label"),box=document.createElement("input");box.type="checkbox";box.value=unit.key;box.dataset.unitKey="1";
   label.title=unit.key;label.append(box,document.createTextNode("Единица "+unit.key.slice(-12)+" · "+unit.quantity+" "+unit.base_uom));unitPanel.append(label,document.createElement("br"));
  }
  if((dossier?.units||[]).length){const p=document.createElement("p");p.textContent="Выберите конкретные ранее принятые единицы. Количество в решении должно совпадать с их количеством в базовых единицах.";unitPanel.prepend(p);}
 }
 async function load(){''',1)
s=s.replace('if(scope===key()&&version===serial&&source===el("returnSource").value){render(data);say("");}','if(scope===key()&&version===serial&&source===el("returnSource").value){render(data);renderUnits();say("");}')
s=s.replace('  if(!/^[0-9]{1,18}', '  const selected=[...unitPanel.querySelectorAll("input:checked")].map(n=>n.value);if(selected.length)body.unit_keys=selected;\n  if(!/^[0-9]{1,18}',1)
s=s.replace('pending=null;dossier=null;say("Возврат согласован','pending=null;dossier=null;unitPanel.replaceChildren();say("Возврат согласован',1)
s=s.replace('++serial;dossier=null;pending=null;','++serial;dossier=null;pending=null;unitPanel.replaceChildren();',1)
s=s.replace(' el("returnLoad").addEventListener',' el("returnLine").addEventListener("change",renderUnits);\n el("returnLoad").addEventListener',1)
print(json.dumps({str(p):s},ensure_ascii=True))
