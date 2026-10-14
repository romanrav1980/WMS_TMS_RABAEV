from pathlib import Path
import json
out={};p=Path("wiki-raw/wms_admin_ui_reference/logistics-costs.html");t=p.read_text(encoding="utf-8");at=t.index('<section class="panel"><label>Фактический рейс')
t=t[:at]+'''<section class="panel"><h2>Расчётный период склада</h2>
<button id="lcReadPeriod" title="Прочитать действующее решение финансового контролёра и его версию">Прочитать настройку периода</button>
<label>Источник даты<select id="lcPeriodMode" title="Выбрать подтверждённую дату для новых начислений"><option value="LOADED_UTC">Погрузка, UTC</option><option value="CASE_ASSEMBLY">Начало сборки CASE</option></select></label>
<label>Часовой пояс склада<input id="lcPeriodZone" maxlength="64" placeholder="Регион IANA" title="Явный регион часового пояса для рабочего дня сборки. Старые даты без пояса не пересчитываются"></label>
<button id="lcSavePeriod" data-permission="create_tt_price" title="Сохранить новую версию настройки с причиной и номером решения выше">Сохранить решение о периоде</button>
<p id="lcPeriod"></p>
<button id="lcReadAssembly" title="Прочитать реальные моменты начала коробок выбранного рейса; начисление не выполняется">Проверить источники начала сборки</button><div id="lcAssembly"></div>
<p>Коробкам нужны достоверные моменты начала. Неполные данные и разные дни в одном месте блокируют начисление по началу сборки. Ранее проведённые суммы сохраняются.</p></section>'''+t[at:]
out[p.as_posix()]=t
p=Path("wiki-raw/wms_admin_ui_reference/logistics-costs.js");t=p.read_text(encoding="utf-8");t=t.replace('rates=null,history=null;','rates=null,history=null,periodPolicy=null;')
at=t.index(' el("lcCalculate").addEventListener')
t=t[:at]+''' async function readPeriod(){await read(async current=>{const ware=positive("lcWare"),result=await request("/warehouses/"+ware+"/period-policy");if(!current())return;periodPolicy=result;el("lcPeriodMode").value=result.period_mode;el("lcPeriodZone").value=result.timezone_region||"";el("lcPeriod").textContent="Версия "+result.version+" · "+(result.period_mode==="CASE_ASSEMBLY"?"Начало CASE · "+result.timezone_region:"Погрузка UTC");});}
 el("lcReadPeriod").addEventListener("click",readPeriod);
 el("lcSavePeriod").addEventListener("click",()=>prepare("/warehouses/"+positive("lcWare")+"/period-policy",()=>{const ware=positive("lcWare");if(!periodPolicy||periodPolicy.warehouse_id!==ware)throw Error("Сначала прочитайте текущую настройку периода.");const mode=el("lcPeriodMode").value;return{operation_id:"COST.PERIOD:"+crypto.randomUUID(),period_mode:mode,timezone_region:mode==="CASE_ASSEMBLY"?el("lcPeriodZone").value.trim():null,expected_version:periodPolicy.version,reason:el("lcReason").value.trim(),decision_reference:el("lcReference").value.trim()};}));
 el("lcReadAssembly").addEventListener("click",()=>read(async current=>{const ware=positive("lcWare"),trip=positive("lcTrip"),region=el("lcPeriodZone").value.trim();if(!region)throw Error("Укажите часовой пояс для просмотра рабочего дня.");const result=await request("/trips/"+trip+"/assembly-period?warehouse_id="+ware+"&timezone_region="+encodeURIComponent(region));if(!current())return;const state={READY:"Источник подтверждён",INCOMPLETE:"Не хватает достоверных моментов начала",MULTIPLE_PERIODS:"Коробки относятся к разным дням"};const summary=document.createElement("p");summary.textContent=state[result.state]||result.state;el("lcAssembly").replaceChildren(summary,...result.lines.map(row=>{const p=document.createElement("p");p.textContent=row.box_identifier+" · "+(row.instant||"точный момент начала отсутствует")+" · "+(row.business_date||"рабочая дата не определена");return p;}));}));
 for(const id of ["lcTrip","lcPeriodZone"])el(id).addEventListener("input",()=>{++serial;el("lcAssembly").replaceChildren();});
'''+t[at:]
t=t.replace('++serial;rates=null;history=null;el("lcMoreHistory")','++serial;rates=null;history=null;periodPolicy=null;el("lcPeriod").textContent="";el("lcAssembly").replaceChildren();el("lcMoreHistory")')
t=t.replace('"lcBasisBoxes"])el(id).value=""','"lcBasisBoxes","lcPeriodZone"])el(id).value=""')
t=t.replace('function changed(){','function changed(){')
# Auth changes invalidate warehouse-specific policy and proof in addition to previous rates/history.
t=t.replace('identity=scope;','identity=scope;periodPolicy=null;el("lcPeriod").textContent="";el("lcAssembly").replaceChildren();')
out[p.as_posix()]=t
print(json.dumps(out))
