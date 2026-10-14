raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace(' let pending=null,busy=false,identity="",serial=0;',' let pending=null,busy=false,identity="",serial=0,unitScans=[],unitPlan="";')
s=s.replace('main input,main button','main input,main button,main select')
# Mount scan form within existing receive section.
needle=' const say=t=>el("iwMessage").textContent=t;'
extra='''
 const marks=document.createElement("section");
 marks.innerHTML='<h3>Маркированный состав приёмки</h3><button id="iwUnitSource" type="button">Загрузить состав выбранного плана</button><p id="iwUnitInfo"></p><label>Система и профиль <select id="iwUnitProfile"></select></label><label>QR физической единицы <input id="iwUnitCode" autocomplete="off"></label><button id="iwUnitAdd" type="button">Добавить скан</button><button id="iwUnitClear" type="button">Очистить сканы</button><p id="iwUnitCount"></p>';
 el("iwReceive").parentElement.append(marks);
 const scanKey=()=>key()+":unit-draft";
 function showScans(){el("iwUnitCount").textContent="Сканов: "+unitScans.length+" · количество товара подтверждается отдельно";}
 function saveScans(next,plan){localStorage.setItem(scanKey(),JSON.stringify({plan,scans:next}));unitScans=next;unitPlan=plan;showScans();}
 async function unitSource(){
  if(busy||pending)return;const plan=el("iwPhysicalPlan").value,scope=key();if(!plan){say("Выберите план.");return;}busy=true;controls();
  try{const source=await request("/plans/"+encodeURIComponent(plan)+"/units");if(scope!==key()||plan!==el("iwPhysicalPlan").value)return;
   if(unitPlan!==plan)saveScans([],plan);
   el("iwUnitProfile").replaceChildren(...source.profiles.map(p=>new Option(p.system_code+" / "+p.profile_code,JSON.stringify([p.system_code,p.profile_code]))));
   el("iwUnitInfo").textContent="Физических единиц: "+source.physical_unit_count+". Требуется скан по каждому обязательному профилю. "+(source.profiles.some(p=>p.scan_mode!=="UNIT")?"Для этого состава нужна приёмка по агрегации; текущая форма не проведёт её.":"Сканируйте QR единиц.");
  }catch(e){if(scope===key())say(e.message);}finally{busy=false;controls();}
 }
 el("iwUnitSource").addEventListener("click",unitSource);
 el("iwUnitAdd").addEventListener("click",()=>{if(busy||pending)return;try{
  const plan=el("iwPhysicalPlan").value;if(!plan||unitPlan!==plan||!el("iwUnitProfile").value)throw Error("Загрузите состав выбранного плана.");
  const [system_code,profile_code]=JSON.parse(el("iwUnitProfile").value),code=el("iwUnitCode").value;
  if(!code)throw Error("Сканируйте QR.");
  if(unitScans.some(s=>s.system_code===system_code&&s.profile_code===profile_code&&s.code===code))throw Error("Этот QR уже добавлен.");
  if(unitScans.length>=20000)throw Error("Превышен предел сканов.");
  saveScans([...unitScans,{system_code,profile_code,code}],plan);el("iwUnitCode").value="";el("iwUnitCode").focus();
 }catch(e){say(e.message);}});
 el("iwUnitCode").addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();el("iwUnitAdd").click();}});
 el("iwUnitClear").addEventListener("click",()=>{if(!busy&&!pending)try{saveScans([],el("iwPhysicalPlan").value);}catch(e){say(e.message);}});
 el("iwPhysicalPlan").addEventListener("change",()=>{el("iwUnitProfile").replaceChildren();el("iwUnitInfo").textContent="Загрузите состав выбранного плана.";showScans();});
'''
s=s.replace(needle,needle+extra)
s=s.replace('if(Object.values(body).some(v=>!v))throw Error("Выберите план', 'if(path==="/receive"&&unitScans.length){if(unitPlan!==body.plan_operation_id)throw Error("Сканы относятся к другому плану.");body.scans=unitScans.map(s=>({...s}));}if(Object.values(body).some(v=>!v))throw Error("Выберите план')
s=s.replace('pending=null;el("iwRows")','pending=null;unitScans=[];unitPlan="";el("iwUnitProfile").replaceChildren();el("iwUnitInfo").textContent="";el("iwUnitCode").value="";try{const draft=JSON.parse(localStorage.getItem(scanKey())||"null");if(draft){unitScans=draft.scans||[];unitPlan=draft.plan||"";}}catch{}showScans();el("iwRows")')
s=s.replace('pending=null;if(intent.path===','pending=null;if(intent.path==="/receive"){localStorage.removeItem(scanKey());unitScans=[];unitPlan="";showScans();}if(intent.path===')
print(json.dumps({str(p):s},ensure_ascii=True))
