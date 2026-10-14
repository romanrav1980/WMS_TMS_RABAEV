from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/trace-manifests.html");s=p.read_text(encoding="utf-8")
s=s.replace('data-required-permission="trace_manifest_import"','data-required-permission="wms_admin_login"')
s=s.replace('<section class="panel"><p>Импорт','<section class="panel" data-permission="trace_manifest_import"><p>Импорт',1)
s=s.replace('<label>JSON-документ отправителя','<label data-permission="trace_manifest_import">JSON-документ отправителя',1)
s=s.replace('<button id="tmImport">','<button id="tmImport" data-permission="trace_manifest_import">',1)
needle='<label>Сканированные агрегации по профилям'
unit="""<label>Способ подтверждения<select id="tmCaptureMode"><option value="AGGREGATION">Агрегации по документу отправителя</option><option value="UNIT">QR каждой физической единицы</option><option value="MIXED">QR штук и агрегации других профилей</option></select></label><button id="tmUnitLoad">Загрузить профили товара</button><label>Номер физической единицы<input id="tmPhysicalUnit" inputmode="numeric" value="1"></label><label>Количество этой единицы в базовой единице<input id="tmPhysicalQty" inputmode="decimal" value="1"></label><label>Профиль маркировки<select id="tmUnitProfile"></select></label><label>QR физической единицы, скан<input id="tmUnitCode" autocomplete="off"></label><button id="tmUnitAdd">Добавить скан к единице</button><button id="tmUnitClear">Очистить список сканов</button><p id="tmUnitMessage" role="status"></p><div id="tmUnitRows"></div>"""
assert needle in s;s=s.replace(needle,unit+needle,1)
s=s.replace('<script src="trace-manifests.js">','<script src="trace-unit-capture.js"></script><script src="trace-manifests.js">')
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/trace-manifests.js");s=p.read_text(encoding="utf-8")
needle='const aggregations=JSON.parse(el("tmScans").value);if(!Array.isArray(aggregations)||!aggregations.length)throw Error("Укажите сканы обязательных агрегаций.");const capture={manifest_operation_id:el("tmManifest").value,units:[],aggregations},uid=el("tmPallet").value;'
replacement='const mode=el("tmCaptureMode").value;let capture=mode==="AGGREGATION"?{units:[],aggregations:[]}:window.retailcaseUnitCapture.capture(mode==="UNIT");if(mode!=="UNIT"){const aggregations=JSON.parse(el("tmScans").value);if(!Array.isArray(aggregations)||!aggregations.length)throw Error("Укажите сканы обязательных агрегаций.");capture={...capture,manifest_operation_id:el("tmManifest").value,aggregations};}const uid=el("tmPallet").value;'
assert needle in s;s=s.replace(needle,replacement,1)
s=s.replace('pending=null;el("tmResult").textContent=JSON.stringify(result,null,2);','pending=null;window.retailcaseUnitCapture.reset();el("tmResult").textContent=JSON.stringify(result,null,2);')
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
