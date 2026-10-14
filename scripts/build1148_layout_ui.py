from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py");f[str(p)]=p.read_text(encoding="utf-8").replace('LEGACY_GROUP_WHOLE_BOX_V1','LEGACY_GROUP_WHOLE_BOX_V2')
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<th>Объём места, м³</th></tr></thead><tbody id="sapAutoRows">','<th>Объём места, м³</th><th>Температурные требования</th></tr></thead><tbody id="sapAutoRows">')
s=s.replace('sap-automatic-preparation.js?v=20261013-1131','sap-automatic-preparation.js?v=20261014-1148')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.js");s=p.read_text(encoding="utf-8")
s=s.replace(" function display(value){"," function temperatureText(stat){return stat.temp_min_c!==undefined&&stat.temp_max_c!==undefined&&(stat.temp_min_c!==null||stat.temp_max_c!==null)?(stat.temp_min_c??'не задано')+' … '+(stat.temp_max_c??'не задано')+' °C':'Не подтверждены';}\n function display(value){")
s=s.replace('td(s.goods_weight_kg),td(s.goods_volume_m3));','td(s.goods_weight_kg),td(s.goods_volume_m3),td(temperatureText(s)));')
s=s.replace('td(stat.goods_weight_kg),td(stat.goods_volume_m3));','td(stat.goods_weight_kg),td(stat.goods_volume_m3),td(temperatureText(stat)));')
s=s.replace('Целые коробки, нормы, масса и объём соблюдены.','Целые коробки, нормы, масса, объём и известные температурные диапазоны соблюдены. Неизвестные требования требуют настройки.')
f[str(p)]=s
p=Path("wiki/subprojects/nicora.md");s=p.read_text(encoding="utf-8").replace("Актуализировано13.10.2026.","Актуализировано 14.10.2026.")
s=s.replace("## Как следить за исполнением","### Совместимость температур в автоматической укладке,1147–1148\n\nСтратегия V2 учитывает текущие складские температурные диапазоны товара. Товары с несовместимыми известными диапазонами и товары с известными/неизвестными требованиями получают разные места. Совместимый диапазон сохраняется в предложении. Некорректная настройка отклоняется; подпись включает текущие настройки. Повторы старых V1 команд возвращают первоначальный результат. Числовой режим автомобиля и фактический температурный допуск остаются отдельной доработкой.\n\n## Как следить за исполнением")
f[str(p)]=s
p=Path("wiki/components/nicora_ni021_auto_preparation_20261013.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n14.10.2026/1148: layoutstrategyV2 distinguishes temperature-compatible packing; source existingSKU ranges/native readonly2047 fields observed, pure1147 casesPASS/architecture7000cycles76debt. UI shows range/unknown perplace. V1savedresults immutable, oldunprepared previews require reread. APIlatestV2 load/replay pending, noDDL/newphysicalfixture.\n"
p=Path("wiki/index.md");f[str(p)]="- [Auto layout V2 /1148](components/nicora_ni021_auto_preparation_20261013.md): temperature-compatible places/current ranges UI; old V1 saved receipts unchanged.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1148: auto temperature compatibility strategyV2/UIranges added; same existing read snapshot/source hash, incompatible/known-vs-unknown separation, invalidrange refusal. Pure1147/readonlysource2047/architecturePASS; nativewriters/oldsavedreceipts untouched. Mainprojectentry updated14Oct; APIV2 readinesspending.\n"
print(json.dumps(f,ensure_ascii=True))
