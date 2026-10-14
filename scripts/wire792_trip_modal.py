from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");t=p.read_text(encoding="utf-8")
old='<label>Номер целевого рейса<input id="sdTarget" inputmode="numeric" placeholder="Номер существующего рейса"></label>'
new='<label>Целевой рейс<div class="trip-choice"><input id="sdTarget" readonly inputmode="numeric" placeholder="Выберите рейс из списка"><button id="sdPickTrip" type="button" disabled>Выбрать рейс</button></div><span id="sdSelectedTrip" class="selected-trip-note"></span></label>'
assert old in t;t=t.replace(old,new)
dialog="""
<dialog id="tpDialog" class="trip-picker" aria-labelledby="tpTitle">
<header class="trip-picker-heading"><div><div class="eyebrow">ПЕРЕНОС СТ</div><h2 id="tpTitle">Выберите рейс</h2><p id="tpSubtitle"></p></div><button id="tpClose" type="button" aria-label="Закрыть выбор рейса">×</button></header>
<form id="tpFilters" class="trip-filters">
<label>Дата с<input id="tpFrom" type="date"></label><label>Дата по<input id="tpTo" type="date"></label>
<label>Район<input id="tpDistrict" maxlength="80" placeholder="Название или часть названия"></label>
<label>Номер магазина<input id="tpStore" maxlength="80" placeholder="Например, 0042"></label>
<button id="tpSearch" type="submit">Найти рейсы</button></form>
<p id="tpMessage" class="trip-picker-message" role="status"></p>
<div class="trip-list-wrap"><div id="tpEmpty" class="waiting-empty">Выберите период поиска.</div>
<table id="tpTable" hidden><thead><tr><th>Рейс</th><th>Дата</th><th>Машина</th><th>Районы</th><th>Магазины</th><th>Паллет в плане</th><th></th></tr></thead><tbody id="tpRows"></tbody></table></div>
<footer class="trip-picker-footer"><span id="tpCount"></span><button id="tpNext" type="button" disabled>Следующие рейсы</button></footer></dialog>
"""
assert 'id="tpDialog"' not in t
t=t.replace('</main>',dialog+'</main>')
t=t.replace('<script src="st-waiting-tasks.js"></script>','<script src="st-waiting-tasks.js"></script><script src="st-trip-picker.js"></script>')
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");t=p.read_text(encoding="utf-8")
anchor=" function pending(){"
assert anchor in t
t=t.replace(anchor," function clearTrip(){el('sdTarget').value='';el('sdSelectedTrip').textContent='';}\n"+anchor)
t=t.replace("el('sdRetry').disabled=busy||!p;","el('sdRetry').disabled=busy||!p;el('sdPickTrip').disabled=busy||!context||!!p;")
t=t.replace("context=null;showSummary(null);controls();","context=null;clearTrip();showSummary(null);controls();")
t=t.replace("epoch++;context=null;showSummary(null);next=null;","epoch++;context=null;clearTrip();showSummary(null);next=null;")
anchor=" for(const id of ['sdTarget','sdReason','sdReference'])el(id).addEventListener"
assert anchor in t
hooks=""" el('sdPickTrip').addEventListener('click',()=>{
  if(context&&!busy)window.dispatchEvent(new CustomEvent('wms-st-trip-picker-open',{detail:{st_number:context.st_number,source_hash:context.source_hash}}));
 });
 window.addEventListener('wms-st-trip-selected',event=>{
  const v=event.detail;
  if(!context||busy||context.st_number!==v.st_number||context.source_hash!==v.source_hash)return;
  el('sdTarget').value=String(v.trip.trip_id);
  el('sdSelectedTrip').textContent=v.trip.shipment_date+' · '+v.trip.vehicle+' · '+(v.trip.districts.join(', ')||'Район не указан');
  controls();
 });
"""
t=t.replace(anchor,hooks+anchor)
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.css");t=p.read_text(encoding="utf-8")
t+="""
.day-page .trip-choice{display:flex;gap:8px;align-items:center}
.day-page .trip-choice input{min-width:0;flex:1}
.day-page .trip-choice button{margin:0;white-space:nowrap;min-height:42px}
.day-page .selected-trip-note{font-size:11px;font-weight:400;color:#7187a6;min-height:15px}
.day-page .trip-picker{width:min(1100px,94vw);max-height:90vh;padding:0;border:1px solid #dce5f2;border-radius:18px;box-shadow:0 28px 80px #16284840;color:#24344b;background:#fff}
.day-page .trip-picker::backdrop{background:#142a4655;backdrop-filter:blur(3px)}
.day-page .trip-picker-heading{display:flex;align-items:flex-start;justify-content:space-between;padding:25px 28px 18px;border-bottom:1px solid #eaf0f7}
.day-page .trip-picker-heading h2{font-size:23px;margin:6px 0}
.day-page .trip-picker-heading p{margin:0;color:#8090a8;font-size:12px}
.day-page #tpClose{margin:0;border:0;background:#f3f6fb;font-size:24px;padding:2px 13px;min-height:36px;color:#6c7f9b}
.day-page .trip-filters{display:grid;grid-template-columns:1fr 1fr 1.4fr 1fr auto;gap:13px;padding:22px 28px;background:#f8faff;align-items:end}
.day-page .trip-filters label{display:flex;margin:0;min-width:0}
.day-page .trip-filters input{min-width:0;width:100%;background:#fff}
.day-page #tpSearch{margin:0;min-height:42px;background:#2867d4;color:#fff;border-color:#2867d4}
.day-page .trip-picker-message{margin:0;padding:14px 28px;font-size:12px;color:#7186a4}
.day-page .trip-list-wrap{padding:0 28px;max-height:46vh;overflow:auto}
.day-page .trip-list-wrap table{margin:0;width:100%;display:table}
.day-page .trip-list-wrap th,.day-page .trip-list-wrap td{padding:13px 10px}
.day-page .pick-trip-button{color:#2867d4;border-color:#c9dbf7}
.day-page .trip-picker-footer{display:flex;justify-content:space-between;align-items:center;padding:13px 28px;border-top:1px solid #eaf0f7;font-size:12px;color:#8595ac}
.day-page .trip-picker-footer button{margin:0}
@media(max-width:850px){.day-page .trip-filters{grid-template-columns:1fr 1fr}.day-page .trip-list-wrap{overflow:auto}.day-page .trip-picker-heading,.day-page .trip-filters{padding:18px}.day-page .trip-choice{flex-wrap:wrap}}
"""
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
